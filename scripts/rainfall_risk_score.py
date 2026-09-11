from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_features.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk.csv"
)

DAILY_ACTUAL_COLUMN = "Daily Actual"
DAILY_DEPARTURE_COLUMN = "Daily Departure Per"


def main():

    print("📥 Loading processed rainfall data...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=["Date"]
    )

    print(f"📊 Records loaded: {len(df)}")

    # ------------------------------------------------------------
    # Calculate rainfall thresholds from historical observations
    # ------------------------------------------------------------

    rainfall_values = df[DAILY_ACTUAL_COLUMN].dropna()

    q50 = rainfall_values.quantile(0.50)
    q75 = rainfall_values.quantile(0.75)
    q90 = rainfall_values.quantile(0.90)
    q95 = rainfall_values.quantile(0.95)

    departure_values = (
        df[DAILY_DEPARTURE_COLUMN]
        .dropna()
    )

    d50 = departure_values.quantile(0.50)
    d75 = departure_values.quantile(0.75)
    d90 = departure_values.quantile(0.90)
    d95 = departure_values.quantile(0.95)

    print("\n🌧️ Rainfall thresholds:")
    print(f"   Q50: {q50:.2f} mm")
    print(f"   Q75: {q75:.2f} mm")
    print(f"   Q90: {q90:.2f} mm")
    print(f"   Q95: {q95:.2f} mm")

    print("\n📈 Departure thresholds:")
    print(f"   D50: {d50:.2f}%")
    print(f"   D75: {d75:.2f}%")
    print(f"   D90: {d90:.2f}%")
    print(f"   D95: {d95:.2f}%")

    # ------------------------------------------------------------
    # Rainfall intensity score
    # ------------------------------------------------------------

    def rainfall_score(value):

        if pd.isna(value):
            return 0

        if value >= q95:
            return 90
        elif value >= q90:
            return 70
        elif value >= q75:
            return 40
        elif value >= q50:
            return 20
        else:
            return 10

    # ------------------------------------------------------------
    # Rainfall departure score
    # ------------------------------------------------------------

    def departure_score(value):

        if pd.isna(value):
            return 0

        if value >= d95:
            return 90
        elif value >= d90:
            return 70
        elif value >= d75:
            return 40
        elif value >= d50:
            return 20
        else:
            return 10

    df["rainfall_intensity_score"] = (
        df[DAILY_ACTUAL_COLUMN]
        .apply(rainfall_score)
    )

    df["rainfall_departure_score"] = (
        df[DAILY_DEPARTURE_COLUMN]
        .apply(departure_score)
    )

    # ------------------------------------------------------------
    # Combined rainfall risk
    # ------------------------------------------------------------

    df["risk_score"] = (
        0.60 * df["rainfall_intensity_score"]
        + 0.40 * df["rainfall_departure_score"]
    )

    # ------------------------------------------------------------
    # Risk category
    # ------------------------------------------------------------

    def risk_category(score):

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
        .apply(risk_category)
    )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n🔎 Latest rainfall risk:")

    print(
        df[
            [
                "District",
                "Date",
                DAILY_ACTUAL_COLUMN,
                DAILY_DEPARTURE_COLUMN,
                "rainfall_intensity_score",
                "rainfall_departure_score",
                "risk_score",
                "risk_category",
            ]
        ].tail(10).to_string(index=False)
    )

    print(
        f"\n💾 Rainfall risk saved: {OUTPUT_PATH}"
    )

    print("\n✅ RAINFALL RISK SCORING COMPLETED")


if __name__ == "__main__":
    main()