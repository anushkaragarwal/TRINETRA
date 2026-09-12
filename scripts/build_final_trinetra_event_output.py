from pathlib import Path
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

RIVER_HAZARD_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_hybrid_hazard.csv"
)

SATELLITE_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "gee_satellite_evidence_summary.csv"
)

TERRAIN_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_hazard_features.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "trinetra_event_dashboard_data.csv"
)


# =========================================================
# TRINETRA MVP HAZARD INTEGRATION
# =========================================================

HYDRO_WEIGHT = 0.70
TERRAIN_WEIGHT = 0.30

# Local terrain context around the event
TERRAIN_RADIUS_KM = 1.0


def find_column(df, candidates):
    normalized = {
        column.lower().strip(): column
        for column in df.columns
    }

    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]

    return None


def classify_risk(score):

    if score >= 90:
        return "CRITICAL"

    elif score >= 75:
        return "HIGH"

    elif score >= 50:
        return "MODERATE"

    elif score >= 25:
        return "LOW"

    else:
        return "VERY LOW"


def get_local_terrain(
    terrain_df,
    event_lat,
    event_lon,
):
    """
    Extract DEM-derived terrain information
    from approximately 1 km around the event.
    """

    km_lat = TERRAIN_RADIUS_KM / 111.0

    km_lon = TERRAIN_RADIUS_KM / (
        111.0
        * np.cos(np.radians(event_lat))
    )

    mask = (
        (terrain_df["lat"] >= event_lat - km_lat)
        &
        (terrain_df["lat"] <= event_lat + km_lat)
        &
        (terrain_df["lon"] >= event_lon - km_lon)
        &
        (terrain_df["lon"] <= event_lon + km_lon)
    )

    local = terrain_df.loc[mask].copy()

    if local.empty:
        raise ValueError(
            "No DEM terrain cells found around "
            "the event location."
        )

    terrain_score = float(
        local["terrain_hazard_score"].median()
    )

    terrain_max = float(
        local["terrain_hazard_score"].max()
    )

    slope_median = float(
        local["slope"].median()
    )

    slope_max = float(
        local["slope"].max()
    )

    elevation_median = float(
        local["elevation"].median()
    )

    return {
        "terrain_hazard_score_0_100":
            terrain_score,

        "terrain_hazard_max_score_0_100":
            terrain_max,

        "terrain_hazard_level":
            classify_risk(terrain_score),

        "terrain_slope_median_deg":
            slope_median,

        "terrain_slope_max_deg":
            slope_max,

        "terrain_elevation_median_m":
            elevation_median,

        "terrain_cells_used":
            len(local),
    }


