from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

src = ROOT / "data" / "river" / "processed" / "river_risk.csv"
dst = ROOT / "data" / "river" / "processed" / "river_risk_daily.csv"


def get_daily_risk_category(score):
    if score < 30:
        return "LOW"
    elif score < 60:
        return "MODERATE"
    elif score < 80:
        return "HIGH"
    return "CRITICAL"


def main():
    print("📥 Loading river risk dataset...")

    df = pd.read_csv(
        src,
        parse_dates=["Data Acquisition Time"],
    )

    discharge_col = (
        "Telemetry Hourly River Water Discharge (m3/sec)"
    )

    # Create daily bucket
    df["date"] = df["Data Acquisition Time"].dt.date

    print("📊 Aggregating 15-minute readings into daily risk summaries...")

    daily = (
        df.groupby(["Station", "date"])
        .agg(
            observations=("risk_score", "size"),

            max_discharge=(
                discharge_col,
                "max",
            ),

            mean_discharge=(
                discharge_col,
                "mean",
            ),

            max_risk_score=(
                "risk_score",
                "max",
            ),

            mean_risk_score=(
                "risk_score",
                "mean",
            ),

            high_or_critical_observations=(
                "risk_category",
                lambda x: x.isin(
                    ["HIGH", "CRITICAL"]
                ).sum(),
            ),
        )
        .reset_index()
    )

    daily["daily_risk_category"] = (
        daily["max_risk_score"]
        .apply(get_daily_risk_category)
    )

    daily = daily.sort_values(
        by=["Station", "date"]
    )

    print("\n📌 Latest 10 daily records:")
    print(
        daily.tail(10).to_string(
            index=False
        )
    )

    print("\n📌 Daily-risk category distribution:")
    print(
        daily["daily_risk_category"]
        .value_counts()
        .to_string()
    )

    print("\n📌 Highest-risk days:")
    print(
        daily.sort_values(
            by="max_risk_score",
            ascending=False,
        )
        .head(10)[
            [
                "Station",
                "date",
                "max_discharge",
                "max_risk_score",
                "high_or_critical_observations",
                "daily_risk_category",
            ]
        ]
        .to_string(index=False)
    )

    dst.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily.to_csv(
        dst,
        index=False,
    )

    print(f"\n✅ Saved daily river risk data to:\n{dst}")
    print(f"📐 Daily dataset shape: {daily.shape}")


if __name__ == "__main__":
    main()