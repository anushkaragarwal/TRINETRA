"""
TRINETRA - RELOCATION AI INFERENCE
==================================

MEMBER 2 ONLY

Purpose:
    Use the trained relocation model to rank safe-site destinations
    for each populated settlement.

Input:
    data/features/population_master.csv
    data/features/safe_sites.csv
    data/features/settlement_coordinates_final_master.csv
    models/relocation_model.pkl

Output:
    data/features/relocation_recommendations.csv

The model:
    - does not modify DEM
    - does not modify landslide data
    - does not train hazard models
    - does not invent coordinates

Only geographically verified settlements and safe sites are used
for distance-based AI recommendations.

The model provides ranking/suitability assistance. It does not
represent historical evacuation ground truth.
"""

from pathlib import Path
import math
import pickle
import re

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

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

MODEL_FILE = (
    ROOT
    / "models"
    / "relocation_model.pkl"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "features"
    / "relocation_recommendations.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TOP_K = 5

MIN_SITE_CAPACITY = 1


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    """Normalize text."""

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
    default=0.0,
):
    """Safely convert a pandas series to numeric."""

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
    """Calculate geographic distance in kilometres."""

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

    lat1 = math.radians(
        float(lat1)
    )

    lon1 = math.radians(
        float(lon1)
    )

    lat2 = math.radians(
        float(lat2)
    )

    lon2 = math.radians(
        float(lon2)
    )

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
    Convert distance into 0-100 score.

    <= 5 km  : 100
    5-20 km  : linear decrease
    >= 20 km : 0
    """

    if pd.isna(distance_km):
        return 0.0

    distance_km = float(
        distance_km
    )

    if distance_km <= 5:
        return 100.0

    if distance_km >= 20:
        return 0.0

    return (
        (
            20.0
            - distance_km
        )
        / 15.0
        * 100.0
    )


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print()
    print(
        "Loading trained relocation AI model..."
    )

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"Model not found:\n"
            f"{MODEL_FILE}\n\n"
            "Run train_relocation_model.py first."
        )

    with open(
        MODEL_FILE,
        "rb",
    ) as file:

        artifact = pickle.load(
            file
        )

    if not isinstance(
        artifact,
        dict,
    ):

        raise ValueError(
            "Invalid relocation model artifact."
        )

    if "model" not in artifact:
        raise ValueError(
            "Model artifact does not contain a trained model."
        )

    if "feature_columns" not in artifact:
        raise ValueError(
            "Model artifact does not contain feature columns."
        )

    model = artifact[
        "model"
    ]

    feature_columns = artifact[
        "feature_columns"
    ]

    print(
        f"Model type: "
        f"{artifact.get('model_type', 'UNKNOWN')}"
    )

    print(
        f"Features: "
        f"{len(feature_columns)}"
    )

    print(
        f"Validation MAE: "
        f"{artifact.get('validation_mae', 'N/A')}"
    )

    print(
        f"Validation R²: "
        f"{artifact.get('validation_r2', 'N/A')}"
    )

    return (
        model,
        feature_columns,
    )


# ============================================================
# LOAD POPULATION
# ============================================================

def load_population():

    print()
    print(
        "Loading population data..."
    )

    if not POPULATION_FILE.exists():

        raise FileNotFoundError(
            f"Population file not found:\n"
            f"{POPULATION_FILE}"
        )

    population = pd.read_csv(
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
        if column not in population.columns
    ]

    if missing:

        raise ValueError(
            "Population file is missing: "
            + ", ".join(missing)
        )

    population["settlement_id"] = (
        population[
            "settlement_id"
        ]
        .astype(str)
        .str.strip()
    )

    population["population"] = (
        numeric_series(
            population[
                "population"
            ]
        )
    )

    population = population[
        population[
            "population"
        ] > 0
    ].copy()

    for column in [
        "STATE",
        "DISTRICT",
        "SUBDISTT",
    ]:

        if column not in population.columns:
            population[column] = ""

    print(
        f"Population settlements: "
        f"{len(population):,}"
    )

    print(
        f"Total population: "
        f"{population['population'].sum():,.0f}"
    )

    return population


# ============================================================
# LOAD SAFE SITES
# ============================================================

def load_safe_sites():

    print()
    print(
        "Loading safe-site data..."
    )

    if not SAFE_SITES_FILE.exists():

        raise FileNotFoundError(
            f"Safe-site file not found:\n"
            f"{SAFE_SITES_FILE}"
        )

    sites = pd.read_csv(
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
        if column not in sites.columns
    ]

    if missing:

        raise ValueError(
            "Safe-site file is missing: "
            + ", ".join(missing)
        )

    sites["site_id"] = (
        sites["site_id"]
        .astype(str)
        .str.strip()
    )

    sites["temporary_capacity"] = (
        numeric_series(
            sites[
                "temporary_capacity"
            ]
        )
        .clip(lower=0)
    )

    sites["integer_capacity"] = (
        np.floor(
            sites[
                "temporary_capacity"
            ]
        )
        .astype(int)
    )

    sites["safe_site_score"] = (
        numeric_series(
            sites[
                "safe_site_score"
            ]
        )
        .clip(0, 100)
    )

    sites["latitude"] = pd.to_numeric(
        sites.get(
            "latitude",
            np.nan,
        ),
        errors="coerce",
    )

    sites["longitude"] = pd.to_numeric(
        sites.get(
            "longitude",
            np.nan,
        ),
        errors="coerce",
    )

    if (
        "accessibility_score"
        in sites.columns
    ):

        sites[
            "accessibility_score"
        ] = (
            numeric_series(
                sites[
                    "accessibility_score"
                ]
            )
            .clip(0, 100)
        )

    else:

        sites[
            "accessibility_score"
        ] = 50.0

    if (
        "infrastructure_score"
        in sites.columns
    ):

        sites[
            "infrastructure_score"
        ] = (
            numeric_series(
                sites[
                    "infrastructure_score"
                ]
            )
            .clip(0, 100)
        )

    else:

        sites[
            "infrastructure_score"
        ] = 50.0

    if (
        "district_name"
        not in sites.columns
    ):

        sites[
            "district_name"
        ] = ""

    sites[
        "district_clean"
    ] = (
        sites[
            "district_name"
        ]
        .apply(clean_text)
    )

    sites["has_coordinates"] = (
        sites["latitude"].notna()
        &
        sites["longitude"].notna()
    )

    # Only sites that can actually receive people.
    sites = sites[
        sites[
            "integer_capacity"
        ] >= MIN_SITE_CAPACITY
    ].copy()

    print(
        f"Safe sites: "
        f"{len(sites):,}"
    )

    print(
        f"Sites with coordinates: "
        f"{sites['has_coordinates'].sum():,}"
    )

    print(
        f"Total capacity: "
        f"{sites['integer_capacity'].sum():,}"
    )

    return sites.reset_index(
        drop=True
    )


# ============================================================
# LOAD COORDINATES
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

    coordinates = pd.read_csv(
        COORDINATES_FILE,
        low_memory=False,
    )

    required = [
        "settlement_id",
        "latitude",
        "longitude",
    ]

    missing = [
        column
        for column in required
        if column not in coordinates.columns
    ]

    if missing:

        raise ValueError(
            "Coordinate file is missing: "
            + ", ".join(missing)
        )

    coordinates["settlement_id"] = (
        coordinates[
            "settlement_id"
        ]
        .astype(str)
        .str.strip()
    )

    coordinates["latitude"] = (
        pd.to_numeric(
            coordinates[
                "latitude"
            ],
            errors="coerce",
        )
    )

    coordinates["longitude"] = (
        pd.to_numeric(
            coordinates[
                "longitude"
            ],
            errors="coerce",
        )
    )

    coordinates = coordinates[
        coordinates["latitude"].notna()
        &
        coordinates["longitude"].notna()
    ].copy()

    coordinates = (
        coordinates
        .drop_duplicates(
            subset=[
                "settlement_id"
            ]
        )
    )

    print(
        f"Usable coordinates: "
        f"{len(coordinates):,}"
    )

    return coordinates


# ============================================================
# ATTACH SOURCE COORDINATES
# ============================================================

def attach_coordinates(
    population,
    coordinates,
):

    print()
    print(
        "Attaching settlement coordinates..."
    )

    lookup = coordinates[
        [
            "settlement_id",
            "latitude",
            "longitude",
        ]
    ].copy()

    population = population.merge(
        lookup,
        on="settlement_id",
        how="left",
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
# CAPACITY NORMALIZATION
# ============================================================

def calculate_capacity_normalization(
    sites,
):

    capacity = sites[
        "integer_capacity"
    ]

    minimum = capacity.min()
    maximum = capacity.max()

    if maximum == minimum:

        sites[
            "capacity_normalized"
        ] = 100.0

    else:

        sites[
            "capacity_normalized"
        ] = (
            (
                capacity
                - minimum
            )
            /
            (
                maximum
                - minimum
            )
            * 100.0
        )

    return sites


# ============================================================
# BUILD AI FEATURES
# ============================================================

def build_feature_row(
    source,
    site,
    distance,
    feature_columns,
):
    """
    Build exactly the feature schema expected by the trained model.
    """

    source_district = clean_text(
        source.get(
            "DISTRICT",
            "",
        )
    )

    site_district = clean_text(
        site.get(
            "district_name",
            "",
        )
    )

    same_district = int(
        bool(
            source_district
            and site_district
            and source_district
            == site_district
        )
    )

    row = {
        "source_population":
            float(
                source[
                    "population"
                ]
            ),

        "source_latitude":
            float(
                source[
                    "latitude"
                ]
            ),

        "source_longitude":
            float(
                source[
                    "longitude"
                ]
            ),

        "site_safe_score":
            float(
                site[
                    "safe_site_score"
                ]
            ),

        "site_capacity":
            float(
                site[
                    "temporary_capacity"
                ]
            ),

        "site_capacity_normalized":
            float(
                site[
                    "capacity_normalized"
                ]
            ),

        "site_accessibility":
            float(
                site[
                    "accessibility_score"
                ]
            ),

        "site_infrastructure":
            float(
                site[
                    "infrastructure_score"
                ]
            ),

        "site_latitude":
            float(
                site[
                    "latitude"
                ]
            ),

        "site_longitude":
            float(
                site[
                    "longitude"
                ]
            ),

        "distance_km":
            float(
                distance
            ),

        "distance_score":
            float(
                distance_score(
                    distance
                )
            ),

        "same_district":
            same_district,
    }

    # Ensure exact model feature order.
    feature_values = []

    for column in feature_columns:

        feature_values.append(
            row.get(
                column,
                0.0,
            )
        )

    return feature_values


# ============================================================
# SCORE CANDIDATES
# ============================================================

def score_candidates(
    source,
    sites,
    model,
    feature_columns,
):
    """
    Score every geographically valid safe site
    for one source settlement.
    """

    candidates = []

    for site_index, site in (
        sites.iterrows()
    ):

        if not site[
            "has_coordinates"
        ]:

            continue

        if int(
            site[
                "remaining_capacity"
            ]
        ) <= 0:

            continue

        distance = haversine_km(
            source["latitude"],
            source["longitude"],
            site["latitude"],
            site["longitude"],
        )

        if pd.isna(distance):
            continue

        feature_values = (
            build_feature_row(
                source,
                site,
                distance,
                feature_columns,
            )
        )

        candidates.append(
            {
                "site_index":
                    site_index,

                "site":
                    site,

                "distance_km":
                    distance,

                "feature_values":
                    feature_values,
            }
        )

    if not candidates:
        return []

    X = pd.DataFrame(
        [
            candidate[
                "feature_values"
            ]
            for candidate in candidates
        ],
        columns=feature_columns,
    )

    predictions = model.predict(
        X
    )

    for candidate, prediction in zip(
        candidates,
        predictions,
    ):

        candidate[
            "ai_score"
        ] = float(
            np.clip(
                prediction,
                0,
                100,
            )
        )

    candidates.sort(
        key=lambda item: (
            item["ai_score"],
            item["site"][
                "safe_site_score"
            ],
            -item["distance_km"],
        ),
        reverse=True,
    )

    return candidates


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    population,
    sites,
    model,
    feature_columns,
):
    """
    Generate top-K AI recommendations per settlement.

    This stage does ranking, not final capacity allocation.
    The optimizer remains responsible for capacity-constrained
    allocation.
    """

    print()
    print(
        "Generating AI relocation recommendations..."
    )

    recommendations = []

    valid_sites = sites[
        sites[
            "has_coordinates"
        ]
    ].copy()

    if valid_sites.empty:

        raise ValueError(
            "No geographically verified safe sites available."
        )

    valid_sites = calculate_capacity_normalization(
        valid_sites
    )

    # Working capacity.
    valid_sites[
        "remaining_capacity"
    ] = valid_sites[
        "integer_capacity"
    ].astype(int)

    for source_index, source in (
        population.iterrows()
    ):

        source_id = str(
            source[
                "settlement_id"
            ]
        )

        source_name = str(
            source[
                "settlement_name"
            ]
        )

        population_count = int(
            source[
                "population"
            ]
        )

        # ----------------------------------------------------
        # No source coordinates.
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

            recommendations.append(
                {
                    "source_settlement_id":
                        source_id,

                    "source_settlement":
                        source_name,

                    "source_population":
                        population_count,

                    "source_district":
                        source.get(
                            "DISTRICT",
                            "",
                        ),

                    "recommendation_rank":
                        0,

                    "site_id":
                        "",

                    "site_name":
                        "",

                    "site_village":
                        "",

                    "site_district":
                        "",

                    "ai_relocation_score":
                        np.nan,

                    "safe_site_score":
                        np.nan,

                    "site_capacity":
                        np.nan,

                    "distance_km":
                        np.nan,

                    "distance_score":
                        np.nan,

                    "accessibility_score":
                        np.nan,

                    "infrastructure_score":
                        np.nan,

                    "remaining_capacity":
                        np.nan,

                    "recommendation_status":
                        "UNRESOLVED",

                    "reason":
                        "SOURCE_COORDINATES_UNAVAILABLE",
                }
            )

            continue

        # ----------------------------------------------------
        # Score sites.
        # ----------------------------------------------------

        candidates = score_candidates(
            source,
            valid_sites,
            model,
            feature_columns,
        )

        if not candidates:

            recommendations.append(
                {
                    "source_settlement_id":
                        source_id,

                    "source_settlement":
                        source_name,

                    "source_population":
                        population_count,

                    "source_district":
                        source.get(
                            "DISTRICT",
                            "",
                        ),

                    "recommendation_rank":
                        0,

                    "site_id":
                        "",

                    "site_name":
                        "",

                    "site_village":
                        "",

                    "site_district":
                        "",

                    "ai_relocation_score":
                        np.nan,

                    "safe_site_score":
                        np.nan,

                    "site_capacity":
                        np.nan,

                    "distance_km":
                        np.nan,

                    "distance_score":
                        np.nan,

                    "accessibility_score":
                        np.nan,

                    "infrastructure_score":
                        np.nan,

                    "remaining_capacity":
                        np.nan,

                    "recommendation_status":
                        "UNRESOLVED",

                    "reason":
                        "NO_GEOGRAPHICALLY_VALID_SITE",
                }
            )

            continue

        # ----------------------------------------------------
        # Keep top K.
        # ----------------------------------------------------

        top_candidates = (
            candidates[
                :TOP_K
            ]
        )

        for rank, candidate in enumerate(
            top_candidates,
            start=1,
        ):

            site = candidate[
                "site"
            ]

            recommendations.append(
                {
                    "source_settlement_id":
                        source_id,

                    "source_settlement":
                        source_name,

                    "source_population":
                        population_count,

                    "source_district":
                        source.get(
                            "DISTRICT",
                            "",
                        ),

                    "recommendation_rank":
                        rank,

                    "site_id":
                        str(
                            site[
                                "site_id"
                            ]
                        ),

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

                    "ai_relocation_score":
                        round(
                            candidate[
                                "ai_score"
                            ],
                            3,
                        ),

                    "safe_site_score":
                        round(
                            float(
                                site[
                                    "safe_site_score"
                                ]
                            ),
                            3,
                        ),

                    "site_capacity":
                        int(
                            site[
                                "integer_capacity"
                            ]
                        ),

                    "distance_km":
                        round(
                            candidate[
                                "distance_km"
                            ],
                            3,
                        ),

                    "distance_score":
                        round(
                            distance_score(
                                candidate[
                                    "distance_km"
                                ]
                            ),
                            3,
                        ),

                    "accessibility_score":
                        round(
                            float(
                                site[
                                    "accessibility_score"
                                ]
                            ),
                            3,
                        ),

                    "infrastructure_score":
                        round(
                            float(
                                site[
                                    "infrastructure_score"
                                ]
                            ),
                            3,
                        ),

                    "remaining_capacity":
                        int(
                            site[
                                "remaining_capacity"
                            ]
                        ),

                    "recommendation_status":
                        (
                            "PRIMARY"
                            if rank == 1
                            else
                            "ALTERNATIVE"
                        ),

                    "reason":
                        (
                            "AI ranked safe-site "
                            "candidate"
                        ),
                }
            )

    return pd.DataFrame(
        recommendations
    )


# ============================================================
# SAVE
# ============================================================

def save_output(
    recommendations,
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    recommendations.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(
        "Output saved:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "TRINETRA - RELOCATION AI INFERENCE"
    )
    print("=" * 70)

    print()
    print(
        "MEMBER 2 ONLY"
    )

    print(
        "DEM / landslide models are not modified."
    )

    # --------------------------------------------------------
    # Load model.
    # --------------------------------------------------------

    (
        model,
        feature_columns,
    ) = load_model()

    # --------------------------------------------------------
    # Load data.
    # --------------------------------------------------------

    population = (
        load_population()
    )

    sites = (
        load_safe_sites()
    )

    coordinates = (
        load_coordinates()
    )

    # --------------------------------------------------------
    # Attach coordinates.
    # --------------------------------------------------------

    population = (
        attach_coordinates(
            population,
            coordinates,
        )
    )

    # --------------------------------------------------------
    # Generate recommendations.
    # --------------------------------------------------------

    recommendations = (
        generate_recommendations(
            population,
            sites,
            model,
            feature_columns,
        )
    )

    if recommendations.empty:

        raise ValueError(
            "No relocation recommendations were generated."
        )

    # --------------------------------------------------------
    # Save.
    # --------------------------------------------------------

    save_output(
        recommendations
    )

    # --------------------------------------------------------
    # Statistics.
    # --------------------------------------------------------

    primary = recommendations[
        recommendations[
            "recommendation_status"
        ]
        == "PRIMARY"
    ]

    unresolved = recommendations[
        recommendations[
            "recommendation_status"
        ]
        == "UNRESOLVED"
    ]

    print()
    print("=" * 70)
    print(
        "RELOCATION AI INFERENCE COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Population settlements: "
        f"{len(population):,}"
    )

    print(
        f"Primary recommendations: "
        f"{len(primary):,}"
    )

    print(
        f"Alternative recommendations: "
        f"{len(recommendations) - len(primary) - len(unresolved):,}"
    )

    print(
        f"Unresolved settlements: "
        f"{len(unresolved):,}"
    )

    # --------------------------------------------------------
    # Score statistics.
    # --------------------------------------------------------

    valid_scores = recommendations[
        recommendations[
            "ai_relocation_score"
        ].notna()
    ][
        "ai_relocation_score"
    ]

    if not valid_scores.empty:

        print()
        print(
            "AI relocation score:"
        )

        print(
            f"  Minimum : "
            f"{valid_scores.min():.2f}"
        )

        print(
            f"  Maximum : "
            f"{valid_scores.max():.2f}"
        )

        print(
            f"  Mean    : "
            f"{valid_scores.mean():.2f}"
        )

    # --------------------------------------------------------
    # Top recommendations.
    # --------------------------------------------------------

    print()
    print(
        "Top primary recommendations:"
    )

    if primary.empty:

        print(
            "  None"
        )

    else:

        display_columns = [
            "source_settlement",
            "source_population",
            "site_id",
            "site_village",
            "ai_relocation_score",
            "safe_site_score",
            "site_capacity",
            "distance_km",
        ]

        print(
            primary[
                display_columns
            ]
            .sort_values(
                by=[
                    "ai_relocation_score",
                ],
                ascending=False,
            )
            .head(15)
            .to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # Unresolved.
    # --------------------------------------------------------

    if not unresolved.empty:

        print()
        print(
            "Unresolved settlements:"
        )

        print(
            unresolved[
                [
                    "source_settlement_id",
                    "source_settlement",
                    "reason",
                ]
            ]
            .drop_duplicates()
            .to_string(
                index=False
            )
        )

    print()
    print(
        "Output:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()