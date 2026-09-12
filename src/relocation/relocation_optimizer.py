"""
TRINETRA - RELOCATION OPTIMIZATION
===================================

MEMBER 2 MODULE

Purpose:
    Allocate population settlements to geographically verified
    safe relocation sites while respecting site capacity.

Inputs:
    data/features/population_master.csv
    data/features/safe_sites.csv
    data/features/settlement_coordinates_final_master.csv

Outputs:
    data/features/relocation_assignments.csv
    data/features/relocation_summary.csv

This module does NOT:
    - modify DEM data
    - modify landslide data
    - train hazard models
    - calculate flood hazard
    - calculate landslide hazard

Hazard information, if available later, can be consumed as an
existing read-only input.

Optimization weights:
    Safety          40%
    Capacity        25%
    Accessibility   15%
    Distance        10%
    Infrastructure  10%

IMPORTANT:
    Only safe sites with verified coordinates are used for
    geographic source -> destination assignment.

    Facilities without coordinates are NOT given invented
    coordinates.
"""

from pathlib import Path
import math
import re

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

POPULATION_FILE = (
    ROOT
    / "data"
    / "features"
    / "population_master.csv"
)

SAFE_SITES_FILE = (
    ROOT
    / "data"
    / "features"
    / "safe_sites.csv"
)

COORDINATES_FILE = (
    ROOT
    / "data"
    / "features"
    / "settlement_coordinates_final_master.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "features"
)

ASSIGNMENT_OUTPUT = (
    OUTPUT_DIR
    / "relocation_assignments.csv"
)

SUMMARY_OUTPUT = (
    OUTPUT_DIR
    / "relocation_summary.csv"
)


# ============================================================
# WEIGHTS
# ============================================================

WEIGHT_SAFETY = 0.40
WEIGHT_CAPACITY = 0.25
WEIGHT_ACCESSIBILITY = 0.15
WEIGHT_DISTANCE = 0.10
WEIGHT_INFRASTRUCTURE = 0.10


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    """Normalize text for matching."""

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    value = re.sub(
        r"\([^)]*\)",
        " ",
        value,
    )

    value = re.sub(
        r"[^A-Z0-9]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def numeric_series(
    series,
    default=0,
):
    """Safely convert pandas series to numeric."""

    return pd.to_numeric(
        series,
        errors="coerce",
    ).fillna(default)


def haversine_km(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """Calculate distance between two coordinates."""

    if any(
        pd.isna(value)
        for value in [
            lat1,
            lon1,
            lat2,
            lon2,
        ]
    ):
        return np.nan

    radius = 6371.0

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))

    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return radius * c


def distance_score(
    distance_km,
):
    """
    Convert distance to a 0-100 score.

    <= 5 km  : 100
    5-20 km  : linearly decreasing
    >= 20 km : 0

    Unknown distance:
        0
    """

    if pd.isna(distance_km):
        return 0.0

    distance_km = float(distance_km)

    if distance_km <= 5:
        return 100.0

    if distance_km >= 20:
        return 0.0

    return (
        (20.0 - distance_km)
        / 15.0
        * 100.0
    )


# ============================================================
# POPULATION
# ============================================================

