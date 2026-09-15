import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

BASE_DIR = Path(__file__).resolve().parents[2]

POPULATION_FILE = BASE_DIR / "data" / "features" / "population_master.csv"
SAFE_SITES_FILE = BASE_DIR / "data" / "features" / "safe_sites.csv"
RIVER_FILE = BASE_DIR / "data" / "river" / "processed" / "river_hybrid_hazard.csv"
RAINFALL_FILE = BASE_DIR / "data" / "rainfall" / "processed" / "rainfall_hybrid_hazard.csv"
TERRAIN_FILE = BASE_DIR / "data" / "features" / "dem_integrated_features.csv"

# The same thresholds and 70/30 hydro-terrain weighting used by /api/trinetra.
def risk_level(score: float) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MODERATE"
    return "LOW"


def _clean_number(value):
    if value is None:
        return None
    try:
        value = float(value)
        return round(value, 2) if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _load_settlement_locations():
    """Use coordinates already matched to settlement IDs in safe_sites.csv.

    population_master.csv contains settlement identity/population but no coordinates.
    Therefore the backend uses the mean coordinate of verified safe-site records
    matched to each settlement as the available map-location proxy.
    """
    population = pd.read_csv(POPULATION_FILE)
    sites = pd.read_csv(SAFE_SITES_FILE)

    required_population = ["settlement_id", "settlement_name", "population"]
    required_sites = [
        "matched_settlement_id",
        "latitude",
        "longitude",
    ]

    if any(c not in population.columns for c in required_population):
        return pd.DataFrame()
    if any(c not in sites.columns for c in required_sites):
        return pd.DataFrame()

    sites = sites.dropna(
        subset=["matched_settlement_id", "latitude", "longitude"]
    ).copy()

    sites["latitude"] = pd.to_numeric(sites["latitude"], errors="coerce")
    sites["longitude"] = pd.to_numeric(sites["longitude"], errors="coerce")
    sites = sites.dropna(subset=["latitude", "longitude"])

    # Keep the configured study area used by the hazard-zone map.
    sites = sites[
        sites["latitude"].between(30.50, 30.80)
        & sites["longitude"].between(79.40, 79.75)
    ]

    coords = (
        sites.groupby("matched_settlement_id", as_index=False)
        .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"))
    )

    settlements = population.merge(
        coords,
        left_on="settlement_id",
        right_on="matched_settlement_id",
        how="inner",
    )

    settlements = settlements.drop_duplicates(subset=["settlement_id"])
    return settlements


def _load_river_index():
    df = pd.read_csv(RIVER_FILE)

    lat_col = "Latitude" if "Latitude" in df.columns else "lat"
    lon_col = "Longitude" if "Longitude" in df.columns else "lon"

    if not all(c in df.columns for c in [lat_col, lon_col, "hybrid_hazard_score"]):
        return None, None

    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df["hybrid_hazard_score"] = pd.to_numeric(
        df["hybrid_hazard_score"], errors="coerce"
    )
    df = df.dropna(subset=[lat_col, lon_col, "hybrid_hazard_score"])

    coords = df[[lat_col, lon_col]].to_numpy(dtype=float)
    return cKDTree(coords), df


def _load_terrain_index():
    df = pd.read_csv(
        TERRAIN_FILE,
        usecols=["lat", "lon", "terrain_hazard_score"],
    )

    for col in ["lat", "lon", "terrain_hazard_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["lat", "lon", "terrain_hazard_score"])
    coords = df[["lat", "lon"]].to_numpy(dtype=float)
    return cKDTree(coords), df


def get_settlement_risk(limit: int = 8):
    settlements = _load_settlement_locations()

    if settlements.empty:
        return {
            "status": "ok",
            "count": 0,
            "settlements": [],
            "message": "No settlement coordinates are available from matched safe-site records.",
        }

    # Rainfall is a corridor-level signal in the current pipeline, so it is
    # applied consistently to each settlement, just as /api/trinetra does.
    rainfall = pd.read_csv(RAINFALL_FILE)
    rainfall_scores = pd.to_numeric(
        rainfall.get("hybrid_hazard_score"), errors="coerce"
    ).dropna()
    rainfall_score = float(rainfall_scores.max()) if not rainfall_scores.empty else 0.0

    river_tree, river_df = _load_river_index()
    terrain_tree, terrain_df = _load_terrain_index()

    query_points = settlements[["latitude", "longitude"]].to_numpy(dtype=float)

    river_scores = np.zeros(len(settlements))
    terrain_scores = np.zeros(len(settlements))

    if river_tree is not None:
        _, river_idx = river_tree.query(query_points, k=1)
        river_scores = river_df.iloc[river_idx]["hybrid_hazard_score"].to_numpy(dtype=float)

    if terrain_tree is not None:
        _, terrain_idx = terrain_tree.query(query_points, k=1)
        terrain_scores = terrain_df.iloc[terrain_idx]["terrain_hazard_score"].to_numpy(dtype=float)

    # Existing TRINETRA formula: 70% hydro + 30% terrain.
    hydro_scores = np.maximum(river_scores, rainfall_score)
    final_scores = 0.70 * hydro_scores + 0.30 * terrain_scores

    settlements = settlements.copy()
    settlements["river_score"] = river_scores
    settlements["rainfall_score"] = rainfall_score
    settlements["terrain_score"] = terrain_scores
    settlements["risk_score"] = final_scores
    settlements["risk_level"] = [risk_level(x) for x in final_scores]

    settlements = settlements.sort_values(
        ["risk_score", "population"], ascending=[False, False]
    ).head(max(1, min(limit, 50)))

    result = []
    for _, row in settlements.iterrows():
        result.append({
            "id": str(row["settlement_id"]),
            "name": str(row["settlement_name"]),
            "latitude": _clean_number(row["latitude"]),
            "longitude": _clean_number(row["longitude"]),
            "population": int(row["population"]),
            "risk_score": _clean_number(row["risk_score"]),
            "risk_level": row["risk_level"],
            "hazards": {
                "river": _clean_number(row["river_score"]),
                "rainfall": _clean_number(row["rainfall_score"]),
                "terrain": _clean_number(row["terrain_score"]),
            },
            "location_source": "matched safe-site coordinates",
            "risk_method": "70% hydro + 30% terrain using nearest river/terrain observations",
        })

    return {
        "status": "ok",
        "count": len(result),
        "settlements": result,
    }
