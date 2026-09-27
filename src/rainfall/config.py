# TRINETRA - Rainfall Configuration

from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# =========================================================
# NWDP RAINFALL API
# =========================================================

RAINFALL_API_URL = (
    "https://nwdp.nwic.gov.in/api/3/action/datastore_search"
)

# NEW HIGH-FREQUENCY RAINFALL RESOURCE
RAINFALL_RESOURCE_ID = (
    "8b406187-0fee-40b9-8cd9-a249e0ce1903"
)

RAINFALL_API_TIMEOUT = 120

# Fetch in batches
RAINFALL_BATCH_SIZE = 1000


# =========================================================
# API FILTERS
# =========================================================

RAINFALL_STATE = "Uttarakhand"

RAINFALL_DISTRICT = "Chamoli"

RAINFALL_AGENCY = "Uttarakhand"


# =========================================================
# REGION
# =========================================================

REGION_NAME = (
    "Joshimath–Vishnuprayag–Badrinath Corridor"
)


# =========================================================
# API SOURCE COLUMNS
#
# These will be finalized after inspecting the new
# high-frequency API response.
# =========================================================

ID_COLUMN = "_id"

STATE_COLUMN = "State"

DISTRICT_COLUMN = "District"

AGENCY_COLUMN = "Agency"

DATE_COLUMN = "Date"


# =========================================================
# RAINFALL FORMULA COMPONENTS
#
# Proposed rainfall trigger from the corrected
# TRINETRA formula sheet:
#
# W =
#   0.35 * 1h intensity
# + 0.20 * 6h total
# + 0.15 * 24h total
# + 0.20 * antecedent rainfall
# + 0.10 * 6h forecast
#
# These are feature names, not assumed API columns.
# They will be generated during processing.
# =========================================================

RAINFALL_1H_COLUMN = "rainfall_mm_1h"

RAINFALL_6H_COLUMN = "rainfall_mm_6h"

RAINFALL_24H_COLUMN = "rainfall_mm_24h"

ANTECEDENT_15D_COLUMN = "antecedent_rainfall_15d"

FORECAST_6H_COLUMN = "forecast_rainfall_mm_6h"


# =========================================================
# OUTPUT
# =========================================================

RAW_RAINFALL_PATH = (
    PROJECT_ROOT
    / "data"
    / "rainfall"
    / "raw"
    / "rainfall_hourly_raw.csv"
)

PROCESSED_RAINFALL_PATH = (
    PROJECT_ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_features.csv"
)

RAINFALL_RISK_PATH = (
    PROJECT_ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk.csv"
)