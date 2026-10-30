import xarray as xr
import pandas as pd
import numpy as np
import torch
import pyproj
import os
from scipy.spatial import cKDTree

from preprocess_radargrams_configs import MATCHING_TOLERANCE, TX_OFFSET_HiCARS1_microseconds
from preprocess_radargrams_configs import C, EPSILON_ICE
from preprocess_radargrams_configs import IMAGE_TILE_WIDTH, IMAGE_TILE_HEIGHT, X_SPACING

def load_L1B_radargram(path_to_granule):
    """
    Load a radargram from a NetCDF file and return the dataset.
    
    Parameters:
    path_to_granule (str): Path to the radargram NetCDF file.
    
    Returns:
    xarray.Dataset: The loaded radargram dataset.
    """
    # 1. L1B data: Open nc file as xarray dataset
    radargram_ds = xr.open_dataset(path_to_granule)
    print("------------------------------")
    print("Now processing Granule ID:", radargram_ds.granule_id)
    print("L1B radargram shape (rows, columns):", radargram_ds["amplitude_high_gain"].T.shape)

    # Sanity check
    columns_without_lonlat = (radargram_ds["lon"].isnull() | radargram_ds["lat"].isnull()).sum().item()
    print(f"L1B radargram number of columns missing LON, LAT or BOTH: {columns_without_lonlat}")

    # If there are any columns without lon/lat, crop the granule or skip this granule
    if columns_without_lonlat > 0:
        # NOTE: Often it is just the last 11/12 columns missing so we can "save" the granule
        radargram_ds_cropped = radargram_ds.isel({"time": slice(0, - columns_without_lonlat)})
        columns_without_lonlat_after_crop = (radargram_ds_cropped["lon"].isnull() | radargram_ds_cropped["lat"].isnull()).sum().item()
        if columns_without_lonlat_after_crop == 0:
            radargram_ds = radargram_ds_cropped
            print(f"INFO: Cropped {columns_without_lonlat} columns from the end of the radargram to remove missing LON, LAT values")
        else:
            print(f"WARNING: Skipping granule {radargram_ds.granule_id} due to missing lon/lat values")

    return radargram_ds

def get_l2_path_from_l1b(granule_id, path_to_l2_folder):
    """
    Generate the corresponding L2 bed elevation file path from the L1B granule ID and the path to the L2 folder.
    
    Parameters:
    granule_id (str): The ID of the L1B granule.
    path_to_l2_folder (str): The path to the L2 folder.
    
    Returns:
    str: The path to the L2 bed elevation file.
    """
    # Replace 1B with 2 in the granule ID to get the corresponding L2 granule ID
    radargram_granule_id_L2 = granule_id[:5] + "2" + granule_id[7:]
    # Remove the last three characters (such as 000, 001 or 002) because L2 data filed exists per survey id, not per granule id
    radargram_survey_id_L2 = radargram_granule_id_L2[:-3]
    # print("L2 survey ID:", radargram_survey_id_L2)
    # radargram_survey_id_L2 ends with _ 
    path_to_l2 = path_to_l2_folder + "/" + radargram_survey_id_L2 + "icethk.txt"
    # print("L2 file path:", PATH_L2)
    
    return path_to_l2

def load_l2_ice_thickness(path_to_l2_file):
    """
    Load the L2 ice thickness data from a text file and return it as a pandas DataFrame.
    
    Parameters:
    path_to_l2_file (str): The path to the L2 ice thickness text file.
    
    Returns:
    pandas.DataFrame: The loaded ice thickness data.
    """
    # Check if the L2 file exists
    if not os.path.exists(path_to_l2_file):
        print(f"WARNING: L2 file {path_to_l2_file} does not exist")
        return None

    # Load header lines (starting with #) from the L2 file first
    with open(path_to_l2_file, "r") as f:
        header_lines = [line for line in f if line.startswith("#")]

    # grab last header line for the column headers
    col_names = header_lines[-1].lstrip("#").split()

    # now import the data into a pandas dataframe, skipping the header lines, but adding the column names from the last header line
    l2_df_raw = pd.read_csv(
        path_to_l2_file,
        sep = r"\s+", 
        # skips any line starting with '#'
        comment = "#", 
        header = None, 
        names = col_names,
    )

    print("L2 shape (rows):", l2_df_raw.shape[0])

    # SANITY CHECK: Completely remove rows with NaN values in the LON or LAT as they are not useful for our purposes
    # print(f"L2 dataframe shape before dropping rows with NaN in LON or LAT: {l2_df_raw.shape[0]}")
    # Drop them so the the lookup will just not return a match for those rows, instead of returning a match with NaN values.
    l2_df = l2_df_raw.dropna(subset = ["LON", "LAT"]) 
    # print(f"L2 dataframe shape after dropping rows with NaN in LON or LAT: {l2_df.shape[0]}")
    print(f"L2 number of columns missing LON, LAT or BOTH: {l2_df_raw.shape[0] - l2_df.shape[0]}")

    # if the L2 dataframe has no valid rows after dropping NaN values, skip this granule
    if l2_df.shape[0] == 0:
        print(f"WARNING: L2 dataframe {path_to_l2_file} has no valid rows after dropping NaN in LON or LAT")
        return None

    return l2_df

