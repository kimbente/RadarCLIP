# locations of tar radargram file
PATH_2015_AN_UTIG_ER2HI1B = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/2015_AN_UTIG.ER2HI1B.tar"
PATH_2016_AN_UTIG_ER2HI1B = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/2016_AN_UTIG.ER2HI1B.tar"
# locations of bed elevation files 
PATH_2015_AN_UTIG_ER2HI2 = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/AAS_4346_EAGLE_ICECAP_LEVEL2_AEROGEOPHYSICS/EAGLE-2015-2016-Level2/Level2/2015_AN_UTIG.ER2HI2"
PATH_2016_AN_UTIG_ER2HI2 = "/Users/kim.bente/Documents/ANT_QGIS/AADC-DATA/AAS_4346_EAGLE_ICECAP_LEVEL2_AEROGEOPHYSICS/EAGLE-2015-2016-Level2/Level2/2016_AN_UTIG.ER2HI2"

# Survey / Instrument / Processing Code
CODE_1B = "ER2HI1B"
CODE_2 = "ER2HI2"

# Assumed variables
# 120 - 130 offsets all still seem to work well
ROWS_CLIPPED_BLANKING = 128

# Visualization parameters
COLOR_MAP = "gray_r"
AMPLITUDE_VMIN = 110
AMPLITUDE_VMAX = 215

# tile parameters
IMAGE_TILE_WIDTH = 336
IMAGE_TILE_HEIGHT = IMAGE_TILE_WIDTH

# approx. the mean reflectivity of the bed in the radargrams, used for normalization
BED_REFLECTIVITY_REFERENCE = 50
