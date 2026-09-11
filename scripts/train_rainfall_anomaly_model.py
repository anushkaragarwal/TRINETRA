from pathlib import Path
import pickle

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_features.csv"
)

MODEL_DIR = ROOT / "models"

MODEL_PATH = (
    MODEL_DIR
    / "rainfall_anomaly_model.pkl"
)

SCALER_PATH = (
    MODEL_DIR
    / "rainfall_anomaly_scaler.pkl"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_anomaly_scores.csv"
)


DATE_COL = "Date"

DAILY_ACTUAL_COL = "Daily Actual"

DAILY_NORMAL_COL = "Daily Normal"

DAILY_DEPARTURE_COL = "Daily Departure Per"

WEEKLY_ACTUAL_COL = "Weekly  Actual"

WEEKLY_NORMAL_COL = "Weekly Normal"

WEEKLY_DEPARTURE_COL = "Weekly Departure Per"


def main():

    print("📥 Loading clean rainfall-feature dataset...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[DATE_COL],
    )

    df = df.sort_values(
        by=["District", DATE_COL]
    ).copy()

    # -----------------------------------------------------
    # Create rainfall-derived features
    # -----------------------------------------------------

    print("\n📊 Creating rainfall anomaly features...")

    # Daily rainfall change
    df["rainfall_change_mm"] = (
        df.groupby("District")[DAILY_ACTUAL_COL]
        .diff()
    )

    # Rolling rainfall statistics.
    # Only current and previous observations are used.
    df["rainfall_rolling_mean_3d"] = (
        df.groupby("District")[DAILY_ACTUAL_COL]
        .transform(
            lambda s: s.rolling(
                window=3,
                min_periods=1,
            ).mean()
        )
    )

    df["rainfall_rolling_std_3d"] = (
        df.groupby("District")[DAILY_ACTUAL_COL]
        .transform(
            lambda s: s.rolling(
                window=3,
                min_periods=1,
            ).std()
        )
        .fillna(0)
    )

    # Absolute change
    df["rainfall_change_abs"] = (
        df["rainfall_change_mm"]
        .abs()
        .fillna(0)
    )

    # -----------------------------------------------------
    # ML features
    # -----------------------------------------------------

    feature_columns = [
        DAILY_ACTUAL_COL,
        DAILY_NORMAL_COL,
        DAILY_DEPARTURE_COL,

        WEEKLY_ACTUAL_COL,
        WEEKLY_NORMAL_COL,
        WEEKLY_DEPARTURE_COL,

        "rainfall_change_abs",
        "rainfall_rolling_mean_3d",
        "rainfall_rolling_std_3d",
    ]

    X = df[feature_columns].copy()

    # Safety against invalid values
    X = X.replace(
        [float("inf"), float("-inf")],
        0,
    )

    X = X.fillna(0)

    print(
        "📊 Training rows:",
        len(X),
    )

    print(
        "🧠 ML features:",
        feature_columns,
    )

    # -----------------------------------------------------
    # Scaling
    # -----------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # -----------------------------------------------------
    # Isolation Forest
    # -----------------------------------------------------

    model = IsolationForest(
        n_estimators=250,
        contamination=0.10,
        random_state=42,
    )

    print(
        "\n🧠 Training Isolation Forest "
        "rainfall anomaly model..."
    )

    model.fit(X_scaled)

    # -1 = anomaly
    #  1 = normal

    df["anomaly_flag"] = (
        model.predict(X_scaled)
    )

    # Higher = more unusual
    df["anomaly_score"] = (
        -model.decision_function(X_scaled)
    )

    df["anomaly_label"] = (
        df["anomaly_flag"]
        .map({
            -1: "ANOMALY",
            1: "NORMAL",
        })
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    anomaly_count = (
        df["anomaly_label"]
        == "ANOMALY"
    ).sum()

    print(
        f"⚠️ Anomalies detected: "
        f"{anomaly_count}"
    )

    print(
        f"📈 Anomaly rate: "
        f"{anomaly_count / len(df) * 100:.2f}%"
    )

    # -----------------------------------------------------
    # Top anomalous observations
    # -----------------------------------------------------

    print(
        "\n🔎 Top anomalous rainfall observations:"
    )

    print(
        df.sort_values(
            by="anomaly_score",
            ascending=False,
        )[
            [
                "District",
                DATE_COL,
                DAILY_ACTUAL_COL,
                DAILY_DEPARTURE_COL,
                "rainfall_change_mm",
                "rainfall_rolling_mean_3d",
                "anomaly_score",
                "anomaly_label",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Save model and scaler
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        MODEL_PATH,
        "wb",
    ) as file:

        pickle.dump(
            model,
            file,
        )

    with open(
        SCALER_PATH,
        "wb",
    ) as file:

        pickle.dump(
            scaler,
            file,
        )

    # -----------------------------------------------------
    # Save anomaly-scored dataset
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\n✅ Model saved: "
        f"{MODEL_PATH}"
    )

    print(
        f"✅ Scaler saved: "
        f"{SCALER_PATH}"
    )

    print(
        f"✅ Anomaly-scored data saved: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()