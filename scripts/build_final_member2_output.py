"""
TRINETRA - Final Member 2 Decision Dataset

Member 2:
    Population
    Population Exposure
    Safe Sites
    Relocation AI
    Relocation Allocation
    Final Decision Layer

This script combines the EXISTING outputs.

It does NOT:
    - train a hazard model
    - modify DEM data
    - modify landslide data
    - retrain relocation AI
    - invent coordinates
    - modify exposure calculations

Inputs:
    data/features/population_master.csv
    data/features/settlement_exposure.csv
    data/features/final_relocation_plan.csv

Outputs:
    data/features/final_member2_decision.csv
    data/features/final_member2_summary.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

POPULATION_PATH = (
    ROOT
    / "data"
    / "features"
    / "population_master.csv"
)

EXPOSURE_PATH = (
    ROOT
    / "data"
    / "features"
    / "settlement_exposure.csv"
)

RELOCATION_PATH = (
    ROOT
    / "data"
    / "features"
    / "final_relocation_plan.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "final_member2_decision.csv"
)

SUMMARY_PATH = (
    ROOT
    / "data"
    / "features"
    / "final_member2_summary.csv"
)


# ============================================================
# HELPERS
# ============================================================

def find_column(df, candidates, required=True):
    """
    Find a column case-insensitively.
    """

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    if required:

        raise KeyError(
            f"Could not find any of these columns:\n"
            f"{candidates}\n\n"
            f"Available columns:\n"
            f"{list(df.columns)}"
        )

    return None


def numeric(df, column, default=0.0):
    """
    Safely convert a column to numeric.
    """

    if column is None:

        return pd.Series(
            default,
            index=df.index,
            dtype=float,
        )

    return pd.to_numeric(
        df[column],
        errors="coerce",
    ).fillna(default)


def clean_text(series):
    """
    Clean string values.
    """

    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
    )


def parse_coordinate_flag(series):
    """
    Robustly interpret coordinate availability.

    Supports:
        True / False
        1 / 0
        YES / NO
        AVAILABLE / UNAVAILABLE
        VERIFIED / UNVERIFIED
        RESOLVED / UNRESOLVED
    """

    if pd.api.types.is_bool_dtype(series):

        return series.fillna(False).astype(bool)

    values = (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return values.isin(
        [
            "TRUE",
            "1",
            "YES",
            "Y",
            "AVAILABLE",
            "VERIFIED",
            "RESOLVED",
            "SUCCESS",
            "SUCCESSFUL",
            "OK",
        ]
    )


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("TRINETRA - FINAL MEMBER 2 DECISION DATASET")
print("=" * 70)


print("\nLoading population master...")

population = pd.read_csv(
    POPULATION_PATH
)

print(
    f"Population records: {len(population)}"
)


print("\nLoading settlement exposure...")

exposure = pd.read_csv(
    EXPOSURE_PATH
)

print(
    f"Exposure records: {len(exposure)}"
)


print("\nLoading final relocation plan...")

relocation = pd.read_csv(
    RELOCATION_PATH
)

print(
    f"Relocation rows: {len(relocation)}"
)


# ============================================================
# POPULATION
# ============================================================

population_id = find_column(
    population,
    [
        "settlement_id",
        "id",
    ],
)

population_name = find_column(
    population,
    [
        "settlement_name",
        "name",
        "name_clean",
    ],
)

population_value = find_column(
    population,
    [
        "population",
        "population_2026",
        "pop_2026_est",
    ],
)


population_work = pd.DataFrame()

population_work["settlement_id"] = (
    population[population_id]
    .astype(str)
    .str.strip()
)

population_work["settlement_name"] = (
    population[population_name]
    .astype(str)
    .str.strip()
)

population_work["population_2026"] = numeric(
    population,
    population_value,
)


population_work = (
    population_work
    .drop_duplicates(
        subset=["settlement_id"]
    )
    .reset_index(drop=True)
)


# ============================================================
# EXPOSURE
# ============================================================

exposure_id = find_column(
    exposure,
    [
        "settlement_id",
        "id",
    ],
)

exposure_name = find_column(
    exposure,
    [
        "settlement_name",
        "name",
    ],
    required=False,
)

exposure_score = find_column(
    exposure,
    [
        "settlement_exposure_score",
        "exposure_score",
    ],
)

exposure_level = find_column(
    exposure,
    [
        "settlement_exposure_level",
        "exposure_level",
    ],
)

hazard_score = find_column(
    exposure,
    [
        "hazard_exposure_score",
        "hazard_score",
    ],
    required=False,
)


# ------------------------------------------------------------
# IMPORTANT:
# Prefer has_coordinates over coordinate_status.
#
# The previous integration code could accidentally read a
# textual status such as "RESOLVED" and classify it incorrectly.
# ------------------------------------------------------------

has_coordinates_col = find_column(
    exposure,
    [
        "has_coordinates",
    ],
    required=False,
)

coordinate_status_col = find_column(
    exposure,
    [
        "coordinate_status",
        "resolution_status",
        "verification_status",
    ],
    required=False,
)

latitude_col = find_column(
    exposure,
    [
        "latitude",
        "lat",
    ],
    required=False,
)

longitude_col = find_column(
    exposure,
    [
        "longitude",
        "lon",
        "lng",
    ],
    required=False,
)

recommended_action = find_column(
    exposure,
    [
        "recommended_action",
    ],
    required=False,
)


exposure_work = pd.DataFrame()

exposure_work["settlement_id"] = (
    exposure[exposure_id]
    .astype(str)
    .str.strip()
)


if exposure_name:

    exposure_work["exposure_name"] = clean_text(
        exposure[exposure_name]
    )

else:

    exposure_work["exposure_name"] = ""


exposure_work["exposure_score"] = numeric(
    exposure,
    exposure_score,
).clip(
    0,
    100,
)


exposure_work["exposure_level"] = (
    clean_text(
        exposure[exposure_level]
    )
    .str.upper()
)


if hazard_score:

    exposure_work["hazard_exposure_score"] = numeric(
        exposure,
        hazard_score,
    ).clip(
        0,
        100,
    )

else:

    exposure_work["hazard_exposure_score"] = 0.0


# ============================================================
# COORDINATE HANDLING
# ============================================================

if latitude_col:

    exposure_work["latitude"] = numeric(
        exposure,
        latitude_col,
        default=np.nan,
    )

else:

    exposure_work["latitude"] = np.nan


if longitude_col:

    exposure_work["longitude"] = numeric(
        exposure,
        longitude_col,
        default=np.nan,
    )

else:

    exposure_work["longitude"] = np.nan


coordinates_from_latlon = (
    exposure_work["latitude"].notna()
    & exposure_work["longitude"].notna()
)


if has_coordinates_col:

    coordinates_from_flag = (
        parse_coordinate_flag(
            exposure[has_coordinates_col]
        )
    )

elif coordinate_status_col:

    coordinates_from_flag = (
        parse_coordinate_flag(
            exposure[coordinate_status_col]
        )
    )

else:

    coordinates_from_flag = pd.Series(
        False,
        index=exposure.index,
    )


# The safest rule:
#
# If latitude AND longitude exist, coordinates are available.
#
# This prevents a textual status column from incorrectly
# overriding valid spatial coordinates.

exposure_work["has_coordinates"] = (
    coordinates_from_latlon
    | coordinates_from_flag.to_numpy()
)


if recommended_action:

    exposure_work["existing_recommended_action"] = clean_text(
        exposure[recommended_action]
    )

else:

    exposure_work["existing_recommended_action"] = ""


exposure_work = (
    exposure_work
    .drop_duplicates(
        subset=["settlement_id"]
    )
    .reset_index(drop=True)
)


# ============================================================
# EXPOSURE QUALITY CHECK
# ============================================================

print("\nExposure coordinate validation")
print("-" * 70)

print(
    f"Exposure records with coordinates: "
    f"{exposure_work['has_coordinates'].sum()}"
)

print(
    f"Exposure records without coordinates: "
    f"{(~exposure_work['has_coordinates']).sum()}"
)


# ============================================================
# RELOCATION
# ============================================================

relocation_source_id = find_column(
    relocation,
    [
        "source_settlement_id",
        "source_id",
    ],
)

destination_id = find_column(
    relocation,
    [
        "destination_site_id",
        "site_id",
    ],
    required=False,
)

destination_name = find_column(
    relocation,
    [
        "destination_site",
        "site_name",
    ],
    required=False,
)

allocated_people = find_column(
    relocation,
    [
        "allocated_people",
        "people_allocated",
    ],
)

ai_score = find_column(
    relocation,
    [
        "ai_score",
        "relocation_ai_score",
    ],
    required=False,
)

distance = find_column(
    relocation,
    [
        "distance_km",
        "relocation_distance_km",
    ],
    required=False,
)

allocation_status = find_column(
    relocation,
    [
        "allocation_status",
    ],
)

allocation_reason = find_column(
    relocation,
    [
        "allocation_reason",
    ],
    required=False,
)


relocation_work = pd.DataFrame()

relocation_work["settlement_id"] = (
    relocation[relocation_source_id]
    .astype(str)
    .str.strip()
)

relocation_work["allocated_people"] = numeric(
    relocation,
    allocated_people,
).clip(
    lower=0
)


if destination_id:

    relocation_work["destination_site_id"] = (
        relocation[destination_id]
        .fillna("")
        .astype(str)
        .str.strip()
    )

else:

    relocation_work["destination_site_id"] = ""


if destination_name:

    relocation_work["destination_site"] = clean_text(
        relocation[destination_name]
    )

else:

    relocation_work["destination_site"] = ""


if ai_score:

    relocation_work["ai_score"] = numeric(
        relocation,
        ai_score,
        default=np.nan,
    )

else:

    relocation_work["ai_score"] = np.nan


if distance:

    relocation_work["distance_km"] = numeric(
        relocation,
        distance,
        default=np.nan,
    )

else:

    relocation_work["distance_km"] = np.nan


relocation_work["allocation_status"] = (
    clean_text(
        relocation[allocation_status]
    )
    .str.upper()
)


if allocation_reason:

    relocation_work["allocation_reason"] = clean_text(
        relocation[allocation_reason]
    )

else:

    relocation_work["allocation_reason"] = ""


# ============================================================
# ALLOCATED RECORDS
# ============================================================

relocation_work["is_allocated"] = (
    relocation_work["allocation_status"]
    == "ALLOCATED"
)


allocated_only = relocation_work[
    relocation_work["is_allocated"]
].copy()


# ============================================================
# AGGREGATE RELOCATION BY SETTLEMENT
# ============================================================

print("\nAggregating relocation results...")


if allocated_only.empty:

    relocation_summary = pd.DataFrame(
        columns=[
            "settlement_id",
            "allocated_population",
            "allocation_rows",
            "best_destination_site_id",
            "best_destination_site",
            "best_ai_score",
            "best_distance_km",
        ]
    )

else:

    totals = (
        allocated_only
        .groupby(
            "settlement_id",
            as_index=False,
        )[
            "allocated_people"
        ]
        .sum()
        .rename(
            columns={
                "allocated_people":
                    "allocated_population"
            }
        )
    )


    allocation_counts = (
        allocated_only
        .groupby(
            "settlement_id",
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size":
                    "allocation_rows"
            }
        )
    )


    best = (
        allocated_only
        .sort_values(
            by=[
                "settlement_id",
                "ai_score",
                "distance_km",
            ],
            ascending=[
                True,
                False,
                True,
            ],
            na_position="last",
        )
        .drop_duplicates(
            subset=["settlement_id"]
        )
    )


    best = best[
        [
            "settlement_id",
            "destination_site_id",
            "destination_site",
            "ai_score",
            "distance_km",
        ]
    ].rename(
        columns={
            "destination_site_id":
                "best_destination_site_id",

            "destination_site":
                "best_destination_site",

            "ai_score":
                "best_ai_score",

            "distance_km":
                "best_distance_km",
        }
    )


    relocation_summary = (
        totals
        .merge(
            allocation_counts,
            on="settlement_id",
            how="left",
        )
        .merge(
            best,
            on="settlement_id",
            how="left",
        )
    )


# ============================================================
# MERGE
# ============================================================

print("\nCombining population + exposure + relocation...")


final = (
    population_work
    .merge(
        exposure_work,
        on="settlement_id",
        how="left",
    )
    .merge(
        relocation_summary,
        on="settlement_id",
        how="left",
    )
)


# ============================================================
# DEFAULT VALUES
# ============================================================

final["allocated_population"] = (
    final["allocated_population"]
    .fillna(0)
    .astype(int)
)

final["allocation_rows"] = (
    final["allocation_rows"]
    .fillna(0)
    .astype(int)
)


final["best_ai_score"] = pd.to_numeric(
    final["best_ai_score"],
    errors="coerce",
)


final["best_distance_km"] = pd.to_numeric(
    final["best_distance_km"],
    errors="coerce",
)


final["best_destination_site_id"] = (
    final["best_destination_site_id"]
    .fillna("")
    .astype(str)
    .str.strip()
)


final["best_destination_site"] = (
    final["best_destination_site"]
    .fillna("")
    .astype(str)
    .str.strip()
)


final["remaining_population"] = (
    final["population_2026"]
    - final["allocated_population"]
).clip(
    lower=0
).astype(int)


# ============================================================
# RELOCATION STATUS
# ============================================================

def relocation_status(row):

    population = int(
        row["population_2026"]
    )

    allocated = int(
        row["allocated_population"]
    )

    has_coordinates = bool(
        row["has_coordinates"]
    )


    if not has_coordinates:

        return "UNRESOLVED_COORDINATES"


    if population <= 0:

        return "NO_POPULATION"


    if allocated >= population:

        return "FULLY_ALLOCATED"


    if allocated > 0:

        return "PARTIALLY_ALLOCATED"


    return "NOT_ALLOCATED"


final["relocation_status"] = (
    final.apply(
        relocation_status,
        axis=1,
    )
)


# ============================================================
# RELOCATION PRIORITY
# ============================================================

"""
The exposure model already incorporates population:

    Exposure = 70% hazard + 30% population