def load_population():

    print()
    print(
        "Loading population master..."
    )

    if not POPULATION_FILE.exists():
        raise FileNotFoundError(
            f"Population file not found:\n"
            f"{POPULATION_FILE}"
        )

    df = pd.read_csv(
        POPULATION_FILE,
        low_memory=False,
    )

    required = [
        "settlement_id",
        "settlement_name",
        "population",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Population master is missing: "
            + ", ".join(missing)
        )

    df["population"] = numeric_series(
        df["population"]
    )

    # Only populated settlements are relocation sources.
    df = df[
        df["population"] > 0
    ].copy()

    df["settlement_id"] = (
        df["settlement_id"]
        .astype(str)
        .str.strip()
    )

    if "settlement_name" not in df.columns:
        df["settlement_name"] = ""

    for column in [
        "STATE",
        "DISTRICT",
        "SUBDISTT",
        "TOWN/VILLAGE",
        "WARD",
        "LEVEL",
        "settlement_type",
    ]:

        if column not in df.columns:
            df[column] = ""

    # Current baseline:
    # all population is considered eligible for planning.
    #
    # We deliberately do not invent a hazard-based evacuation
    # percentage here.
    df["relocation_share"] = 1.0

    df["people_to_relocate"] = np.ceil(
        df["population"]
        * df["relocation_share"]
    ).astype(int)

    print(
        f"Population settlements: "
        f"{len(df):,}"
    )

    print(
        f"Total population: "
        f"{df['population'].sum():,.0f}"
    )

    print(
        f"Total relocation demand: "
        f"{df['people_to_relocate'].sum():,}"
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# SAFE SITES
# ============================================================

def load_safe_sites():

    print()
    print(
        "Loading safe sites..."
    )

    if not SAFE_SITES_FILE.exists():
        raise FileNotFoundError(
            f"Safe-sites file not found:\n"
            f"{SAFE_SITES_FILE}\n\n"
            "Run safe_sites.py first."
        )

    df = pd.read_csv(
        SAFE_SITES_FILE,
        low_memory=False,
    )

    required = [
        "site_id",
        "temporary_capacity",
        "safe_site_score",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "safe_sites.csv is missing: "
            + ", ".join(missing)
        )

    df["temporary_capacity"] = (
        numeric_series(
            df["temporary_capacity"]
        )
        .clip(lower=0)
    )

    # A person cannot be allocated as 0.5 person.
    df["integer_capacity"] = (
        np.floor(
            df["temporary_capacity"]
        )
        .astype(int)
    )

    df["safe_site_score"] = (
        numeric_series(
            df["safe_site_score"]
        )
        .clip(0, 100)
    )

    if "site_status" not in df.columns:
        df["site_status"] = (
            "UNKNOWN"
        )

    if "latitude" not in df.columns:
        df["latitude"] = np.nan

    if "longitude" not in df.columns:
        df["longitude"] = np.nan

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce",
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce",
    )

    df["has_coordinates"] = (
        df["latitude"].notna()
        &
        df["longitude"].notna()
    )

    # --------------------------------------------------------
    # Accessibility
    # --------------------------------------------------------

    if (
        "accessibility_score"
        in df.columns
    ):

        df["accessibility_final"] = (
            numeric_series(
                df[
                    "accessibility_score"
                ]
            )
            .clip(0, 100)
        )

    else:

        df[
            "accessibility_final"
        ] = 50.0

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    infrastructure_columns = [
        "water_score",
        "electricity_score",
        "land_score",
        "boundary_wall_score",
        "safety_score",
    ]

    existing = [
        column
        for column
        in infrastructure_columns
        if column in df.columns
    ]

    if existing:

        df[
            "infrastructure_final"
        ] = (
            df[existing]
            .apply(
                pd.to_numeric,
                errors="coerce",
            )
            .fillna(0)
            .mean(axis=1)
            .clip(0, 100)
        )

    else:

        df[
            "infrastructure_final"
        ] = 50.0

    # --------------------------------------------------------
    # Capacity score
    # --------------------------------------------------------

    capacity = (
        df["integer_capacity"]
    )

    minimum = capacity.min()
    maximum = capacity.max()

    if maximum == minimum:

        df[
            "capacity_final"
        ] = 100.0

    else:

        df[
            "capacity_final"
        ] = (
            (
                capacity - minimum
            )
            /
            (
                maximum - minimum
            )
            * 100.0
        )

    # --------------------------------------------------------
    # Base relocation score
    # --------------------------------------------------------

    df[
        "base_relocation_score"
    ] = (
        WEIGHT_SAFETY
        * df["safe_site_score"]

        +

        WEIGHT_CAPACITY
        * df["capacity_final"]

        +

        WEIGHT_ACCESSIBILITY
        * df["accessibility_final"]

        +

        WEIGHT_INFRASTRUCTURE
        * df["infrastructure_final"]
    )

    print(
        f"Safe sites loaded: "
        f"{len(df):,}"
    )

    print(
        f"Total safe-site capacity: "
        f"{df['integer_capacity'].sum():,}"
    )

    print(
        f"Sites with coordinates: "
        f"{df['has_coordinates'].sum():,}"
    )

    print(
        f"Sites without coordinates: "
        f"{(~df['has_coordinates']).sum():,}"
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# SETTLEMENT COORDINATES
# ============================================================

def load_coordinates():

    print()
    print(
        "Loading settlement coordinates..."
    )

    if not COORDINATES_FILE.exists():
        raise FileNotFoundError(
            f"Coordinate file not found:\n"
            f"{COORDINATES_FILE}"
        )

    df = pd.read_csv(
        COORDINATES_FILE,
        low_memory=False,
    )

    required = [
        "settlement_id",
        "settlement_name",
        "latitude",
        "longitude",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Coordinate file is missing: "
            + ", ".join(missing)
        )

    df["settlement_id"] = (
        df["settlement_id"]
        .astype(str)
        .str.strip()
    )

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce",
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce",
    )

    df["has_coordinates"] = (
        df["latitude"].notna()
        &
        df["longitude"].notna()
    )

    print(
        f"Coordinate records: "
        f"{len(df):,}"
    )

    print(
        f"Usable coordinates: "
        f"{df['has_coordinates'].sum():,}"
    )

    return df


