import os
import math
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from backend.services.river import (
    get_latest_river,
    refresh_river,
)

from backend.services.rainfall import (
    get_latest_rainfall,
    refresh_rainfall,
)

from backend.services.satellite import (
    get_latest_satellite,
    refresh_satellite,
)

from backend.services.terrain import (
    get_latest_terrain,
    refresh_terrain,
)

from backend.services.hazard_zones import (
    get_hazard_zones,
)

from backend.services.settlement_risk import (
    get_settlement_risk,
)

from backend.services.relocation import (
    refresh_relocation_data,
    get_relocation_summary,
    get_top_relocations,
    get_relocation_decisions,
    get_safe_sites,
)


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

app = FastAPI(title="TRINETRA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MONGODB
# ============================================================

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]


# ============================================================
# HELPERS
# ============================================================

FINAL_EVENT_OUTPUT = (
    "data/outputs/trinetra_event_dashboard_data.csv"
)


def clean(data):
    """
    Recursively remove NaN / infinite values so FastAPI
    can safely serialize the response.
    """

    if isinstance(data, list):
        return [clean(x) for x in data]

    if isinstance(data, dict):
        return {
            k: clean(v)
            for k, v in data.items()
        }

    if isinstance(data, float):
        if not math.isfinite(data):
            return None

    return data


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        if pd.isna(value):
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def safe_bool(value, default=False):
    """
    Safely convert CSV values to boolean.
    """

    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return default

    value = str(value).strip().lower()

    if value in {"true", "1", "yes", "y"}:
        return True

    if value in {"false", "0", "no", "n"}:
        return False

    return default


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    try:
        client.admin.command("ping")

        return {
            "status": "ok",
            "mongodb": "connected",
        }

    except Exception as e:

        return {
            "status": "error",
            "mongodb": str(e),
        }


# ============================================================
# API STATUS
# ============================================================

@app.get("/api/status")
def api_status():

    return {
        "project": "TRINETRA",
        "backend": "online",
        "mongodb": "connected",
    }


# ============================================================
# HAZARDS
# ============================================================

@app.get("/api/hazards")
def get_hazards():

    return clean({
        "status": "ok",
        "river": get_latest_river(),
        "rainfall": get_latest_rainfall(),
        "satellite": get_latest_satellite(),
        "terrain": get_latest_terrain(),
    })


# ============================================================
# REFRESH ALL
# ============================================================

@app.post("/api/refresh")
def refresh_all():

    return {
        "status": "ok",
        "river": refresh_river(),
        "rainfall": refresh_rainfall(),
        "satellite": refresh_satellite(),
        "terrain": refresh_terrain(),
    }


# ============================================================
# FINAL TRINETRA MVP RESULT
# ============================================================

@app.get("/api/trinetra")
def trinetra_result():

    """
    Return the final frozen TRINETRA MVP event.

    IMPORTANT:
    This endpoint intentionally reads the already-generated
    final event output instead of recalculating hazard scores.

    The final event pipeline already applies:
        River       = 40%
        Rainfall    = 30%
        Landslide   = 30%

    This keeps the API and dashboard synchronized with the
    final MVP output.
    """

    try:

        if not os.path.exists(FINAL_EVENT_OUTPUT):

            return {
                "project": "TRINETRA",
                "status": "error",
                "message": (
                    "Final TRINETRA event output not found: "
                    f"{FINAL_EVENT_OUTPUT}"
                ),
            }

        df = pd.read_csv(FINAL_EVENT_OUTPUT)

        if df.empty:

            return {
                "project": "TRINETRA",
                "status": "error",
                "message": "Final TRINETRA event output is empty",
            }

        row = df.iloc[0]

        # ----------------------------------------------------
        # FINAL MVP COMPONENT SCORES
        # ----------------------------------------------------

        river_score = safe_float(
            row.get("river_risk_score_0_100", 0)
        )

        rainfall_score = safe_float(
            row.get("rainfall_risk_score_0_100", 0)
        )

        landslide_score = safe_float(
    row.get("landslide_hazard_score_0_100", 0)
)
        final_score = safe_float(
            row.get("trinetra_hazard_score_0_100", 0)
        )

        satellite_score = safe_float(
    row.get("satellite_evidence_score_0_100", 0)
)

        risk_level = str(
            row.get(
                "trinetra_hazard_level",
                "UNKNOWN",
            )
        )

        # ----------------------------------------------------
        # EVENT INFORMATION
        # ----------------------------------------------------

        event_id = str(
            row.get("event_id", "")
        )

        event_date = str(
            row.get("event_date", "")
        )

        rainfall_available = safe_bool(
            row.get("rainfall_available", False)
        )

        rainfall_start = str(
            row.get("rainfall_coverage_start", "")
        )

        rainfall_end = str(
            row.get("rainfall_coverage_end", "")
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        response = {

            "project": "TRINETRA",

            "status": "ok",

            "hazard_score": round(
                final_score,
                2,
            ),

            "risk_level": risk_level,

            "alert": risk_level in {
                "HIGH",
                "CRITICAL",
            },

            "components": {

    "river_score": round(
        river_score,
        2,
    ),

    "rainfall_score": round(
        rainfall_score,
        2,
    ),

    "landslide_score": round(
        landslide_score,
        2,
    ),

    "satellite_score": round(
        satellite_score,
        2,
    ),

    # Backward-compatible fields used by the existing dashboard
    "terrain_score": round(
        max(
            [
                safe_float(x.get("terrain_hazard_score", 0))
                for x in get_latest_terrain()
                if isinstance(x, dict)
            ],
            default=0,
        ),
        2,
    ),

    "satellite_products": len(
        get_latest_satellite()
    ),
},

            "event": {

                "event_id": event_id,

                "event_date": event_date,

                "rainfall_available":
                    rainfall_available,

                "rainfall_coverage_start":
                    rainfall_start,

                "rainfall_coverage_end":
                    rainfall_end,
            },

            "data_sources": {

                "river": "CWC",

                "rainfall":
                    "existing rainfall pipeline",

                "landslide":
                    "DEM + landslide ML pipeline",

                "satellite":
                    "Copernicus Sentinel-1/Sentinel-2",

                "terrain":
                    "DEM",
            },
        }

        return clean(response)

    except Exception as e:

        return {
            "project": "TRINETRA",
            "status": "error",
            "message": str(e),
        }


# ============================================================
# HAZARD ZONES
# ============================================================

@app.get("/api/hazard-zones")
def hazard_zones():

    return get_hazard_zones()


# ============================================================
# RELOCATION REFRESH
# ============================================================

@app.post("/api/relocation/refresh")
def refresh_relocation():

    return refresh_relocation_data()


# ============================================================
# SAFE SITES
# ============================================================

@app.get("/api/safe-sites")
def safe_sites(limit: int = 2000):

    return get_safe_sites(limit)


# ============================================================
# RELOCATION SUMMARY
# ============================================================

@app.get("/api/relocation/summary")
def relocation_summary():

    return get_relocation_summary()


# ============================================================
# TOP RELOCATIONS
# ============================================================

@app.get("/api/relocation/top")
def top_relocations(limit: int = 20):

    return get_top_relocations(limit)


# ============================================================
# RELOCATION DECISIONS
# ============================================================

@app.get("/api/relocation/decisions")
def relocation_decisions(limit: int = 20):

    return get_relocation_decisions(limit)


# ============================================================
# SETTLEMENT RISK
# ============================================================

@app.get("/api/risk/settlements")
def risk_settlements(limit: int = 8):

    return get_settlement_risk(limit)