Therefore we use the existing exposure score as the
settlement-level relocation priority signal.

Population is NOT added a second time.
"""

final["relocation_priority_score"] = (
    pd.to_numeric(
        final["exposure_score"],
        errors="coerce",
    )
    .fillna(0)
    .clip(
        0,
        100,
    )
    .round(2)
)


def priority_level(score):

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MODERATE"

    return "LOW"


final["relocation_priority_level"] = (
    final["relocation_priority_score"]
    .apply(priority_level)
)


# ============================================================
# FINAL DECISION
# ============================================================

def final_decision(row):

    priority = row[
        "relocation_priority_level"
    ]

    status = row[
        "relocation_status"
    ]


    if status == "UNRESOLVED_COORDINATES":

        return "COORDINATE_VERIFICATION_REQUIRED"


    if status == "NO_POPULATION":

        return "NO_POPULATION"


    if priority == "CRITICAL":

        if status == "FULLY_ALLOCATED":
            return "HIGH_PRIORITY_RELOCATION_READY"

        if status == "PARTIALLY_ALLOCATED":
            return "URGENT_RELOCATION_CAPACITY_REQUIRED"

        return "URGENT_RELOCATION_REQUIRED"


    if priority == "HIGH":

        if status == "FULLY_ALLOCATED":
            return "HIGH_PRIORITY_RELOCATION_READY"

        if status == "PARTIALLY_ALLOCATED":
            return "ADDITIONAL_CAPACITY_REQUIRED"

        return "RELOCATION_RECOMMENDED"


    if priority == "MODERATE":

        if status == "FULLY_ALLOCATED":
            return "MONITOR_AND_RELOCATE_IF_TRIGGERED"

        if status == "PARTIALLY_ALLOCATED":
            return "ADDITIONAL_CAPACITY_REQUIRED"

        return "MONITOR"


    return "MONITOR"


final["final_decision"] = (
    final.apply(
        final_decision,
        axis=1,
    )
)


# ============================================================
# DATA QUALITY
# ============================================================

final["exposure_available"] = (
    final["exposure_score"].notna()
)


final["relocation_recommendation_available"] = (
    final["best_destination_site_id"] != ""
)


final["decision_data_quality"] = "COMPLETE"


final.loc[
    ~final["exposure_available"],
    "decision_data_quality"
] = "EXPOSURE_MISSING"


final.loc[
    ~final["has_coordinates"],
    "decision_data_quality"
] = "COORDINATES_UNRESOLVED"


final.loc[
    (
        ~final["exposure_available"]
        & ~final["has_coordinates"]
    ),
    "decision_data_quality"
] = (
    "EXPOSURE_AND_COORDINATES_MISSING"
)


# ============================================================
# FINAL COLUMNS
# ============================================================

final_columns = [
    "settlement_id",
    "settlement_name",

    "population_2026",

    "latitude",
    "longitude",
    "has_coordinates",

    "hazard_exposure_score",
    "exposure_score",
    "exposure_level",

    "relocation_priority_score",
    "relocation_priority_level",

    "allocated_population",
    "remaining_population",
    "relocation_status",

    "best_destination_site_id",
    "best_destination_site",
    "best_ai_score",
    "best_distance_km",
    "allocation_rows",

    "final_decision",

    "existing_recommended_action",

    "exposure_available",
    "relocation_recommendation_available",
    "decision_data_quality",
]


final = final[
    final_columns
].copy()


# ============================================================
# SORT
# ============================================================

final = final.sort_values(
    by=[
        "relocation_priority_score",
        "population_2026",
    ],
    ascending=[
        False,
        False,
    ],
).reset_index(
    drop=True
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


final.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

total_population = int(
    final["population_2026"].sum()
)

total_allocated = int(
    final["allocated_population"].sum()
)

total_remaining = int(
    final["remaining_population"].sum()
)


summary_rows = [
    {
        "metric": "total_settlements",
        "value": len(final),
    },
    {
        "metric": "total_population_2026",
        "value": total_population,
    },
    {
        "metric": "settlements_with_coordinates",
        "value": int(
            final["has_coordinates"].sum()
        ),
    },
    {
        "metric": "settlements_without_coordinates",
        "value": int(
            (~final["has_coordinates"]).sum()
        ),
    },
    {
        "metric": "settlements_with_exposure",
        "value": int(
            final["exposure_available"].sum()
        ),
    },
    {
        "metric": "allocated_population",
        "value": total_allocated,
    },
    {
        "metric": "remaining_population",
        "value": total_remaining,
    },
    {
        "metric": "allocation_rate_percent",
        "value": round(
            (
                total_allocated
                / total_population
                * 100
            )
            if total_population > 0
            else 0,
            2,
        ),
    },
    {
        "metric": "fully_allocated_settlements",
        "value": int(
            (
                final["relocation_status"]
                == "FULLY_ALLOCATED"
            ).sum()
        ),
    },
    {
        "metric": "partially_allocated_settlements",
        "value": int(
            (
                final["relocation_status"]
                == "PARTIALLY_ALLOCATED"
            ).sum()
        ),
    },
    {
        "metric": "not_allocated_settlements",
        "value": int(
            (
                final["relocation_status"]
                == "NOT_ALLOCATED"
            ).sum()
        ),
    },
    {
        "metric": "unresolved_coordinate_settlements",
        "value": int(
            (
                final["relocation_status"]
                == "UNRESOLVED_COORDINATES"
            ).sum()
        ),
    },
]


summary = pd.DataFrame(
    summary_rows
)


summary.to_csv(
    SUMMARY_PATH,
    index=False,
)


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("FINAL MEMBER 2 RESULTS")
print("=" * 70)

print(
    f"Total settlements: "
    f"{len(final)}"
)

print(
    f"Total population: "
    f"{total_population:,}"
)

print(
    f"Settlements with coordinates: "
    f"{final['has_coordinates'].sum()}"
)

print(
    f"Settlements without coordinates: "
    f"{(~final['has_coordinates']).sum()}"
)

print(
    f"Settlements with exposure: "
    f"{final['exposure_available'].sum()}"
)

print(
    f"Allocated population: "
    f"{total_allocated:,}"
)

print(
    f"Remaining population: "
    f"{total_remaining:,}"
)

allocation_rate = (
    total_allocated
    / total_population
    * 100
    if total_population > 0
    else 0
)

print(
    f"Allocation rate: "
    f"{allocation_rate:.2f}%"
)


print("\nRelocation status:")
print(
    final[
        "relocation_status"
    ]
    .value_counts()
    .to_string()
)


print("\nPriority level:")
print(
    final[
        "relocation_priority_level"
    ]
    .value_counts()
    .to_string()
)


print("\nFinal decision:")
print(
    final[
        "final_decision"
    ]
    .value_counts()
    .to_string()
)


print("\nTop priority settlements:")

top_columns = [
    "settlement_name",
    "population_2026",
    "exposure_score",
    "relocation_priority_level",
    "relocation_status",
    "allocated_population",
    "remaining_population",
    "best_destination_site",
    "best_ai_score",
]


print(
    final[
        top_columns
    ]
    .head(15)
    .to_string(
        index=False
    )
)


print("\n" + "=" * 70)
print("OUTPUT FILES")
print("=" * 70)

print(
    f"Final Member-2 dataset:\n"
    f"{OUTPUT_PATH}"
)

print(
    f"\nSummary:\n"
    f"{SUMMARY_PATH}"
)

print("\nDone.")