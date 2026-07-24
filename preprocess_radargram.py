# Run in conda ibiz environment
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import os
import pyproj
from scipy.spatial import cKDTree

# CONFIGS
from preprocess_radargrams_configs import PATH_2016_AN_UTIG_ER2HI1B, PATH_2016_AN_UTIG_ER2HI2, CODE_1B, CODE_2
from preprocess_radargrams_configs import MATCHING_TOLERANCE, ROWS_CLIPPED_BLANKING, C, EPSILON_ICE
from preprocess_radargrams_configs import AMPLITUDE_VMIN, AMPLITUDE_VMAX, COLOR_MAP
from preprocess_radargrams_configs import IMAGE_TILE_WIDTH, IMAGE_TILE_HEIGHT

#################################
### PROCESS 2016 AN UTIG DATA ###
#################################

# Go one level deeper into the tar file to get the folder containing the .nc files
PATH_2016_AN_UTIG_ER2HI1B_folder = os.path.join(PATH_2016_AN_UTIG_ER2HI1B, "2016_AN_UTIG.ER2HI1B")

list_of_nc_files_2016_UTIG_full_paths = [
    os.path.join(PATH_2016_AN_UTIG_ER2HI1B_folder, f)
    for f in os.listdir(PATH_2016_AN_UTIG_ER2HI1B_folder)
    if f.endswith(".nc")
]

print(f"Number of .nc files (granules) in 2016 AN UTIG ER2HI1B folder: {len(list_of_nc_files_2016_UTIG_full_paths)}")