# scripts/process_river.py
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from river.processor import process_dataframe  # uses filter + clean + features

def main():
    # 1. Raw file path (jo fetch_river ne save kiya tha)
    raw_path = ROOT / "data" / "river" / "raw" / "cwc_uttarakhand_raw.csv"

    print("📥 Loading raw river data from:", raw_path)
    df_raw = pd.read_csv(raw_path)
    print("Raw shape:", df_raw.shape)

    # 2. Run full processing pipeline
    df_proc = process_dataframe(df_raw)

    # 3. Save processed/features dataset
    out_dir = ROOT / "data" / "river" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "river_features.csv"

    df_proc.to_csv(out_path, index=False)
    print("💾 Saved processed river data to:", out_path)
    print("Processed shape:", df_proc.shape)


if __name__ == "__main__":
    main()