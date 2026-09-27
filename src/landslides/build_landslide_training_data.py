from pathlib import Path
import numpy as np
import pandas as pd


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_features_labeled_2014_2017.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_training_data.csv"
)


# =========================================================
# CONFIGURATION
# =========================================================

FEATURES = [
    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation",
]

TARGET = "historical_landslide"

EVENT_COLUMN = "landslide_id"

# Number of negative cells per positive cell.
NEGATIVE_RATIO = 10

# Approximate local-control radius.
#
# We use latitude/longitude distance because the CSV
# contains geographic coordinates.
LOCAL_RADIUS_DEGREES = 0.01

RANDOM_STATE = 42


# =========================================================
# LOAD
# =========================================================

print("=" * 70)
print("BUILDING LANDSLIDE LOCAL-CONTROL TRAINING DATA")
print("=" * 70)

df = pd.read_csv(
    INPUT_PATH
)

print(
    "\nTotal terrain cells:",
    len(df)
)


# =========================================================
# CLEAN
# =========================================================

for column in FEATURES + [
    "lat",
    "lon",
    TARGET,
]:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df = df.dropna(
    subset=FEATURES + [
        "lat",
        "lon",
        TARGET,
    ]
).copy()

df[TARGET] = (
    df[TARGET]
    .astype(int)
)


# =========================================================
# POSITIVE / NEGATIVE
# =========================================================

positive = df[
    df[TARGET] == 1
].copy()

negative = df[
    df[TARGET] == 0
].copy()


print(
    "Positive cells:",
    len(positive)
)

print(
    "Negative cells:",
    len(negative)
)

print(
    "Historical events:",
    positive[EVENT_COLUMN]
    .nunique()
)


# =========================================================
# BUILD LOCAL NEGATIVE CONTROLS
# =========================================================

rng = np.random.default_rng(
    RANDOM_STATE
)

training_parts = []


for event_id, event_positive in (
    positive.groupby(
        EVENT_COLUMN
    )
):

    print(
        f"\nProcessing {event_id}..."
    )

    # -----------------------------------------------------
    # Event centre
    # -----------------------------------------------------

    centre_lat = (
        event_positive["lat"]
        .mean()
    )

    centre_lon = (
        event_positive["lon"]
        .mean()
    )

    # -----------------------------------------------------
    # Find geographically local negatives
    # -----------------------------------------------------

    lat_diff = (
        negative["lat"]
        - centre_lat
    )

    lon_diff = (
        negative["lon"]
        - centre_lon
    )

    distance = np.sqrt(
        lat_diff ** 2
        + lon_diff ** 2
    )

    local_negative = negative[
        distance
        <= LOCAL_RADIUS_DEGREES
    ].copy()

    print(
        "Local negative candidates:",
        len(local_negative)
    )

    # -----------------------------------------------------
    # We need enough controls.
    # -----------------------------------------------------

    desired_count = (
        len(event_positive)
        * NEGATIVE_RATIO
    )

    if len(local_negative) < desired_count:

        print(
            "WARNING: not enough local negatives."
        )

        print(
            "Using all available local negatives."
        )

        selected_negative = (
            local_negative
            .copy()
        )

    else:

        selected_negative = (
            local_negative
            .sample(
                n=desired_count,
                random_state=(
                    RANDOM_STATE
                    + len(training_parts)
                )
            )
            .copy()
        )

    # -----------------------------------------------------
    # Mark source event
    # -----------------------------------------------------

    event_positive = (
        event_positive.copy()
    )

    event_positive[
        "training_event"
    ] = event_id

    selected_negative[
        "training_event"
    ] = event_id

    selected_negative[
        "control_for_event"
    ] = event_id

    event_positive[
        "control_for_event"
    ] = event_id

    # -----------------------------------------------------
    # Combine
    # -----------------------------------------------------

    training_parts.append(
        event_positive
    )

    training_parts.append(
        selected_negative
    )

    print(
        "Positive cells:",
        len(event_positive)
    )

    print(
        "Selected negatives:",
        len(selected_negative)
    )


# =========================================================
# COMBINE
# =========================================================

training = pd.concat(
    training_parts,
    ignore_index=True
)


# =========================================================
# REMOVE DUPLICATE CELLS
# =========================================================

training = training.drop_duplicates(
    subset=[
        "cell_id",
        "training_event",
    ]
).copy()


# =========================================================
# SHUFFLE
# =========================================================

training = training.sample(
    frac=1.0,
    random_state=RANDOM_STATE
).reset_index(
    drop=True
)


# =========================================================
# SUMMARY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "LOCAL-CONTROL TRAINING DATA"
)

print(
    "=" * 70
)

print(
    "Total rows:",
    len(training)
)

print(
    "\nTarget distribution:"
)

print(
    training[
        TARGET
    ]
    .value_counts()
    .sort_index()
    .to_string()
)

print(
    "\nRows by event:"
)

print(
    training[
        "training_event"
    ]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# SAVE
# =========================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

training.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    "\nSaved:"
)

print(
    OUTPUT_PATH
)

print(
    "\nDONE."
)