"""
TRINETRA - Resolve Missing Settlement Coordinates

Member 2: Population / Relocation

Strategy
--------
1. Read the 101 Census settlements.
2. Preserve existing accepted coordinates.
3. Remove rejected coordinates.
4. Use Census village code as the stable settlement identity.
5. Query Nominatim using:
       village name + Census code + Joshimath + Chamoli
6. Reject results outside the Joshimath/Chamoli area.
7. Never invent coordinates.
8. Produce a review file for ambiguous matches.

This is a coordinate acquisition stage only.
No hazard calculations are performed here.
"""

from pathlib import Path
import time

import pandas as pd

from geopy.geocoders import Nominatim
from geopy.exc import (
    GeocoderTimedOut,
    GeocoderServiceError,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_final.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "settlement_coordinates_resolved.csv"
)

REVIEW_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "coordinate_resolution_review.csv"
)


# ============================================================
# CONFIG
# ============================================================

REQUEST_DELAY = 1.2

geolocator = Nominatim(
    user_agent="trinetra-settlement-coordinate-resolver"
)


# ============================================================
# EXPECTED AREA
# ============================================================

def valid_region(lat, lon):
    """
    Broad geographic bounds around Joshimath/Chamoli.
    """

    if pd.isna(lat) or pd.isna(lon):
        return False

    return (
        30.0 <= float(lat) <= 31.2
        and
        79.0 <= float(lon) <= 80.2
    )


def address_is_relevant(address):
    """
    Check whether the returned address belongs to the
    intended Joshimath/Chamoli region.
    """

    if not address:
        return False

    address = address.lower()

    bad_terms = [
        "champawat",
        "pauri garhwal",
        "kotdwara",
        "nainital",
        "lalkuan",
        "pokhari",
    ]

    for term in bad_terms:
        if term in address:
            return False

    good_terms = [
        "joshimath",
        "chamoli",
        "badrinath",
        "tapovan",
        "tapoban",
        "niti",
        "suraithota",
    ]

    return any(
        term in address
        for term in good_terms
    )


# ============================================================
# QUERY BUILDER
# ============================================================

def build_queries(name, code):
    """
    Generate increasingly broad queries.

    Census code is included where useful but is not assumed
    to be understood by the geocoder.
    """

    return [
        f"{name}, {code}, Joshimath, Chamoli, Uttarakhand, India",
        f"{name}, Joshimath, Chamoli, Uttarakhand, India",
        f"{name}, Chamoli, Uttarakhand, India",
    ]


# ============================================================
# RESOLVE ONE SETTLEMENT
# ============================================================

