"""
TRINETRA - RELOCATION AI MODEL TRAINING
=======================================

MEMBER 2 ONLY

Purpose:
    Train a machine-learning ranking model for relocation suitability.

The model learns the relationship between:
    source settlement
    +
    candidate safe site
    =
    relocation suitability

IMPORTANT:
    TRINETRA currently does not contain historical labelled evacuation
    decisions. Therefore this script does NOT claim to train on
    real-world evacuation ground truth.

Instead, it creates a transparent training target from the validated
Member-2 relocation suitability components.

The resulting model is intended to learn/rank candidate destinations
and can later be replaced or retrained with real historical evacuation
labels when such data becomes available.

Inputs:
    data/features/population_master.csv
    data/features/safe_sites.csv
    data/features/settlement_coordinates_final_master.csv

Output:
    models/relocation_model.pkl

This script does NOT:
    - modify DEM
    - modify landslide data
    - train a landslide model
    - train a flood model
    - modify Member-1 code
"""

from pathlib import Path
import math
import pickle
import re

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


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

MODEL_DIR = (
    ROOT
    / "models"
)

MODEL_FILE = (
    MODEL_DIR
    / "relocation_model.pkl"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

RANDOM_STATE = 42

N_ESTIMATORS = 300

TEST_SIZE = 0.20

MIN_TRAINING_ROWS = 100


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
    default=0.0,
):
    """Convert a pandas series to numeric safely."""

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
    """Calculate distance between two geographic coordinates."""

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
    Convert distance into a 0-100 suitability score.

    <= 5 km:
        100

    5-20 km:
        linearly decreases

    >= 20 km:
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
# LOAD POPULATION
# ============================================================

