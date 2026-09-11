from pathlib import Path
import pickle

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_features.csv"
)

MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "river_anomaly_model.pkl"
SCALER_PATH = MODEL_DIR / "river_anomaly_scaler.pkl"

OUTPUT_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_anomaly_scores.csv"
)

DISCHARGE_COL = (
    "Telemetry Hourly River Water Discharge (m3/sec)"
)


def main():
    print("📥 Loading clean river-feature dataset...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=["Data Acquisition Time"],
    )

    # Create rolling features using only past/current values.
    # min_periods avoids dropping initial few rows unnecessarily.
    df["discharge_rolling_mean_1h"] = (
        df[DISCHARGE_COL]
        .rolling(window=4, min_periods=1)
        .mean()
    )

    df["discharge_rolling_std_1h"] = (
        df[DISCHARGE_COL]
        .rolling(window=4, min_periods=1)
        .std()
        .fillna(0)
    )

    df["discharge_change_abs"] = (
        df["discharge_change_m3s"]
        .abs()
        .fillna(0)
    )

    df["discharge_rate_abs"] = (
        df["discharge_rate_m3s_per_hour"]
        .abs()
        .fillna(0)
    )

    feature_columns = [
        DISCHARGE_COL,
        "discharge_rolling_mean_1h",
        "discharge_rolling_std_1h",
        "discharge_change_abs",
        "discharge_rate_abs",
    ]

    X = df[feature_columns].copy()

    # Safety: replace any unexpected missing/infinite values.
    X = X.replace([float("inf"), float("-inf")], 0)
    X = X.fillna(0)

    print("📊 Training rows:", len(X))
    print("🧠 ML features:", feature_columns)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # contamination=0.03 means model marks ~3% most unusual
    # records as anomalies; tune after analysing outputs.
    model = IsolationForest(
        n_estimators=250,
        contamination=0.03,
        random_state=42,
    )

    print("🧠 Training Isolation Forest anomaly model...")
    model.fit(X_scaled)

    # IsolationForest: -1 = anomaly; 1 = normal
    df["anomaly_flag"] = model.predict(X_scaled)

    # Higher value = more unusual after negating decision_function
    df["anomaly_score"] = -model.decision_function(X_scaled)

    df["anomaly_label"] = df["anomaly_flag"].map({
        -1: "ANOMALY",
        1: "NORMAL",
    })

    anomaly_count = (
        df["anomaly_label"] == "ANOMALY"
    ).sum()

    print(f"⚠️ Anomalies detected: {anomaly_count}")
    print(
        f"📈 Anomaly rate: "
        f"{anomaly_count / len(df) * 100:.2f}%"
    )

    print("\n🔎 Top 15 anomalous observations:")
    print(
        df.sort_values(
            by="anomaly_score",
            ascending=False,
        )[
            [
                "Station",
                "Data Acquisition Time",
                DISCHARGE_COL,
                "discharge_change_m3s",
                "discharge_rate_m3s_per_hour",
                "anomaly_score",
                "anomaly_label",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(model, file)

    with open(SCALER_PATH, "wb") as file:
        pickle.dump(scaler, file)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n✅ Model saved: {MODEL_PATH}")
    print(f"✅ Scaler saved: {SCALER_PATH}")
    print(f"✅ Anomaly-scored data saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()