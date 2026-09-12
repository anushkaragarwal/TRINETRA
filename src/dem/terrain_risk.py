from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_features.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_risk.csv"
)


def percentile_score(series):
    """
    Convert a terrain feature into a relative 0-100
    percentile score within the MVP AOI.
    """
    return (
        series.rank(
            method="average",
            pct=True
        ) * 100
    )


def risk_level(score):
    if score >= 75:
        return "HIGH"
    elif score >= 50:
        return "MODERATE"
    elif score >= 25:
        return "LOW"
    return "VERY LOW"


def main():

    print("📥 Loading terrain features...")

    terrain = pd.read_csv(INPUT_PATH)

    print(f"Rows loaded: {len(terrain)}")

    print("\nColumns:")
    print(terrain.columns.tolist())

    required_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
    ]

    missing = [
        column
        for column in required_columns
        if column not in terrain.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # -----------------------------------------------------
    # Clean numeric terrain values
    # -----------------------------------------------------

    numeric_columns = [
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
    ]

    for column in numeric_columns:
        terrain[column] = pd.to_numeric(
            terrain[column],
            errors="coerce",
        )

    terrain = terrain.dropna(
        subset=numeric_columns
    ).copy()

    # -----------------------------------------------------
    # Terrain component scores
    # -----------------------------------------------------

    # Steeper terrain generally represents greater
    # terrain / landslide susceptibility.
    terrain["slope_score"] = percentile_score(
        terrain["slope"]
    )

    # Absolute curvature represents magnitude of
    # local topographic change.
    terrain["curvature_score"] = percentile_score(
        terrain["curvature"].abs()
    )

    # Log transformation reduces the effect of very
    # large flow-accumulation values.
    terrain["flow_accumulation_score"] = percentile_score(
        np.log1p(
            terrain["flow_accumulation"]
        )
    )

    # Elevation is retained as a terrain descriptor and
    # given a smaller contribution to the prototype score.
    terrain["elevation_score"] = percentile_score(
        terrain["elevation"]
    )

    # -----------------------------------------------------
    # Terrain risk score
    # -----------------------------------------------------

    terrain["terrain_risk_score"] = (
        0.50 * terrain["slope_score"]
        + 0.20 * terrain["curvature_score"]
        + 0.20 * terrain["flow_accumulation_score"]
        + 0.10 * terrain["elevation_score"]
    ).round(2)

    terrain["terrain_risk_level"] = (
        terrain["terrain_risk_score"]
        .apply(risk_level)
    )

    # -----------------------------------------------------
    # Save terrain risk layer
    # -----------------------------------------------------

    output_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "slope_score",
        "curvature_score",
        "flow_accumulation_score",
        "elevation_score",
        "terrain_risk_score",
        "terrain_risk_level",
    ]

    terrain = terrain[
        output_columns
    ]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    terrain.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\n" + "=" * 50)
    print("TERRAIN RISK COMPLETE")
    print("=" * 50)

    print(f"Rows: {len(terrain)}")

    print(
        f"Risk score range: "
        f"{terrain['terrain_risk_score'].min():.2f} "
        f"to "
        f"{terrain['terrain_risk_score'].max():.2f}"
    )

    print("\nRisk distribution:")

    print(
        terrain["terrain_risk_level"]
        .value_counts()
        .to_string()
    )

    print("\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()