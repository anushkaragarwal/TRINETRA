# scripts/fetch_river.py
import sys
from pathlib import Path

# Add src to Python path so we can import river.*
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from river.cwc_api import fetch_cwc_data  # uses NWDP CWC dataset
from river.processor import validate_data


def main():
    print("Fetching CWC river data...")
    df = fetch_cwc_data()
    print("Raw shape:", df.shape)

    print("Validating...")
    validate_data(df)

    out_dir = ROOT / "data" / "river" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "cwc_uttarakhand_raw.csv"

    df.to_csv(out_path, index=False)
    print("Saved raw data to:", out_path)


if __name__ == "__main__":
    main()