lonlat_to_polarstereo = pyproj.Transformer.from_crs(crs_from = pyproj.CRS("epsg:4326"),
                                                    crs_to = pyproj.CRS("epsg:3031"),
                                                    always_xy = True) # xy order convention

def add_polarstereo_coordinates(l2_df):
    """
    Add polar stereographic coordinates to the L2 dataframe.
    
    Parameters:
    l2_df (pandas.DataFrame): The L2 dataframe with LON and LAT columns.
    
    Returns:
    pandas.DataFrame: The L2 dataframe with added X and Y columns for polar stereographic coordinates.
    """
    # Convert LON, LAT to polar stereographic coordinates
    l2_df["X"], l2_df["Y"] = lonlat_to_polarstereo.transform(l2_df["LON"].values, l2_df["LAT"].values)
    
    return l2_df

def merge_radargram_and_l1b(radargram_ds, l2_df):

    # KCTree worked the best here because there are some minor inconsistencies between the L1B and L2 data (e.g. float32 and float64 coordinates), so we need to find the nearest neighbor in the L2 data for each L1B trace.
    # Make dtype consistent for both: radargram coords are originally float32, but L2 coords are from a txt file with 6 decimals, so we need to convert them to float64 for the KDTree to work properly.
    l1b_lon = radargram_ds["lon"].values.astype(np.float64)
    l1b_lat = radargram_ds["lat"].values.astype(np.float64)

    l2_lon = l2_df["LON"].values.astype(np.float64)
    l2_lat = l2_df["LAT"].values.astype(np.float64)

    # stack
    l1b_coords = np.column_stack([l1b_lon, l1b_lat])
    l2_coords = np.column_stack([l2_lon, l2_lat])

    # build tree on l2_df (the side we're looking up / pulling matches from)
    tree = cKDTree(l2_coords)

    distances, indices = tree.query(l1b_coords, distance_upper_bound = MATCHING_TOLERANCE)

    # boolean indicator of whether each L1B trace has a match in the L2 data within the matching tolerance
    has_match = distances < MATCHING_TOLERANCE

    # where has_match is True, use the index from indices, otherwise use 0 to avoid indexing errors
    safe_indices = np.where(has_match, indices, 0)  # placeholder for unmatched rows

    matched_l2_subset = l2_df.iloc[safe_indices].reset_index(drop = True)

    # fill rows that weren't matched with NaN
    matched_l2_subset.loc[~ has_match] = np.nan

    # Communicate how many matches were found
    if has_match.sum() == len(l1b_coords):
        print(f"Matched: {has_match.sum()} / {len(l1b_coords)}")
    else:
        # print in red to indicate a partial match
        print(f"\033[91mMatched: {has_match.sum()} / {len(l1b_coords)}\033[0m")

    # select columns that will be added to the radargram xarray dataset
    selected_cols = ["THK", "BED_ELEVATION", "SURFACE_ELEVATION", "PARTIAL_BED_REFLECT", "SRF_REFLECT", "SRF_RNG", "X", "Y"]

    # Add the selected columns from the matched L2 subset to the radargram xarray dataset
    for col in selected_cols:
        # Add along time dimension in xarray
        radargram_ds[f"l2_{col}"] = ("time", matched_l2_subset[col].values)

    # free-up memory
    del tree

    return radargram_ds

########
# Calculate refractive index of ice
n = np.sqrt(EPSILON_ICE)
# Calculate speed of light in ice
v_ice = C / n 