# ============================================================
# ATTACH COORDINATES TO POPULATION
# ============================================================

def attach_population_coordinates(
    population,
    coordinates,
):

    print()
    print(
        "Attaching settlement coordinates..."
    )

    coordinate_lookup = (
        coordinates[
            coordinates["has_coordinates"]
        ][
            [
                "settlement_id",
                "latitude",
                "longitude",
            ]
        ]
        .drop_duplicates(
            subset=[
                "settlement_id"
            ]
        )
    )

    population = population.copy()

    population = population.merge(
        coordinate_lookup,
        on="settlement_id",
        how="left",
        suffixes=(
            "",
            "_coordinate",
        ),
    )

    population["has_coordinates"] = (
        population["latitude"].notna()
        &
        population["longitude"].notna()
    )

    print(
        f"Settlements with coordinates: "
        f"{population['has_coordinates'].sum():,}"
    )

    print(
        f"Settlements without coordinates: "
        f"{(~population['has_coordinates']).sum():,}"
    )

    return population


# ============================================================
# CANDIDATE SCORE
# ============================================================

def calculate_candidate_scores(
    source,
    sites,
):

    candidates = sites[
        sites["remaining_capacity"] > 0
    ].copy()

    if candidates.empty:
        return candidates

    source_lat = source["latitude"]
    source_lon = source["longitude"]

    distances = []

    for _, site in (
        candidates.iterrows()
    ):

        distance = haversine_km(
            source_lat,
            source_lon,
            site["latitude"],
            site["longitude"],
        )

        distances.append(
            distance
        )

    candidates[
        "distance_km"
    ] = distances

    candidates[
        "distance_score"
    ] = (
        candidates[
            "distance_km"
        ]
        .apply(distance_score)
    )

    candidates[
        "relocation_score"
    ] = (
        candidates[
            "base_relocation_score"
        ]
        +
        WEIGHT_DISTANCE
        * candidates[
            "distance_score"
        ]
    )

    # --------------------------------------------------------
    # Same-district preference
    # --------------------------------------------------------

    source_district = clean_text(
        source.get(
            "DISTRICT",
            "",
        )
    )

    if (
        "district_name"
        in candidates.columns
    ):

        candidates[
            "same_district"
        ] = (
            candidates[
                "district_name"
            ]
            .apply(clean_text)
            .eq(
                source_district
            )
        )

        candidates.loc[
            candidates[
                "same_district"
            ],
            "relocation_score",
        ] += 3.0

    else:

        candidates[
            "same_district"
        ] = False

    # --------------------------------------------------------
    # Only geographically valid sites.
    # --------------------------------------------------------

    candidates = candidates[
        candidates["latitude"].notna()
        &
        candidates["longitude"].notna()
    ].copy()

    candidates = candidates.sort_values(
        by=[
            "relocation_score",
            "safe_site_score",
            "remaining_capacity",
            "distance_km",
        ],
        ascending=[
            False,
            False,
            False,
            True,
        ],
    )

    return candidates


# ============================================================
# OPTIMIZATION
# ============================================================

