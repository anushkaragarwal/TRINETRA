from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

POPULATION_PATH = (
    ROOT
    / "data"
    / "population"
    / "population_habitations_2026.csv"
)

HAZARD_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_hybrid_hazard.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "habitation_risk_priority.csv"
)

TIME_COL = "Data Acquisition Time"


# ---------------------------------------------------------
# MODE SETTINGS
# ---------------------------------------------------------
# LIVE:
# Uses the latest available CWC-based hybrid hazard record.
#
# HISTORICAL_SCENARIO:
# Uses the strongest observed river-hazard event in the
# current data, for red-zone / relocation demo and testing.
# ---------------------------------------------------------
MODE = "HISTORICAL_SCENARIO"


# ---------------------------------------------------------
# MVP EXPOSURE / PROXIMITY MAPPING
# ---------------------------------------------------------
# These are transparent prototype proximity bands for the
# Joshimath–Vishnuprayag–Badrinath corridor.
#
# In the production version, replace them with actual GIS:
# village coordinates + river distance + road access +
# slope / landslide layer + flood-inundation layers.
# ---------------------------------------------------------
CORRIDOR_BANDS = {
    "Badrinathpuri": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 90,
    },
    "Mana": {
        "distance_band": "UPPER_CORRIDOR",
        "proximity_score": 85,
    },
    "Khiron": {
        "distance_band": "UPPER_CORRIDOR",
        "proximity_score": 85,
    },
    "Thaing": {
        "distance_band": "UPPER_CORRIDOR",
        "proximity_score": 80,
    },
    "Pandukaswar": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 90,
    },
    "Pulana Chak Bhyudar": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 85,
    },
    "Bhyudar": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 80,
    },
    "Joshimath": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 95,
    },
    "Topovan": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 90,
    },
    "Raini Chak Subhai": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 85,
    },
    "Malari": {
        "distance_band": "NEAR_CORRIDOR",
        "proximity_score": 85,
    },
}


def normalize_name(value):
    """
    Make town and village names consistent for matching.

    Example:
    'Joshimath  (NPP)' -> 'JOSHIMATH'
    'Badrinathpuri (NP)' -> 'BADRINATHPURI'
    """
    return (
        str(value)
        .upper()
        .replace("(NPP)", "")
        .replace("(NP)", "")
        .strip()
    )


def zone_label(score):
    """
    Convert 0-100 priority score into a red-zone category.
    """
    if score >= 75:
        return "RED"
    elif score >= 55:
        return "ORANGE"
    elif score >= 35:
        return "YELLOW"
    return "GREEN"


def action_label(zone):
    """
    Suggested operational action for each priority zone.
    """
    actions = {
        "RED": (
            "Immediate field verification; prepare evacuation "
            "and relocation plan"
        ),
        "ORANGE": (
            "Increase monitoring; prepare shelters and "
            "issue pre-alert"
        ),
        "YELLOW": (
            "Monitor conditions; validate local "
            "preparedness resources"
        ),
        "GREEN": (
            "Routine monitoring"
        ),
    }

    return actions[zone]


def select_hazard_context(hazard):
    """
    Select either the latest record for live mode or the
    strongest observed event for historical replay mode.
    """

    if MODE == "LIVE":
        selected = (
            hazard.sort_values(TIME_COL)
            .groupby("Station")
            .tail(1)
            .copy()
        )

    elif MODE == "HISTORICAL_SCENARIO":
        selected = (
            hazard.sort_values(
                by="hybrid_hazard_score",
                ascending=False,
            )
            .head(1)
            .copy()
        )

    else:
        raise ValueError(
            "MODE must be 'LIVE' or 'HISTORICAL_SCENARIO'."
        )

    return selected


