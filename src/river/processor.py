import pandas as pd

from config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    MIN_LAT,
    MAX_LAT,
    MIN_LON,
    MAX_LON,
    STATION_COLUMN,
    LATITUDE_COLUMN,
    LONGITUDE_COLUMN,
    TIME_COLUMN,
    DISCHARGE_COLUMN,
)


def load_data():
    print("📂 Loading CWC river data...")

    df = pd.read_csv(RAW_DATA_PATH)

    print(f"✅ Loaded {len(df)} records")

    return df


def filter_mvp_area(df):
    print("\n📍 Filtering MVP area...")

    df = df.copy()

    # API may return coordinates as strings
    df[LATITUDE_COLUMN] = pd.to_numeric(
        df[LATITUDE_COLUMN],
        errors="coerce",
    )

    df[LONGITUDE_COLUMN] = pd.to_numeric(
        df[LONGITUDE_COLUMN],
        errors="coerce",
    )

    filtered = df[
        (df[LATITUDE_COLUMN] >= MIN_LAT)
        & (df[LATITUDE_COLUMN] <= MAX_LAT)
        & (df[LONGITUDE_COLUMN] >= MIN_LON)
        & (df[LONGITUDE_COLUMN] <= MAX_LON)
    ].copy()

    print(
        f"✅ Records inside MVP: {len(filtered)}"
    )

    stations = (
        filtered[STATION_COLUMN]
        .dropna()
        .unique()
    )

    print(
        f"📡 Stations found: {len(stations)}"
    )

    for station in stations:
        print(f"   → {station}")

    return filtered


def clean_data(df):
    print("\n🧹 Cleaning data...")

    df = df.copy()

    # Convert timestamp
    df[TIME_COLUMN] = pd.to_datetime(
        df[TIME_COLUMN],
        errors="coerce",
    )

    # Convert discharge to numeric
    df[DISCHARGE_COLUMN] = pd.to_numeric(
        df[DISCHARGE_COLUMN],
        errors="coerce",
    )

    # Remove invalid timestamps
    df = df.dropna(
        subset=[TIME_COLUMN]
    )

    # Remove invalid discharge
    df = df.dropna(
        subset=[DISCHARGE_COLUMN]
    )

    # Discharge cannot be negative
    df = df[
        df[DISCHARGE_COLUMN] >= 0
    ]

    # Sort chronologically
    df = df.sort_values(
        by=[
            STATION_COLUMN,
            TIME_COLUMN,
        ]
    )

    # Remove duplicate observations
    df = df.drop_duplicates(
        subset=[
            STATION_COLUMN,
            TIME_COLUMN,
        ]
    )

    print(
        f"✅ Clean records: {len(df)}"
    )

    return df


def calculate_features(df):
    print("\n📊 Calculating river features...")

    df = df.copy()

    # ---------------------------------------------------------
    # DISCHARGE CHANGE
    # ---------------------------------------------------------

    df["discharge_change_m3s"] = (
        df.groupby(STATION_COLUMN)[
            DISCHARGE_COLUMN
        ].diff()
    )

    # ---------------------------------------------------------
    # TIME DIFFERENCE
    # ---------------------------------------------------------

    df["time_difference_hours"] = (
        df.groupby(STATION_COLUMN)[
            TIME_COLUMN
        ]
        .diff()
        .dt.total_seconds()
        / 3600
    )

    # ---------------------------------------------------------
    # RATE OF DISCHARGE CHANGE
    # ---------------------------------------------------------

    df["discharge_rate_m3s_per_hour"] = (
        df["discharge_change_m3s"]
        / df["time_difference_hours"]
    )

    return df


def validate_data(df):
    print("\n🔍 Validating processed data...")

    print(
        f"Records          : {len(df)}"
    )

    print(
        f"Stations         : "
        f"{df[STATION_COLUMN].nunique()}"
    )

    print(
        f"Start time       : "
        f"{df[TIME_COLUMN].min()}"
    )

    print(
        f"End time         : "
        f"{df[TIME_COLUMN].max()}"
    )

    print(
        f"Minimum discharge: "
        f"{df[DISCHARGE_COLUMN].min()}"
    )

    print(
        f"Maximum discharge: "
        f"{df[DISCHARGE_COLUMN].max()}"
    )

    print("\nMissing values:")

    missing = df.isna().sum()

    missing = missing[
        missing > 0
    ]

    if len(missing) == 0:
        print("   None")
    else:
        print(missing)

    print("\n✅ Validation completed")


def save_data(df):
    print("\n💾 Saving processed data...")

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False,
    )

    print(
        f"✅ Saved processed data to:\n"
        f"{PROCESSED_DATA_PATH}"
    )


def process_dataframe(df):
    print("\n🌊 Processing river data...")

    df = filter_mvp_area(df)

    df = clean_data(df)

    df = calculate_features(df)

    validate_data(df)

    return df


def process():
    df = load_data()

    df = process_dataframe(df)

    save_data(df)

    return df