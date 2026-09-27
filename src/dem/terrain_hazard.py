from pathlib import Path
import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_risk.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_hazard_features.csv"
)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print("📥 Loading terrain risk data...")

    terrain = pd.read_csv(INPUT_PATH)

    print(f"Rows loaded: {len(terrain)}")

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "terrain_risk_score",
        "terrain_risk_level",
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

    # --------------------------------------------------------
    # Clean numeric values
    # --------------------------------------------------------

    numeric_columns = [
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "terrain_risk_score",
    ]

    for column in numeric_columns:

        terrain[column] = pd.to_numeric(
            terrain[column],
            errors="coerce"
        )

    terrain = terrain.dropna(
        subset=numeric_columns
    ).copy()

    # --------------------------------------------------------
    # Create standardized terrain hazard fields
    # --------------------------------------------------------

    terrain["terrain_hazard_score"] = (
        terrain["terrain_risk_score"]
    )

    terrain["terrain_hazard_level"] = (
        terrain["terrain_risk_level"]
    )

    terrain["hazard_source"] = "DEM"

    # --------------------------------------------------------
    # Final output columns
    # --------------------------------------------------------

    output_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "terrain_risk_score",
        "terrain_risk_level",
        "terrain_hazard_score",
        "terrain_hazard_level",
        "hazard_source",
    ]

    terrain = terrain[output_columns]

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    terrain.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("TERRAIN HAZARD FEATURE LAYER COMPLETE")
    print("=" * 60)

    print(f"Rows: {len(terrain)}")
    print(
        f"Terrain hazard score: "
        f"{terrain['terrain_hazard_score'].min():.2f}"
        f" to "
        f"{terrain['terrain_hazard_score'].max():.2f}"
    )

    print("\nHazard level distribution:")
    print(
        terrain["terrain_hazard_level"]
        .value_counts()
        .to_string()
    )

    print("\nHazard source:")
    print(
        terrain["hazard_source"]
        .value_counts()
        .to_string()
    )

    print("\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()