def main():
    print("📥 Loading projected habitation population...")

    population = pd.read_csv(POPULATION_PATH)

    # Keep only places with residents.
    # This removes administrative / forest placeholder rows
    # such as zero-population village records.
    population = population[
        population["POP_2026_EST"] > 0
    ].copy()

    print(
        f"✅ Inhabited habitations retained: "
        f"{len(population)}"
    )

    print("📥 Loading hybrid river-hazard data...")

    hazard = pd.read_csv(
        HAZARD_PATH,
        parse_dates=[TIME_COL],
    )

    selected_hazard = select_hazard_context(hazard)

    station_hazard_score = float(
        selected_hazard["hybrid_hazard_score"].iloc[0]
    )

    station_hazard_category = str(
        selected_hazard["hybrid_risk_category"].iloc[0]
    )

    hazard_time = selected_hazard[
        TIME_COL
    ].iloc[0]

    station_name = selected_hazard[
        "Station"
    ].iloc[0]

    print("\n📍 Selected station hazard context:")
    print(f"Mode: {MODE}")
    print(f"Station: {station_name}")
    print(f"Timestamp: {hazard_time}")
    print(f"Hybrid hazard score: {station_hazard_score}")
    print(f"Risk category: {station_hazard_category}")

    # Normalize all Census habitation names.
    population["NAME_NORMALIZED"] = (
        population["NAME"]
        .apply(normalize_name)
    )

    # Convert transparent proximity mapping into DataFrame.
    mapping_rows = []

    for name, details in CORRIDOR_BANDS.items():
        mapping_rows.append({
            "NAME_NORMALIZED": normalize_name(name),
            "distance_band": details["distance_band"],
            "proximity_score": details["proximity_score"],
        })

    mapping = pd.DataFrame(mapping_rows)

    # Only priority-score the mapped MVP corridor habitations.
    priority = population.merge(
        mapping,
        on="NAME_NORMALIZED",
        how="inner",
    )

    if priority.empty:
        raise RuntimeError(
            "No habitation names matched CORRIDOR_BANDS. "
            "Check spelling and normalization."
        )

    # ---------------------------------------------------------
    # Population exposure score: 0-100.
    # Relative to the highest populated selected habitation.
    # ---------------------------------------------------------
    max_population = priority["POP_2026_EST"].max()

    priority["population_exposure_score"] = (
        priority["POP_2026_EST"]
        / max_population
        * 100
    ).round(2)

    # ---------------------------------------------------------
    # Final priority formula:
    #
    # 50% current/historical river hazard
    # 30% corridor/risk proximity
    # 20% population exposure
    # ---------------------------------------------------------
    priority["habitation_priority_score"] = (
        0.50 * station_hazard_score
        + 0.30 * priority["proximity_score"]
        + 0.20 * priority["population_exposure_score"]
    ).round(2)

    priority["red_zone_label"] = (
        priority["habitation_priority_score"]
        .apply(zone_label)
    )

    priority["recommended_action"] = (
        priority["red_zone_label"]
        .apply(action_label)
    )

    # Traceability fields: useful in dashboard and PPT.
    priority["analysis_mode"] = MODE
    priority["assigned_station"] = station_name
    priority["hazard_timestamp"] = hazard_time
    priority["station_hazard_score"] = station_hazard_score
    priority["station_hazard_category"] = (
        station_hazard_category
    )

    final_columns = [
        "NAME",
        "LEVEL",
        "TRU",
        "NO_HH",
        "POP_2011",
        "POP_2026_EST",
        "analysis_mode",
        "assigned_station",
        "hazard_timestamp",
        "station_hazard_score",
        "station_hazard_category",
        "distance_band",
        "proximity_score",
        "population_exposure_score",
        "habitation_priority_score",
        "red_zone_label",
        "recommended_action",
    ]

    priority = priority[
        final_columns
    ].sort_values(
        by="habitation_priority_score",
        ascending=False,
    )

    print("\n🚨 Habitation priority results:")
    print(
        priority.to_string(
            index=False
        )
    )

    print("\n📊 Zone distribution:")
    print(
        priority["red_zone_label"]
        .value_counts()
        .to_string()
    )

    print("\n👥 Population by zone:")
    print(
        priority.groupby("red_zone_label")[
            "POP_2026_EST"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .to_string()
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    priority.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\n✅ Saved habitation priority table to:\n"
        f"{OUTPUT_PATH}"
    )

    print(
        f"📐 Output shape: {priority.shape}"
    )


if __name__ == "__main__":
    main()