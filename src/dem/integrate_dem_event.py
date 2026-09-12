from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[2]

DEM_PATH = (
    ROOT
    / "data"
    / "features"
    / "dem_integrated_features.csv"
)

EVENT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "trinetra_event_dashboard_data.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "trinetra_event_with_dem.csv"
)


def main():

    print("📥 Loading DEM integrated features...")
    dem = pd.read_csv(DEM_PATH)

    print(f"DEM cells: {len(dem)}")

    print("\n📥 Loading TRINETRA event data...")
    event = pd.read_csv(EVENT_PATH)

    print(f"Events: {len(event)}")

    # ---------------------------------------------------------
    # Check required columns
    # ---------------------------------------------------------

    dem_required = [
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "terrain_hazard_score",
        "terrain_hazard_level",
    ]

    event_required = [
        "latitude",
        "longitude",
    ]

    missing_dem = [
        col for col in dem_required
        if col not in dem.columns
    ]

    missing_event = [
        col for col in event_required
        if col not in event.columns
    ]

    if missing_dem:
        raise ValueError(
            f"Missing DEM columns: {missing_dem}"
        )

    if missing_event:
        raise ValueError(
            f"Missing event columns: {missing_event}"
        )

    # ---------------------------------------------------------
    # Convert coordinates to numeric
    # ---------------------------------------------------------

    dem["lat"] = pd.to_numeric(
        dem["lat"],
        errors="coerce"
    )

    dem["lon"] = pd.to_numeric(
        dem["lon"],
        errors="coerce"
    )

    event["latitude"] = pd.to_numeric(
        event["latitude"],
        errors="coerce"
    )

    event["longitude"] = pd.to_numeric(
        event["longitude"],
        errors="coerce"
    )

    dem = dem.dropna(
        subset=["lat", "lon"]
    ).copy()

    event = event.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    # ---------------------------------------------------------
    # Find nearest DEM cell for each event
    # ---------------------------------------------------------

    print("\n🔎 Finding nearest DEM cell...")

    dem_lat = dem["lat"].to_numpy()
    dem_lon = dem["lon"].to_numpy()

    matched_rows = []

    for _, row in event.iterrows():

        event_lat = row["latitude"]
        event_lon = row["longitude"]

        # Approximate geographic distance.
        # Longitude is adjusted for latitude.
        lat_diff = dem_lat - event_lat
        lon_diff = (
            dem_lon - event_lon
        ) * np.cos(
            np.radians(event_lat)
        )

        distance = (
            lat_diff ** 2
            + lon_diff ** 2
        )

        nearest_index = np.argmin(distance)

        nearest_dem = dem.iloc[
            nearest_index
        ]

        result = row.to_dict()

        result["dem_cell_id"] = (
            nearest_dem["cell_id"]
        )

        result["dem_elevation"] = (
            nearest_dem["elevation"]
        )

        result["dem_slope"] = (
            nearest_dem["slope"]
        )

        result["dem_aspect"] = (
            nearest_dem["aspect"]
        )

        result["dem_curvature"] = (
            nearest_dem["curvature"]
        )

        result["dem_flow_accumulation"] = (
            nearest_dem["flow_accumulation"]
        )

        result["dem_terrain_hazard_score"] = (
            nearest_dem["terrain_hazard_score"]
        )

        result["dem_terrain_hazard_level"] = (
            nearest_dem["terrain_hazard_level"]
        )

        matched_rows.append(result)

    output = pd.DataFrame(
        matched_rows
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("DEM EVENT INTEGRATION COMPLETE")
    print("=" * 60)

    print(f"Events processed : {len(event)}")
    print(f"Events matched   : {len(output)}")

    print("\nDEM fields attached to event:")

    print("- dem_cell_id")
    print("- dem_elevation")
    print("- dem_slope")
    print("- dem_aspect")
    print("- dem_curvature")
    print("- dem_flow_accumulation")
    print("- dem_terrain_hazard_score")
    print("- dem_terrain_hazard_level")

    print("\nExample:")
    print(
        output[
            [
                "latitude",
                "longitude",
                "dem_elevation",
                "dem_slope",
                "dem_terrain_hazard_score",
                "dem_terrain_hazard_level",
            ]
        ].to_string(index=False)
    )

    print("\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()