"""
TRINETRA - Coordinate Verification
Member 2: Population / Relocation

Purpose
-------
Validate coordinates produced by coordinate_builder.py.

This script DOES NOT modify coordinates.

It identifies:
    ACCEPT  -> likely valid Joshimath-area match
    REVIEW  -> suspicious / needs manual verification
    REJECT  -> clearly wrong geographic match
    MISSING -> no coordinate available

Outputs:
    data/features/coordinate_review_required.csv
    data/features/settlement_coordinates_verified.csv
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
    / "settlement_locations.csv"
)

REVIEW_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "coordinate_review_required.csv"
)

VERIFIED_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_verified.csv"
)


# ============================================================
# EXPECTED GEOGRAPHIC AREA
# ============================================================

EXPECTED_TERMS = [
    "joshimath",
    "chamoli",
    "uttarakhand",
    "badrinath",
    "tapoban",
    "tapovan",
    "suraithota",
    "garurganga",
    "kimana",
    "subhain",
]


# Places that are obviously outside our intended area.
# These are based on the returned geocoding address,
# NOT on manually changing coordinates.

KNOWN_WRONG_TERMS = [
    "champawat",
    "pauri",
    "pauri garhwal",
    "kotdwara",
    "nainital",
    "lalkuan",
    "pokhari",
]


# ============================================================
# HELPERS
# ============================================================

def normalize_text(value):
    """
    Normalize text for comparison.
    """

    if pd.isna(value):
        return ""

    return (
        str(value)
        .lower()
        .strip()
    )


def classify_match(row):
    """
    Classify one geocoded settlement.

    Returns:
        status
        reason
    """

    latitude = pd.to_numeric(
        row.get("latitude"),
        errors="coerce"
    )

    longitude = pd.to_numeric(
        row.get("longitude"),
        errors="coerce"
    )

    settlement_name = normalize_text(
        row.get("settlement_name")
    )

    address = normalize_text(
        row.get("matched_address")
    )

    # --------------------------------------------------------
    # Missing coordinates
    # --------------------------------------------------------

    if pd.isna(latitude) or pd.isna(longitude):

        return (
            "MISSING",
            "No coordinates available"
        )

    # --------------------------------------------------------
    # Geographic bounds
    #
    # Broad Joshimath/Chamoli bounds.
    # These are deliberately generous.
    # --------------------------------------------------------

    if not (
        30.0 <= latitude <= 31.2
        and
        79.0 <= longitude <= 80.2
    ):

        return (
            "REJECT",
            "Coordinates fall outside the expected "
            "Joshimath/Chamoli region"
        )

    # --------------------------------------------------------
    # Known wrong locations
    # --------------------------------------------------------

    wrong_matches = [
        term
        for term in KNOWN_WRONG_TERMS
        if term in address
    ]

    if wrong_matches:

        return (
            "REJECT",
            "Returned address contains outside-area "
            "location: "
            + ", ".join(wrong_matches)
        )

    # --------------------------------------------------------
    # Expected geographic terms
    # --------------------------------------------------------

    matched_terms = [
        term
        for term in EXPECTED_TERMS
        if term in address
    ]

    # --------------------------------------------------------
    # Strong match
    # --------------------------------------------------------

    if (
        "joshimath" in address
        and
        "chamoli" in address
    ):

        return (
            "ACCEPT",
            "Address explicitly identifies Joshimath "
            "and Chamoli"
        )

    # --------------------------------------------------------
    # Good regional match
    # --------------------------------------------------------

    if (
        "chamoli" in address
        and
        "uttarakhand" in address
    ):

        return (
            "REVIEW",
            "Chamoli/Uttarakhand match, but "
            "Joshimath not explicitly confirmed"
        )

    # --------------------------------------------------------
    # Nearby geographic feature / locality
    # --------------------------------------------------------

    if matched_terms:

        return (
            "REVIEW",
            "Potential Joshimath-area match based on "
            "returned locality"
        )

    # --------------------------------------------------------
    # No useful geographic evidence
    # --------------------------------------------------------

    return (
        "REVIEW",
        "Coordinate exists but returned address "
        "does not clearly identify the target area"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("TRINETRA - COORDINATE VERIFICATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"\nInput file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(
        f"\nLoaded settlements: {len(df)}"
    )

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    results = []

    for _, row in df.iterrows():

        status, reason = classify_match(row)

        results.append({
            "settlement_id": row.get(
                "settlement_id"
            ),

            "settlement_name": row.get(
                "settlement_name"
            ),

            "latitude": row.get(
                "latitude"
            ),

            "longitude": row.get(
                "longitude"
            ),

            "coordinate_source": row.get(
                "coordinate_source"
            ),

            "coordinate_confidence": row.get(
                "coordinate_confidence"
            ),

            "matched_address": row.get(
                "matched_address"
            ),

            "geocoding_query": row.get(
                "geocoding_query"
            ),

            "verification_status": status,

            "verification_reason": reason,
        })

    verified = pd.DataFrame(results)

    # --------------------------------------------------------
    # Save complete verification dataset
    # --------------------------------------------------------

    VERIFIED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    verified.to_csv(
        VERIFIED_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Save review/rejection/missing records
    # --------------------------------------------------------

    review = verified[
        verified["verification_status"] != "ACCEPT"
    ].copy()

    review.to_csv(
        REVIEW_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    counts = (
        verified["verification_status"]
        .value_counts()
    )

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for status in [
        "ACCEPT",
        "REVIEW",
        "REJECT",
        "MISSING",
    ]:

        print(
            f"{status:<10}: "
            f"{counts.get(status, 0)}"
        )

    # --------------------------------------------------------
    # Detailed suspicious matches
    # --------------------------------------------------------

    print(
        "\n===== MATCHES REQUIRING ATTENTION ====="
    )

    attention = verified[
        verified["verification_status"].isin(
            ["REVIEW", "REJECT"]
        )
    ]

    if len(attention) == 0:

        print("None")

    else:

        for _, row in attention.iterrows():

            print(
                f"\n{row['settlement_name']}"
            )

            print(
                f"  Status : "
                f"{row['verification_status']}"
            )

            print(
                f"  Reason : "
                f"{row['verification_reason']}"
            )

            print(
                f"  Coordinates: "
                f"{row['latitude']}, "
                f"{row['longitude']}"
            )

            print(
                f"  Address: "
                f"{row['matched_address']}"
            )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FILES CREATED")
    print("=" * 70)

    print(
        f"\nVerified dataset:\n{VERIFIED_FILE}"
    )

    print(
        f"\nReview dataset:\n{REVIEW_FILE}"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "REVIEW and REJECT coordinates must not be used "
        "for exposure calculations until verified."
    )


if __name__ == "__main__":
    main()