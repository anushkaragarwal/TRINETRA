from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "data" / "river" / "processed" / "river_features.csv"
dst = ROOT / "data" / "river" / "processed" / "river_risk.csv"

def main():
    df = pd.read_csv(src, parse_dates=["Data Acquisition Time"])

    discharge_col = "Telemetry Hourly River Water Discharge (m3/sec)"
    rate_col = "discharge_rate_m3s_per_hour"

    # Level-based score thresholds
    q25 = df[discharge_col].quantile(0.25)
    q75 = df[discharge_col].quantile(0.75)
    q95 = df[discharge_col].quantile(0.95)

    def level_score(x):
        if x <= q25:
            return 10
        if x <= q75:
            return 40
        if x <= q95:
            return 70
        return 90

    df["level_score"] = df[discharge_col].apply(level_score)

    # Rate-based score thresholds
    rate_abs = df[rate_col].abs().fillna(0.0)
    r50 = rate_abs.quantile(0.50)
    r80 = rate_abs.quantile(0.80)
    r95 = rate_abs.quantile(0.95)

    def rate_score(x):
        if x <= r50:
            return 10
        if x <= r80:
            return 40
        if x <= r95:
            return 70
        return 90

    df["rate_score"] = rate_abs.apply(rate_score)

    # Combined risk score
    df["risk_score"] = 0.6 * df["level_score"] + 0.4 * df["rate_score"]

    def risk_label(s):
        if s < 30:
            return "LOW"
        if s < 60:
            return "MODERATE"
        if s < 80:
            return "HIGH"
        return "CRITICAL"

    df["risk_category"] = df["risk_score"].apply(risk_label)

    print(
        df[[
            "Station",
            "Data Acquisition Time",
            discharge_col,
            "risk_score",
            "risk_category",
        ]].tail(10).to_string(index=False)
    )

    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst, index=False)
    print("Saved:", dst)

if __name__ == "__main__":
    main()