"""
TRINETRA - Finalize Settlement Coordinates

Member 2: Population / Relocation

Purpose
-------
Finalize the settlement coordinate dataset after web-based resolution.

Rules
-----
1. Preserve all already-resolved coordinates.
2. Add only coordinates with a defensible source.
3. Do NOT invent coordinates.
4. Explicitly keep unresolved settlements as unresolved.
5. Joshimath (NPP) is assigned its published geographic coordinate.
6. Produce a clean master coordinate file for the next pipeline stage.

Input
-----
data/features/settlement_coordinates_web_verified.csv

Output
------
data/features/settlement_coordinates_final_master.csv
data/features/settlement_coordinate_final_review.csv
"""

from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_web_verified.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_final_master.csv"
)

REVIEW_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinate_final_review.csv"
)


# ============================================================
# VERIFIED MANUAL COORDINATES
# ============================================================

VERIFIED_COORDINATES = {

    # --------------------------------------------------------
    # Joshimath town
    # --------------------------------------------------------
    "SETTLEMENT_800291": {
        "latitude": 30.555000,
        "longitude": 79.565000,
        "source": (
            "Published geographic coordinate for Joshimath; "
            "cross-checked with geographic literature"
        ),
        "confidence": "HIGH",
    },

}


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("TRINETRA - FINALIZE SETTLEMENT COORDINATES")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(
        f"\nLoaded settlements: {len(df)}"
    )

    required_columns = {
        "settlement_id",
        "settlement_name",
        "latitude",
        "longitude",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Input file is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # Normalize coordinate columns
    # --------------------------------------------------------

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Make sure metadata columns exist
    # --------------------------------------------------------

    if "coordinate_source" not in df.columns:

        df["coordinate_source"] = ""

    if "coordinate_confidence" not in df.columns:

        df["coordinate_confidence"] = ""

    # --------------------------------------------------------
    # Apply only explicitly verified overrides
    # --------------------------------------------------------

    applied = []

    for settlement_id, info in VERIFIED_COORDINATES.items():

        mask = (
            df["settlement_id"].astype(str)
            == settlement_id
        )

        if not mask.any():

            print(
                f"\nWARNING: settlement not found: "
                f"{settlement_id}"
            )

            continue

        df.loc[mask, "latitude"] = info["latitude"]
        df.loc[mask, "longitude"] = info["longitude"]

        df.loc[
            mask,
            "coordinate_source"
        ] = info["source"]

        df.loc[
            mask,
            "coordinate_confidence"
        ] = info["confidence"]

        applied.append(
            settlement_id
        )

        name = (
            df.loc[
                mask,
                "settlement_name"
            ]
            .iloc[0]
        )

        print(
            f"\nVERIFIED: {name}"
        )

        print(
            f"  Latitude : {info['latitude']}"
        )

        print(
            f"  Longitude: {info['longitude']}"
        )

        print(
            f"  Confidence: {info['confidence']}"
        )

    # --------------------------------------------------------
    # Mark remaining missing coordinates explicitly
    # --------------------------------------------------------

    missing_mask = (
        df["latitude"].isna()
        |
        df["longitude"].isna()
    )

    df.loc[
        missing_mask,
        "coordinate_confidence"
    ] = "UNRESOLVED"

    df.loc[
        missing_mask,
        "coordinate_source"
    ] = "NO_VERIFIED_COORDINATE"

    # --------------------------------------------------------
    # Coordinate status
    # --------------------------------------------------------

    df["coordinate_status"] = "RESOLVED"

    df.loc[
        missing_mask,
        "coordinate_status"
    ] = "UNRESOLVED"

    # --------------------------------------------------------
    # Review table
    # --------------------------------------------------------

    review = df[
        [
            "settlement_id",
            "settlement_name",
            "latitude",
            "longitude",
            "coordinate_source",
            "coordinate_confidence",
            "coordinate_status",
        ]
    ].copy()

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    review.to_csv(
        REVIEW_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    resolved_mask = (
        df["latitude"].notna()
        &
        df["longitude"].notna()
    )

    unresolved_mask = ~resolved_mask

    print("\n" + "=" * 70)
    print("FINAL COORDINATE DATASET")
    print("=" * 70)

    print(
        f"\nTotal settlements    : {len(df)}"
    )

    print(
        f"Resolved coordinates : "
        f"{resolved_mask.sum()}"
    )

    print(
        f"Unresolved coordinates: "
        f"{unresolved_mask.sum()}"
    )

    if unresolved_mask.any():

        print(
            "\nRemaining unresolved settlements:"
        )

        print(
            df.loc[
                unresolved_mask,
                [
                    "settlement_id",
                    "settlement_name"
                ]
            ].to_string(
                index=False
            )
        )

    print(
        f"\nFinal dataset:\n{OUTPUT_FILE}"
    )

    print(
        f"\nReview file:\n{REVIEW_FILE}"
    )

    print(
        "\nThese unresolved settlements will NOT "
        "receive invented coordinates."
    )


if __name__ == "__main__":
    main()