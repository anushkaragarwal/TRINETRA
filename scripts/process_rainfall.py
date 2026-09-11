# scripts/process_rainfall.py

import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RAINFALL_SRC = ROOT / "src" / "rainfall"

sys.path.append(str(RAINFALL_SRC))


# ---------------------------------------------------------
# Rainfall processor
# ---------------------------------------------------------

from processor import process_dataframe


def main():

    # -----------------------------------------------------
    # 1. Load raw rainfall data
    # -----------------------------------------------------

    raw_path = (
        ROOT
        / "data"
        / "rainfall"
        / "raw"
        / "rainfall_raw.csv"
    )

    print(
        "📥 Loading raw rainfall data from:",
        raw_path,
    )

    df_raw = pd.read_csv(
        raw_path
    )

    print(
        "Raw shape:",
        df_raw.shape,
    )

    # -----------------------------------------------------
    # 2. Run complete rainfall processing pipeline
    # -----------------------------------------------------

    print(
        "\n🌧️ Processing rainfall data..."
    )

    df_proc = process_dataframe(
        df_raw
    )

    # -----------------------------------------------------
    # 3. Save processed/features dataset
    # -----------------------------------------------------

    out_dir = (
        ROOT
        / "data"
        / "rainfall"
        / "processed"
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    out_path = (
        out_dir
        / "rainfall_features.csv"
    )

    df_proc.to_csv(
        out_path,
        index=False,
    )

    print(
        "\n💾 Saved processed rainfall data to:",
        out_path,
    )

    print(
        "Processed shape:",
        df_proc.shape,
    )


if __name__ == "__main__":
    main()