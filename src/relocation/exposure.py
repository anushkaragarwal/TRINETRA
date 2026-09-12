"""
TRINETRA - Settlement Exposure Model

Member 2: Population / Relocation

Purpose
-------
Calculate settlement-level hazard exposure by combining:

1. Population
2. Local DEM-derived terrain hazard
3. Nearest event-level TRINETRA hazard
4. Geographic distance to the nearest hazard event

The model produces a transparent, explainable exposure score.

Important
---------
Population is treated as EXPOSURE, not as a causal hazard predictor.

The hazard score comes from:
    - DEM terrain hazard
    - Existing TRINETRA event hazard

Satellite evidence is retained as supporting evidence and is NOT
used as a direct causal hazard predictor.

Unresolved settlements remain in the output but are marked
COORDINATES_UNRESOLVED and are not assigned invented spatial values.

Input
-----
data/features/population_master.csv
data/features/settlement_coordinates_final_master.csv
data/features/dem_integrated_features.csv
data/outputs/trinetra_event_dashboard_data.csv

Output
------
data/features/settlement_exposure.csv
"""


from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

POPULATION_FILE = (
    DATA_DIR
    / "features"
    / "population_master.csv"
)

COORDINATE_FILE = (
    DATA_DIR
    / "features"
    / "settlement_coordinates_final_master.csv"
)

DEM_FILE = (
    DATA_DIR
    / "features"
    / "dem_integrated_features.csv"
)

EVENT_FILE = (
    DATA_DIR
    / "outputs"
    / "trinetra_event_dashboard_data.csv"
)

OUTPUT_FILE = (
    DATA_DIR
    / "features"
    / "settlement_exposure.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum distance at which an event is considered relevant.
# Beyond this distance, the event contribution is set to zero.
MAX_EVENT_DISTANCE_KM = 25.0

# Weight of local DEM terrain hazard.
TERRAIN_WEIGHT = 0.40

# Weight of nearest existing TRINETRA event hazard.
EVENT_WEIGHT = 0.60

# Population contribution to the final exposure score.
POPULATION_WEIGHT = 0.30

# Hazard contribution to the final exposure score.
HAZARD_WEIGHT = 0.70


# ============================================================
# VALIDATION
# ============================================================

def require_file(path):
    """Ensure an input file exists."""

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{path}"
        )