def convert_radargram_to_elevations(radargram_ds_l2):
    """
    Convert radargram data to elevations using the L2 bed and surface elevations.
    
    Parameters:
    radargram_ds_l2 (xarray.Dataset): The radargram dataset with L2 data merged.
    
    Returns:
    xarray.Dataset: The radargram dataset with added elevation data.
    """
    ### Convert fasttime to TWTT ###
    # Make a new coordinate variable for two-way travel time (TWTT) in microseconds, adjusted for the TX-record offset
    radargram_ds_l2 = radargram_ds_l2.assign_coords(
        twtt_us = ("fasttime_dim", radargram_ds_l2.fasttime.values - TX_OFFSET_HiCARS1_microseconds)
    )

    radargram_ds_l2["twtt_us"].attrs["units"] = "microseconds"
    radargram_ds_l2["twtt_us"].attrs["long_name"] = "two-way travel time since pulse transmission"

    ### AIR GAP HANDLING ###
    # air gap = plane altitude above surface = one-way distance from antenna to surface, in meters
    # NOTE: Alternatively use surface range (SRF_RNG) from L2 data, directly
    air_gap_m = radargram_ds_l2.altitude.values - radargram_ds_l2.l2_SURFACE_ELEVATION.values

    # Two-way travel time spent in air (round trip through air only, given air gap in meters (GIVEN) and speed of light in vacuum)
    air_twtt_seconds = (2 * air_gap_m) / C

    # Convert TWTT (in microseconds) from y-axis to seconds
    twtt_in_seconds = radargram_ds_l2.twtt_us.values * 1e-6

    ### ICE HANDLING ###
    # Subtract the air portion, leaving only the ice portion of the TWTT
    # twtt_in_seconds is a column vector (y-axis), air_twtt_seconds is a row vector (x-axis), so we can broadcast the subtraction to get a 2D array of ice TWTT values
    # NOTE: negative values mean time still in air, so we can mask those out later if needed
    ice_twtt_seconds = twtt_in_seconds.ravel()[:, np.newaxis] - air_twtt_seconds.ravel()[np.newaxis, :]

    # mask is true where sample is still in air (before surface return)
    in_air_mask = ice_twtt_seconds < 0

    # CONTAINER 2d array
    one_way_distance_m = np.empty_like(ice_twtt_seconds)

    ### FILL AIR CELLS given air resistance (speed of light in air) ###
    one_way_distance_m[in_air_mask] = C * twtt_in_seconds[:, np.newaxis].repeat(ice_twtt_seconds.shape[1], axis = 1)[in_air_mask] / 2

    ### FILL ICE CELLS given ice resistance (speed of light in ice) ###
    one_way_distance_m[ ~ in_air_mask] = (air_gap_m[np.newaxis, :] + v_ice * ice_twtt_seconds / 2)[ ~ in_air_mask]

    # Get elevation above sea level (m) for column of the radargram, by subtracting the one-way distance from the plane altitude
    # This makes it Absolute
    elevation_m = radargram_ds_l2.altitude.values[None, :] - one_way_distance_m

    return elevation_m

def generate_bed_idx_and_mask(elevations_m, radargram_ds_l2):
    """
    Generate a bed mask based on the elevations and L2 bed elevation data.
    
    Parameters:
    elevations_m (numpy.ndarray): The 2D array of elevations in meters.
    radargram_ds_l2 (xarray.Dataset): The radargram dataset with L2 data merged.
    
    Returns:
    numpy.ndarray: A boolean mask indicating where the bed is present.
    """
    # Retrieve interpreted bed elevation values (in meters above sea level)
    # shape (4000,)
    # NOTE: some of the bed elevation values are NaN, so we need to handle that
    bed_elevation = radargram_ds_l2.l2_BED_ELEVATION.values

    # For each column, find the row index where elevation_m is closest to bed_elevation
    # NOTE: we need floats to allow for NaN values, so we cast to float
    bed_idx = np.argmin(np.abs(elevations_m - bed_elevation[np.newaxis, :]), axis = 0).astype(float)

    # Propagate NaN where bed_elevation itself was NaN
    bed_idx[np.isnan(bed_elevation)] = np.nan

    ### MASK ###
    x_axis_index = np.arange(elevations_m.shape[1])
    # container
    bed_mask = np.zeros_like(elevations_m, dtype = bool)
    # Set only the row index where the bed is located to True, for each column
    # some nan values are shown as 0
    valid = np.isfinite(bed_idx)
    bed_mask[bed_idx[valid].astype(int), x_axis_index[valid]] = True

    return bed_idx, bed_mask