def optimize(
    population,
    sites,
):

    print()
    print("=" * 70)
    print(
        "RUNNING RELOCATION OPTIMIZATION"
    )
    print("=" * 70)

    population = population.copy()
    sites = sites.copy()

    sites[
        "remaining_capacity"
    ] = sites[
        "integer_capacity"
    ].astype(int)

    total_demand = int(
        population[
            "people_to_relocate"
        ].sum()
    )

    total_capacity = int(
        sites[
            "remaining_capacity"
        ].sum()
    )

    geographic_sites = sites[
        sites["has_coordinates"]
        &
        (
            sites[
                "remaining_capacity"
            ] > 0
        )
    ].copy()

    geographic_capacity = int(
        geographic_sites[
            "remaining_capacity"
        ].sum()
    )

    print()
    print(
        f"Total relocation demand : "
        f"{total_demand:,}"
    )

    print(
        f"Total safe-site capacity: "
        f"{total_capacity:,}"
    )

    print(
        f"Geographic sites         : "
        f"{len(geographic_sites):,}"
    )

    print(
        f"Geographic capacity      : "
        f"{geographic_capacity:,}"
    )

    # --------------------------------------------------------
    # Sort large settlements first.
    # --------------------------------------------------------

    population = population.sort_values(
        by=[
            "people_to_relocate",
            "population",
        ],
        ascending=False,
    ).reset_index(
        drop=True
    )

    assignments = []

    allocated_total = 0

    # --------------------------------------------------------
    # Process every populated settlement.
    # --------------------------------------------------------

    for _, source in (
        population.iterrows()
    ):

        demand = int(
            source[
                "people_to_relocate"
            ]
        )

        if demand <= 0:
            continue

        # ----------------------------------------------------
        # Source coordinate unavailable.
        # ----------------------------------------------------

        if (
            pd.isna(
                source["latitude"]
            )
            or
            pd.isna(
                source["longitude"]
            )
        ):

            assignments.append(
                {
                    "source_settlement_id":
                        source[
                            "settlement_id"
                        ],

                    "source_settlement":
                        source[
                            "settlement_name"
                        ],

                    "source_district":
                        source.get(
                            "DISTRICT",
                            "",
                        ),

                    "source_population":
                        int(
                            source[
                                "population"
                            ]
                        ),

                    "relocation_demand":
                        demand,

                    "site_id":
                        "",

                    "site_name":
                        "",

                    "allocated_people":
                        0,

                    "distance_km":
                        np.nan,

                    "relocation_score":
                        0.0,

                    "allocation_status":
                        "UNALLOCATED",

                    "unallocated_reason":
                        "SOURCE_COORDINATES_UNAVAILABLE",
                }
            )

            continue

        # ----------------------------------------------------
        # Generate candidates.
        # ----------------------------------------------------

        candidates = (
            calculate_candidate_scores(
                source,
                geographic_sites,
            )
        )

        remaining_demand = demand

        # ----------------------------------------------------
        # Allocate.
        # ----------------------------------------------------

        for site_index, site in (
            candidates.iterrows()
        ):

            if remaining_demand <= 0:
                break

            available = int(
                geographic_sites.loc[
                    site_index,
                    "remaining_capacity",
                ]
            )

            if available <= 0:
                continue

            allocation = min(
                remaining_demand,
                available,
            )

            if allocation <= 0:
                continue

            before = available

            geographic_sites.loc[
                site_index,
                "remaining_capacity",
            ] = (
                available
                - allocation
            )

            after = int(
                geographic_sites.loc[
                    site_index,
                    "remaining_capacity",
                ]
            )

            remaining_demand -= (
                allocation
            )

            allocated_total += (
                allocation
            )

            assignments.append(
                {
                    "source_settlement_id":
                        source[
                            "settlement_id"
                        ],

                    "source_settlement":
                        source[
                            "settlement_name"
                        ],

                    "source_district":
                        source.get(
                            "DISTRICT",
                            "",
                        ),

                    "source_population":
                        int(
                            source[
                                "population"
                            ]
                        ),

                    "relocation_demand":
                        demand,

                    "site_id":
                        site[
                            "site_id"
                        ],

                    "site_name":
                        site.get(
                            "site_name",
                            "Educational Facility",
                        ),

                    "site_village":
                        site.get(
                            "village_name",
                            "",
                        ),

                    "site_district":
                        site.get(
                            "district_name",
                            "",
                        ),

                    "allocated_people":
                        int(
                            allocation
                        ),

                    "site_capacity_before":
                        int(before),

                    "site_capacity_after":
                        int(after),

                    "safe_site_score":
                        round(
                            float(
                                site[
                                    "safe_site_score"
                                ]
                            ),
                            2,
                        ),

                    "accessibility_score":
                        round(
                            float(
                                site[
                                    "accessibility_final"
                                ]
                            ),
                            2,
                        ),

                    "infrastructure_score":
                        round(
                            float(
                                site[
                                    "infrastructure_final"
                                ]
                            ),
                            2,
                        ),

                    "distance_km":
                        (
                            round(
                                float(
                                    site[
                                        "distance_km"
                                    ]
                                ),
                                3,
                            )
                            if pd.notna(
                                site[
                                    "distance_km"
                                ]
                            )
                            else np.nan
                        ),

                    "distance_score":
                        round(
                            float(
                                site[
                                    "distance_score"
                                ]
                            ),
                            2,
                        ),

                    "relocation_score":
                        round(
                            float(
                                site[
                                    "relocation_score"
                                ]
                            ),
                            2,
                        ),

                    "allocation_status":
                        "ALLOCATED",

                    "unallocated_reason":
                        "",
                }
            )

        # ----------------------------------------------------
        # Remaining demand.
        # ----------------------------------------------------

        if remaining_demand > 0:

            assignments.append(
                {
                    "source_settlement_id":
                        source[
                            "settlement_id"
                        ],

                    "source_settlement":
                        source[
                            "settlement_name"
                        ],

                    "source_district":
                        source.get(
                            "DISTRICT",
                            "",
                        ),

                    "source_population":
                        int(
                            source[
                                "population"
                            ]
                        ),

                    "relocation_demand":
                        demand,

                    "site_id":
                        "",

                    "site_name":
                        "",

                    "site_village":
                        "",

                    "site_district":
                        "",

                    "allocated_people":
                        0,

                    "site_capacity_before":
                        0,

                    "site_capacity_after":
                        0,

                    "safe_site_score":
                        0.0,

                    "accessibility_score":
                        0.0,

                    "infrastructure_score":
                        0.0,

                    "distance_km":
                        np.nan,

                    "distance_score":
                        0.0,

                    "relocation_score":
                        0.0,

                    "allocation_status":
                        "UNALLOCATED",

                    "unallocated_reason":
                        "INSUFFICIENT_GEOGRAPHIC_CAPACITY",
                }
            )

    assignments = pd.DataFrame(
        assignments
    )

    return (
        assignments,
        geographic_sites,
        total_demand,
        total_capacity,
        geographic_capacity,
        allocated_total,
    )


