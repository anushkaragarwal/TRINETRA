from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_training_data.csv"
)

MODEL_DIR = ROOT / "models"

MODEL_PATH = (
    MODEL_DIR
    / "landslide_model.pkl"
)

PREDICTION_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_predictions.csv"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# CONFIGURATION
# =========================================================

BASE_FEATURES = [
    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation",
]

TARGET = "historical_landslide"

GROUP_COLUMN = "training_event"

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("=" * 70)
print("LANDSLIDE MODEL V2")
print("=" * 70)

print("\nLoading training data...")

df = pd.read_csv(
    INPUT_PATH
)

print(
    "Rows:",
    len(df)
)


# =========================================================
# CLEAN
# =========================================================

for column in BASE_FEATURES + [
    TARGET
]:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df = df.dropna(
    subset=BASE_FEATURES + [
        TARGET,
        GROUP_COLUMN
    ]
).copy()

df[TARGET] = (
    df[TARGET]
    .astype(int)
)


# =========================================================
# ASPECT ENCODING
# =========================================================
#
# Aspect is circular:
#
# 359 degrees ≈ 1 degree
#
# A normal numerical representation incorrectly treats
# them as far apart.
#
# Convert aspect into two continuous variables.
# =========================================================

aspect_rad = np.deg2rad(
    df["aspect"]
)

df["aspect_sin"] = np.sin(
    aspect_rad
)

df["aspect_cos"] = np.cos(
    aspect_rad
)


# =========================================================
# FINAL FEATURES
# =========================================================

FEATURES = [
    "elevation",
    "slope",
    "aspect_sin",
    "aspect_cos",
    "curvature",
    "flow_accumulation",
]


X = df[
    FEATURES
]

y = df[
    TARGET
]

groups = df[
    GROUP_COLUMN
]


print(
    "\nFeatures:"
)

for feature in FEATURES:
    print(
        "-",
        feature
    )


print(
    "\nTarget distribution:"
)

print(
    y.value_counts()
    .sort_index()
)


print(
    "\nEvents:",
    groups.nunique()
)


# =========================================================
# EVENT-AWARE CROSS VALIDATION
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "EVENT-AWARE VALIDATION"
)

print(
    "=" * 70
)


unique_groups = (
    groups
    .unique()
)

n_splits = min(
    5,
    len(unique_groups)
)

group_kfold = GroupKFold(
    n_splits=n_splits
)


validation_results = []


for fold, (
    train_idx,
    test_idx
) in enumerate(
    group_kfold.split(
        X,
        y,
        groups
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

    test_groups = groups.iloc[
        test_idx
    ]

    print(
        f"\nFold {fold}"
    )

    print(
        "Test events:",
        test_groups
        .unique()
        .tolist()
    )

    print(
        "Training rows:",
        len(X_train)
    )

    print(
        "Testing rows:",
        len(X_test)
    )

    print(
        "Positive test rows:",
        int(y_test.sum())
    )


    # -----------------------------------------------------
    # MODEL
    # -----------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=15,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=(
            RANDOM_STATE + fold
        ),
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )


    # -----------------------------------------------------
    # PROBABILITY
    # -----------------------------------------------------

    y_prob = (
        model
        .predict_proba(X_test)[:, 1]
    )

    y_pred = (
        y_prob >= 0.5
    ).astype(int)


    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    roc_auc = roc_auc_score(
        y_test,
        y_prob
    )

    pr_auc = average_precision_score(
        y_test,
        y_prob
    )


    precision, recall, thresholds = (
        precision_recall_curve(
            y_test,
            y_prob
        )
    )


    # F1 for threshold analysis.
    f1 = (
        2
        * precision
        * recall
        / (
            precision
            + recall
            + 1e-12
        )
    )

    best_index = np.argmax(
        f1
    )

    if best_index < len(
        thresholds
    ):

        best_threshold = (
            thresholds[
                best_index
            ]
        )

        best_f1 = (
            f1[
                best_index
            ]
        )

    else:

        best_threshold = 0.5
        best_f1 = 0.0


    print(
        "ROC-AUC:",
        round(
            roc_auc,
            4
        )
    )

    print(
        "PR-AUC:",
        round(
            pr_auc,
            4
        )
    )

    print(
        "Best F1 threshold:",
        round(
            best_threshold,
            4
        )
    )

    print(
        "Best F1:",
        round(
            best_f1,
            4
        )
    )


    # -----------------------------------------------------
    # DEFAULT 0.5 REPORT
    # -----------------------------------------------------

    print(
        "\nClassification report "
        "(threshold=0.5):"
    )

    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )


    validation_results.append({
        "fold": fold,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "best_threshold": best_threshold,
        "best_f1": best_f1,
        "test_rows": len(y_test),
        "test_positive": int(
            y_test.sum()
        ),
    })


