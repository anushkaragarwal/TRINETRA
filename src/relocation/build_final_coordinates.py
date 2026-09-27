from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_verified.csv"
)

OVERRIDE_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinate_overrides.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_final.csv"
)


def main():

    print("=" * 65)
    print("TRINETRA - FINAL SETTLEMENT COORDINATES")
    print("=" * 65)

    source = pd.read_csv(SOURCE_FILE)

    if OVERRIDE_FILE.exists():
        overrides = pd.read_csv(OVERRIDE_FILE)
    else:
        overrides = pd.DataFrame(
            columns=[
                "settlement_name",
                "latitude",
                "longitude",
                "coordinate_source",
                "coordinate_confidence",
                "verification_note",
            ]
        )

    # --------------------------------------------------------
    # Normalize names
    # --------------------------------------------------------

    source["name_key"] = (
        source["settlement_name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    overrides["name_key"] = (
        overrides["settlement_name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Remove rejected coordinates
    # --------------------------------------------------------

    rejected = (
        source["verification_status"] == "REJECT"
    )

    source.loc[
        rejected,
        [
            "latitude",
            "longitude",
            "coordinate_source",
            "coordinate_confidence",
            "matched_address",
        ]
    ] = pd.NA

    source.loc[
        rejected,
        "verification_status"
    ] = "MISSING"

    # --------------------------------------------------------
    # Apply overrides
    # --------------------------------------------------------

    override_columns = [
        "latitude",
        "longitude",
        "coordinate_source",
        "coordinate_confidence",
        "verification_note",
    ]

    merged = source.copy()

    override_map = overrides.set_index(
        "name_key"
    )

    for index, row in merged.iterrows():

        key = row["name_key"]

        if key not in override_map.index:
            continue

        override = override_map.loc[key]

        if pd.notna(override["latitude"]) and pd.notna(
            override["longitude"]
        ):

            merged.at[
                index, "latitude"
            ] = override["latitude"]

            merged.at[
                index, "longitude"
            ] = override["longitude"]

            merged.at[
                index, "coordinate_source"
            ] = override["coordinate_source"]

            merged.at[
                index, "coordinate_confidence"
            ] = override["coordinate_confidence"]

            merged.at[
                index, "verification_status"
            ] = "ACCEPT"

            merged.at[
                index, "verification_reason"
            ] = override["verification_note"]

    # --------------------------------------------------------
    # Remove helper
    # --------------------------------------------------------

    merged.drop(
        columns=["name_key"],
        inplace=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    merged.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    valid = (
        merged["latitude"].notna()
        &
        merged["longitude"].notna()
    )

    print(
        f"\nTotal settlements : {len(merged)}"
    )

    print(
        f"Usable coordinates: {valid.sum()}"
    )

    print(
        f"Still missing     : {(~valid).sum()}"
    )

    print(
        f"\nSaved:\n{OUTPUT_FILE}"
    )

    print(
        "\nRemaining settlements:"
    )

    print(
        merged.loc[
            ~valid,
            "settlement_name"
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()