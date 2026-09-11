from pathlib import Path
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

OUTPUT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "trinetra_event_dashboard_data.csv"
)


def find_column(df, candidates):
    normalized = {
        column.lower().strip(): column
        for column in df.columns
    }

    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]

    return None


def main():
    river_df = pd.read_csv(RIVER_HAZARD_PATH)
    satellite_df = pd.read_csv(SATELLITE_PATH)

    print("📥 Loading TRINETRA input files...")
    print(f"River rows     : {len(river_df)}")
    print(f"Satellite rows : {len(satellite_df)}")

    station_column = find_column(
        river_df,
        [
            "station_name",
            "station",
            "site_name",
            "location_name",
        ],
    )

    latitude_column = find_column(
        river_df,
        [
            "latitude",
            "lat",
        ],
    )

    longitude_column = find_column(
        river_df,
        [
            "longitude",
            "lon",
            "lng",
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

    print("\n🔎 River columns detected:")
    print(f"Station column : {station_column}")
    print(f"Latitude column: {latitude_column}")
    print(f"Longitude col. : {longitude_column}")
    print(f"Score column   : {hazard_score_column}")
    print(f"Level column   : {risk_level_column}")

    if station_column is None:
        raise ValueError(
            "Could not identify a station-name column in "
            "river_hybrid_hazard.csv."
        )

    satellite_row = satellite_df.iloc[0].copy()

    satellite_lat = float(
        satellite_row["latitude"]
    )

    satellite_lon = float(
        satellite_row["longitude"]
    )

    # First try matching by station name.
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
        river_df["_station_normalized"]
        .apply(
            lambda value: any(
                term in value
                for term in target_station_terms
            )
        )
    ].copy()

    # If station-name matching finds nothing, match by coordinates.
    if matched.empty and latitude_column and longitude_column:
        river_df["_distance"] = (
            (
                pd.to_numeric(
                    river_df[latitude_column],
                    errors="coerce",
                )
                - satellite_lat
            ).abs()
            +
            (
                pd.to_numeric(
                    river_df[longitude_column],
                    errors="coerce",
                )
                - satellite_lon
            ).abs()
        )

        matched = river_df.nsmallest(
            1,
            "_distance",
        ).copy()

        print(
            "\n⚠️ Station-name match was not found. "
            "Using nearest coordinate match."
        )

    if matched.empty:
        raise ValueError(
            "No matching river record could be found for "
            "the satellite evidence event."
        )

    # Choose highest hazard row if several Lambagarh rows exist.
    if hazard_score_column:
        matched[hazard_score_column] = pd.to_numeric(
            matched[hazard_score_column],
            errors="coerce",
        )

        selected_river_row = matched.sort_values(
            by=hazard_score_column,
            ascending=False,
        ).iloc[0]

    else:
        selected_river_row = matched.iloc[0]

    hydrological_score = (
        float(selected_river_row[hazard_score_column])
        if hazard_score_column
        else None
    )

    hydrological_level = (
        str(selected_river_row[risk_level_column])
        if risk_level_column
        else "UNKNOWN"
    )

    dashboard_row = {
        "event_id": satellite_row["event_id"],
        "station_name": satellite_row["station_name"],
        "event_time_ist": satellite_row["event_time_ist"],
        "latitude": satellite_lat,
        "longitude": satellite_lon,

        "hydrological_risk_score_0_100": hydrological_score,
        "hydrological_risk_level": hydrological_level,

        "satellite_evidence_score_0_100": float(
            satellite_row[
                "satellite_evidence_score_0_100"
            ]
        ),
        "satellite_evidence_class": satellite_row[
            "satellite_evidence_class"
        ],
        "satellite_evidence_status": satellite_row[
            "satellite_evidence_status"
        ],

        "sentinel2_candidate_new_water_ha": float(
            satellite_row[
                "sentinel2_candidate_new_water_ha"
            ]
        ),
        "sentinel2_net_water_change_ha": float(
            satellite_row[
                "sentinel2_net_water_change_ha"
            ]
        ),
        "sentinel1_mean_vv_change_db": float(
            satellite_row[
                "sentinel1_mean_vv_change_db"
            ]
        ),
        "sentinel1_candidate_new_water_ha": float(
            satellite_row[
                "sentinel1_candidate_new_water_ha"
            ]
        ),

        "system_interpretation": (
            "Hydrological indicators and satellite evidence "
            "are displayed separately. High river risk does not "
            "automatically mean satellite-confirmed flooding."
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

    print("\n✅ Final TRINETRA dashboard dataset created.")
    print(f"Output: {OUTPUT_PATH}")

    print("\n📊 Final event summary:")
    print(
        output_df.T.to_string(
            header=False
        )
    )


if __name__ == "__main__":
    main()