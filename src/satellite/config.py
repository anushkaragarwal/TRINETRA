# TRINETRA Satellite Configuration

CATALOGUE_URL = (
    "https://catalogue.dataspace.copernicus.eu/"
    "odata/v1/Products"
)

# TRINETRA MVP monitoring area
REGION_NAME = "Joshimath–Vishnuprayag–Badrinath Corridor"

MIN_LAT = 30.50
MAX_LAT = 30.80

MIN_LON = 79.40
MAX_LON = 79.75

# Copernicus OData geometry (longitude latitude order)
AOI = (
    f"POLYGON(("
    f"{MIN_LON} {MIN_LAT},"
    f"{MAX_LON} {MIN_LAT},"
    f"{MAX_LON} {MAX_LAT},"
    f"{MIN_LON} {MAX_LAT},"
    f"{MIN_LON} {MIN_LAT}"
    f"))"
)

# Metadata search controls
SEARCH_DAYS = 90
MAX_PRODUCTS = 20

# Used later for Sentinel-2 optical imagery only
MAX_CLOUD_COVER = 40