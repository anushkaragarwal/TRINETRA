"""
TRINETRA - Settlement Coordinate Builder
Member 2: Population / Relocation

Purpose
-------
Acquire geographic coordinates for the 101 settlements in
population_master.csv.

Source
------
OpenStreetMap Nominatim through geopy.

Important
---------
No coordinates are invented.

Every successful result stores:
- coordinate_source
- coordinate_confidence
- geocoding_query

Unmatched settlements remain NaN.
"""

from pathlib import Path
import time

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "population_master.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_locations.csv"
)


# ============================================================
# CONFIG
# ============================================================

COUNTRY = "India"
STATE = "Uttarakhand"
DISTRICT = "Chamoli"
SUBDISTRICT = "Joshimath"

REQUEST_DELAY = 1.1


# ============================================================
# GEOCODER
# ============================================================

geolocator = Nominatim(
    user_agent="trinetra-relocation-coordinate-builder"
)


# ============================================================
# HELPERS
# ============================================================

def clean_name(name):
    """
    Clean settlement names before geocoding.
    """

    if pd.isna(name):
        return ""

    name = str(name).strip()

    return name


def build_queries(settlement_name):
    """
    Generate progressively broader geocoding queries.

    More specific queries are attempted first.
    """

    name = clean_name(settlement_name)

    return [
        f"{name}, {SUBDISTRICT}, {DISTRICT}, {STATE}, {COUNTRY}",
        f"{name}, {DISTRICT}, {STATE}, {COUNTRY}",
        f"{name}, {STATE}, {COUNTRY}",
    ]


def geocode_settlement(settlement_name):
    """
    Try multiple queries.

    Returns:
        latitude
        longitude
        source
        confidence
        matched_address
        query
    """

    queries = build_queries(settlement_name)

    for query in queries:

        try:

            location = geolocator.geocode(
                query,
                exactly_one=True,
                addressdetails=True,
                timeout=10
            )

            time.sleep(REQUEST_DELAY)

            if location is not None:

                address = (
                    location.address
                    if location.address
                    else ""
                )

                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "coordinate_source": (
                        "OpenStreetMap Nominatim"
                    ),
                    "coordinate_confidence": "MEDIUM",
                    "matched_address": address,
                    "geocoding_query": query,
                }

        except (
            GeocoderTimedOut,
            GeocoderServiceError,
            Exception,
        ) as exc:

            print(
                f"Geocoding error for "
                f"'{settlement_name}': {exc}"
            )

            time.sleep(2)

    return {
        "latitude": None,
        "longitude": None,
        "coordinate_source": "MISSING",
        "coordinate_confidence": "MISSING",
        "matched_address": "",
        "geocoding_query": "",
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)
    print("TRINETRA - SETTLEMENT COORDINATE BUILDER")
    print("=" * 65)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"\nInput file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(
        f"\nLoaded settlements: {len(df)}"
    )

    # --------------------------------------------------------
    # Existing coordinates?
    # --------------------------------------------------------

    if (
        "latitude" in df.columns
        and "longitude" in df.columns
    ):

        existing = (
            df["latitude"].notna()
            & df["longitude"].notna()
        ).sum()

        print(
            f"Existing coordinates: "
            f"{existing}/{len(df)}"
        )

    # --------------------------------------------------------
    # Initialize columns
    # --------------------------------------------------------

    df["latitude"] = pd.NA
    df["longitude"] = pd.NA

    df["coordinate_source"] = "MISSING"
    df["coordinate_confidence"] = "MISSING"
    df["matched_address"] = ""
    df["geocoding_query"] = ""

    # --------------------------------------------------------
    # Geocode each settlement
    # --------------------------------------------------------

    for index, row in df.iterrows():

        settlement_name = clean_name(
            row.get("settlement_name", "")
        )

        print(
            f"\n[{index + 1}/{len(df)}] "
            f"{settlement_name}"
        )

        if not settlement_name:

            print("  SKIPPED: empty settlement name")
            continue

        result = geocode_settlement(
            settlement_name
        )

        df.at[index, "latitude"] = (
            result["latitude"]
        )

        df.at[index, "longitude"] = (
            result["longitude"]
        )

        df.at[index, "coordinate_source"] = (
            result["coordinate_source"]
        )

        df.at[index, "coordinate_confidence"] = (
            result["coordinate_confidence"]
        )

        df.at[index, "matched_address"] = (
            result["matched_address"]
        )

        df.at[index, "geocoding_query"] = (
            result["geocoding_query"]
        )

        if result["latitude"] is not None:

            print(
                f"  FOUND: "
                f"{result['latitude']}, "
                f"{result['longitude']}"
            )

            print(
                f"  MATCH: "
                f"{result['matched_address']}"
            )

        else:

            print("  NOT FOUND")

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    valid = (
        pd.to_numeric(
            df["latitude"],
            errors="coerce"
        ).notna()
        &
        pd.to_numeric(
            df["longitude"],
            errors="coerce"
        ).notna()
    )

    invalid = ~valid

    df.loc[
        invalid,
        [
            "latitude",
            "longitude"
        ]
    ] = pd.NA

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    found = valid.sum()
    missing = invalid.sum()

    print("\n" + "=" * 65)
    print("COORDINATE BUILD COMPLETE")
    print("=" * 65)

    print(
        f"\nTotal settlements : {len(df)}"
    )

    print(
        f"Coordinates found : {found}"
    )

    print(
        f"Coordinates missing: {missing}"
    )

    print(
        f"\nSaved to:\n{OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # Missing settlements
    # --------------------------------------------------------

    if missing > 0:

        print(
            "\n===== UNMATCHED SETTLEMENTS ====="
        )

        missing_df = df.loc[
            invalid,
            ["settlement_id", "settlement_name"]
        ]

        for _, row in missing_df.iterrows():

            print(
                f"- {row['settlement_name']}"
            )

    print(
        "\nNext step:"
    )

    print(
        "Verify geocoded locations before "
        "building exposure.py."
    )


if __name__ == "__main__":
    main()