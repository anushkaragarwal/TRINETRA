# TRINETRA - River Hydrology Configuration

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------
# MVP REGION
# ---------------------------------------------------------

REGION_NAME = "Joshimath–Vishnuprayag–Badrinath Corridor"

MIN_LAT = 30.50
MAX_LAT = 30.80

MIN_LON = 79.40
MAX_LON = 79.75

# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "river"
    / "raw"
    / "cwc_uttarakhand_sample.csv"
)

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "river"
    / "processed"
    / "river_features.csv"
)

# ---------------------------------------------------------
# CWC DATA COLUMNS
# ---------------------------------------------------------

STATION_COLUMN = "Station"

LATITUDE_COLUMN = "Latitude"

LONGITUDE_COLUMN = "Longitude"

TIME_COLUMN = "Data Acquisition Time"

DISCHARGE_COLUMN = (
    "Telemetry Hourly River Water Discharge (m3/sec)"
)

# ---------------------------------------------------------
# CWC API
# ---------------------------------------------------------

CWC_API_URL = (
    "https://nwdp.nwic.gov.in/api/3/action/datastore_search"
)

# 1970-2025 Uttarakhand CWC River Discharge resource
CWC_RESOURCE_ID = (
    "1b80bcae-de13-48ff-a08b-733a87167735"
)

CWC_API_TIMEOUT = 120

# Number of records requested per API call
CWC_BATCH_SIZE = 1000

# API filters
CWC_STATE = "Uttarakhand"
CWC_DISTRICT = "Chamoli"
CWC_AGENCY = "CWC"