def resolve(name, code):

    queries = build_queries(
        name,
        code
    )

    for query in queries:

        try:

            location = geolocator.geocode(
                query,
                exactly_one=True,
                addressdetails=True,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if location is None:
                continue

            lat = location.latitude
            lon = location.longitude
            address = location.address or ""

            # Geographic validation
            if not valid_region(lat, lon):
                continue

            # Address validation
            if not address_is_relevant(address):
                continue

            return {
                "latitude": lat,
                "longitude": lon,
                "coordinate_source":
                    "OpenStreetMap Nominatim - Census-aware query",
                "coordinate_confidence": "MEDIUM",
                "matched_address": address,
                "resolution_query": query,
                "resolution_status": "RESOLVED",
            }

        except (
            GeocoderTimedOut,
            GeocoderServiceError,
        ):

            time.sleep(2)

        except Exception as exc:

            print(
                f"    Geocoder error: {exc}"
            )

            time.sleep(2)

    return {
        "latitude": None,
        "longitude": None,
        "coordinate_source": "MISSING",
        "coordinate_confidence": "MISSING",
        "matched_address": "",
        "resolution_query": "",
        "resolution_status": "UNRESOLVED",
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("TRINETRA - CENSUS-AWARE COORDINATE RESOLVER")
    print("=" * 70)

    df = pd.read_csv(INPUT_FILE)

    print(
        f"\nLoaded settlements: {len(df)}"
    )

    # --------------------------------------------------------
    # Ensure Census village code exists
    # --------------------------------------------------------

    # ------------------------------------------------------------
    # Resolve the Census village/town code
    # ------------------------------------------------------------

    # settlement_coordinates_final.csv is already a normalized
    # dataset, so the original TOWN/VILLAGE column may not exist.
    # Recover the Census code from population_master.csv.

    population_master_path = DATA_DIR / "features" / "population_master.csv"

    if "census_code" in df.columns:
        df["census_code"] = (
            df["census_code"]
            .astype("string")
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )
    elif "TOWN/VILLAGE" in df.columns:
        df["census_code"] = (
            df["TOWN/VILLAGE"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
        )
    else:
        if not population_master_path.exists():
            raise FileNotFoundError(
                f"Cannot find population master file: {population_master_path}"
            )

        pop = pd.read_csv(population_master_path, dtype=str)

        required_pop_cols = {"settlement_name", "TOWN/VILLAGE"}

        missing_pop_cols = required_pop_cols - set(pop.columns)

        if missing_pop_cols:
            raise ValueError(
                f"population_master.csv is missing columns: "
                f"{sorted(missing_pop_cols)}"
            )

        pop["settlement_name_key"] = (
            pop["settlement_name"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df["settlement_name_key"] = (
            df["settlement_name"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        code_map = (
            pop[["settlement_name_key", "TOWN/VILLAGE"]]
            .drop_duplicates("settlement_name_key")
            .set_index("settlement_name_key")["TOWN/VILLAGE"]
            .to_dict()
        )

        df["census_code"] = df["settlement_name_key"].map(code_map)

        df["census_code"] = (
            df["census_code"]
            .astype("string")
            .str.replace(".0", "", regex=False)
            .str.strip()
        )

        df.drop(columns=["settlement_name_key"], inplace=True, errors="ignore")

    print(
        "Settlements with Census codes:",
        df["census_code"].notna().sum()
    )
    print(
        "Settlements without Census codes:",
        df["census_code"].isna().sum()
    )

    # --------------------------------------------------------
    # Start from existing final dataset
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
    # Resolve only missing coordinates
    # --------------------------------------------------------

    missing_mask = (
        df["latitude"].isna()
        |
        df["longitude"].isna()
    )

    missing_rows = df[missing_mask].copy()

    print(
        f"Already usable: "
        f"{len(df) - len(missing_rows)}"
    )

    print(
        f"Need resolution: "
        f"{len(missing_rows)}"
    )

    results = []

    for position, (index, row) in enumerate(
        missing_rows.iterrows(),
        start=1
    ):

        name = str(
            row["settlement_name"]
        ).strip()

        census_code = str(
            row["census_code"]
        ).strip()

        print(
            f"\n[{position}/{len(missing_rows)}] "
            f"{name} "
            f"(Census code: {census_code})"
        )

        result = resolve(
            name,
            census_code
        )

        for key, value in result.items():

            df.at[index, key] = value

        if result["resolution_status"] == "RESOLVED":

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

            print(
                "  NOT RESOLVED"
            )

        results.append({
            "settlement_id":
                row["settlement_id"],

            "settlement_name":
                name,

            "census_code":
                census_code,

            "latitude":
                result["latitude"],

            "longitude":
                result["longitude"],

            "coordinate_source":
                result["coordinate_source"],

            "coordinate_confidence":
                result["coordinate_confidence"],

            "matched_address":
                result["matched_address"],

            "resolution_query":
                result["resolution_query"],

            "resolution_status":
                result["resolution_status"],
        })

    # --------------------------------------------------------
    # Save complete dataset
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Save resolution review
    # --------------------------------------------------------

    review = pd.DataFrame(results)

    review.to_csv(
        REVIEW_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    valid = (
        df["latitude"].notna()
        &
        df["longitude"].notna()
    )

    print("\n" + "=" * 70)
    print("RESOLUTION COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal settlements : {len(df)}"
    )

    print(
        f"Usable coordinates: {valid.sum()}"
    )

    print(
        f"Still missing     : {(~valid).sum()}"
    )

    print(
        f"\nFull output:\n{OUTPUT_FILE}"
    )

    print(
        f"\nReview output:\n{REVIEW_FILE}"
    )


if __name__ == "__main__":
    main()