# ============================================================
# SUMMARY
# ============================================================

def create_summary(
    assignments,
    population,
):

    if assignments.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Allocated population by source.
    # --------------------------------------------------------

    allocated = assignments[
        assignments[
            "allocation_status"
        ]
        == "ALLOCATED"
    ].copy()

    if allocated.empty:

        allocated_summary = pd.DataFrame(
            columns=[
                "source_settlement_id",
                "people_allocated",
                "destination_sites",
                "average_distance_km",
                "average_relocation_score",
            ]
        )

    else:

        allocated_summary = (
            allocated
            .groupby(
                "source_settlement_id",
                as_index=False,
            )
            .agg(
                people_allocated=(
                    "allocated_people",
                    "sum",
                ),

                destination_sites=(
                    "site_id",
                    "nunique",
                ),

                average_distance_km=(
                    "distance_km",
                    "mean",
                ),

                average_relocation_score=(
                    "relocation_score",
                    "mean",
                ),
            )
        )

    # --------------------------------------------------------
    # Demand.
    # --------------------------------------------------------

    summary = population[
        [
            "settlement_id",
            "settlement_name",
            "population",
            "people_to_relocate",
        ]
    ].copy()

    summary = summary.rename(
        columns={
            "people_to_relocate":
                "relocation_demand",
        }
    )

    summary = summary.merge(
        allocated_summary,
        left_on="settlement_id",
        right_on="source_settlement_id",
        how="left",
    )

    summary[
        "people_allocated"
    ] = (
        summary[
            "people_allocated"
        ]
        .fillna(0)
        .astype(int)
    )

    summary[
        "destination_sites"
    ] = (
        summary[
            "destination_sites"
        ]
        .fillna(0)
        .astype(int)
    )

    summary[
        "people_unallocated"
    ] = (
        summary[
            "relocation_demand"
        ]
        -
        summary[
            "people_allocated"
        ]
    )

    summary[
        "allocation_rate_pct"
    ] = np.where(
        summary[
            "relocation_demand"
        ] > 0,

        (
            summary[
                "people_allocated"
            ]
            /
            summary[
                "relocation_demand"
            ]
            * 100
        ),

        0,
    )

    summary[
        "average_distance_km"
    ] = (
        summary[
            "average_distance_km"
        ]
        .round(3)
    )

    summary[
        "average_relocation_score"
    ] = (
        summary[
            "average_relocation_score"
        ]
        .round(2)
    )

    summary[
        "relocation_status"
    ] = np.select(
        [
            summary[
                "allocation_rate_pct"
            ] >= 99.99,

            summary[
                "allocation_rate_pct"
            ] > 0,
        ],

        [
            "FULLY_ALLOCATED",
            "PARTIALLY_ALLOCATED",
        ],

        default="NOT_ALLOCATED",
    )

    summary = summary.sort_values(
        by="relocation_demand",
        ascending=False,
    )

    return summary