def main():

    print("Loading TRINETRA input files...")

    river_df = pd.read_csv(
        RIVER_HAZARD_PATH
    )

    satellite_df = pd.read_csv(
        SATELLITE_PATH
    )

    terrain_df = pd.read_csv(
        TERRAIN_PATH
    )

    print(
        f"River rows     : {len(river_df)}"
    )

    print(
        f"Satellite rows : {len(satellite_df)}"
    )

    print(
        f"Terrain rows   : {len(terrain_df)}"
    )

    # =====================================================
    # FIND RIVER COLUMNS
    # =====================================================

    station_column = find_column(
        river_df,
        [
            "station_name",
            "station",
            "site_name",
            "location_name",
        ],
    )

    hazard_score_column = find_column(
        river_df,
        [
            "hybrid_hazard_score",
            "hazard_score",
            "risk_score",
        ],
    )

    risk_level_column = find_column(
        river_df,
        [
            "hybrid_hazard_level",
            "hazard_level",
            "risk_level",
            "risk_category",
        ],
    )

    if station_column is None:
        raise ValueError(
            "Could not identify station-name column."
        )

    if hazard_score_column is None:
        raise ValueError(
            "Could not identify river hazard score column."
        )

    # =====================================================
    # SATELLITE EVENT
    # =====================================================

    satellite_row = satellite_df.iloc[0].copy()

    event_lat = float(
        satellite_row["latitude"]
    )

    event_lon = float(
        satellite_row["longitude"]
    )

    # =====================================================
    # MATCH LAMBAGARH RIVER EVENT
    # =====================================================

    river_df["_station_normalized"] = (
        river_df[station_column]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    target_station_terms = [
        "lambagarh",
        "lambagarh river station",
    ]

    matched = river_df[
        river_df["_station_normalized"].apply(
            lambda value: any(
                term in value
                for term in target_station_terms
            )
        )
    ].copy()

    if matched.empty:
        raise ValueError(
            "No Lambagarh river record found."
        )

    matched[hazard_score_column] = pd.to_numeric(
        matched[hazard_score_column],
        errors="coerce",
    )

    selected_river_row = (
        matched
        .sort_values(
            by=hazard_score_column,
            ascending=False,
        )
        .iloc[0]
    )

    hydrological_score = float(
        selected_river_row[
            hazard_score_column
        ]
    )

    if risk_level_column:

        hydrological_level = str(
            selected_river_row[
                risk_level_column
            ]
        )

    else:

        hydrological_level = classify_risk(
            hydrological_score
        )

    # =====================================================
    # DEM INTEGRATION
    # =====================================================

    terrain = get_local_terrain(
        terrain_df,
        event_lat,
        event_lon,
    )

    terrain_score = terrain[
        "terrain_hazard_score_0_100"
    ]

    # =====================================================
    # FINAL TRINETRA HAZARD SCORE
    # =====================================================

    trinetra_hazard_score = (
        HYDRO_WEIGHT
        * hydrological_score
        +
        TERRAIN_WEIGHT
        * terrain_score
    )

    trinetra_hazard_score = float(
        np.clip(
            trinetra_hazard_score,
            0,
            100,
        )
    )

    trinetra_hazard_level = classify_risk(
        trinetra_hazard_score
    )

    # =====================================================
    # SATELLITE EVIDENCE
    # =====================================================

    satellite_score = float(
        satellite_row[
            "satellite_evidence_score_0_100"
        ]
    )

    # =====================================================
    # FINAL DASHBOARD DATA
    # =====================================================

    dashboard_row = {

        "event_id":
            satellite_row["event_id"],

        "station_name":
            satellite_row["station_name"],

        "event_time_ist":
            satellite_row["event_time_ist"],

        "latitude":
            event_lat,

        "longitude":
            event_lon,

        # -----------------------------
        # HYDROLOGICAL
        # -----------------------------

        "hydrological_risk_score_0_100":
            hydrological_score,

        "hydrological_risk_level":
            hydrological_level,

        # -----------------------------
        # DEM / TERRAIN
        # -----------------------------

        "terrain_hazard_score_0_100":
            terrain_score,

        "terrain_hazard_max_score_0_100":
            terrain[
                "terrain_hazard_max_score_0_100"
            ],

        "terrain_hazard_level":
            terrain[
                "terrain_hazard_level"
            ],

        "terrain_slope_median_deg":
            terrain[
                "terrain_slope_median_deg"
            ],

        "terrain_slope_max_deg":
            terrain[
                "terrain_slope_max_deg"
            ],

        "terrain_elevation_median_m":
            terrain[
                "terrain_elevation_median_m"
            ],

        "terrain_cells_used":
            terrain[
                "terrain_cells_used"
            ],

        # -----------------------------
        # FINAL TRINETRA
        # -----------------------------

        "trinetra_hazard_score_0_100":
            trinetra_hazard_score,

        "trinetra_hazard_level":
            trinetra_hazard_level,

        # -----------------------------
        # SATELLITE EVIDENCE
        # -----------------------------

        "satellite_evidence_score_0_100":
            satellite_score,

        "satellite_evidence_class":
            satellite_row[
                "satellite_evidence_class"
            ],

        "satellite_evidence_status":
            satellite_row[
                "satellite_evidence_status"
            ],

        "sentinel2_candidate_new_water_ha":
            float(
                satellite_row[
                    "sentinel2_candidate_new_water_ha"
                ]
            ),

        "sentinel2_net_water_change_ha":
            float(
                satellite_row[
                    "sentinel2_net_water_change_ha"
                ]
            ),

        "sentinel1_mean_vv_change_db":
            float(
                satellite_row[
                    "sentinel1_mean_vv_change_db"
                ]
            ),

        "sentinel1_candidate_new_water_ha":
            float(
                satellite_row[
                    "sentinel1_candidate_new_water_ha"
                ]
            ),

        "system_interpretation": (
            "TRINETRA combines dynamic "
            "hydrological hazard with "
            "local DEM-derived terrain "
            "hazard. Satellite observations "
            "are retained separately as "
            "supporting post-event evidence."
        ),
    }

    output_df = pd.DataFrame(
        [dashboard_row]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # =====================================================
    # FINAL REPORT
    # =====================================================

    print()
    print("=" * 60)
    print("TRINETRA DEM INTEGRATION COMPLETE")
    print("=" * 60)

    print(
        f"Event location     : "
        f"{event_lat:.6f}, {event_lon:.6f}"
    )

    print(
        f"Hydrological score : "
        f"{hydrological_score:.2f}"
    )

    print(
        f"Terrain score      : "
        f"{terrain_score:.2f}"
    )

    print(
        f"Terrain max        : "
        f"{terrain['terrain_hazard_max_score_0_100']:.2f}"
    )

    print(
        f"Terrain cells      : "
        f"{terrain['terrain_cells_used']}"
    )

    print(
        f"TRINETRA score     : "
        f"{trinetra_hazard_score:.2f}"
    )

    print(
        f"TRINETRA level     : "
        f"{trinetra_hazard_level}"
    )

    print()
    print("Saved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()