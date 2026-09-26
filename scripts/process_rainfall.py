from pathlib import Path
import sys
import pandas as pd

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.rainfall.processor import process_dataframe


INPUT_PATH = ROOT / "data" / "rainfall" / "raw" / "rainfall_hourly_raw.csv"
OUTPUT_PATH = ROOT / "data" / "rainfall" / "processed" / "rainfall_features.csv"


def main():
    print("Processing rainfall data...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Rainfall raw file not found:\n{INPUT_PATH}"
        )

    df_raw = pd.read_csv(INPUT_PATH)

    print(f"Raw records: {len(df_raw)}")
    print(f"Raw columns: {len(df_raw.columns)}")

    df_processed = process_dataframe(df_raw)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_csv(OUTPUT_PATH, index=False)

    print("\nProcessing complete.")
    print(f"Processed records: {len(df_processed)}")
    print(f"Processed columns: {len(df_processed.columns)}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nColumns:")
    print(df_processed.columns.tolist())

    print("\nFirst 5 records:")
    print(df_processed.head().to_string(index=False))


if __name__ == "__main__":
    main()