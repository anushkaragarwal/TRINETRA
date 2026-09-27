import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold


# =========================================================
# PATHS
# =========================================================

INPUT_PATH = (
    "data/features/"
    "terrain_features_labeled_2014_2017.csv"
)

MODEL_DIR = "models"
MODEL_PATH = "models/landslide_model.pkl"

PREDICTION_PATH = (
    "data/features/landslide_predictions.csv"
)

os.makedirs(MODEL_DIR, exist_ok=True)


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

# Random seed for reproducibility.
RANDOM_STATE = 42

# Minimum distance, in degrees, from a mapped landslide
# for selecting a negative training cell.
#
# ~0.002 degrees is roughly a couple hundred metres
# around this latitude.
NEGATIVE_BUFFER_DEGREES = 0.002


# =========================================================
# 1. LOAD DATA
# =========================================================

print("=" * 70)
print("LANDSLIDE MODEL TRAINING")
print("=" * 70)

print("\nLoading labeled terrain data...")

df = pd.read_csv(INPUT_PATH)

print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# =========================================================
# 2. VALIDATE REQUIRED COLUMNS
# =========================================================

required_columns = (
    FEATURES
    + [
        TARGET,
        EVENT_COLUMN,
        "lat",
        "lon",
    ]
)

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )


# =========================================================
# 3. CLEAN DATA
# =========================================================

