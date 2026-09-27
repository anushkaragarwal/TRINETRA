from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RIVER_FILE = (
    BASE_DIR
    / "data"
    / "river"
    / "processed"
    / "river_hybrid_hazard.csv"
)

RAIN_FILE = (
    BASE_DIR
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk.csv"
)

TERRAIN_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "terrain_hazard_features.csv"
)

LANDSLIDE_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "landslide_hazard_features.csv"
)


# ============================================================
# CONFIG
# ============================================================

TOP_N_PER_HAZARD = 20


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(score):
    """
    TRINETRA common risk bands.

    <30       LOW
    30–<60    MODERATE
    60–<80    HIGH
    >=80      CRITICAL
    """

    if not np.isfinite(score):
        return "UNKNOWN"

    if score < 30:
        return "LOW"

    if score < 60:
        return "MODERATE"

    if score < 80:
        return "HIGH"

    return "CRITICAL"


# ============================================================
# NUMERIC HELPER
# ============================================================

def numeric_series(df, column):
    """
    Convert a dataframe column to numeric safely.
    """

    return pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# UNIQUE SPATIAL ZONE HELPER
# ============================================================

def get_unique_top_zones(
    df,
    lat_col,
    lon_col,
    score_col,
    zone_type,
    top_n=TOP_N_PER_HAZARD,
):
    """
    Return top spatially unique hazard zones.

    Repeated temporal observations at the same physical
    location are collapsed into one map zone.

    Coordinates are rounded to 5 decimal places before
    deduplication. For each spatial location, the highest
    available hazard score is retained.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Create spatial grouping keys
    # --------------------------------------------------------

    df["_lat_key"] = df[lat_col].round(5)
    df["_lon_key"] = df[lon_col].round(5)

    # --------------------------------------------------------
    # Sort by hazard severity
    # --------------------------------------------------------

    df = df.sort_values(
        score_col,
        ascending=False,
    )

    # --------------------------------------------------------
    # Keep only one record per spatial location
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=[
            "_lat_key",
            "_lon_key",
        ],
        keep="first",
    )

    # --------------------------------------------------------
    # Keep top spatial locations
    # --------------------------------------------------------

    df = df.head(top_n)

    # --------------------------------------------------------
    # Build API objects
    # --------------------------------------------------------

    zones = []

    for _, row in df.iterrows():

        score = float(
            row[score_col]
        )

        zones.append(
            {
                "type": zone_type,
                "lat": float(row[lat_col]),
                "lon": float(row[lon_col]),
                "hazard_score": round(
                    score,
                    2,
                ),
                "risk_level": classify_risk(
                    score
                ),
            }
        )

    return zones


# ============================================================
# RIVER ZONES
# ============================================================

def get_river_zones():

    if not RIVER_FILE.exists():
        return []

    df = pd.read_csv(
        RIVER_FILE
    )

    required = [
        "Latitude",
        "Longitude",
        "hybrid_hazard_score",
    ]

    if not all(
        column in df.columns
        for column in required
    ):
        return []

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    df["Latitude"] = numeric_series(
        df,
        "Latitude",
    )

    df["Longitude"] = numeric_series(
        df,
        "Longitude",
    )

    df["hybrid_hazard_score"] = numeric_series(
        df,
        "hybrid_hazard_score",
    )

    # --------------------------------------------------------
    # Remove invalid observations
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "Latitude",
            "Longitude",
            "hybrid_hazard_score",
        ]
    )

    df = df[
        np.isfinite(
            df["hybrid_hazard_score"]
        )
    ]

    # --------------------------------------------------------
    # Spatially unique top river zones
    # --------------------------------------------------------

    return get_unique_top_zones(
        df=df,
        lat_col="Latitude",
        lon_col="Longitude",
        score_col="hybrid_hazard_score",
        zone_type="river",
        top_n=TOP_N_PER_HAZARD,
    )


# ============================================================
# RAINFALL ZONES
# ============================================================

def get_rainfall_zones():

    if not RAIN_FILE.exists():
        return []

    df = pd.read_csv(
        RAIN_FILE
    )

    required = [
        "Latitude",
        "Longitude",
        "rainfall_risk_score",
    ]

    if not all(
        column in df.columns
        for column in required
    ):
        return []

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    df["Latitude"] = numeric_series(
        df,
        "Latitude",
    )

    df["Longitude"] = numeric_series(
        df,
        "Longitude",
    )

    df["rainfall_risk_score"] = numeric_series(
        df,
        "rainfall_risk_score",
    )

    # --------------------------------------------------------
    # Remove invalid observations
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "Latitude",
            "Longitude",
            "rainfall_risk_score",
        ]
    )

    df = df[
        np.isfinite(
            df["rainfall_risk_score"]
        )
    ]

    # --------------------------------------------------------
    # Spatially unique top rainfall zones
    # --------------------------------------------------------

    return get_unique_top_zones(
        df=df,
        lat_col="Latitude",
        lon_col="Longitude",
        score_col="rainfall_risk_score",
        zone_type="rainfall",
        top_n=TOP_N_PER_HAZARD,
    )


# ============================================================
# TERRAIN ZONES
# ============================================================

def get_terrain_zones():

    if not TERRAIN_FILE.exists():
        return []

    df = pd.read_csv(
        TERRAIN_FILE,
        usecols=[
            "lat",
            "lon",
            "terrain_hazard_score",
        ],
    )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    df["lat"] = numeric_series(
        df,
        "lat",
    )

    df["lon"] = numeric_series(
        df,
        "lon",
    )

    df["terrain_hazard_score"] = numeric_series(
        df,
        "terrain_hazard_score",
    )

    # --------------------------------------------------------
    # Remove invalid observations
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "lat",
            "lon",
            "terrain_hazard_score",
        ]
    )

    df = df[
        np.isfinite(
            df["terrain_hazard_score"]
        )
    ]

    # --------------------------------------------------------
    # Spatially unique top terrain zones
    # --------------------------------------------------------

    return get_unique_top_zones(
        df=df,
        lat_col="lat",
        lon_col="lon",
        score_col="terrain_hazard_score",
        zone_type="terrain",
        top_n=TOP_N_PER_HAZARD,
    )


# ============================================================
# LANDSLIDE ZONES
# ============================================================

def get_landslide_zones():

    if not LANDSLIDE_FILE.exists():
        return []

    df = pd.read_csv(
        LANDSLIDE_FILE,
        usecols=[
            "lat",
            "lon",
            "hazard_score",
        ],
    )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    df["lat"] = numeric_series(
        df,
        "lat",
    )

    df["lon"] = numeric_series(
        df,
        "lon",
    )

    df["hazard_score"] = numeric_series(
        df,
        "hazard_score",
    )

    # --------------------------------------------------------
    # Remove invalid observations
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "lat",
            "lon",
            "hazard_score",
        ]
    )

    df = df[
        np.isfinite(
            df["hazard_score"]
        )
    ]

    # --------------------------------------------------------
    # Spatially unique top landslide zones
    # --------------------------------------------------------

    return get_unique_top_zones(
        df=df,
        lat_col="lat",
        lon_col="lon",
        score_col="hazard_score",
        zone_type="landslide",
        top_n=TOP_N_PER_HAZARD,
    )


# ============================================================
# MAIN API FUNCTION
# ============================================================

def get_hazard_zones():

    zones = []

    # --------------------------------------------------------
    # River
    # --------------------------------------------------------

    zones.extend(
        get_river_zones()
    )

    # --------------------------------------------------------
    # Rainfall
    # --------------------------------------------------------

    zones.extend(
        get_rainfall_zones()
    )

    # --------------------------------------------------------
    # Terrain
    # --------------------------------------------------------

    zones.extend(
        get_terrain_zones()
    )

    # --------------------------------------------------------
    # Landslide
    # --------------------------------------------------------

    zones.extend(
        get_landslide_zones()
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "status": "ok",
        "zone_count": len(zones),
        "zones": zones,
    }