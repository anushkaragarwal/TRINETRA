from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

FEATURE_DIR = ROOT / "data" / "features"

POPULATION_FILE = FEATURE_DIR / "population_master.csv"
FACILITY_FILE = FEATURE_DIR / "facility_master.csv"


# ============================================================
# POSSIBLE COORDINATE COLUMN NAMES
# ============================================================

LATITUDE_NAMES = {
    "latitude",
    "lat",
    "y",
}

LONGITUDE_NAMES = {
    "longitude",
    "lon",
    "lng",
    "x",
}


# ============================================================
# FIND COORDINATE COLUMNS
# ============================================================

def find_coordinate_columns(df: pd.DataFrame):

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    latitude_column = None
    longitude_column = None

    for name in LATITUDE_NAMES:
        if name in normalized:
            latitude_column = normalized[name]
            break

    for name in LONGITUDE_NAMES:
        if name in normalized:
            longitude_column = normalized[name]
            break

    return latitude_column, longitude_column


# ============================================================
# VALIDATE COORDINATES
# ============================================================

def validate_dataset(
    path: Path,
    identifier_column: str,
):

    print("\n" + "=" * 60)
    print(f"DATASET: {path.name}")
    print("=" * 60)

    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    df = pd.read_csv(path)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    latitude_column, longitude_column = find_coordinate_columns(df)

    if latitude_column is None or longitude_column is None:

        print("\n⚠️ COORDINATES NOT FOUND")

        print("\nAvailable columns:")

        for column in df.columns:
            print(f"  - {column}")

        return

    print("\nCoordinates found:")

    print(f"Latitude column : {latitude_column}")
    print(f"Longitude column: {longitude_column}")

    lat = pd.to_numeric(
        df[latitude_column],
        errors="coerce"
    )

    lon = pd.to_numeric(
        df[longitude_column],
        errors="coerce"
    )

    valid = (
        lat.between(-90, 90)
        &
        lon.between(-180, 180)
    )

    print(f"\nValid coordinates : {valid.sum()}")
    print(f"Invalid coordinates: {(~valid).sum()}")

    print("\nCoordinate coverage:")

    print(
        f"Latitude range : "
        f"{lat.min()} → {lat.max()}"
    )

    print(
        f"Longitude range: "
        f"{lon.min()} → {lon.max()}"
    )

    if identifier_column in df.columns:

        print("\nSample locations:")

        sample = df.loc[
            valid,
            [
                identifier_column,
                latitude_column,
                longitude_column,
            ]
        ].head(10)

        print(
            sample.to_string(
                index=False
            )
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("TRINETRA - COORDINATE VALIDATION")
    print("=" * 60)

    validate_dataset(
        POPULATION_FILE,
        "settlement_id"
    )

    validate_dataset(
        FACILITY_FILE,
        "pseudocode"
    )

    print("\n")
    print("=" * 60)
    print("COORDINATE VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()