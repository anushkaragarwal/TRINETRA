from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

RISK_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_risk.csv"
)

ANOMALY_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_anomaly_scores.csv"
)

FORECAST_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_forecast_predictions.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_hybrid_hazard.csv"
)

TIME_COL = "Data Acquisition Time"

DISCHARGE_COL = (
    "Telemetry Hourly River Water Discharge (m3/sec)"
)


def risk_category(score):
    if score < 30:
        return "LOW"
    elif score < 60:
        return "MODERATE"
    elif score < 80:
        return "HIGH"
    return "CRITICAL"


def forecast_severity_score(value, q75, q90, q95):
    if pd.isna(value):
        return 0
    elif value <= q75:
        return 10
    elif value <= q90:
        return 40
    elif value <= q95:
        return 70
    return 100


def main():
    print("📥 Loading rule-based risk data...")
    risk = pd.read_csv(
        RISK_PATH,
        parse_dates=[TIME_COL],
    )

    print("📥 Loading anomaly ML data...")
    anomaly = pd.read_csv(
        ANOMALY_PATH,
        parse_dates=[TIME_COL],
    )

    print("📥 Loading 1-hour forecast ML data...")
    forecast = pd.read_csv(
        FORECAST_PATH,
        parse_dates=[TIME_COL],
    )

    # Keep only the columns needed from anomaly output.
    anomaly_small = anomaly[
        [
            "Station",
            TIME_COL,
            "anomaly_score",
            "anomaly_label",
        ]
    ].copy()

    # Keep only the columns needed from forecast output.
    forecast_small = forecast[
        [
            "Station",
            TIME_COL,
            "predicted_discharge_1h",
        ]
    ].copy()

    print("🔗 Merging rule risk with anomaly model output...")

    merged = risk.merge(
        anomaly_small,
        on=["Station", TIME_COL],
        how="left",
    )

    print("🔗 Adding forecast output...")

    merged = merged.merge(
        forecast_small,
        on=["Station", TIME_COL],
        how="left",
    )

    # -----------------------------------------------------
    # A) Anomaly severity score: 0-100
    # -----------------------------------------------------

    merged["anomaly_score"] = (
        merged["anomaly_score"]
        .fillna(0)
    )

    anomaly_rows = merged[
        merged["anomaly_label"] == "ANOMALY"
    ].copy()

    if not anomaly_rows.empty:
        min_anomaly = anomaly_rows["anomaly_score"].min()
        max_anomaly = anomaly_rows["anomaly_score"].max()

        if max_anomaly > min_anomaly:
            merged["anomaly_severity"] = np.where(
                merged["anomaly_label"] == "ANOMALY",
                (
                    (
                        merged["anomaly_score"]
                        - min_anomaly
                    )
                    / (max_anomaly - min_anomaly)
                    * 100
                ),
                0,
            )
        else:
            merged["anomaly_severity"] = np.where(
                merged["anomaly_label"] == "ANOMALY",
                100,
                0,
            )
    else:
        merged["anomaly_severity"] = 0

    # -----------------------------------------------------
    # B) Forecast severity score: 0-100
    # Thresholds are based on historical discharge values.
    # -----------------------------------------------------

    q75 = merged[DISCHARGE_COL].quantile(0.75)
    q90 = merged[DISCHARGE_COL].quantile(0.90)
    q95 = merged[DISCHARGE_COL].quantile(0.95)

    print("\n📌 Historical discharge thresholds:")
    print(f"75th percentile: {q75:.2f} m³/s")
    print(f"90th percentile: {q90:.2f} m³/s")
    print(f"95th percentile: {q95:.2f} m³/s")

    merged["forecast_severity"] = (
        merged["predicted_discharge_1h"]
        .apply(
            lambda x: forecast_severity_score(
                x,
                q75,
                q90,
                q95,
            )
        )
    )

    # -----------------------------------------------------
    # C) Final hybrid hazard score: 0-100
    # 50% rules + 25% anomaly ML + 25% forecast ML
    # -----------------------------------------------------

    merged["hybrid_hazard_score"] = (
        0.50 * merged["risk_score"]
        + 0.25 * merged["anomaly_severity"]
        + 0.25 * merged["forecast_severity"]
    ).round(2)

    merged["hybrid_risk_category"] = (
        merged["hybrid_hazard_score"]
        .apply(risk_category)
    )

    # Is the one-hour forecast available?
    merged["forecast_available"] = (
        merged["predicted_discharge_1h"]
        .notna()
    )

    # Sort output properly.
    merged = merged.sort_values(
        by=["Station", TIME_COL]
    )

    # Print compact output summary.
    print("\n📊 Hybrid risk-category distribution:")
    print(
        merged["hybrid_risk_category"]
        .value_counts()
        .to_string()
    )

    print("\n🚨 Top 15 hybrid-hazard observations:")
    print(
        merged.sort_values(
            by="hybrid_hazard_score",
            ascending=False,
        )[
            [
                "Station",
                TIME_COL,
                DISCHARGE_COL,
                "risk_score",
                "anomaly_label",
                "anomaly_severity",
                "predicted_discharge_1h",
                "forecast_severity",
                "hybrid_hazard_score",
                "hybrid_risk_category",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    merged.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"\n✅ Saved hybrid hazard dataset to:\n{OUTPUT_PATH}")
    print(f"📐 Final dataset shape: {merged.shape}")


if __name__ == "__main__":
    main()