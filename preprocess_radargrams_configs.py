# locations of tar radargram file (L1B)
PATH_2015_AN_UTIG_ER2HI1B = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/2015_AN_UTIG.ER2HI1B.tar"
PATH_2016_AN_UTIG_ER2HI1B = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/2016_AN_UTIG.ER2HI1B.tar"

# locations of bed elevation files (L2)
PATH_2015_AN_UTIG_ER2HI2 = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/AAS_4346_EAGLE_ICECAP_LEVEL2_AEROGEOPHYSICS/EAGLE-2015-2016-Level2/Level2/2015_AN_UTIG.ER2HI2"
PATH_2016_AN_UTIG_ER2HI2 = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/AAS_4346_EAGLE_ICECAP_LEVEL2_AEROGEOPHYSICS/EAGLE-2015-2016-Level2/Level2/2016_AN_UTIG.ER2HI2"

# Survey / Instrument / Processing Code
CODE_1B = "ER2HI1B"
CODE_2 = "ER2HI2"

# Matching tolerance for coordinate matching in degrees (reconciling text lon/lat values and float values in the radargram datasets)
# NOTE: max distance is not larger than 7 m which should be fine for 22m spaced data
MATCHING_TOLERANCE = 1e-2 

# tile parameters
IMAGE_TILE_WIDTH = 336
IMAGE_TILE_HEIGHT = IMAGE_TILE_WIDTH

# Spacing
# X_SPACING == IMAGE_TILE_WIDTH results in non-overlapping tiles, i.e. the smallest dataset size. 
# NOTE: Choose smaller numbers, e.g. 20 to select every 20th pixel in x direction as the center pixel.
X_SPACING = IMAGE_TILE_WIDTH

# Radioglaciology parameters
# speed of light in vacuum
C = 299_792_458  # m/s

# relative permittivity (epsilon_r) of ice (~ 3.15 is standard for glacial ice)
# documented constant used in HiCARS 1: https://nsidc.org/sites/default/files/ir1hi2-v001-userguide.pdf
EPSILON_ICE = 3.15

# approx. the mean reflectivity of the bed in the radargrams, used for normalization
BED_REFLECTIVITY_REFERENCE = 50

# see radargram_ds.attrs["TX-record_offset"] in each radragram file
TX_OFFSET_EAGLE_HiCARS2_microseconds = 2.550
TX_OFFSET_IceBridge_HiCARS1_microseconds = 50.00
TX_OFFSET_IceBridge_HiCARS2_microseconds = 3.112

# Visualization parameters
COLOR_MAP = "gray_r"
AMPLITUDE_VMIN = 110
AMPLITUDE_VMAX = 215