# Define before loop to avoid re-creating the transformer for each granule
HALF_TILE_WIDTH = IMAGE_TILE_WIDTH // 2
HALF_TILE_HEIGHT = IMAGE_TILE_HEIGHT // 2

def crop_tiles_extract_metadata(radargram_ds_l2, elevations_m, bed_idx):
    # Extract and transpose high gain amplitude 2D array 
    amplitude = radargram_ds_l2["amplitude_high_gain"].values.T
    # Extract shape
    n_rows, n_cols = amplitude.shape

    # Get list of x_center_indices that will result in a full tile
    # Note: Avoids looping
    x_center_indices_candidates = np.arange(HALF_TILE_WIDTH, n_cols - HALF_TILE_WIDTH, X_SPACING)
    # center y on the interface between bed and ice
    # Note: this inlcludes NaN values, which will be filtered out 
    y_center_indices_candidates = bed_idx[x_center_indices_candidates]

    # 1. Drop tiles that don't have a valid bed pick (NaN) for the center_index
    valid_indices = ~ np.isnan(y_center_indices_candidates)
    # Keep valid indices only
    # Assure data type is int, as it will be used for indexing
    x_center_indices = np.round(x_center_indices_candidates[valid_indices]).astype(int)
    y_center_indices = np.round(y_center_indices_candidates[valid_indices]).astype(int)

    # 2. Check that vertical range fits within the radargram, and drop tiles that don't fit
    in_vertical_range = (y_center_indices - HALF_TILE_HEIGHT >= 0) & \
                (y_center_indices + HALF_TILE_HEIGHT <= n_rows)
    # overwrite is okay here
    x_center_indices = x_center_indices[in_vertical_range]
    y_center_indices = y_center_indices[in_vertical_range]

    # 3. Calculate the indices of the tiles
    x_min_index, x_max_index = x_center_indices - HALF_TILE_WIDTH, x_center_indices + HALF_TILE_WIDTH -1
    y_min_index, y_max_index = y_center_indices - HALF_TILE_HEIGHT, y_center_indices + HALF_TILE_HEIGHT -1

    if x_center_indices.size == 0:
        return None, None

    # 3D numpy array e.g. (9, 336, 336)
    tiles = np.stack([amplitude[y - HALF_TILE_HEIGHT:y + HALF_TILE_HEIGHT, x - HALF_TILE_WIDTH:x + HALF_TILE_WIDTH] for x, y in zip(x_center_indices, y_center_indices)]).astype(np.float32, copy = False)

    # metadata
    metadata = pd.DataFrame({
            # NOTE: survey_id can be derived from granule_id, so we don't need to store it separately
            # "survey_id": radargram_ds_l2.survey_id,
            "granule_id": radargram_ds_l2.granule_id,
            "x_center_idx": x_center_indices,
            "y_center_idx": y_center_indices,
            "tile_id": [f"{radargram_ds_l2.granule_id}_{x:04d}" for x in x_center_indices],
            "X": radargram_ds_l2["l2_X"].values[x_center_indices], 
            "Y": radargram_ds_l2["l2_Y"].values[x_center_indices],
            "LON": radargram_ds_l2["lon"].values[x_center_indices], 
            "LAT": radargram_ds_l2["lat"].values[x_center_indices],
            "bed_elevation": radargram_ds_l2["l2_BED_ELEVATION"].values[x_center_indices],
            "surface_elevation": radargram_ds_l2["l2_SURFACE_ELEVATION"].values[x_center_indices],
            "ice_thickness": radargram_ds_l2["l2_THK"].values[x_center_indices],
            "partial_bed_reflect": radargram_ds_l2["l2_PARTIAL_BED_REFLECT"].values[x_center_indices],
            "srf_reflect": radargram_ds_l2["l2_SRF_REFLECT"].values[x_center_indices],
            "tile_along_track_span_m": np.hypot(radargram_ds_l2["l2_X"].values[x_max_index] - radargram_ds_l2["l2_X"].values[x_min_index], radargram_ds_l2["l2_Y"].values[x_max_index] - radargram_ds_l2["l2_Y"].values[x_min_index]),
            "tile_vertical_span_m": elevations_m[y_max_index, x_center_indices] - elevations_m[y_min_index, x_center_indices], 
            "bed_std_m": [np.nanstd(radargram_ds_l2["l2_BED_ELEVATION"].values[x_min : x_max]) for x_min, x_max in zip(x_min_index, x_max_index)],})

    return tiles, metadata
