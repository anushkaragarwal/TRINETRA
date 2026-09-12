from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "population"
OUTPUT_DIR = ROOT / "data" / "features"

PROFILE_FILE = DATA_DIR / "0502_prof1.csv"
FACILITY_FILE = DATA_DIR / "0502_fac.csv"
SAFETY_FILE = DATA_DIR / "0502_safety.csv"

OUTPUT_FILE = OUTPUT_DIR / "facility_master.csv"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    if "pseudocode" not in df.columns:
        raise ValueError(f"'pseudocode' column missing from {path}")

    return df


def main() -> None:
    print("Loading facility datasets...")

    profile = load_csv(PROFILE_FILE)
    facility = load_csv(FACILITY_FILE)
    safety = load_csv(SAFETY_FILE)

    print(f"Profile rows : {len(profile)}")
    print(f"Facility rows: {len(facility)}")
    print(f"Safety rows  : {len(safety)}")

    # Remove accidental duplicate keys before joining.
    profile = profile.drop_duplicates(subset="pseudocode")
    facility = facility.drop_duplicates(subset="pseudocode")
    safety = safety.drop_duplicates(subset="pseudocode")

    # Prefix overlapping/non-key fields so the origin remains clear.
    facility_columns = [
        c for c in facility.columns
        if c != "pseudocode"
    ]

    safety_columns = [
        c for c in safety.columns
        if c != "pseudocode"
    ]

    facility = facility.rename(
        columns={c: f"facility_{c}" for c in facility_columns}
    )

    safety = safety.rename(
        columns={c: f"safety_{c}" for c in safety_columns}
    )

    # Merge all three datasets.
    merged = profile.merge(
        facility,
        on="pseudocode",
        how="left",
        validate="one_to_one"
    )

    merged = merged.merge(
        safety,
        on="pseudocode",
        how="left",
        validate="one_to_one"
    )

    # Basic missing-value accounting.
    missing = merged.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    print("\nMissing values:")
    if missing.empty:
        print("None")
    else:
        print(missing.to_string())

    # Ensure output directory exists.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    merged.to_csv(OUTPUT_FILE, index=False)

    print("\nFacility master dataset created:")
    print(OUTPUT_FILE)

    print("\nFinal shape:")
    print(merged.shape)

    print("\nColumns:")
    print(list(merged.columns))


if __name__ == "__main__":
    main()