from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "population"
OUTPUT_DIR = ROOT / "data" / "features"

INPUT_FILE = DATA_DIR / "population_habitations_2026.csv"
OUTPUT_FILE = OUTPUT_DIR / "population_master.csv"


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "STATE",
    "DISTRICT",
    "SUBDISTT",
    "TOWN/VILLAGE",
    "LEVEL",
    "NAME",
    "TRU",
    "NO_HH",
    "TOT_P",
    "TOT_M",
    "TOT_F",
    "POPULATION_YEAR",
    "SOURCE",
    "NAME_CLEAN",
    "POP_2011",
    "POP_2026_EST",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_population(path: Path) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Population file not found:\n{path}"
        )

    df = pd.read_csv(path)

    print(f"Loaded: {path.name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(missing_columns)
        )

    return df


# ============================================================
# CLEAN DATA
# ============================================================

def clean_population(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # --------------------------------------------------------
    # Clean names
    # --------------------------------------------------------

    df["NAME"] = (
        df["NAME"]
        .astype(str)
        .str.strip()
    )

    df["NAME_CLEAN"] = (
        df["NAME_CLEAN"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "STATE",
        "DISTRICT",
        "SUBDISTT",
        "TOWN/VILLAGE",
        "WARD",
        "NO_HH",
        "TOT_P",
        "TOT_M",
        "TOT_F",
        "POP_2011",
        "POP_2026_EST",
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Remove invalid population records
    # --------------------------------------------------------

    df = df[
        df["POP_2026_EST"].notna()
    ].copy()

    df = df[
        df["POP_2026_EST"] >= 0
    ].copy()

    # --------------------------------------------------------
    # Remove duplicate habitations
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["TOWN/VILLAGE"]
    ).copy()

    return df


# ============================================================
# CREATE STANDARDIZED COLUMNS
# ============================================================

def create_standard_columns(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Stable internal settlement identifier.
    df["settlement_id"] = (
        "SETTLEMENT_"
        + df["TOWN/VILLAGE"]
        .astype("Int64")
        .astype(str)
    )

    # Human-readable settlement name.
    df["settlement_name"] = df["NAME"]

    # Population used by the 2026 relocation model.
    df["population"] = df["POP_2026_EST"]

    # Historical population retained for comparison.
    df["population_2011"] = df["POP_2011"]

    # Population growth since Census 2011.
    df["population_growth"] = (
        df["population"]
        - df["population_2011"]
    )

    # Percentage growth.
    df["population_growth_pct"] = 0.0

    valid = df["population_2011"] > 0

    df.loc[valid, "population_growth_pct"] = (
        (
            df.loc[valid, "population"]
            - df.loc[valid, "population_2011"]
        )
        / df.loc[valid, "population_2011"]
    ) * 100.0

    # Households.
    df["households"] = df["NO_HH"]

    # Rural/urban classification.
    df["settlement_type"] = df["TRU"]

    return df


# ============================================================
# SELECT FINAL COLUMNS
# ============================================================

def select_columns(df: pd.DataFrame) -> pd.DataFrame:

    columns = [
        "settlement_id",
        "settlement_name",

        "STATE",
        "DISTRICT",
        "SUBDISTT",

        "TOWN/VILLAGE",
        "WARD",
        "LEVEL",

        "settlement_type",

        "NO_HH",
        "households",

        "TOT_P",
        "TOT_M",
        "TOT_F",

        "population_2011",
        "population",
        "population_growth",
        "population_growth_pct",

        "POPULATION_YEAR",
        "SOURCE",

        "NAME_CLEAN",
    ]

    return df[columns].copy()


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("\n========================================")
    print("TRINETRA - POPULATION PREPARATION")
    print("========================================\n")

    # 1. Load
    df = load_population(INPUT_FILE)

    # 2. Clean
    df = clean_population(df)

    print(f"\nAfter cleaning: {len(df)} settlements")

    # 3. Standardize
    df = create_standard_columns(df)

    # 4. Select final schema
    df = select_columns(df)

    # 5. Create output directory
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # 6. Save
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # REPORT
    # ========================================================

    print("\n========================================")
    print("POPULATION DATASET CREATED")
    print("========================================")

    print(f"\nOutput:")
    print(OUTPUT_FILE)

    print(f"\nNumber of settlements: {len(df)}")

    print(
        f"Total estimated 2026 population: "
        f"{df['population'].sum():,.0f}"
    )

    print(
        f"Total 2011 population: "
        f"{df['population_2011'].sum():,.0f}"
    )

    print(
        f"Average settlement population: "
        f"{df['population'].mean():,.2f}"
    )

    print("\nLargest settlements:")

    print(
        df[
            [
                "settlement_id",
                "settlement_name",
                "population",
            ]
        ]
        .sort_values(
            "population",
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )

    print("\n========================================")
    print("DONE")
    print("========================================\n")


if __name__ == "__main__":
    main()