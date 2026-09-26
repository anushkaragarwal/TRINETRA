from pathlib import Path
import pickle

import numpy as np
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

MODEL_PATH = MODEL_DIR / "rainfall_anomaly_model.pkl"

SCALER_PATH = MODEL_DIR / "rainfall_anomaly_scaler.pkl"

OUTPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_anomaly_scores.csv"
)


DATE_COL = "Data Acquisition Time"
STATION_COL = "Station"


def require_columns(df, columns):
    missing = [col for col in columns if col not in df.columns]

    if missing:
        raise ValueError(
            "Missing required rainfall columns: "
            + ", ".join(missing)
        )


def main():

    print("📥 Loading clean rainfall-feature dataset...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[DATE_COL],
    )

    print(f"📊 Loaded rows: {len(df)}")

    print(
        "📋 Rainfall dataset columns:"
    )

    print(
        df.columns.tolist()
    )

    require_columns(
        df,
        [
            DATE_COL,
            STATION_COL,
            "rainfall_mm_1h",
            "rainfall_mm_6h",
            "rainfall_mm_24h",
            "antecedent_rainfall_mm_15d",
        ],
    )

    # -----------------------------------------------------
    # Sort observations
    # -----------------------------------------------------

    df = df.sort_values(
        by=[STATION_COL, DATE_COL]
    ).copy()

    # -----------------------------------------------------
    # Numeric conversion
    # -----------------------------------------------------

    rainfall_columns = [
        "rainfall_mm_1h",
        "rainfall_mm_6h",
        "rainfall_mm_24h",
        "antecedent_rainfall_mm_15d",
    ]

    for col in rainfall_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    # -----------------------------------------------------
    # Create rainfall anomaly features
    # -----------------------------------------------------

    print("\n📊 Creating rainfall anomaly features...")

    # Change in 1-hour rainfall between observations.
    # Calculated separately for each station.
    df["rainfall_change_mm"] = (
        df.groupby(STATION_COL)["rainfall_mm_1h"]
        .diff()
    )

    # Rolling rainfall statistics.
    #
    # The dataset is irregularly sampled, so these are
    # observation-window statistics rather than assuming
    # every row represents exactly one hour.
    df["rainfall_rolling_mean_3obs"] = (
        df.groupby(STATION_COL)["rainfall_mm_1h"]
        .transform(
            lambda s: s.rolling(
                window=3,
                min_periods=1,
            ).mean()
        )
    )

    df["rainfall_rolling_std_3obs"] = (
        df.groupby(STATION_COL)["rainfall_mm_1h"]
        .transform(
            lambda s: s.rolling(
                window=3,
                min_periods=1,
            ).std()
        )
        .fillna(0)
    )

    # Absolute rainfall change
    df["rainfall_change_abs"] = (
        df["rainfall_change_mm"]
        .abs()
        .fillna(0)
    )

    # -----------------------------------------------------
    # ML features
    # -----------------------------------------------------

    feature_columns = [
        "rainfall_mm_1h",
        "rainfall_mm_6h",
        "rainfall_mm_24h",
        "antecedent_rainfall_mm_15d",
        "rainfall_change_abs",
        "rainfall_rolling_mean_3obs",
        "rainfall_rolling_std_3obs",
    ]

    X = df[feature_columns].copy()

    # Replace invalid values
    X = X.replace(
        [np.inf, -np.inf],
        np.nan,
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

    df["anomaly_flag"] = model.predict(
        X_scaled
    )

    # Higher = more unusual
    df["anomaly_score"] = (
        -model.decision_function(X_scaled)
    )

    df["anomaly_label"] = (
        df["anomaly_flag"]
        .map(
            {
                -1: "ANOMALY",
                1: "NORMAL",
            }
        )
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    anomaly_count = (
        df["anomaly_label"] == "ANOMALY"
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
                STATION_COL,
                DATE_COL,
                "rainfall_mm_1h",
                "rainfall_mm_6h",
                "rainfall_mm_24h",
                "antecedent_rainfall_mm_15d",
                "rainfall_change_mm",
                "rainfall_rolling_mean_3obs",
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