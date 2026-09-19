# TRINETRA - Rainfall Configuration

from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# =========================================================
# NWDP / IMD RAINFALL API
# =========================================================

RAINFALL_API_URL = (
    "https://nwdp.nwic.gov.in/api/3/action/datastore_search"
)

# IMD / Rainfall resource
RAINFALL_RESOURCE_ID = (
    "8752174f-1d17-4aaf-8058-2eb396f50157"
)

# API request timeout in seconds
RAINFALL_API_TIMEOUT = 120

# Number of records fetched per request
RAINFALL_BATCH_SIZE = 1000


# =========================================================
# API FILTERS
# =========================================================

RAINFALL_STATE = "UTTARAKHAND"

RAINFALL_DISTRICT = "CHAMOLI"


# =========================================================
# REGION
# =========================================================

REGION_NAME = (
    "Joshimath–Vishnuprayag–Badrinath Corridor"
)


# =========================================================
# SOURCE COLUMN NAMES
# =========================================================

ID_COLUMN = "_id"

STATE_COLUMN = "State"

DISTRICT_COLUMN = "District"

DATE_COLUMN = "Date"


# =========================================================
# DAILY RAINFALL
# =========================================================

DAILY_ACTUAL_COLUMN = "Daily Actual"

DAILY_NORMAL_COLUMN = "Daily Normal"

DAILY_DEPARTURE_COLUMN = "Daily Departure Per"

DAILY_CATEGORY_COLUMN = "Daily Category"


# =========================================================
# WEEKLY RAINFALL
# =========================================================

WEEK_DATE_COLUMN = "Week Date"

WEEKLY_ACTUAL_COLUMN = "Weekly \nActual"

WEEKLY_NORMAL_COLUMN = "Weekly Normal"

WEEKLY_DEPARTURE_COLUMN = "Weekly Departure Per"

WEEKLY_CATEGORY_COLUMN = "Weekly Category"


# =========================================================
# CUMULATIVE RAINFALL
# =========================================================

CUMULATIVE_DATE_COLUMN = "Cumulative Date"

CUMULATIVE_ACTUAL_COLUMN = "Cumulative Actual"

CUMULATIVE_NORMAL_COLUMN = "Cumulative Normal"

CUMULATIVE_DEPARTURE_COLUMN = (
    "Cumulative Departue Per"
)

CUMULATIVE_CATEGORY_COLUMN = (
    "Cumulative \nCategory"
)


# =========================================================
# MONTHLY RAINFALL
# =========================================================

MONTHLY_DATE_COLUMN = "Monthly Date"

MONTHLY_ACTUAL_COLUMN = "Monthly Acutual"

MONTHLY_NORMAL_COLUMN = "Monthly Normal"

MONTHLY_DEPARTURE_COLUMN = (
    "Monthly \nDeparture Per"
)

MONTHLY_CATEGORY_COLUMN = (
    "Monthly Category"
)