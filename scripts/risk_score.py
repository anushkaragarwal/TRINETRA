from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SRC = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_features.csv"
)

DST = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_risk.csv"
)

def main():

    print("📥 Loading processed river data...")

    df = pd.read_csv(
        SRC,
        parse_dates=["Data Acquisition Time"]
    )

    print(f"📊 Records loaded: {len(df)}")

    discharge_col = (
        "Telemetry Hourly River Water Discharge (m3/sec)"
    )

    rate_col = (
        "discharge_rate_m3s_per_hour"
    )

    discharge_values = (
        df[discharge_col]
        .dropna()
    )

    q25 = discharge_values.quantile(0.25)
    q75 = discharge_values.quantile(0.75)
    q95 = discharge_values.quantile(0.95)

    print("\n🌊 Discharge thresholds:")
    print(f"   Q25: {q25:.2f} m³/s")
    print(f"   Q75: {q75:.2f} m³/s")
    print(f"   Q95: {q95:.2f} m³/s")


    def level_score(value):

        if pd.isna(value):
            return 0

        if value <= q25:
            return 10

        elif value <= q75:
            return 40

        elif value <= q95:
            return 70

        else:
            return 90


    df["level_score"] = (
        df[discharge_col]
        .apply(level_score)
    )

    rising_rate = (
        df[rate_col]
        .clip(lower=0)
        .fillna(0.0)
    )

    df["rising_discharge_rate"] = rising_rate

    r50 = rising_rate.quantile(0.50)
    r80 = rising_rate.quantile(0.80)
    r95 = rising_rate.quantile(0.95)

    print("\n📈 Rising discharge-rate thresholds:")
    print(f"   R50: {r50:.4f} m³/s/hour")
    print(f"   R80: {r80:.4f} m³/s/hour")
    print(f"   R95: {r95:.4f} m³/s/hour")


    def rate_score(value):

        if value <= r50:
            return 10

        elif value <= r80:
            return 40

        elif value <= r95:
            return 70

        else:
            return 90


    df["rate_score"] = (
        rising_rate
        .apply(rate_score)
    )


    df["risk_score"] = (
        0.60 * df["level_score"]
        + 0.40 * df["rate_score"]
    ).round(2)

    def risk_label(score):

        if score < 30:
            return "LOW"

        elif score < 60:
            return "MODERATE"

        elif score < 80:
            return "HIGH"

        else:
            return "CRITICAL"


    df["risk_category"] = (
        df["risk_score"]
        .apply(risk_label)
    )

    print("\n🚨 Latest river risk observations:")

    print(
        df[
            [
                "Station",
                "Data Acquisition Time",
                discharge_col,
                rate_col,
                "rising_discharge_rate",
                "level_score",
                "rate_score",
                "risk_score",
                "risk_category",
            ]
        ]
        .tail(10)
        .to_string(index=False)
    )

    print("\n📊 River risk-category distribution:")

    print(
        df["risk_category"]
        .value_counts()
        .to_string()
    )

    DST.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        DST,
        index=False
    )

    print(
        f"\n💾 River risk data saved to:\n{DST}"
    )

    print("\n✅ RIVER RISK SCORING COMPLETED")

if __name__ == "__main__":
    main()