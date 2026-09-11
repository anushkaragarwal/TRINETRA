import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAINFALL_SRC = ROOT / "src" / "rainfall"

sys.path.append(str(RAINFALL_SRC))

from imd_api import fetch_rainfall_data
from processor import validate_data

def main():

    print("Fetching rainfall data from NWDP / IMD API...")

    # ---------------------------------------------------------
    # 1. Fetch data from API
    # ---------------------------------------------------------

    df = fetch_rainfall_data()

    print("Raw shape:", df.shape)

    # ---------------------------------------------------------
    # 2. Validate API data
    # ---------------------------------------------------------

    print("Validating...")

    validate_data(df)

    # ---------------------------------------------------------
    # 3. Save raw API response
    # ---------------------------------------------------------

    out_dir = (
        ROOT
        / "data"
        / "rainfall"
        / "raw"
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    out_path = (
        out_dir
        / "rainfall_raw.csv"
    )

    df.to_csv(
        out_path,
        index=False,
    )

    print(
        "Saved raw rainfall data to:",
        out_path,
    )


if __name__ == "__main__":
    main()