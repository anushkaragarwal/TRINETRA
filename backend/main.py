import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from backend.services.river import get_latest_river, refresh_river
from backend.services.rainfall import get_latest_rainfall, refresh_rainfall
from backend.services.satellite import get_latest_satellite, refresh_satellite
from backend.services.terrain import get_latest_terrain, refresh_terrain
from backend.services.hazard_zones import get_hazard_zones
from backend.services.settlement_risk import get_settlement_risk
from backend.services.relocation import (
    refresh_relocation_data,
    get_relocation_summary,
    get_top_relocations,
    get_relocation_decisions,
    get_safe_sites
)
load_dotenv()

app = FastAPI(title="TRINETRA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return {
            "status": "ok",
            "mongodb": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "mongodb": str(e)
        }
@app.get("/api/status")
def api_status():
    return {
        "project": "TRINETRA",
        "backend": "online",
        "mongodb": "connected"
    }
from backend.services.river import get_latest_river
from backend.services.rainfall import get_latest_rainfall
from backend.services.satellite import get_latest_satellite


@app.get("/api/hazards")
def get_hazards():
    import math

    def clean(data):
        if isinstance(data, list):
            return [clean(x) for x in data]

        if isinstance(data, dict):
            return {k: clean(v) for k, v in data.items()}

        if isinstance(data, float) and not math.isfinite(data):
            return None

        return data

    return clean({
        "status": "ok",
        "river": get_latest_river(),
        "rainfall": get_latest_rainfall(),
        "satellite": get_latest_satellite(),
        "terrain": get_latest_terrain()
    })
@app.post("/api/refresh")
def refresh_all():

    return {
        "status": "ok",
        "river": refresh_river(),
        "rainfall": refresh_rainfall(),
        "satellite": refresh_satellite(),
        "terrain": refresh_terrain()
    }
@app.get("/api/trinetra")
def trinetra_result():

    import math

    river = get_latest_river()
    rainfall = get_latest_rainfall()
    satellite = get_latest_satellite()
    terrain = get_latest_terrain()

    def clean(data):
        if isinstance(data, list):
            return [clean(x) for x in data]

        if isinstance(data, dict):
            return {k: clean(v) for k, v in data.items()}

        if isinstance(data, float) and not math.isfinite(data):
            return None

        return data

    # -----------------------------
    # RIVER SCORE
    # -----------------------------
    river_score = 0

    if river:
        river_scores = [
            x.get("hybrid_hazard_score", 0)
            for x in river
            if isinstance(x.get("hybrid_hazard_score"), (int, float))
        ]

        if river_scores:
            river_score = max(river_scores)

    # -----------------------------
    # RAINFALL SCORE
    # -----------------------------
    rainfall_score = 0

    if rainfall:
        rainfall_scores = [
            x.get("hybrid_hazard_score", 0)
            for x in rainfall
            if isinstance(x.get("hybrid_hazard_score"), (int, float))
        ]

        if rainfall_scores:
            rainfall_score = max(rainfall_scores)

    # -----------------------------
    # TERRAIN SCORE
    # -----------------------------
    terrain_score = 0

    if terrain:
        terrain_scores = [
            x.get("terrain_hazard_score", 0)
            for x in terrain
            if isinstance(x.get("terrain_hazard_score"), (int, float))
        ]

        if terrain_scores:
            terrain_score = max(terrain_scores)

    # -----------------------------
    # HYDRO + TERRAIN
    # Existing project weighting:
    # Hydro = 70%
    # Terrain = 30%
    # -----------------------------

    hydro_score = max(river_score, rainfall_score)

    final_score = (
        0.70 * hydro_score
        + 0.30 * terrain_score
    )

    if final_score >= 75:
        risk_level = "CRITICAL"
    elif final_score >= 50:
        risk_level = "HIGH"
    elif final_score >= 25:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    alert = risk_level in ["HIGH", "CRITICAL"]

    return clean({
        "project": "TRINETRA",

        "status": "ok",

        "hazard_score": round(final_score, 2),

        "risk_level": risk_level,

        "alert": alert,

        "components": {
            "river_score": round(river_score, 2),
            "rainfall_score": round(rainfall_score, 2),
            "terrain_score": round(terrain_score, 2),
            "satellite_products": len(satellite)
        },

        "data_sources": {
            "river": "CWC",
            "rainfall": "existing rainfall pipeline",
            "satellite": "Copernicus Sentinel-1",
            "terrain": "DEM"
        }
    })
@app.get("/api/hazard-zones")
def hazard_zones():
    return get_hazard_zones()

@app.post("/api/relocation/refresh")
def refresh_relocation():
    return refresh_relocation_data()



@app.get("/api/safe-sites")
def safe_sites(limit: int = 2000):
    return get_safe_sites(limit)

@app.get("/api/relocation/summary")
def relocation_summary():
    return get_relocation_summary()
@app.get("/api/relocation/top")
def top_relocations(limit: int = 20):
    return get_top_relocations(limit)
@app.get("/api/relocation/decisions")
def relocation_decisions(limit: int = 20):
    return get_relocation_decisions(limit)

@app.get("/api/risk/settlements")
def risk_settlements(limit: int = 8):
    return get_settlement_risk(limit)
