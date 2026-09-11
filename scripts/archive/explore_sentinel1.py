from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

PATH = (
    ROOT
    / "data"
    / "satellite"
    / "sentinel1_metadata.csv"
)


def main():
    df = pd.read_csv(
        PATH,
        parse_dates=[
            "acquisition_time_utc",
            "completion_time_utc",
        ],
    )

    print("Shape:", df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nAcquisition-time range:")
    print(
        df["acquisition_time_utc"].min(),
        "→",
        df["acquisition_time_utc"].max(),
    )

    print("\nScenes by acquisition date:")
    print(
        df.groupby("acquisition_date")
        .size()
        .to_string()
    )

    print("\nLatest 10 clean scenes:")
    print(
        df[
            [
                "product_name",
                "acquisition_time_utc",
                "product_type",
                "s3_path",
            ]
        ]
        .tail(10)
        .to_string(index=False)
    )

    print("\nMissing values:")
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("None")
    else:
        print(missing.to_string())


if __name__ == "__main__":
    main()