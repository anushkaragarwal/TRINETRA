from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

TERRAIN_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_features.csv"
)

HAZARD_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_hazard_features.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "dem_integrated_features.csv"
)


def main():

    print("📥 Loading DEM terrain features...")
    terrain = pd.read_csv(TERRAIN_PATH)

    print(f"Terrain rows: {len(terrain)}")

    print("\n📥 Loading DEM terrain hazard layer...")
    hazard = pd.read_csv(HAZARD_PATH)

    print(f"Hazard rows: {len(hazard)}")

    # --------------------------------------------------
    # Check common spatial key
    # --------------------------------------------------

    if "cell_id" not in terrain.columns:
        raise ValueError("cell_id missing from terrain_features.csv")

    if "cell_id" not in hazard.columns:
        raise ValueError(
            "cell_id missing from terrain_hazard_features.csv"
        )

    # --------------------------------------------------
    # Keep only DEM-derived hazard information
    # --------------------------------------------------

    hazard_columns = [
        "cell_id",
        "terrain_hazard_score",
        "terrain_hazard_level",
        "hazard_source",
    ]

    missing = [
        column
        for column in hazard_columns
        if column not in hazard.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in terrain hazard layer: {missing}"
        )

    hazard = hazard[hazard_columns].copy()

    # --------------------------------------------------
    # Integrate using spatial cell_id
    # --------------------------------------------------

    dem = terrain.merge(
        hazard,
        on="cell_id",
        how="left",
        validate="one_to_one",
    )

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    if len(dem) != len(terrain):
        raise RuntimeError(
            "DEM integration changed the number of terrain cells."
        )

    missing_hazard = dem["terrain_hazard_score"].isna().sum()

    if missing_hazard > 0:
        raise RuntimeError(
            f"{missing_hazard} terrain cells have no hazard score."
        )

    # --------------------------------------------------
    # Final DEM integration layer
    # --------------------------------------------------

    output_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "terrain_hazard_score",
        "terrain_hazard_level",
        "hazard_source",
    ]

    dem = dem[output_columns]

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dem.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\n" + "=" * 60)
    print("DEM INTEGRATION COMPLETE")
    print("=" * 60)

    print(f"Terrain cells       : {len(terrain)}")
    print(f"Integrated cells    : {len(dem)}")
    print(
        f"Hazard score range : "
        f"{dem['terrain_hazard_score'].min():.2f} "
        f"to "
        f"{dem['terrain_hazard_score'].max():.2f}"
    )

    print("\nDEM features integrated:")
    print("- elevation")
    print("- slope")
    print("- aspect")
    print("- curvature")
    print("- flow_accumulation")
    print("- terrain_hazard_score")
    print("- terrain_hazard_level")

    print(f"\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()