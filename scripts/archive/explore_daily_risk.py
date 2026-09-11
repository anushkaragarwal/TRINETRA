# scripts/explore_daily_risk.py
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

path = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_risk_daily.csv"
)

df = pd.read_csv(path)

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nRisk category counts:")
print(
    df["daily_risk_category"]
    .value_counts()
    .to_string()
)

print("\nTop 10 highest risk days:")
print(
    df.sort_values(
        by="max_risk_score",
        ascending=False,
    )[
        [
            "Station",
            "date",
            "max_discharge",
            "max_risk_score",
            "high_or_critical_observations",
            "daily_risk_category",
        ]
    ]
    .head(10)
    .to_string(index=False)
)