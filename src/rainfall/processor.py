# TRINETRA - Rainfall Data Processor

import pandas as pd

from config import (
    RAINFALL_DISTRICT,

    STATE_COLUMN,
    DISTRICT_COLUMN,
    DATE_COLUMN,

    DAILY_ACTUAL_COLUMN,
    DAILY_NORMAL_COLUMN,
    DAILY_DEPARTURE_COLUMN,

    WEEKLY_ACTUAL_COLUMN,
    WEEKLY_NORMAL_COLUMN,
    WEEKLY_DEPARTURE_COLUMN,

    CUMULATIVE_ACTUAL_COLUMN,
    CUMULATIVE_NORMAL_COLUMN,
    CUMULATIVE_DEPARTURE_COLUMN,

    MONTHLY_ACTUAL_COLUMN,
    MONTHLY_NORMAL_COLUMN,
    MONTHLY_DEPARTURE_COLUMN,
)


def normalize_columns(df):

    print("\n🔧 Normalizing rainfall columns...")

    df = df.copy()

    # Remove newline/carriage-return characters
    # from API column names.

    renamed_columns = {}

    for column in df.columns:

        clean_name = (
            str(column)
            .replace("\n", " ")
            .replace("\r", "")
            .strip()
        )

        renamed_columns[column] = clean_name

    df = df.rename(
        columns=renamed_columns
    )

    # Fix source spelling inconsistencies
    # confirmed from the NWDP API response.

    df = df.rename(
        columns={
            "Cumulative Departue Per":
                "Cumulative Departure Per",

            "Monthly Acutual":
                "Monthly Actual",
        }
    )

    return df


def filter_district(df):

    print("\n📍 Filtering Chamoli district...")

    df = df.copy()

    df[DISTRICT_COLUMN] = (
        df[DISTRICT_COLUMN]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    filtered = df[
        df[DISTRICT_COLUMN]
        == RAINFALL_DISTRICT
    ].copy()

    print(
        f"✅ Chamoli records: "
        f"{len(filtered)}"
    )

    return filtered


def clean_dates(df):

    df = df.copy()

    df[DATE_COLUMN] = pd.to_datetime(
        df[DATE_COLUMN],
        errors="coerce",
    )

    df = df.dropna(
        subset=[DATE_COLUMN]
    )

    return df


def clean_rainfall_values(df):

    print(
        "\n🧹 Cleaning rainfall values..."
    )

    df = df.copy()

    # --------------------------------------------------------
    # Numeric rainfall fields
    # --------------------------------------------------------

    numeric_columns = [
        DAILY_ACTUAL_COLUMN,
        DAILY_NORMAL_COLUMN,

        WEEKLY_ACTUAL_COLUMN,
        WEEKLY_NORMAL_COLUMN,

        CUMULATIVE_ACTUAL_COLUMN,
        CUMULATIVE_NORMAL_COLUMN,

        MONTHLY_ACTUAL_COLUMN,
        MONTHLY_NORMAL_COLUMN,
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Departure percentage fields
    # --------------------------------------------------------

    departure_columns = [
        DAILY_DEPARTURE_COLUMN,
        WEEKLY_DEPARTURE_COLUMN,
        CUMULATIVE_DEPARTURE_COLUMN,
        MONTHLY_DEPARTURE_COLUMN,
    ]

    for column in departure_columns:

        if column not in df.columns:
            continue

        df[column] = (
            df[column]
            .astype(str)
            .str.replace(
                "%",
                "",
                regex=False,
            )
            .str.strip()
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    print("✅ Rainfall values cleaned.")

    return df


def remove_invalid_values(df):

    df = df.copy()

    rainfall_columns = [
        DAILY_ACTUAL_COLUMN,
        WEEKLY_ACTUAL_COLUMN,
        CUMULATIVE_ACTUAL_COLUMN,
        MONTHLY_ACTUAL_COLUMN,
    ]

    for column in rainfall_columns:

        if column not in df.columns:
            continue

        df = df[
            df[column].isna()
            | (df[column] >= 0)
        ]

    return df


def remove_duplicates(df):

    df = df.copy()

    df = df.drop_duplicates(
        subset=[
            DISTRICT_COLUMN,
            DATE_COLUMN,
        ],
        keep="last",
    )

    return df


def sort_data(df):

    return (
        df
        .sort_values(
            by=[
                DISTRICT_COLUMN,
                DATE_COLUMN,
            ]
        )
        .reset_index(drop=True)
    )


def validate_data(df):

    print(
        "\n🔍 Validating rainfall data..."
    )

    print(
        f"District      : "
        f"{df[DISTRICT_COLUMN].unique()}"
    )

    print(
        f"Records       : "
        f"{len(df)}"
    )

    print(
        f"Start date    : "
        f"{df[DATE_COLUMN].min()}"
    )

    print(
        f"End date      : "
        f"{df[DATE_COLUMN].max()}"
    )

    print(
        f"Maximum daily : "
        f"{df[DAILY_ACTUAL_COLUMN].max()} mm"
    )

    print("\nMissing values:")

    missing = df.isna().sum()

    missing = missing[
        missing > 0
    ]

    if missing.empty:
        print("   None")
    else:
        print(missing)

    print(
        "\n✅ Rainfall validation completed."
    )


def process_dataframe(df):

    print(
        "\n🌧️ Processing IMD rainfall data..."
    )

    # 1. Normalize API field names
    df = normalize_columns(df)

    # 2. Keep target district
    df = filter_district(df)

    # 3. Clean date
    df = clean_dates(df)

    # 4. Convert rainfall values
    df = clean_rainfall_values(df)

    # 5. Remove impossible rainfall values
    df = remove_invalid_values(df)

    # 6. Remove duplicate daily observations
    df = remove_duplicates(df)

    # 7. Sort chronologically
    df = sort_data(df)

    # 8. Validate
    validate_data(df)

    return df