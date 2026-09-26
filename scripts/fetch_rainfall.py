import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

RAINFALL_SRC = (
    ROOT
    / "src"
    / "rainfall"
)

sys.path.append(
    str(RAINFALL_SRC)
)

from imd_api import fetch_rainfall_data


def main():

    print(
        "🌧️ Fetching HIGH-FREQUENCY rainfall data "
        "from NWDP..."
    )

    df = fetch_rainfall_data()

    print(
        "\n📊 Raw dataset shape:",
        df.shape,
    )

    print(
        "\n📋 API columns:"
    )

    for column in df.columns:
        print(
            f"   - {column}"
        )

    print(
        "\n🔎 First 10 records:"
    )

    print(
        df.head(10)
        .to_string(index=False)
    )

    print(
        "\n🔎 Last 10 records:"
    )

    print(
        df.tail(10)
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Save raw API response
    # -----------------------------------------------------

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
        / "rainfall_hourly_raw.csv"
    )

    df.to_csv(
        out_path,
        index=False,
    )

    print(
        "\n💾 Saved raw rainfall data to:"
    )

    print(
        out_path
    )

    print(
        "\n✅ HIGH-FREQUENCY RAINFALL FETCH COMPLETED"
    )


if __name__ == "__main__":
    main()