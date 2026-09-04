# TRINETRA configuration

CATALOGUE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Final TRINETRA monitoring region
REGION_NAME = "Joshimath–Vishnuprayag–Badrinath Corridor"

MIN_LAT = 30.50
MAX_LAT = 30.80
MIN_LON = 79.40
MAX_LON = 79.75

AOI = (
    f"POLYGON(("
    f"{MIN_LON} {MIN_LAT},"
    f"{MAX_LON} {MIN_LAT},"
    f"{MAX_LON} {MAX_LAT},"
    f"{MIN_LON} {MAX_LAT},"
    f"{MIN_LON} {MIN_LAT}"
    f"))"
)

MAX_CLOUD_COVER = 40
SEARCH_DAYS = 40
MAX_PRODUCTS = 20