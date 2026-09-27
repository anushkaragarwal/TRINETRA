# scripts/explore_processed.py
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proc_path = ROOT / "data" / "river" / "processed" / "river_features.csv"

df = pd.read_csv(proc_path, parse_dates=["Data Acquisition Time"])

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print(df.head())

print("\nStations:", df["Station"].nunique())
print("Time range:", df["Data Acquisition Time"].min(), "→", df["Data Acquisition Time"].max())
print("\nDischarge stats:")
print(df["Telemetry Hourly River Water Discharge (m3/sec)"].describe())