def load_population():

    print()
    print("Loading population data...")

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
        population["settlement_id"]
        .astype(str)
        .str.strip()
    )

    population["population"] = (
        numeric_series(
            population["population"]
        )
    )

    population = population[
        population["population"] > 0
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

    return population.reset_index(
        drop=True
    )


# ============================================================
# LOAD SAFE SITES
# ============================================================

def load_safe_sites():

    print()
    print("Loading safe-site data...")

    if not SAFE_SITES_FILE.exists():
        raise FileNotFoundError(
            f"Safe-site file not found:\n"
            f"{SAFE_SITES_FILE}\n\n"
            "Run safe_sites.py first."
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

    sites["district_clean"] = (
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

    print(
        f"Safe sites: "
        f"{len(sites):,}"
    )

    print(
        f"Sites with coordinates: "
        f"{sites['has_coordinates'].sum():,}"
    )

    print(
        f"Total temporary capacity: "
        f"{sites['temporary_capacity'].sum():,.0f}"
    )

    return sites.reset_index(
        drop=True
    )


# ============================================================
# LOAD COORDINATES
# ============================================================

def load_coordinates():

    print()
    print("Loading settlement coordinates...")

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

    coordinates = coordinates.drop_duplicates(
        subset=[
            "settlement_id"
        ]
    )

    print(
        f"Usable coordinate records: "
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
        "Attaching population coordinates..."
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
# BUILD TRAINING PAIRS
# ============================================================

def build_training_pairs(
    population,
    sites,
):
    """
    Create source-settlement / safe-site pairs.

    Only geographically valid source settlements and safe sites
    are used because distance is an important relocation feature.

    To prevent an excessively large Cartesian product, candidate
    sites are limited to the closest 25 sites for each settlement.

    The training target is a transparent suitability score created
    from existing Member-2 features.

    Target components:

        Safe-site quality       40%
        Capacity                25%
        Accessibility           15%
        Distance                10%
        Infrastructure          10%
    """

    print()
    print(
        "Building relocation training pairs..."
    )

    valid_population = population[
        population["has_coordinates"]
    ].copy()

    valid_sites = sites[
        sites["has_coordinates"]
        &
        (
            sites[
                "temporary_capacity"
            ] > 0
        )
    ].copy()

    print(
        f"Source settlements available: "
        f"{len(valid_population):,}"
    )

    print(
        f"Geographic safe sites available: "
        f"{len(valid_sites):,}"
    )

    if (
        valid_population.empty
        or valid_sites.empty
    ):

        raise ValueError(
            "Not enough geographic data to build "
            "relocation training pairs."
        )

    rows = []

    # --------------------------------------------------------
    # Capacity normalization
    # --------------------------------------------------------

    site_capacity = (
        valid_sites[
            "temporary_capacity"
        ]
    )

    cap_min = site_capacity.min()
    cap_max = site_capacity.max()

    if cap_max == cap_min:

        valid_sites[
            "capacity_normalized"
        ] = 100.0

    else:

        valid_sites[
            "capacity_normalized"
        ] = (
            (
                site_capacity
                - cap_min
            )
            /
            (
                cap_max
                - cap_min
            )
            * 100.0
        )

    # --------------------------------------------------------
    # Build pairs.
    # --------------------------------------------------------

    for _, source in (
        valid_population.iterrows()
    ):

        source_lat = source[
            "latitude"
        ]

        source_lon = source[
            "longitude"
        ]

        source_district = clean_text(
            source.get(
                "DISTRICT",
                "",
            )
        )

        candidates = []

        for _, site in (
            valid_sites.iterrows()
        ):

            distance = haversine_km(
                source_lat,
                source_lon,
                site["latitude"],
                site["longitude"],
            )

            if pd.isna(distance):
                continue

            candidates.append(
                (
                    distance,
                    site,
                )
            )

        if not candidates:
            continue

        # ----------------------------------------------------
        # Limit candidate sites per source settlement.
        # ----------------------------------------------------

        candidates.sort(
            key=lambda item: item[0]
        )

        candidates = candidates[:25]

        for distance, site in candidates:

            distance_component = (
                distance_score(
                    distance
                )
            )

            same_district = int(
                bool(
                    source_district
                    and
                    site[
                        "district_clean"
                    ]
                    and
                    source_district
                    ==
                    site[
                        "district_clean"
                    ]
                )
            )

            # ------------------------------------------------
            # Training target.
            #
            # This is not historical ground truth.
            # It is a transparent ranking signal.
            # ------------------------------------------------

            target = (
                0.40
                * float(
                    site[
                        "safe_site_score"
                    ]
                )

                +

                0.25
                * float(
                    site[
                        "capacity_normalized"
                    ]
                )

                +

                0.15
                * float(
                    site[
                        "accessibility_score"
                    ]
                )

                +

                0.10
                * distance_component

                +

                0.10
                * float(
                    site[
                        "infrastructure_score"
                    ]
                )
            )

            # Same-district preference is encoded as a small
            # ranking adjustment rather than a dominant factor.
            if same_district:
                target += 3.0

            target = min(
                100.0,
                max(
                    0.0,
                    target,
                ),
            )

            rows.append(
                {
                    # Source features
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

                    # Site features
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

                    # Relationship features
                    "distance_km":
                        float(
                            distance
                        ),

                    "distance_score":
                        float(
                            distance_component
                        ),

                    "same_district":
                        same_district,

                    # Target
                    "relocation_suitability":
                        float(
                            target
                        ),
                }
            )

    pairs = pd.DataFrame(
        rows
    )

    if pairs.empty:
        raise ValueError(
            "No training pairs could be generated."
        )

    print(
        f"Training pairs generated: "
        f"{len(pairs):,}"
    )

    print(
        f"Target minimum: "
        f"{pairs['relocation_suitability'].min():.2f}"
    )

    print(
        f"Target maximum: "
        f"{pairs['relocation_suitability'].max():.2f}"
    )

    print(
        f"Target mean: "
        f"{pairs['relocation_suitability'].mean():.2f}"
    )

    return pairs


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(
    pairs,
):
    """
    Train Random Forest regression model.
    """

    print()
    print(
        "Training relocation AI model..."
    )

    feature_columns = [
        "source_population",
        "source_latitude",
        "source_longitude",

        "site_safe_score",
        "site_capacity",
        "site_capacity_normalized",
        "site_accessibility",
        "site_infrastructure",

        "site_latitude",
        "site_longitude",

        "distance_km",
        "distance_score",
        "same_district",
    ]

    target_column = (
        "relocation_suitability"
    )

    X = pairs[
        feature_columns
    ].copy()

    y = pairs[
        target_column
    ].copy()

    if len(X) < MIN_TRAINING_ROWS:
        raise ValueError(
            f"Only {len(X)} training rows available. "
            f"At least {MIN_TRAINING_ROWS} are required."
        )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
        )
    )

    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        max_depth=12,
        min_samples_leaf=2,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    print()
    print(
        "Model evaluation:"
    )

    print(
        f"  Training rows : "
        f"{len(X_train):,}"
    )

    print(
        f"  Test rows     : "
        f"{len(X_test):,}"
    )

    print(
        f"  MAE           : "
        f"{mae:.4f}"
    )

    print(
        f"  R²            : "
        f"{r2:.4f}"
    )

    # --------------------------------------------------------
    # Feature importance.
    # --------------------------------------------------------

    importance = pd.DataFrame(
        {
            "feature":
                feature_columns,

            "importance":
                model.feature_importances_,
        }
    ).sort_values(
        by="importance",
        ascending=False,
    )

    print()
    print(
        "Feature importance:"
    )

    print(
        importance.to_string(
            index=False
        )
    )

    return (
        model,
        feature_columns,
        mae,
        r2,
        importance,
    )


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model,
    feature_columns,
    mae,
    r2,
    importance,
):

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,

        "feature_columns":
            feature_columns,

        "model_type":
            "RandomForestRegressor",

        "random_state":
            RANDOM_STATE,

        "n_estimators":
            N_ESTIMATORS,

        "test_size":
            TEST_SIZE,

        "validation_mae":
            float(mae),

        "validation_r2":
            float(r2),

        "feature_importance":
            importance.to_dict(
                orient="records"
            ),

        "target_definition":
            (
                "Transparent Member-2 relocation "
                "suitability ranking signal based on "
                "safe-site score, capacity, accessibility, "
                "distance, and infrastructure. "
                "Not historical evacuation ground truth."
            ),

        "weights": {
            "safety": 0.40,
            "capacity": 0.25,
            "accessibility": 0.15,
            "distance": 0.10,
            "infrastructure": 0.10,
        },
    }

    with open(
        MODEL_FILE,
        "wb",
    ) as file:

        pickle.dump(
            artifact,
            file,
        )

    print()
    print(
        "Model saved:"
    )

    print(
        MODEL_FILE
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "TRINETRA - RELOCATION AI MODEL TRAINING"
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
    # Build training pairs.
    # --------------------------------------------------------

    pairs = (
        build_training_pairs(
            population,
            sites,
        )
    )

    # --------------------------------------------------------
    # Train.
    # --------------------------------------------------------

    (
        model,
        feature_columns,
        mae,
        r2,
        importance,
    ) = train_model(
        pairs
    )

    # --------------------------------------------------------
    # Save.
    # --------------------------------------------------------

    save_model(
        model,
        feature_columns,
        mae,
        r2,
        importance,
    )

    # --------------------------------------------------------
    # Final.
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "RELOCATION AI TRAINING COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Training pairs : "
        f"{len(pairs):,}"
    )

    print(
        f"Validation MAE : "
        f"{mae:.4f}"
    )

    print(
        f"Validation R²  : "
        f"{r2:.4f}"
    )

    print()
    print(
        "Model artifact:"
    )

    print(
        MODEL_FILE
    )

    print()
    print(
        "Next Member-2 step:"
    )

    print(
        "Run the relocation AI inference module "
        "to rank candidate safe sites for each settlement."
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()