# =========================================================
# VALIDATION SUMMARY
# =========================================================

results = pd.DataFrame(
    validation_results
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
    results.round(4)
    .to_string(
        index=False
    )
)


print(
    "\nMean metrics:"
)

print(
    "ROC-AUC:",
    round(
        results["roc_auc"].mean(),
        4
    )
)

print(
    "PR-AUC:",
    round(
        results["pr_auc"].mean(),
        4
    )
)

print(
    "Best F1:",
    round(
        results["best_f1"].mean(),
        4
    )
)

print(
    "Mean best threshold:",
    round(
        results["best_threshold"].mean(),
        4
    )
)


# =========================================================
# TRAIN FINAL MODEL
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


final_model = RandomForestClassifier(
    n_estimators=400,
    max_depth=15,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

final_model.fit(
    X,
    y
)


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

importance = pd.DataFrame({
    "feature": FEATURES,
    "importance":
        final_model.feature_importances_
})

importance = (
    importance
    .sort_values(
        "importance",
        ascending=False
    )
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
# SAVE MODEL
# =========================================================

joblib.dump(
    final_model,
    MODEL_PATH
)


print(
    "\nModel saved:"
)

print(
    MODEL_PATH
)


# =========================================================
# PREDICT FULL DEM GRID
# =========================================================

print(
    "\nGenerating landslide susceptibility "
    "for the complete DEM training grid..."
)

# For now we predict the same terrain cells that
# were used to build the labeled terrain dataset.
#
# Later, this can be replaced with the full
# dem_integrated_features.csv grid.

full = pd.read_csv(
    ROOT
    / "data"
    / "features"
    / "terrain_features.csv"
)


for column in BASE_FEATURES:

    full[column] = pd.to_numeric(
        full[column],
        errors="coerce"
    )


full = full.dropna(
    subset=BASE_FEATURES
).copy()


full_aspect_rad = np.deg2rad(
    full["aspect"]
)

full["aspect_sin"] = np.sin(
    full_aspect_rad
)

full["aspect_cos"] = np.cos(
    full_aspect_rad
)


full_X = full[
    FEATURES
]


full["landslide_probability"] = (
    final_model
    .predict_proba(full_X)[:, 1]
)


full["landslide_score"] = (
    full["landslide_probability"]
    * 100
).round(2)


# =========================================================
# INITIAL LEVELS
# =========================================================
#
# These are provisional.
# We will recalibrate them after inspecting the
# actual probability distribution.
# =========================================================

def susceptibility_level(score):

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MODERATE"

    return "LOW"


full["landslide_level"] = (
    full["landslide_score"]
    .apply(
        susceptibility_level
    )
)


# =========================================================
# SAVE PREDICTIONS
# =========================================================

output_columns = [
    "cell_id",
    "lat",
    "lon",
    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation",
    "landslide_probability",
    "landslide_score",
    "landslide_level",
]


full[
    output_columns
].to_csv(
    PREDICTION_PATH,
    index=False
)


# =========================================================
# SUMMARY
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
    "\nPrediction rows:",
    len(full)
)

print(
    "\nSusceptibility distribution:"
)

print(
    full[
        "landslide_level"
    ]
    .value_counts()
    .to_string()
)

print(
    "\nProbability statistics:"
)

print(
    full[
        "landslide_probability"
    ]
    .describe()
    .round(4)
    .to_string()
)

print(
    "\nPredictions saved:"
)

print(
    PREDICTION_PATH
)