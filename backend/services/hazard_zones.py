from pathlib import Path
import math

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

RIVER_FILE = BASE_DIR / "data" / "river" / "processed" / "river_hybrid_hazard.csv"
RAIN_FILE = BASE_DIR / "data" / "rainfall" / "processed" / "rainfall_hybrid_hazard.csv"
TERRAIN_FILE = BASE_DIR / "data" / "features" / "dem_integrated_features.csv"


def get_hazard_zones():
    zones = []

    # -------------------------
    # RIVER
    # -------------------------
        # -------------------------
    # RIVER
    # -------------------------
    if RIVER_FILE.exists():
        df = pd.read_csv(RIVER_FILE)

        if (
            "Latitude" in df.columns
            and "Longitude" in df.columns
            and "hybrid_hazard_score" in df.columns
        ):
            df["Latitude"] = pd.to_numeric(
                df["Latitude"],
                errors="coerce"
            )

            df["Longitude"] = pd.to_numeric(
                df["Longitude"],
                errors="coerce"
            )

            df["hybrid_hazard_score"] = pd.to_numeric(
                df["hybrid_hazard_score"],
                errors="coerce"
            )

            df = df.dropna(
                subset=[
                    "Latitude",
                    "Longitude",
                    "hybrid_hazard_score"
                ]
            )

            for _, row in df.nlargest(
                20,
                "hybrid_hazard_score"
            ).iterrows():

                score = float(
                    row["hybrid_hazard_score"]
                )

                if score >= 75:
                    level = "CRITICAL"
                elif score >= 50:
                    level = "HIGH"
                elif score >= 25:
                    level = "MODERATE"
                else:
                    level = "LOW"

                zones.append({
                    "type": "river",
                    "lat": float(row["Latitude"]),
                    "lon": float(row["Longitude"]),
                    "hazard_score": round(score, 2),
                    "risk_level": level
                })

    # -------------------------
    # RAINFALL
    # -------------------------
    if RAIN_FILE.exists():
        df = pd.read_csv(RAIN_FILE)

        if "hybrid_hazard_score" in df.columns:
            for _, row in df.nlargest(20, "hybrid_hazard_score").iterrows():

                score = float(row["hybrid_hazard_score"])

                if score >= 75:
                    level = "CRITICAL"
                elif score >= 50:
                    level = "HIGH"
                elif score >= 25:
                    level = "MODERATE"
                else:
                    level = "LOW"

                zones.append({
                    "type": "rainfall",
                    "lat": 30.66,
                    "lon": 79.52,
                    "hazard_score": round(score, 2),
                    "risk_level": level
                })

    # -------------------------
    # TERRAIN
    # -------------------------
    if TERRAIN_FILE.exists():
        df = pd.read_csv(
            TERRAIN_FILE,
            usecols=["lat", "lon", "terrain_hazard_score"]
        )

        for _, row in df.nlargest(20, "terrain_hazard_score").iterrows():

            score = float(row["terrain_hazard_score"])

            if score >= 75:
                level = "CRITICAL"
            elif score >= 50:
                level = "HIGH"
            elif score >= 25:
                level = "MODERATE"
            else:
                level = "LOW"

            zones.append({
                "type": "terrain",
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "hazard_score": round(score, 2),
                "risk_level": level
            })

    return {
        "status": "ok",
        "zone_count": len(zones),
        "zones": zones
    }