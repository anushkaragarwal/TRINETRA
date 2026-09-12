import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)


# =========================================================
# PATHS
# =========================================================

INPUT_PATH = "data/features/terrain_features_labeled_2014_2017.csv"

MODEL_DIR = "models"
MODEL_PATH = "models/landslide_model.pkl"

os.makedirs(MODEL_DIR, exist_ok=True)


# =========================================================
# 1. LOAD DATA
# =========================================================

print("Loading labeled terrain data...")

df = pd.read_csv(INPUT_PATH)

print("Rows:", len(df))
print("Columns:", list(df.columns))


# =========================================================
# 2. FEATURES AND TARGET
# =========================================================

FEATURES = [
    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation"
]

TARGET = "historical_landslide"


X = df[FEATURES]
y = df[TARGET]


# =========================================================
# 3. CHECK LABEL DISTRIBUTION
# =========================================================

print("\nLabel distribution:")
print(y.value_counts())

print("\nPositive landslide cells:", int(y.sum()))
print("Negative cells:", int((y == 0).sum()))


# =========================================================
# 4. TRAIN-TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# =========================================================
# 5. TRAIN RANDOM FOREST
# =========================================================

print("\nTraining landslide model...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# =========================================================
# 6. EVALUATION
# =========================================================

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("\n========================================")
print("LANDSLIDE MODEL RESULTS")
print("========================================")

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

try:
    auc = roc_auc_score(y_test, y_prob)
    print("\nROC-AUC:", round(auc, 4))
except ValueError:
    print("\nROC-AUC could not be calculated.")


# =========================================================
# 7. FEATURE IMPORTANCE
# =========================================================

importance = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance)


# =========================================================
# 8. SAVE MODEL
# =========================================================

joblib.dump(model, MODEL_PATH)

print("\n========================================")
print("MODEL TRAINING COMPLETE")
print("========================================")

print("Saved model:")
print(MODEL_PATH)