# ============================================================
# SAVE
# ============================================================

def save_outputs(
    assignments,
    summary,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assignments.to_csv(
        ASSIGNMENT_OUTPUT,
        index=False,
    )

    summary.to_csv(
        SUMMARY_OUTPUT,
        index=False,
    )

    print()
    print("Outputs:")

    print(
        f"  {ASSIGNMENT_OUTPUT}"
    )

    print(
        f"  {SUMMARY_OUTPUT}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "TRINETRA - RELOCATION OPTIMIZATION"
    )
    print("=" * 70)

    population = (
        load_population()
    )

    sites = (
        load_safe_sites()
    )

    coordinates = (
        load_coordinates()
    )

    population = (
        attach_population_coordinates(
            population,
            coordinates,
        )
    )

    (
        assignments,
        remaining_sites,
        total_demand,
        total_capacity,
        geographic_capacity,
        allocated_total,
    ) = optimize(
        population,
        sites,
    )

    summary = (
        create_summary(
            assignments,
            population,
        )
    )

    save_outputs(
        assignments,
        summary,
    )

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    if assignments.empty:

        print()
        print(
            "No relocation assignments generated."
        )

        return

    allocated_rows = assignments[
        assignments[
            "allocation_status"
        ]
        == "ALLOCATED"
    ]

    allocated_people = int(
        allocated_rows[
            "allocated_people"
        ].sum()
    )

    # Correct calculation:
    # demand - actual allocated people
    unallocated_people = (
        total_demand
        - allocated_people
    )

    if total_demand > 0:

        allocation_rate = (
            allocated_people
            /
            total_demand
            *
            100
        )

    else:

        allocation_rate = 0.0

    # --------------------------------------------------------
    # Unallocated reasons.
    # --------------------------------------------------------

    reason_counts = (
        assignments[
            assignments[
                "allocation_status"
            ]
            == "UNALLOCATED"
        ][
            "unallocated_reason"
        ]
        .value_counts()
    )

    # --------------------------------------------------------
    # Final report.
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "TRINETRA RELOCATION OPTIMIZATION COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Total population demand       : "
        f"{total_demand:,}"
    )

    print(
        f"Total safe-site capacity      : "
        f"{total_capacity:,}"
    )

    print(
        f"Geographically verified sites : "
        f"{int(remaining_sites['latitude'].notna().sum()):,}"
    )

    print(
        f"Geographic capacity available : "
        f"{geographic_capacity:,}"
    )

    print(
        f"People allocated              : "
        f"{allocated_people:,}"
    )

    print(
        f"People unallocated            : "
        f"{unallocated_people:,}"
    )

    print(
        f"Allocation rate               : "
        f"{allocation_rate:.2f}%"
    )

    print()
    print(
        "Unallocated reasons:"
    )

    if reason_counts.empty:

        print(
            "  None"
        )

    else:

        for reason, count in (
            reason_counts.items()
        ):

            print(
                f"  {reason:<40}: "
                f"{count:,} assignment rows"
            )

    # --------------------------------------------------------
    # Top assignments.
    # --------------------------------------------------------

    print()
    print(
        "Top relocation assignments:"
    )

    if allocated_rows.empty:

        print(
            "  No geographic assignments available."
        )

    else:

        display_columns = [
            "source_settlement",
            "site_name",
            "allocated_people",
            "distance_km",
            "relocation_score",
        ]

        available_columns = [
            column
            for column
            in display_columns
            if column
            in allocated_rows.columns
        ]

        print(
            allocated_rows[
                available_columns
            ]
            .sort_values(
                by=[
                    "relocation_score",
                    "allocated_people",
                ],
                ascending=False,
            )
            .head(15)
            .to_string(
                index=False
            )
        )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()