from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

RISK_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk.csv"
)

ANOMALY_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_anomaly_scores.csv"
)

FORECAST_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_forecast_predictions.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_hybrid_hazard.csv"
)


def hazard_category(score):

    if score < 30:
        return "LOW"
    elif score < 60:
        return "MODERATE"
    elif score < 80:
        return "HIGH"
    else:
        return "CRITICAL"


def main():

    print("📥 Loading rainfall risk data...")

    risk = pd.read_csv(
        RISK_PATH,
        parse_dates=["Date"]
    )

    print("📥 Loading rainfall anomaly data...")

    anomaly = pd.read_csv(
        ANOMALY_PATH,
        parse_dates=["Date"]
    )

    print("📥 Loading rainfall forecast data...")

    forecast = pd.read_csv(
        FORECAST_PATH,
        parse_dates=["Date"]
    )

    # ------------------------------------------------------------
    # Merge risk + anomaly
    # ------------------------------------------------------------

    df = risk.merge(
        anomaly[
            [
                "District",
                "Date",
                "anomaly_flag",
                "anomaly_score",
                "anomaly_label",
            ]
        ],
        on=["District", "Date"],
        how="left"
    )

    # ------------------------------------------------------------
    # Anomaly severity
    # ------------------------------------------------------------

    anomaly_scores = df.loc[
        df["anomaly_label"] == "ANOMALY",
        "anomaly_score"
    ].dropna()

    df["anomaly_severity"] = 0.0

    if len(anomaly_scores) > 0:

        anomaly_min = anomaly_scores.min()
        anomaly_max = anomaly_scores.max()

        anomaly_mask = (
            df["anomaly_label"] == "ANOMALY"
        )

        if anomaly_max > anomaly_min:

            df.loc[anomaly_mask, "anomaly_severity"] = (
                (
                    df.loc[anomaly_mask, "anomaly_score"]
                    - anomaly_min
                )
                /
                (
                    anomaly_max
                    - anomaly_min
                )
                * 100
            )

        else:

            df.loc[anomaly_mask, "anomaly_severity"] = 100.0

    # ------------------------------------------------------------
    # Historical rainfall thresholds
    # ------------------------------------------------------------

    historical_rainfall = (
        df["Daily Actual"]
        .dropna()
    )

    q75 = historical_rainfall.quantile(0.75)
    q90 = historical_rainfall.quantile(0.90)
    q95 = historical_rainfall.quantile(0.95)

    # ------------------------------------------------------------
    # Forecast severity function
    # ------------------------------------------------------------

    def forecast_severity(value):

        if pd.isna(value):
            return 0

        if value >= q95:
            return 100
        elif value >= q90:
            return 70
        elif value >= q75:
            return 40
        else:
            return 10

    # ------------------------------------------------------------
    # Historical forecast predictions
    # ------------------------------------------------------------

    historical_forecast = forecast[
        forecast["target_rainfall_1d"].notna()
    ].copy()

    historical_forecast["forecast_date"] = (
        historical_forecast["Date"]
        + pd.Timedelta(days=1)
    )

    # ------------------------------------------------------------
    # Operational forecast
    # ------------------------------------------------------------

    operational_forecast = forecast[
        forecast["target_rainfall_1d"].isna()
    ].copy()

    operational_forecast["forecast_date"] = (
        operational_forecast["Date"]
        + pd.Timedelta(days=1)
    )

    if not operational_forecast.empty:

        latest_forecast = (
            operational_forecast
            .sort_values("Date")
            .groupby(
                "District",
                as_index=False
            )
            .tail(1)
        )

    else:

        latest_forecast = pd.DataFrame()

    # ------------------------------------------------------------
    # Add operational forecast to current/latest observation
    # ------------------------------------------------------------

    if not latest_forecast.empty:

        latest_forecast = latest_forecast[
            [
                "District",
                "Date",
                "forecast_date",
                "predicted_rainfall_1d",
            ]
        ].copy()

        latest_forecast["forecast_severity"] = (
            latest_forecast[
                "predicted_rainfall_1d"
            ]
            .apply(forecast_severity)
        )

        print(
            "\n🔮 Operational rainfall forecast:"
        )

        print(
            latest_forecast.to_string(
                index=False
            )
        )

    # ------------------------------------------------------------
    # Current observed hybrid hazard
    # ------------------------------------------------------------

    df["forecast_severity"] = 0.0

    # Only historical predictions whose Date matches
    # the current observation are used here.

    historical_forecast_for_merge = (
        historical_forecast[
            [
                "District",
                "Date",
                "predicted_rainfall_1d",
            ]
        ]
    )

    df = df.merge(
        historical_forecast_for_merge,
        on=["District", "Date"],
        how="left"
    )

    df["forecast_severity"] = (
        df["predicted_rainfall_1d"]
        .apply(forecast_severity)
    )

    # ------------------------------------------------------------
    # Hybrid hazard score
    # ------------------------------------------------------------

    df["hybrid_hazard_score"] = (
        0.50 * df["risk_score"]
        + 0.25 * df["anomaly_severity"]
        + 0.25 * df["forecast_severity"]
    )

    df["hazard_category"] = (
        df["hybrid_hazard_score"]
        .apply(hazard_category)
    )

    # ------------------------------------------------------------
    # Save observed-date hazard
    # ------------------------------------------------------------

    df = df.sort_values(
        by=["District", "Date"]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ------------------------------------------------------------
    # Display latest observed hazard
    # ------------------------------------------------------------

    print(
        "\n🚨 Latest observed rainfall hybrid hazard:"
    )

    print(
        df[
            [
                "District",
                "Date",
                "Daily Actual",
                "risk_score",
                "risk_category",
                "anomaly_severity",
                "predicted_rainfall_1d",
                "forecast_severity",
                "hybrid_hazard_score",
                "hazard_category",
            ]
        ]
        .tail(10)
        .to_string(index=False)
    )

    # ------------------------------------------------------------
    # Display next-day operational hazard context
    # ------------------------------------------------------------

    if not latest_forecast.empty:

        latest_observation = (
            df.sort_values("Date")
            .groupby(
                "District",
                as_index=False
            )
            .tail(1)
        )

        operational = latest_forecast.merge(
            latest_observation[
                [
                    "District",
                    "Date",
                    "risk_score",
                    "risk_category",
                    "anomaly_severity",
                ]
            ],
            on=["District", "Date"],
            how="left"
        )

        operational["hybrid_hazard_score"] = (
            0.50 * operational["risk_score"]
            + 0.25 * operational["anomaly_severity"]
            + 0.25 * operational["forecast_severity"]
        )

        operational["hazard_category"] = (
            operational["hybrid_hazard_score"]
            .apply(hazard_category)
        )

        print(
            "\n🚨 Next-day operational rainfall hazard:"
        )

        print(
            operational[
                [
                    "District",
                    "Date",
                    "forecast_date",
                    "risk_score",
                    "risk_category",
                    "anomaly_severity",
                    "predicted_rainfall_1d",
                    "forecast_severity",
                    "hybrid_hazard_score",
                    "hazard_category",
                ]
            ].to_string(index=False)
        )

    print(
        f"\n💾 Rainfall hybrid hazard saved: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\n✅ RAINFALL HYBRID HAZARD COMPLETED"
    )


if __name__ == "__main__":
    main()