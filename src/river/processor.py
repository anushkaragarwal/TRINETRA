import pandas as pd

from .config import (
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


def filter_mvp_area(df):
    """
    Keep only river observations inside the
    TRINETRA MVP geographic region.
    """

    print("\n📍 Filtering MVP area...")

    df = df.copy()

    # Convert coordinates to numeric
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
    """
    Clean and normalize CWC river observations.
    """

    print("\n🧹 Cleaning river data...")

    df = df.copy()

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    df[TIME_COLUMN] = pd.to_datetime(
    df[TIME_COLUMN],
    format="%d-%m-%Y %H:%M",
    errors="coerce",
    )

    # ---------------------------------------------------------
    # Discharge
    # ---------------------------------------------------------

    df[DISCHARGE_COLUMN] = pd.to_numeric(
        df[DISCHARGE_COLUMN],
        errors="coerce",
    )

    # ---------------------------------------------------------
    # Remove invalid timestamps
    # ---------------------------------------------------------

    df = df.dropna(
        subset=[TIME_COLUMN]
    )

    # ---------------------------------------------------------
    # Remove missing discharge
    # ---------------------------------------------------------

    df = df.dropna(
        subset=[DISCHARGE_COLUMN]
    )

    # ---------------------------------------------------------
    # Remove physically invalid negative discharge
    # ---------------------------------------------------------

    df = df[
        df[DISCHARGE_COLUMN] >= 0
    ]

    # ---------------------------------------------------------
    # Sort by station and time
    # ---------------------------------------------------------

    df = df.sort_values(
        by=[
            STATION_COLUMN,
            TIME_COLUMN,
        ]
    )

    # ---------------------------------------------------------
    # Remove duplicate observations
    # ---------------------------------------------------------

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
    """
    Calculate basic hydrological features.

    These are data/feature-engineering outputs,
    not AI predictions.
    """

    print("\n📊 Calculating hydrological features...")

    df = df.copy()

    # ---------------------------------------------------------
    # Change in discharge
    # ---------------------------------------------------------

    df["discharge_change_m3s"] = (
        df.groupby(STATION_COLUMN)[
            DISCHARGE_COLUMN
        ].diff()
    )

    # ---------------------------------------------------------
    # Time difference
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
    # Rate of discharge change
    # ---------------------------------------------------------

    df["discharge_rate_m3s_per_hour"] = (
        df["discharge_change_m3s"]
        / df["time_difference_hours"]
    )

    return df


def validate_data(df):
    """
    Basic validation of the processed river data.
    """

    print("\n🔍 Validating river data...")

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


def process_dataframe(df):
    """
    Complete River data-processing pipeline.

    Input:
        Raw CWC API DataFrame

    Output:
        Clean, spatially filtered,
        feature-enriched DataFrame
    """

    print("\n🌊 Processing CWC river data...")

    df = filter_mvp_area(df)

    df = clean_data(df)

    df = calculate_features(df)

    validate_data(df)

    return df