def require_columns(df, columns, filename):
    """Ensure required columns exist."""

    missing = set(columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: "
            f"{sorted(missing)}"
        )


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_km(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate great-circle distance in kilometres.

    Inputs can be scalars or numpy arrays.
    """

    earth_radius_km = 6371.0088

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2.0) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2.0) ** 2
    )

    a = np.clip(a, 0.0, 1.0)

    return (
        2.0
        * earth_radius_km
        * np.arcsin(np.sqrt(a))
    )


# ============================================================
# NORMALIZATION
# ============================================================

def minmax_score(series):
    """
    Convert a numeric series to 0-100.

    Constant non-null values become 50.
    """

    values = pd.to_numeric(
        series,
        errors="coerce"
    )

    valid = values.notna()

    result = pd.Series(
        np.nan,
        index=series.index,
        dtype=float
    )

    if not valid.any():
        return result

    minimum = values[valid].min()
    maximum = values[valid].max()

    if maximum == minimum:

        result.loc[valid] = 50.0

    else:

        result.loc[valid] = (
            (
                values[valid] - minimum
            )
            /
            (
                maximum - minimum
            )
            * 100.0
        )

    return result


# ============================================================
# RISK LEVEL
# ============================================================

def risk_level(score):
    """Convert a 0-100 score into a readable risk category."""

    if pd.isna(score):
        return "UNAVAILABLE"

    score = float(score)

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 40:
        return "MODERATE"

    if score >= 20:
        return "LOW"

    return "VERY_LOW"


# ============================================================
# FIND NEAREST DEM CELL
# ============================================================

def find_nearest_dem(
    settlement_lat,
    settlement_lon,
    dem_lat,
    dem_lon
):
    """
    Find the nearest DEM cell using vectorized Haversine
    calculation.

    The DEM is large, so this function is used only for the
    95 resolved settlements rather than every DEM row.
    """

    distances = haversine_km(
        settlement_lat,
        settlement_lon,
        dem_lat,
        dem_lon
    )

    index = int(
        np.nanargmin(distances)
    )

    return (
        index,
        float(distances[index])
    )


# ============================================================
# FIND NEAREST EVENT
# ============================================================

def find_nearest_event(
    settlement_lat,
    settlement_lon,
    event_df
):
    """
    Find the nearest event with valid coordinates.
    """

    if event_df.empty:
        return None

    event_lat = event_df["latitude"].to_numpy(
        dtype=float
    )

    event_lon = event_df["longitude"].to_numpy(
        dtype=float
    )

    distances = haversine_km(
        settlement_lat,
        settlement_lon,
        event_lat,
        event_lon
    )

    index = int(
        np.nanargmin(distances)
    )

    return (
        event_df.iloc[index],
        float(distances[index])
    )


# ============================================================
# EVENT DISTANCE FACTOR
# ============================================================

def event_distance_factor(distance_km):
    """
    Convert distance to a relevance factor.

    0 km       -> 1.00
    25 km+     -> 0.00

    Linear decay is used for transparency.
    """

    if pd.isna(distance_km):
        return 0.0

    distance_km = float(distance_km)

    if distance_km >= MAX_EVENT_DISTANCE_KM:
        return 0.0

    if distance_km <= 0:
        return 1.0

    return (
        1.0
        -
        distance_km / MAX_EVENT_DISTANCE_KM
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("TRINETRA - SETTLEMENT EXPOSURE MODEL")
    print("=" * 70)

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    for path in [
        POPULATION_FILE,
        COORDINATE_FILE,
        DEM_FILE,
        EVENT_FILE,
    ]:

        require_file(path)

    # --------------------------------------------------------
    # Load population
    # --------------------------------------------------------

    print("\nLoading population data...")

    population = pd.read_csv(
        POPULATION_FILE
    )

    require_columns(
        population,
        [
            "settlement_id",
            "settlement_name",
            "population",
        ],
        "population_master.csv"
    )

    print(
        f"Population settlements: "
        f"{len(population)}"
    )

    # --------------------------------------------------------
    # Load coordinates
    # --------------------------------------------------------

    print("Loading settlement coordinates...")

    coordinates = pd.read_csv(
        COORDINATE_FILE
    )

    require_columns(
        coordinates,
        [
            "settlement_id",
            "settlement_name",
            "latitude",
            "longitude",
        ],
        "settlement_coordinates_final_master.csv"
    )

    print(
        f"Coordinate settlements: "
        f"{len(coordinates)}"
    )

    # --------------------------------------------------------
    # Merge population + coordinates
    # --------------------------------------------------------

    settlements = population.merge(
        coordinates[
            [
                "settlement_id",
                "latitude",
                "longitude",
                "coordinate_source",
                "coordinate_confidence",
                "coordinate_status",
            ]
        ],
        on="settlement_id",
        how="left",
        suffixes=("", "_coordinate")
    )

    # --------------------------------------------------------
    # Normalize coordinates
    # --------------------------------------------------------

    settlements["latitude"] = pd.to_numeric(
        settlements["latitude"],
        errors="coerce"
    )

    settlements["longitude"] = pd.to_numeric(
        settlements["longitude"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Normalize population
    # --------------------------------------------------------

    settlements["population"] = pd.to_numeric(
        settlements["population"],
        errors="coerce"
    ).fillna(0)

    settlements["population_2011"] = pd.to_numeric(
        settlements.get(
            "population_2011",
            pd.Series(
                np.nan,
                index=settlements.index
            )
        ),
        errors="coerce"
    )

    # --------------------------------------------------------
    # Population score
    # --------------------------------------------------------

    settlements["population_exposure_score"] = (
        minmax_score(
            settlements["population"]
        )
    )

    # --------------------------------------------------------
    # Coordinate status
    # --------------------------------------------------------

    settlements["spatial_status"] = np.where(
        settlements["latitude"].notna()
        &
        settlements["longitude"].notna(),
        "COORDINATES_AVAILABLE",
        "COORDINATES_UNRESOLVED"
    )

    # ========================================================
    # LOAD DEM
    # ========================================================

    print("\nLoading DEM terrain data...")

    dem = pd.read_csv(
        DEM_FILE
    )

    require_columns(
        dem,
        [
            "cell_id",
            "lat",
            "lon",
            "terrain_hazard_score",
        ],
        "dem_integrated_features.csv"
    )

    dem["lat"] = pd.to_numeric(
        dem["lat"],
        errors="coerce"
    )

    dem["lon"] = pd.to_numeric(
        dem["lon"],
        errors="coerce"
    )

    dem["terrain_hazard_score"] = pd.to_numeric(
        dem["terrain_hazard_score"],
        errors="coerce"
    )

    dem = dem.dropna(
        subset=[
            "lat",
            "lon",
            "terrain_hazard_score",
        ]
    ).reset_index(drop=True)

    print(
        f"Usable DEM cells: {len(dem)}"
    )

    dem_lat = dem["lat"].to_numpy(
        dtype=float
    )

    dem_lon = dem["lon"].to_numpy(
        dtype=float
    )

    # ========================================================
    # LOAD EVENTS
    # ========================================================

    print("\nLoading TRINETRA event data...")

    events = pd.read_csv(
        EVENT_FILE
    )

    require_columns(
        events,
        [
            "event_id",
            "station_name",
            "latitude",
            "longitude",
            "trinetra_hazard_score_0_100",
            "trinetra_hazard_level",
        ],
        "trinetra_event_dashboard_data.csv"
    )

    events["latitude"] = pd.to_numeric(
        events["latitude"],
        errors="coerce"
    )

    events["longitude"] = pd.to_numeric(
        events["longitude"],
        errors="coerce"
    )

    events["trinetra_hazard_score_0_100"] = pd.to_numeric(
        events["trinetra_hazard_score_0_100"],
        errors="coerce"
    )

    events = events.dropna(
        subset=[
            "latitude",
            "longitude",
            "trinetra_hazard_score_0_100",
        ]
    ).reset_index(drop=True)

    print(
        f"Usable hazard events: {len(events)}"
    )

    # ========================================================
    # PROCESS SETTLEMENTS
    # ========================================================

    print("\nCalculating settlement exposure...")

    terrain_scores = []
    terrain_distances = []

    event_scores = []
    event_distances = []
    event_factors = []
    event_ids = []
    event_stations = []
    event_levels = []
    event_times = []

    # --------------------------------------------------------
    # Iterate only over settlements, not DEM cells
    # --------------------------------------------------------

    for position, row in settlements.iterrows():

        latitude = row["latitude"]
        longitude = row["longitude"]

        # ----------------------------------------------------
        # No coordinates
        # ----------------------------------------------------

        if pd.isna(latitude) or pd.isna(longitude):

            terrain_scores.append(np.nan)
            terrain_distances.append(np.nan)

            event_scores.append(np.nan)
            event_distances.append(np.nan)
            event_factors.append(0.0)

            event_ids.append("")
            event_stations.append("")
            event_levels.append("")
            event_times.append("")

            continue

        # ----------------------------------------------------
        # Nearest DEM cell
        # ----------------------------------------------------

        dem_index, dem_distance = find_nearest_dem(
            latitude,
            longitude,
            dem_lat,
            dem_lon
        )

        nearest_dem = dem.iloc[
            dem_index
        ]

        terrain_scores.append(
            float(
                nearest_dem[
                    "terrain_hazard_score"
                ]
            )
        )

        terrain_distances.append(
            dem_distance
        )

        # ----------------------------------------------------
        # Nearest event
        # ----------------------------------------------------

        nearest_event_result = find_nearest_event(
            latitude,
            longitude,
            events
        )

        if nearest_event_result is None:

            event_scores.append(np.nan)
            event_distances.append(np.nan)
            event_factors.append(0.0)

            event_ids.append("")
            event_stations.append("")
            event_levels.append("")
            event_times.append("")

            continue

        nearest_event, event_distance = (
            nearest_event_result
        )

        factor = event_distance_factor(
            event_distance
        )

        raw_event_score = float(
            nearest_event[
                "trinetra_hazard_score_0_100"
            ]
        )

        # ----------------------------------------------------
        # Distance-adjusted event hazard
        # ----------------------------------------------------

        adjusted_event_score = (
            raw_event_score
            * factor
        )

        event_scores.append(
            adjusted_event_score
        )

        event_distances.append(
            event_distance
        )

        event_factors.append(
            factor
        )

        event_ids.append(
            str(
                nearest_event["event_id"]
            )
        )

        event_stations.append(
            str(
                nearest_event["station_name"]
            )
        )

        event_levels.append(
            str(
                nearest_event[
                    "trinetra_hazard_level"
                ]
            )
        )

        event_times.append(
            str(
                nearest_event[
                    "event_time_ist"
                ]
            )
        )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if (
            (position + 1) % 10 == 0
            or
            position == len(settlements) - 1
        ):

            print(
                f"  Processed "
                f"{position + 1}/"
                f"{len(settlements)}"
            )

    # ========================================================
    # ATTACH SPATIAL RESULTS
    # ========================================================

    settlements[
        "nearest_dem_terrain_hazard_score"
    ] = terrain_scores

    settlements[
        "nearest_dem_distance_km"
    ] = terrain_distances

    settlements[
        "nearest_event_hazard_score"
    ] = event_scores

    settlements[
        "nearest_event_distance_km"
    ] = event_distances

    settlements[
        "event_distance_factor"
    ] = event_factors

    settlements[
        "nearest_event_id"
    ] = event_ids

    settlements[
        "nearest_event_station"
    ] = event_stations

    settlements[
        "nearest_event_hazard_level"
    ] = event_levels

    settlements[
        "nearest_event_time"
    ] = event_times

    # ========================================================
    # COMBINED HAZARD SCORE
    # ========================================================

    # --------------------------------------------------------
    # Terrain component
    # --------------------------------------------------------

    settlements[
        "terrain_component"
    ] = (
        settlements[
            "nearest_dem_terrain_hazard_score"
        ]
        * TERRAIN_WEIGHT
    )

    # --------------------------------------------------------
    # Event component
    # --------------------------------------------------------

    settlements[
        "event_component"
    ] = (
        settlements[
            "nearest_event_hazard_score"
        ]
        * EVENT_WEIGHT
    )

    # --------------------------------------------------------
    # Combined hazard
    # --------------------------------------------------------

    settlements[
        "hazard_exposure_score"
    ] = (
        settlements[
            "terrain_component"
        ]
        .fillna(0)
        +
        settlements[
            "event_component"
        ]
        .fillna(0)
    )

    # --------------------------------------------------------
    # If no event exists nearby, use terrain alone
    # --------------------------------------------------------

    terrain_available = (
        settlements[
            "nearest_dem_terrain_hazard_score"
        ].notna()
    )

    event_available = (
        settlements[
            "nearest_event_hazard_score"
        ].notna()
        &
        (
            settlements[
                "event_distance_factor"
            ] > 0
        )
    )

    # Terrain-only fallback
    terrain_only_mask = (
        terrain_available
        &
        ~event_available
    )

    settlements.loc[
        terrain_only_mask,
        "hazard_exposure_score"
    ] = settlements.loc[
        terrain_only_mask,
        "nearest_dem_terrain_hazard_score"
    ]

    # No spatial information
    no_spatial_mask = ~terrain_available

    settlements.loc[
        no_spatial_mask,
        "hazard_exposure_score"
    ] = np.nan

    # --------------------------------------------------------
    # Clip score
    # --------------------------------------------------------

    settlements[
        "hazard_exposure_score"
    ] = settlements[
        "hazard_exposure_score"
    ].clip(
        lower=0,
        upper=100
    )

    # ========================================================
    # FINAL EXPOSURE SCORE
    # ========================================================

    # --------------------------------------------------------
    # Hazard dominates the score.
    #
    # Population does NOT modify the hazard itself.
    # It only contributes to exposure.
    # --------------------------------------------------------

    settlements[
        "settlement_exposure_score"
    ] = (
        settlements[
            "hazard_exposure_score"
        ]
        * HAZARD_WEIGHT
        +
        settlements[
            "population_exposure_score"
        ]
        * POPULATION_WEIGHT
    )

    # --------------------------------------------------------
    # Clip
    # --------------------------------------------------------

    settlements[
        "settlement_exposure_score"
    ] = settlements[
        "settlement_exposure_score"
    ].clip(
        lower=0,
        upper=100
    )

    # ========================================================
    # LEVELS
    # ========================================================

    settlements[
        "hazard_exposure_level"
    ] = settlements[
        "hazard_exposure_score"
    ].apply(
        risk_level
    )

    settlements[
        "settlement_exposure_level"
    ] = settlements[
        "settlement_exposure_score"
    ].apply(
        risk_level
    )

    # ========================================================
    # EXPOSURE STATUS
    # ========================================================

    def determine_status(row):

        if (
            pd.isna(row["latitude"])
            or
            pd.isna(row["longitude"])
        ):
            return "COORDINATES_UNRESOLVED"

        if pd.isna(
            row["nearest_dem_terrain_hazard_score"]
        ):
            return "NO_DEM_MATCH"

        if (
            pd.isna(
                row["nearest_event_hazard_score"]
            )
            or
            row["event_distance_factor"] <= 0
        ):
            return "TERRAIN_ONLY"

        return "FULL_SPATIAL_EXPOSURE"

    settlements[
        "exposure_status"
    ] = settlements.apply(
        determine_status,
        axis=1
    )

    # ========================================================
    # RECOMMENDED ACTION
    # ========================================================

    def recommended_action(row):

        score = row[
            "settlement_exposure_score"
        ]

        if pd.isna(score):

            return (
                "Coordinate verification required"
            )

        if score >= 80:

            return (
                "Immediate field verification; "
                "prepare evacuation and relocation assessment"
            )

        if score >= 60:

            return (
                "High-priority monitoring and "
                "relocation preparedness"
            )

        if score >= 40:

            return (
                "Enhanced monitoring and "
                "preparedness"
            )

        if score >= 20:

            return (
                "Routine monitoring"
            )

        return (
            "Normal monitoring"
        )

    settlements[
        "recommended_action"
    ] = settlements.apply(
        recommended_action,
        axis=1
    )

    # ========================================================
    # ROUND NUMERIC VALUES
    # ========================================================

    numeric_columns = [
        "population",
        "population_2011",
        "latitude",
        "longitude",
        "population_exposure_score",
        "nearest_dem_terrain_hazard_score",
        "nearest_dem_distance_km",
        "nearest_event_hazard_score",
        "nearest_event_distance_km",
        "event_distance_factor",
        "terrain_component",
        "event_component",
        "hazard_exposure_score",
        "settlement_exposure_score",
    ]

    for column in numeric_columns:

        if column in settlements.columns:

            settlements[column] = settlements[
                column
            ].round(4)

    # ========================================================
    # OUTPUT COLUMN ORDER
    # ========================================================

    preferred_columns = [
        "settlement_id",
        "settlement_name",
        "population",
        "population_2011",

        "latitude",
        "longitude",

        "coordinate_source",
        "coordinate_confidence",
        "coordinate_status",

        "nearest_dem_terrain_hazard_score",
        "nearest_dem_distance_km",

        "nearest_event_id",
        "nearest_event_station",
        "nearest_event_time",
        "nearest_event_distance_km",
        "nearest_event_hazard_score",
        "nearest_event_hazard_level",
        "event_distance_factor",

        "terrain_component",
        "event_component",

        "hazard_exposure_score",
        "hazard_exposure_level",

        "population_exposure_score",

        "settlement_exposure_score",
        "settlement_exposure_level",

        "spatial_status",
        "exposure_status",

        "recommended_action",
    ]

    existing_columns = [
        column
        for column in preferred_columns
        if column in settlements.columns
    ]

    remaining_columns = [
        column
        for column in settlements.columns
        if column not in existing_columns
    ]

    settlements = settlements[
        existing_columns
        +
        remaining_columns
    ]

    # ========================================================
    # SAVE
    # ========================================================

    settlements.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    resolved = (
        settlements["latitude"].notna()
        &
        settlements["longitude"].notna()
    )

    unresolved = ~resolved

    full_spatial = (
        settlements[
            "exposure_status"
        ]
        == "FULL_SPATIAL_EXPOSURE"
    )

    terrain_only = (
        settlements[
            "exposure_status"
        ]
        == "TERRAIN_ONLY"
    )

    print("\n" + "=" * 70)
    print("EXPOSURE MODEL COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal settlements       : "
        f"{len(settlements)}"
    )

    print(
        f"Coordinates available   : "
        f"{resolved.sum()}"
    )

    print(
        f"Coordinates unresolved  : "
        f"{unresolved.sum()}"
    )

    print(
        f"Full spatial exposure  : "
        f"{full_spatial.sum()}"
    )

    print(
        f"Terrain-only exposure  : "
        f"{terrain_only.sum()}"
    )

    if settlements[
        "settlement_exposure_score"
    ].notna().any():

        print(
            "\nHighest exposure settlements:"
        )

        top = settlements[
            [
                "settlement_name",
                "population",
                "hazard_exposure_score",
                "settlement_exposure_score",
                "settlement_exposure_level",
            ]
        ].dropna(
            subset=[
                "settlement_exposure_score"
            ]
        ).sort_values(
            "settlement_exposure_score",
            ascending=False
        ).head(10)

        print(
            top.to_string(
                index=False
            )
        )

    if unresolved.any():

        print(
            "\nUnresolved settlements:"
        )

        print(
            settlements.loc[
                unresolved,
                [
                    "settlement_id",
                    "settlement_name",
                    "population",
                ]
            ].to_string(
                index=False
            )
        )

    print(
        f"\nOutput:\n{OUTPUT_FILE}"
    )

    print("\nExposure formula:")
    print(
        "Hazard = "
        "40% local DEM terrain + "
        "60% distance-adjusted TRINETRA event hazard"
    )

    print(
        "Exposure = "
        "70% hazard + "
        "30% population"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()