numeric_columns = FEATURES + [
    "lat",
    "lon",
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df[TARGET] = pd.to_numeric(
    df[TARGET],
    errors="coerce"
)

df = df.dropna(
    subset=numeric_columns + [TARGET]
).copy()

df[TARGET] = df[TARGET].astype(int)


# =========================================================
# 4. BASIC LABEL CHECK
# =========================================================

print("\nLabel distribution:")

print(
    df[TARGET]
    .value_counts()
    .sort_index()
)

positive = df[
    df[TARGET] == 1
].copy()

negative = df[
    df[TARGET] == 0
].copy()

print(
    "\nPositive cells:",
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
# 5. EVENT SUMMARY
# =========================================================

print("\nPositive cells per historical event:")

print(
    positive[
        EVENT_COLUMN
    ]
    .value_counts()
    .sort_index()
)


# =========================================================
# 6. NEGATIVE SAMPLING
# =========================================================

print("\nSelecting controlled negative sample...")

rng = np.random.default_rng(
    RANDOM_STATE
)

# ---------------------------------------------------------
# Remove negatives very close to known landslides.
# ---------------------------------------------------------

positive_lat = positive[
    "lat"
].to_numpy()

positive_lon = positive[
    "lon"
].to_numpy()

negative_lat = negative[
    "lat"
].to_numpy()

negative_lon = negative[
    "lon"
].to_numpy()


safe_negative_mask = np.ones(
    len(negative),
    dtype=bool
)

# Process in chunks so memory stays reasonable.
chunk_size = 100000

for start in range(
    0,
    len(negative),
    chunk_size
):

    end = min(
        start + chunk_size,
        len(negative)
    )

    lat_chunk = (
        negative_lat[start:end]
    )

    lon_chunk = (
        negative_lon[start:end]
    )

    # Find the nearest historical landslide
    # using squared geographic distance.
    #
    # This is sufficient for a small local AOI.
    min_distance = np.full(
        len(lat_chunk),
        np.inf
    )

    for p_lat, p_lon in zip(
        positive_lat,
        positive_lon
    ):

        distance = (
            (lat_chunk - p_lat) ** 2
            +
            (lon_chunk - p_lon) ** 2
        )

        min_distance = np.minimum(
            min_distance,
            distance
        )

    safe_negative_mask[start:end] = (
        min_distance
        >= NEGATIVE_BUFFER_DEGREES ** 2
    )


safe_negative = negative[
    safe_negative_mask
].copy()

print(
    "Safe negative cells:",
    len(safe_negative)
)


# =========================================================
# 7. CONTROL NEGATIVE / POSITIVE RATIO
# =========================================================

desired_negative_count = (
    len(positive)
    * NEGATIVE_RATIO
)

desired_negative_count = int(
    min(
        desired_negative_count,
        len(safe_negative)
    )
)

if desired_negative_count < len(
    positive
):
    raise ValueError(
        "Not enough safe negative cells "
        "for the requested training ratio."
    )


negative_sample = (
    safe_negative
    .sample(
        n=desired_negative_count,
        random_state=RANDOM_STATE
    )
    .copy()
)


training_df = pd.concat(
    [
        positive,
        negative_sample,
    ],
    ignore_index=True
)

training_df = training_df.sample(
    frac=1.0,
    random_state=RANDOM_STATE
).reset_index(
    drop=True
)


print(
    "\nTraining dataset:"
)

print(
    "Positive:",
    int(
        training_df[TARGET].sum()
    )
)

print(
    "Negative:",
    int(
        (training_df[TARGET] == 0).sum()
    )
)

print(
    "Total:",
    len(training_df)
)


# =========================================================
# 8. PREPARE FEATURES
# =========================================================

X = training_df[
    FEATURES
].copy()

y = training_df[
    TARGET
].copy()


# =========================================================
# 9. EVENT-AWARE VALIDATION
# =========================================================

print("\n" + "=" * 70)
print("EVENT-AWARE VALIDATION")
print("=" * 70)

# ---------------------------------------------------------
# Positive cells have their real event ID.
#
# Negative cells are assigned to synthetic groups based
# on geographic blocks. This prevents all negatives from
# becoming one giant validation group.
# ---------------------------------------------------------

BLOCK_SIZE = 0.02

training_df["spatial_block"] = (
    np.floor(
        training_df["lat"]
        / BLOCK_SIZE
    ).astype(int).astype(str)
    + "_"
    +
    np.floor(
        training_df["lon"]
        / BLOCK_SIZE
    ).astype(int).astype(str)
)

# For positive cells:
# use actual landslide event.
#
# For negatives:
# use spatial block.
#
# This creates groups that are geographically meaningful.
positive_group = (
    "EVENT_"
    + training_df[EVENT_COLUMN]
    .fillna("UNKNOWN")
    .astype(str)
)

negative_group = (
    "NEG_"
    + training_df["spatial_block"]
)

groups = np.where(
    training_df[TARGET] == 1,
    positive_group,
    negative_group
)

groups = pd.Series(
    groups,
    index=training_df.index
)


# =========================================================
# 10. BUILD VALIDATION SPLITS
# =========================================================

unique_positive_events = (
    positive[EVENT_COLUMN]
    .dropna()
    .unique()
)

n_splits = min(
    5,
    len(unique_positive_events)
)

if n_splits < 2:
    raise ValueError(
        "Not enough historical events "
        "for validation."
    )

gkf = GroupKFold(
    n_splits=n_splits
)


# =========================================================
# 11. VALIDATION MODEL
# =========================================================

fold_results = []

for fold, (
    train_idx,
    test_idx
) in enumerate(
    gkf.split(
        X,
        y,
        groups=groups
    ),
    start=1
):

    X_train = X.iloc[
        train_idx
    ]

    X_test = X.iloc[
        test_idx
    ]

    y_train = y.iloc[
        train_idx
    ]

    y_test = y.iloc[
        test_idx
    ]

    # Make sure both classes exist.
    if (
        y_train.nunique() < 2
        or y_test.nunique() < 2
    ):
        print(
            f"\nFold {fold}: skipped "
            "(only one class present)"
        )
        continue

    fold_model = (
        RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    )

    fold_model.fit(
        X_train,
        y_train
    )

    y_prob = (
        fold_model
        .predict_proba(X_test)[:, 1]
    )

    # Default threshold only for reporting.
    y_pred = (
        y_prob >= 0.5
    ).astype(int)

    roc_auc = roc_auc_score(
        y_test,
        y_prob
    )

    pr_auc = average_precision_score(
        y_test,
        y_prob
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    fold_results.append(
        {
            "fold": fold,
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "test_rows": len(
                test_idx
            ),
            "test_positive": int(
                y_test.sum()
            ),
        }
    )

    print(
        f"\nFold {fold}"
    )

    print(
        "Test rows:",
        len(test_idx)
    )

    print(
        "Positive test rows:",
        int(y_test.sum())
    )

    print(
        "ROC-AUC:",
        round(roc_auc, 4)
    )

    print(
        "PR-AUC:",
        round(pr_auc, 4)
    )

    print(
        "Precision:",
        round(precision, 4)
    )

    print(
        "Recall:",
        round(recall, 4)
    )

    print(
        "F1:",
        round(f1, 4)
    )


# =========================================================
# 12. VALIDATION SUMMARY
# =========================================================

if fold_results:

    results_df = pd.DataFrame(
        fold_results
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "VALIDATION SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        results_df.to_string(
            index=False
        )
    )

    print("\nMean metrics:")

    print(
        results_df[
            [
                "roc_auc",
                "pr_auc",
                "precision",
                "recall",
                "f1",
            ]
        ]
        .mean()
        .round(4)
        .to_string()
    )

else:

    print(
        "\nNo valid validation folds."
    )


# =========================================================
# 13. TRAIN FINAL MODEL
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "TRAINING FINAL LANDSLIDE MODEL"
)

print(
    "=" * 70
)

final_model = (
    RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
)

final_model.fit(
    X,
    y
)


# =========================================================
# 14. FEATURE IMPORTANCE
# =========================================================

importance = pd.DataFrame(
    {
        "feature": FEATURES,
        "importance":
            final_model.feature_importances_,
    }
)

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print(
    "\nFeature importance:"
)

print(
    importance.to_string(
        index=False
    )
)


# =========================================================
# 15. PREDICT ENTIRE DEM GRID
# =========================================================

print(
    "\nGenerating landslide susceptibility "
    "for the complete DEM grid..."
)

all_X = df[
    FEATURES
].copy()

probability = (
    final_model
    .predict_proba(all_X)[:, 1]
)


# =========================================================
# 16. CONVERT TO 0–100 SUSCEPTIBILITY SCORE
# =========================================================

df["landslide_probability"] = (
    probability
)

df["landslide_score"] = (
    probability * 100
).round(2)


# =========================================================
# 17. SUSCEPTIBILITY LEVEL
# =========================================================

def susceptibility_level(
    score
):

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MODERATE"

    return "LOW"


df["landslide_level"] = (
    df["landslide_score"]
    .apply(
        susceptibility_level
    )
)


# =========================================================
# 18. SAVE PREDICTIONS
# =========================================================

prediction_columns = [
    "cell_id",
    "lat",
    "lon",
    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation",
    "historical_landslide",
    "landslide_id",
    "landslide_year",
    "landslide_probability",
    "landslide_score",
    "landslide_level",
]

predictions = df[
    prediction_columns
].copy()

predictions.to_csv(
    PREDICTION_PATH,
    index=False
)


# =========================================================
# 19. SAVE MODEL
# =========================================================

joblib.dump(
    final_model,
    MODEL_PATH
)


# =========================================================
# 20. FINAL SUMMARY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "LANDSLIDE MODEL COMPLETE"
)

print(
    "=" * 70
)

print(
    "\nModel:",
    MODEL_PATH
)

print(
    "Predictions:",
    PREDICTION_PATH
)

print(
    "\nSusceptibility distribution:"
)

print(
    predictions[
        "landslide_level"
    ]
    .value_counts()
    .to_string()
)

print(
    "\nScore statistics:"
)

print(
    predictions[
        "landslide_score"
    ]
    .describe()
    .round(2)
    .to_string()
)

print(
    "\nDone."
)