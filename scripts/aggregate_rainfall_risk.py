from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk_daily.csv"
)

DATE_COLUMN = "Date"


def risk_category(score):

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

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[DATE_COLUMN]
    )

    print(f"📊 Records loaded: {len(df)}")

    # ------------------------------------------------------------
    # Create daily date bucket
    # ------------------------------------------------------------

    df["date"] = df[DATE_COLUMN].dt.date

    # ------------------------------------------------------------
    # Aggregate rainfall risk by district and day
    # ------------------------------------------------------------

    daily = (
        df.groupby(
            ["District", "date"],
            as_index=False
        )
        .agg(
            observations=("risk_score", "count"),
            max_daily_rainfall_mm=("Daily Actual", "max"),
            mean_daily_rainfall_mm=("Daily Actual", "mean"),
            max_risk_score=("risk_score", "max"),
            mean_risk_score=("risk_score", "mean"),
            high_count=(
                "risk_category",
                lambda x: (x == "HIGH").sum()
            ),
            critical_count=(
                "risk_category",
                lambda x: (x == "CRITICAL").sum()
            ),
        )
    )

    # ------------------------------------------------------------
    # Daily risk category
    # ------------------------------------------------------------

    daily["risk_category"] = (
        daily["max_risk_score"]
        .apply(risk_category)
    )

    # ------------------------------------------------------------
    # Sort
    # ------------------------------------------------------------

    daily = daily.sort_values(
        by=["District", "date"]
    )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    daily.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n📊 Daily rainfall risk:")

    print(
        daily.tail(10).to_string(index=False)
    )

    print(
        f"\n💾 Daily rainfall risk saved: {OUTPUT_PATH}"
    )

    print("\n✅ DAILY RAINFALL RISK AGGREGATION COMPLETED")


if __name__ == "__main__":
    main()