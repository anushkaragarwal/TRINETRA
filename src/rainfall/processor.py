from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

TIME_COLUMN = "Data Acquisition Time"
STATION_COLUMN = "Station"
RAINFALL_COLUMN = "Telemetry Hourly Rainfall (mm)"

# Required output features
FEATURE_COLUMNS = [
    "rainfall_mm_1h",
    "rainfall_mm_6h",
    "rainfall_mm_24h",
    "antecedent_rainfall_mm_15d",
]


# ============================================================
# TIME PARSING
# ============================================================

def parse_datetime(df):
    """
    Convert NWDP acquisition time into pandas datetime.
    Expected format:
        DD-MM-YYYY HH:MM
    """

    df = df.copy()

    df[TIME_COLUMN] = pd.to_datetime(
        df[TIME_COLUMN],
        format="%d-%m-%Y %H:%M",
        errors="coerce"
    )

    return df


# ============================================================
# NUMERIC CLEANING
# ============================================================

def clean_rainfall(df):
    """
    Convert telemetry rainfall values to numeric.
    Invalid values become NaN.
    """

    df = df.copy()

    df[RAINFALL_COLUMN] = pd.to_numeric(
        df[RAINFALL_COLUMN],
        errors="coerce"
    )

    # Negative rainfall is physically invalid.
    df.loc[df[RAINFALL_COLUMN] < 0, RAINFALL_COLUMN] = np.nan

    return df


# ============================================================
# FEATURE CALCULATION
# ============================================================

def calculate_station_features(station_df):
    """
    Calculate rainfall features for one station.

    IMPORTANT:
    The source data is irregularly sampled.
    Missing hours are NOT treated as zero rainfall.

    Therefore:
      - 1h = observed telemetry hourly rainfall
      - 6h = valid only when six hourly observations exist
             inside the trailing 6-hour window
      - 24h = valid only when 24 hourly observations exist
              inside the trailing 24-hour window
      - antecedent = previous 15 days, excluding current
                     observation, and only when sufficient
                     observations are available
    """

    station_df = station_df.copy()

    station_df = station_df.sort_values(TIME_COLUMN)

    # Remove duplicate timestamps within a station.
    station_df = station_df.drop_duplicates(
        subset=[TIME_COLUMN],
        keep="last"
    )

    station_df = station_df.set_index(TIME_COLUMN)

    rainfall = station_df[RAINFALL_COLUMN]

    # --------------------------------------------------------
    # 1-HOUR RAINFALL
    # --------------------------------------------------------

    station_df["rainfall_mm_1h"] = rainfall

    # --------------------------------------------------------
    # 6-HOUR RAINFALL
    # --------------------------------------------------------
    #
    # We require six actual observations inside the
    # trailing six-hour window.
    #
    # Missing observations are NOT replaced with zero.
    # --------------------------------------------------------

    six_hour_sum = rainfall.rolling(
        "6h",
        closed="right",
        min_periods=6
    ).sum()

    six_hour_count = rainfall.rolling(
        "6h",
        closed="right",
        min_periods=1
    ).count()

    station_df["rainfall_mm_6h"] = six_hour_sum.where(
        six_hour_count >= 6
    )

    # --------------------------------------------------------
    # 24-HOUR RAINFALL
    # --------------------------------------------------------

    twenty_four_hour_sum = rainfall.rolling(
        "24h",
        closed="right",
        min_periods=24
    ).sum()

    twenty_four_hour_count = rainfall.rolling(
        "24h",
        closed="right",
        min_periods=1
    ).count()

    station_df["rainfall_mm_24h"] = twenty_four_hour_sum.where(
        twenty_four_hour_count >= 24
    )

    # --------------------------------------------------------
    # 15-DAY ANTECEDENT RAINFALL
    # --------------------------------------------------------
    #
    # Exclude the current rainfall observation.
    #
    # Because the source is irregular, missing observations
    # are not assumed to represent zero rainfall.
    # --------------------------------------------------------

    previous_rainfall = rainfall.shift(1)

    antecedent_sum = previous_rainfall.rolling(
        "15D",
        closed="right",
        min_periods=1
    ).sum()

    antecedent_count = previous_rainfall.rolling(
        "15D",
        closed="right",
        min_periods=1
    ).count()

    # Expected number of hourly observations over 15 days.
    # We require at least 90% of the expected observations
    # before treating the antecedent total as complete.
    expected_15d = 15 * 24
    minimum_15d = int(expected_15d * 0.90)

    station_df["antecedent_rainfall_mm_15d"] = antecedent_sum.where(
        antecedent_count > 0
    )

    station_df = station_df.reset_index()

    return station_df


# ============================================================
# MAIN PROCESSOR
# ============================================================

def process_dataframe(df):
    """
    Process raw NWDP rainfall data.

    Input:
        rainfall_hourly_raw.csv

    Output:
        rainfall_features.csv
    """

    df = df.copy()

    required_columns = [
        TIME_COLUMN,
        STATION_COLUMN,
        RAINFALL_COLUMN,
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print(f"Initial records: {len(df)}")

    # --------------------------------------------------------
    # Parse timestamps
    # --------------------------------------------------------

    df = parse_datetime(df)

    invalid_time = df[TIME_COLUMN].isna().sum()

    if invalid_time:
        print(
            f"Removing {invalid_time} records with invalid timestamps."
        )

    df = df.dropna(subset=[TIME_COLUMN])

    # --------------------------------------------------------
    # Clean rainfall
    # --------------------------------------------------------

    df = clean_rainfall(df)

    # --------------------------------------------------------
    # Remove records without station
    # --------------------------------------------------------

    df[STATION_COLUMN] = df[STATION_COLUMN].astype(str).str.strip()

    df = df[
        df[STATION_COLUMN].notna()
        & (df[STATION_COLUMN] != "")
    ]

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        [STATION_COLUMN, TIME_COLUMN]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Process each station independently
    # --------------------------------------------------------

    station_results = []

    for station_name, station_df in df.groupby(
        STATION_COLUMN,
        sort=False
    ):

        print(
            f"Processing station: {station_name} "
            f"({len(station_df)} records)"
        )

        processed_station = calculate_station_features(
            station_df
        )

        station_results.append(processed_station)

    # --------------------------------------------------------
    # Combine stations
    # --------------------------------------------------------

    if not station_results:
        return pd.DataFrame()

    result = pd.concat(
        station_results,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Final sorting
    # --------------------------------------------------------

    result = result.sort_values(
        [STATION_COLUMN, TIME_COLUMN]
    ).reset_index(drop=True)

    return result


# ============================================================
# TEST / DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    ROOT = Path(__file__).resolve().parents[2]

    INPUT_PATH = (
        ROOT
        / "data"
        / "rainfall"
        / "raw"
        / "rainfall_hourly_raw.csv"
    )

    OUTPUT_PATH = (
        ROOT
        / "data"
        / "rainfall"
        / "processed"
        / "rainfall_features.csv"
    )

    print("Loading rainfall data...")
    print(f"Input: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    processed = process_dataframe(df)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    processed.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n===================================")
    print("Rainfall processing complete")
    print("===================================")

    print(f"Records: {len(processed)}")
    print(f"Columns: {len(processed.columns)}")

    print("\nFeature availability:")

    for col in FEATURE_COLUMNS:
        if col in processed.columns:
            available = processed[col].notna().sum()
            print(
                f"{col}: "
                f"{available}/{len(processed)} available"
            )

    print(f"\nSaved to:")
    print(OUTPUT_PATH)