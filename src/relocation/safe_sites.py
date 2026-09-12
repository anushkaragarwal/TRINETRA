"""
TRINETRA - SAFE SITE IDENTIFICATION
===================================

MEMBER 2 MODULE

Purpose:
    Identify suitable educational facilities that can be used as
    temporary relocation / evacuation sites.

This module:
    - Uses the existing facility_master.csv
    - Uses the existing settlement coordinate master
    - Calculates facility suitability
    - Calculates temporary capacity
    - Performs multi-level facility -> settlement coordinate matching
    - Calculates proximity to population settlements
    - Produces safe_sites.csv

This module DOES NOT:
    - train DEM models
    - modify DEM data
    - train landslide models
    - modify landslide data
    - calculate flood hazard
    - calculate landslide hazard

No coordinates are invented.
If a facility cannot be reliably matched, it remains unresolved.
"""

from pathlib import Path
import math
import re

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

FACILITY_FILE = (
    ROOT / "data" / "features" / "facility_master.csv"
)

EXPOSURE_FILE = (
    ROOT / "data" / "features" / "settlement_exposure.csv"
)

COORDINATE_FILE = (
    ROOT
    / "data"
    / "features"
    / "settlement_coordinates_final_master.csv"
)

OUTPUT_FILE = (
    ROOT / "data" / "features" / "safe_sites.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

PEOPLE_PER_CLASSROOM = 25

EMERGENCY_CAPACITY_FACTOR = 0.50

MIN_TEMPORARY_CAPACITY = 20

# Safe-site score
WEIGHT_FACILITY = 0.40
WEIGHT_CAPACITY = 0.25
WEIGHT_ACCESSIBILITY = 0.20
WEIGHT_INFRASTRUCTURE = 0.15


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    """
    Normalize administrative names for robust matching.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    # Remove content inside brackets.
    value = re.sub(r"\([^)]*\)", " ", value)

    # Replace punctuation with spaces.
    value = re.sub(r"[^A-Z0-9]+", " ", value)

    # Normalize whitespace.
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_pincode(value):
    """
    Normalize pincode values.
    """

    if pd.isna(value):
        return ""

    text = str(value).strip()

    # Handle values such as 123456.0
    if text.endswith(".0"):
        text = text[:-2]

    digits = re.sub(r"\D", "", text)

    if len(digits) == 6:
        return digits

    return ""


def numeric(value, default=0):
    """
    Convert a single value safely to float.
    """

    try:
        if pd.isna(value):
            return default

        result = float(value)

        if math.isnan(result):
            return default

        return result

    except (ValueError, TypeError):
        return default


def numeric_series(series, default=0):
    """
    Convert a pandas series to numeric safely.
    """

    return pd.to_numeric(
        series,
        errors="coerce",
    ).fillna(default)


def find_column(df, candidates):
    """
    Find the first available column from candidate names.
    """

    for column in candidates:
        if column in df.columns:
            return column

    return None


def yes_no_score(value):
    """
    Convert common coded yes/no fields to 0-100.

    Known numeric convention used by the supplied facility data:
        1 = positive / available
        2 = negative / unavailable

    Unknown values are treated conservatively as 0.
    """

    if pd.isna(value):
        return 0.0

    try:
        value = float(value)

        if value == 1:
            return 100.0

        if value == 2:
            return 0.0

    except (ValueError, TypeError):
        pass

    text = clean_text(value)

    if text in {
        "YES",
        "Y",
        "TRUE",
        "AVAILABLE",
        "FUNCTIONAL",
        "GOOD",
    }:
        return 100.0

    if text in {
        "NO",
        "N",
        "FALSE",
        "NOT AVAILABLE",
        "NON FUNCTIONAL",
        "BAD",
    }:
        return 0.0

    return 0.0


def minmax_score(series):
    """
    Normalize a numeric series to 0-100.
    """

    values = numeric_series(series)

    minimum = values.min()
    maximum = values.max()

    if maximum == minimum:
        return pd.Series(
            100.0,
            index=series.index,
        )

    return (
        (values - minimum)
        / (maximum - minimum)
        * 100.0
    )


def haversine_km(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """
    Calculate great-circle distance between two points.
    """

    if any(
        pd.isna(value)
        for value in [
            lat1,
            lon1,
            lat2,
            lon2,
        ]
    ):
        return np.nan

    radius = 6371.0

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return radius * c


# ============================================================
# LOAD FACILITIES
# ============================================================

def load_facilities():

    print()
    print("Loading facility data...")

    if not FACILITY_FILE.exists():
        raise FileNotFoundError(
            f"Facility file not found:\n{FACILITY_FILE}"
        )

    facilities = pd.read_csv(
        FACILITY_FILE,
        low_memory=False,
    )

    print(
        f"Facility records: {len(facilities):,}"
    )

    return facilities


# ============================================================
# LOAD EXPOSURE
# ============================================================

def load_exposure():

    print()
    print("Loading settlement exposure data...")

    if not EXPOSURE_FILE.exists():

        print(
            "WARNING: settlement_exposure.csv not found."
        )

        print(
            "Continuing without hazard/exposure fields."
        )

        return pd.DataFrame()

    exposure = pd.read_csv(
        EXPOSURE_FILE,
        low_memory=False,
    )

    print(
        f"Exposure settlements: {len(exposure):,}"
    )

    return exposure


# ============================================================
# LOAD COORDINATES
# ============================================================

def load_coordinates():

    print()
    print("Loading settlement coordinates...")

    if not COORDINATE_FILE.exists():
        raise FileNotFoundError(
            f"Coordinate file not found:\n{COORDINATE_FILE}"
        )

    coordinates = pd.read_csv(
        COORDINATE_FILE,
        low_memory=False,
    )

    required = [
        "settlement_id",
        "settlement_name",
        "latitude",
        "longitude",
    ]

    missing = [
        column
        for column in required
        if column not in coordinates.columns
    ]

    if missing:
        raise ValueError(
            "Coordinate file is missing columns: "
            + ", ".join(missing)
        )

    coordinates["latitude"] = pd.to_numeric(
        coordinates["latitude"],
        errors="coerce",
    )

    coordinates["longitude"] = pd.to_numeric(
        coordinates["longitude"],
        errors="coerce",
    )

    coordinates["settlement_name_clean"] = (
        coordinates["settlement_name"]
        .apply(clean_text)
    )

    coordinates["settlement_id"] = (
        coordinates["settlement_id"]
        .astype(str)
        .str.strip()
    )

    coordinates["district_clean"] = ""

    if "DISTRICT" in coordinates.columns:
        coordinates["district_clean"] = (
            coordinates["DISTRICT"]
            .apply(clean_text)
        )

    elif "district" in coordinates.columns:
        coordinates["district_clean"] = (
            coordinates["district"]
            .apply(clean_text)
        )

    coordinates["block_clean"] = ""

    if "SUBDISTT" in coordinates.columns:
        coordinates["block_clean"] = (
            coordinates["SUBDISTT"]
            .apply(clean_text)
        )

    elif "block" in coordinates.columns:
        coordinates["block_clean"] = (
            coordinates["block"]
            .apply(clean_text)
        )

    coordinates["ward_clean"] = ""

    if "WARD" in coordinates.columns:
        coordinates["ward_clean"] = (
            coordinates["WARD"]
            .apply(clean_text)
        )

    coordinates["pincode_clean"] = ""

    if "pincode" in coordinates.columns:
        coordinates["pincode_clean"] = (
            coordinates["pincode"]
            .apply(normalize_pincode)
        )

    coordinates["has_coordinates"] = (
        coordinates["latitude"].notna()
        & coordinates["longitude"].notna()
    )

    print(
        f"Coordinate records: {len(coordinates):,}"
    )

    print(
        "Usable coordinates: "
        f"{coordinates['has_coordinates'].sum():,}"
    )

    return coordinates


# ============================================================
# IDENTIFY FACILITY FIELDS
# ============================================================

def identify_fields(facilities):

    print()
    print("Identifying facility fields...")
    print()

    fields = {}

    fields["facility_id"] = find_column(
        facilities,
        [
            "pseudocode",
            "facility_id",
            "school_id",
            "id",
        ],
    )

    fields["village"] = find_column(
        facilities,
        [
            "lgd_vill_name",
            "village_name",
            "village",
            "town_village",
        ],
    )

    fields["urban"] = find_column(
        facilities,
        [
            "lgd_urban_local_body_name",
            "urban_local_body_name",
            "urban_local_body",
        ],
    )

    fields["ward"] = find_column(
        facilities,
        [
            "lgd_ward_name",
            "ward_name",
            "ward",
        ],
    )

    fields["block"] = find_column(
        facilities,
        [
            "lgd_block_name",
            "block_name",
            "block",
        ],
    )

    fields["district"] = find_column(
        facilities,
        [
            "district",
            "district_name",
        ],
    )

    fields["pincode"] = find_column(
        facilities,
        [
            "pincode",
            "pin_code",
        ],
    )

    fields["school_category"] = find_column(
        facilities,
        [
            "school_category",
        ],
    )

    fields["school_type"] = find_column(
        facilities,
        [
            "school_type",
        ],
    )

    fields["building_status"] = find_column(
        facilities,
        [
            "facility_building_status",
        ],
    )

    fields["total_classrooms"] = find_column(
        facilities,
        [
            "facility_total_class_rooms",
            "total_classrooms",
        ],
    )

    fields["good_classrooms"] = find_column(
        facilities,
        [
            "facility_classrooms_in_good_condition",
            "good_classrooms",
        ],
    )

    fields["minor_repair"] = find_column(
        facilities,
        [
            "facility_classrooms_needs_minor_repair",
        ],
    )

    fields["major_repair"] = find_column(
        facilities,
        [
            "facility_classrooms_needs_major_repair",
        ],
    )

    fields["road"] = find_column(
        facilities,
        [
            "approachable_road",
        ],
    )

    fields["land"] = find_column(
        facilities,
        [
            "facility_land_avl_yn",
        ],
    )

    fields["electricity"] = find_column(
        facilities,
        [
            "facility_electricity_availability",
        ],
    )

    fields["tap"] = find_column(
        facilities,
        [
            "facility_tap_yn",
        ],
    )

    fields["hand_pump"] = find_column(
        facilities,
        [
            "facility_hand_pump_yn",
        ],
    )

    fields["tap_functional"] = find_column(
        facilities,
        [
            "facility_tap_fun_yn",
        ],
    )

    fields["boundary"] = find_column(
        facilities,
        [
            "facility_boundary_wall",
        ],
    )

    fields["safety_plan"] = find_column(
        facilities,
        [
            "safety_sdmp_plan_yn",
        ],
    )

    fields["structural_audit"] = find_column(
        facilities,
        [
            "safety_struct_safaud_yn",
        ],
    )

    fields["fire_extinguisher"] = find_column(
        facilities,
        [
            "safety_fire_ext_yn",
        ],
    )

    labels = {
        "facility_id": "Facility ID",
        "village": "Village",
        "urban": "Urban local body",
        "ward": "Ward",
        "block": "Block",
        "district": "District",
        "pincode": "Pincode",
        "school_category": "School category",
        "school_type": "School type",
        "building_status": "Building status",
        "total_classrooms": "Total classrooms",
        "good_classrooms": "Good classrooms",
        "minor_repair": "Minor repair rooms",
        "major_repair": "Major repair rooms",
        "road": "Road access",
        "land": "Land available",
        "electricity": "Electricity",
        "tap": "Tap water",
        "hand_pump": "Hand pump",
        "tap_functional": "Functional water",
        "boundary": "Boundary wall",
        "safety_plan": "Safety plan",
        "structural_audit": "Structural audit",
        "fire_extinguisher": "Fire extinguisher",
    }

    for key, label in labels.items():
        print(
            f"  {label:<22}: "
            f"{fields.get(key)}"
        )

    return fields


# ============================================================
# CALCULATE FACILITY SCORES
# ============================================================

def calculate_facility_scores(
    facilities,
    fields,
):

    print()
    print("Calculating facility suitability...")

    df = facilities.copy()

    # --------------------------------------------------------
    # Classroom fields
    # --------------------------------------------------------

    if fields["total_classrooms"]:
        df["total_classrooms"] = numeric_series(
            df[fields["total_classrooms"]]
        )
    else:
        df["total_classrooms"] = 0.0

    if fields["good_classrooms"]:
        df["good_classrooms"] = numeric_series(
            df[fields["good_classrooms"]]
        )
    else:
        df["good_classrooms"] = 0.0

    if fields["minor_repair"]:
        df["minor_repair_classrooms"] = numeric_series(
            df[fields["minor_repair"]]
        )
    else:
        df["minor_repair_classrooms"] = 0.0

    if fields["major_repair"]:
        df["major_repair_classrooms"] = numeric_series(
            df[fields["major_repair"]]
        )
    else:
        df["major_repair_classrooms"] = 0.0

    # --------------------------------------------------------
    # Capacity
    # --------------------------------------------------------

    df["normal_classroom_capacity"] = (
        df["good_classrooms"]
        * PEOPLE_PER_CLASSROOM
    )

    df["temporary_capacity"] = (
        df["normal_classroom_capacity"]
        * EMERGENCY_CAPACITY_FACTOR
    )

    df["available_capacity"] = (
        df["temporary_capacity"]
        .round()
        .astype(int)
    )

    # --------------------------------------------------------
    # Building condition score
    #
    # We use actual good/total classroom ratio rather than
    # assuming meanings for categorical building-status codes.
    # --------------------------------------------------------

    df["building_score"] = np.where(
        df["total_classrooms"] > 0,
        (
            df["good_classrooms"]
            / df["total_classrooms"]
        ) * 100.0,
        0.0,
    )

    df["building_score"] = (
        df["building_score"]
        .clip(0, 100)
    )

    # --------------------------------------------------------
    # Road
    # --------------------------------------------------------

    if fields["road"]:
        df["road_score"] = (
            df[fields["road"]]
            .apply(yes_no_score)
        )
    else:
        df["road_score"] = 0.0

    # --------------------------------------------------------
    # Land
    # --------------------------------------------------------

    if fields["land"]:
        df["land_score"] = (
            df[fields["land"]]
            .apply(yes_no_score)
        )
    else:
        df["land_score"] = 0.0

    # --------------------------------------------------------
    # Electricity
    # --------------------------------------------------------

    if fields["electricity"]:
        df["electricity_score"] = (
            df[fields["electricity"]]
            .apply(yes_no_score)
        )
    else:
        df["electricity_score"] = 0.0

    # --------------------------------------------------------
    # Water
    # --------------------------------------------------------

    water_scores = []

    for index in df.index:

        scores = []

        if fields["tap"]:
            scores.append(
                yes_no_score(
                    df.at[
                        index,
                        fields["tap"],
                    ]
                )
            )

        if fields["hand_pump"]:
            scores.append(
                yes_no_score(
                    df.at[
                        index,
                        fields["hand_pump"],
                    ]
                )
            )

        if fields["tap_functional"]:
            scores.append(
                yes_no_score(
                    df.at[
                        index,
                        fields["tap_functional"],
                    ]
                )
            )

        if scores:
            water_scores.append(
                max(scores)
            )
        else:
            water_scores.append(0.0)

    df["water_score"] = water_scores

    # --------------------------------------------------------
    # Boundary wall
    # --------------------------------------------------------

    if fields["boundary"]:
        df["boundary_wall_score"] = (
            df[fields["boundary"]]
            .apply(yes_no_score)
        )
    else:
        df["boundary_wall_score"] = 0.0

    # --------------------------------------------------------
    # Safety fields
    # --------------------------------------------------------

    safety_scores = []

    for index in df.index:

        values = []

        for key in [
            "safety_plan",
            "structural_audit",
            "fire_extinguisher",
        ]:

            column = fields[key]

            if column:
                values.append(
                    yes_no_score(
                        df.at[index, column]
                    )
                )

        if values:
            safety_scores.append(
                np.mean(values)
            )
        else:
            safety_scores.append(0.0)

    df["safety_score"] = safety_scores

    # --------------------------------------------------------
    # Accessibility
    # --------------------------------------------------------

    df["accessibility_score"] = (
        0.60 * df["road_score"]
        + 0.20 * df["water_score"]
        + 0.20 * df["electricity_score"]
    )

    # --------------------------------------------------------
    # Capacity score
    # --------------------------------------------------------

    df["capacity_score"] = minmax_score(
        df["temporary_capacity"]
    )

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    df["infrastructure_score"] = (
        0.30 * df["water_score"]
        + 0.30 * df["electricity_score"]
        + 0.15 * df["land_score"]
        + 0.10 * df["boundary_wall_score"]
        + 0.15 * df["safety_score"]
    )

    # --------------------------------------------------------
    # Facility suitability
    # --------------------------------------------------------

    df["facility_suitability_score"] = (
        0.30 * df["building_score"]
        + 0.25 * df["capacity_score"]
        + 0.15 * df["road_score"]
        + 0.10 * df["water_score"]
        + 0.10 * df["electricity_score"]
        + 0.10 * df["safety_score"]
    )

    # --------------------------------------------------------
    # Final safe-site score
    # --------------------------------------------------------

    df["safe_site_score"] = (
        WEIGHT_FACILITY
        * df["facility_suitability_score"]
        + WEIGHT_CAPACITY
        * df["capacity_score"]
        + WEIGHT_ACCESSIBILITY
        * df["accessibility_score"]
        + WEIGHT_INFRASTRUCTURE
        * df["infrastructure_score"]
    )

    df["safe_site_score"] = (
        df["safe_site_score"]
        .clip(0, 100)
        .round(2)
    )

    return df


# ============================================================
# PREPARE FACILITY MATCHING FIELDS
# ============================================================

def prepare_matching_fields(
    facilities,
    fields,
):

    df = facilities.copy()

    def add_clean(
        output,
        source,
    ):

        if source and source in df.columns:
            df[output] = (
                df[source]
                .apply(clean_text)
            )
        else:
            df[output] = ""

    add_clean(
        "match_village",
        fields["village"],
    )

    add_clean(
        "match_urban",
        fields["urban"],
    )

    add_clean(
        "match_ward",
        fields["ward"],
    )

    add_clean(
        "match_block",
        fields["block"],
    )

    add_clean(
        "match_district",
        fields["district"],
    )

    if fields["pincode"]:
        df["match_pincode"] = (
            df[fields["pincode"]]
            .apply(normalize_pincode)
        )
    else:
        df["match_pincode"] = ""

    return df


# ============================================================
# BUILD COORDINATE LOOKUPS
# ============================================================

def build_coordinate_lookups(coordinates):

    valid = coordinates[
        coordinates["has_coordinates"]
    ].copy()

    lookups = {}

    # --------------------------------------------------------
    # Name lookup
    # --------------------------------------------------------

    lookups["name"] = {}

    for _, row in valid.iterrows():

        key = row["settlement_name_clean"]

        if not key:
            continue

        lookups["name"].setdefault(
            key,
            [],
        ).append(row)

    # --------------------------------------------------------
    # District + name
    # --------------------------------------------------------

    lookups["district_name"] = {}

    for _, row in valid.iterrows():

        name = row["settlement_name_clean"]
        district = row["district_clean"]

        if not name:
            continue

        key = (
            district,
            name,
        )

        lookups["district_name"].setdefault(
            key,
            [],
        ).append(row)

    # --------------------------------------------------------
    # Block + name
    # --------------------------------------------------------

    lookups["block_name"] = {}

    for _, row in valid.iterrows():

        name = row["settlement_name_clean"]
        block = row["block_clean"]

        if not name:
            continue

        key = (
            block,
            name,
        )

        lookups["block_name"].setdefault(
            key,
            [],
        ).append(row)

    # --------------------------------------------------------
    # District + block + name
    # --------------------------------------------------------

    lookups["district_block_name"] = {}

    for _, row in valid.iterrows():

        name = row["settlement_name_clean"]
        block = row["block_clean"]
        district = row["district_clean"]

        if not name:
            continue

        key = (
            district,
            block,
            name,
        )

        lookups["district_block_name"].setdefault(
            key,
            [],
        ).append(row)

    # --------------------------------------------------------
    # Ward + urban body
    # --------------------------------------------------------

    lookups["urban_ward"] = {}

    for _, row in valid.iterrows():

        ward = row["ward_clean"]

        # Settlement name acts as the locality / urban body
        # fallback where explicit urban body isn't present.
        name = row["settlement_name_clean"]

        if not ward or not name:
            continue

        key = (
            name,
            ward,
        )

        lookups["urban_ward"].setdefault(
            key,
            [],
        ).append(row)

    # --------------------------------------------------------
    # Pincode
    # --------------------------------------------------------

    lookups["pincode"] = {}

    for _, row in valid.iterrows():

        pincode = row["pincode_clean"]

        if not pincode:
            continue

        lookups["pincode"].setdefault(
            pincode,
            [],
        ).append(row)

    return lookups


# ============================================================
# SELECT UNIQUE MATCH
# ============================================================

def choose_match(
    matches,
    facility_row,
):

    if not matches:
        return None

    # Remove duplicate coordinate records.
    unique = {}

    for row in matches:

        key = (
            str(row["settlement_id"]),
            float(row["latitude"]),
            float(row["longitude"]),
        )

        unique[key] = row

    matches = list(unique.values())

    if len(matches) == 1:
        return matches[0]

    # If multiple candidates exist, prefer same district.
    facility_district = facility_row[
        "match_district"
    ]

    district_matches = [
        row
        for row in matches
        if facility_district
        and row["district_clean"]
        == facility_district
    ]

    if len(district_matches) == 1:
        return district_matches[0]

    # Multiple equally plausible matches are NOT resolved.
    return None


# ============================================================
# MATCH ONE FACILITY
# ============================================================

def match_facility(
    row,
    lookups,
):

    village = row["match_village"]
    urban = row["match_urban"]
    ward = row["match_ward"]
    block = row["match_block"]
    district = row["match_district"]
    pincode = row["match_pincode"]

    # --------------------------------------------------------
    # 1. District + block + village
    # --------------------------------------------------------

    if village:

        matches = lookups[
            "district_block_name"
        ].get(
            (
                district,
                block,
                village,
            ),
            [],
        )

        match = choose_match(
            matches,
            row,
        )

        if match is not None:
            return (
                match,
                "DISTRICT_BLOCK_VILLAGE",
            )

    # --------------------------------------------------------
    # 2. District + village
    # --------------------------------------------------------

    if village:

        matches = lookups[
            "district_name"
        ].get(
            (
                district,
                village,
            ),
            [],
        )

        match = choose_match(
            matches,
            row,
        )

        if match is not None:
            return (
                match,
                "DISTRICT_VILLAGE",
            )

    # --------------------------------------------------------
    # 3. Block + village
    # --------------------------------------------------------

    if village:

        matches = lookups[
            "block_name"
        ].get(
            (
                block,
                village,
            ),
            [],
        )

        match = choose_match(
            matches,
            row,
        )

        if match is not None:
            return (
                match,
                "BLOCK_VILLAGE",
            )

    # --------------------------------------------------------
    # 4. Exact village name
    # --------------------------------------------------------

    if village:

        matches = lookups[
            "name"
        ].get(
            village,
            [],
        )

        match = choose_match(
            matches,
            row,
        )

        if match is not None:
            return (
                match,
                "VILLAGE_NAME",
            )

    # --------------------------------------------------------
    # 5. Urban body + ward
    # --------------------------------------------------------

    if urban and ward:

        matches = lookups[
            "urban_ward"
        ].get(
            (
                urban,
                ward,
            ),
            [],
        )

        match = choose_match(
            matches,
            row,
        )

        if match is not None:
            return (
                match,
                "URBAN_WARD",
            )

    # --------------------------------------------------------
    # 6. Pincode
    #
    # Only accept a pincode when it uniquely identifies a
    # coordinate record.
    # --------------------------------------------------------

    if pincode:

        matches = lookups[
            "pincode"
        ].get(
            pincode,
            [],
        )

        match = choose_match(
            matches,
            row,
        )

        if match is not None:
            return (
                match,
                "PINCODE",
            )

    return (
        None,
        "UNRESOLVED",
    )


# ============================================================
# MATCH ALL FACILITIES
# ============================================================

def match_facilities_to_coordinates(
    facilities,
    coordinates,
):

    print()
    print(
        "Matching facility locations to settlements..."
    )

    df = facilities.copy()

    lookups = build_coordinate_lookups(
        coordinates
    )

    df["latitude"] = np.nan
    df["longitude"] = np.nan

    df["matched_settlement_id"] = ""
    df["matched_address"] = ""

    df["coordinate_confidence"] = (
        "UNRESOLVED"
    )

    df["coordinate_match_method"] = (
        "UNRESOLVED"
    )

    match_counts = {}

    for index, row in df.iterrows():

        match, method = match_facility(
            row,
            lookups,
        )

        if match is None:

            match_counts[method] = (
                match_counts.get(method, 0)
                + 1
            )

            continue

        df.at[
            index,
            "latitude",
        ] = match["latitude"]

        df.at[
            index,
            "longitude",
        ] = match["longitude"]

        df.at[
            index,
            "matched_settlement_id",
        ] = str(
            match["settlement_id"]
        )

        df.at[
            index,
            "matched_address",
        ] = str(
            match["settlement_name"]
        )

        df.at[
            index,
            "coordinate_match_method",
        ] = method

        # Confidence levels.
        if method in {
            "DISTRICT_BLOCK_VILLAGE",
            "DISTRICT_VILLAGE",
        }:
            confidence = "HIGH"

        elif method in {
            "BLOCK_VILLAGE",
            "VILLAGE_NAME",
        }:
            confidence = "MEDIUM"

        elif method == "URBAN_WARD":
            confidence = "MEDIUM"

        elif method == "PINCODE":
            confidence = "LOW"

        else:
            confidence = "UNRESOLVED"

        df.at[
            index,
            "coordinate_confidence",
        ] = confidence

        match_counts[method] = (
            match_counts.get(method, 0)
            + 1
        )

    df["has_coordinates"] = (
        df["latitude"].notna()
        & df["longitude"].notna()
    )

    print()
    print("Coordinate matching results:")

    for method, count in sorted(
        match_counts.items(),
        key=lambda item: item[0],
    ):
        print(
            f"  {method:<30}: {count:,}"
        )

    print()
    print(
        "Facilities with coordinates: "
        f"{df['has_coordinates'].sum():,}"
    )

    print(
        "Facilities without coordinates: "
        f"{(~df['has_coordinates']).sum():,}"
    )

    return df


# ============================================================
# CALCULATE PROXIMITY
# ============================================================

def calculate_proximity(
    sites,
    coordinates,
):

    print()
    print(
        "Calculating proximity to population settlements..."
    )

    sites = sites.copy()

    valid_coordinates = coordinates[
        coordinates["has_coordinates"]
    ].copy()

    if valid_coordinates.empty:

        sites["nearest_settlement_id"] = ""
        sites["nearest_settlement_name"] = ""
        sites["nearest_settlement_distance_km"] = np.nan

        return sites

    settlement_points = (
        valid_coordinates[
            [
                "settlement_id",
                "settlement_name",
                "latitude",
                "longitude",
            ]
        ]
        .drop_duplicates(
            subset=["settlement_id"]
        )
    )

    nearest_ids = []
    nearest_names = []
    nearest_distances = []

    for _, site in sites.iterrows():

        if (
            pd.isna(site["latitude"])
            or pd.isna(site["longitude"])
        ):

            nearest_ids.append("")
            nearest_names.append("")
            nearest_distances.append(np.nan)

            continue

        minimum_distance = np.inf
        minimum_id = ""
        minimum_name = ""

        for _, settlement in (
            settlement_points.iterrows()
        ):

            distance = haversine_km(
                site["latitude"],
                site["longitude"],
                settlement["latitude"],
                settlement["longitude"],
            )

            if (
                pd.notna(distance)
                and distance < minimum_distance
            ):

                minimum_distance = distance
                minimum_id = str(
                    settlement["settlement_id"]
                )
                minimum_name = str(
                    settlement["settlement_name"]
                )

        if minimum_distance == np.inf:
            minimum_distance = np.nan

        nearest_ids.append(minimum_id)
        nearest_names.append(minimum_name)
        nearest_distances.append(
            minimum_distance
        )

    sites["nearest_settlement_id"] = (
        nearest_ids
    )

    sites["nearest_settlement_name"] = (
        nearest_names
    )

    sites["nearest_settlement_distance_km"] = (
        nearest_distances
    )

    return sites


# ============================================================
# CREATE FINAL OUTPUT
# ============================================================

def create_output(
    facilities,
    fields,
):

    df = facilities.copy()

    # --------------------------------------------------------
    # Site ID
    # --------------------------------------------------------

    if fields["facility_id"]:

        df["site_id"] = (
            df[fields["facility_id"]]
            .astype(str)
            .str.strip()
        )

    else:

        df["site_id"] = (
            pd.Series(
                range(
                    1,
                    len(df) + 1,
                ),
                index=df.index,
            )
            .astype(str)
        )

    # --------------------------------------------------------
    # Names
    # --------------------------------------------------------

    df["site_name"] = "Educational Facility"

    df["village_name"] = ""

    if fields["village"]:
        df["village_name"] = (
            df[fields["village"]]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["urban_local_body_name"] = ""

    if fields["urban"]:
        df["urban_local_body_name"] = (
            df[fields["urban"]]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["ward_name"] = ""

    if fields["ward"]:
        df["ward_name"] = (
            df[fields["ward"]]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["block_name"] = ""

    if fields["block"]:
        df["block_name"] = (
            df[fields["block"]]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["district_name"] = ""

    if fields["district"]:
        df["district_name"] = (
            df[fields["district"]]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # Codes
    # --------------------------------------------------------

    if fields["school_category"]:
        df["school_category_code"] = (
            df[fields["school_category"]]
        )
    else:
        df["school_category_code"] = np.nan

    if fields["school_type"]:
        df["school_type_code"] = (
            df[fields["school_type"]]
        )
    else:
        df["school_type_code"] = np.nan

    # --------------------------------------------------------
    # Site cluster
    # --------------------------------------------------------

    df["site_cluster"] = np.where(
        df["village_name"].str.strip() != "",
        df["village_name"],
        df["urban_local_body_name"],
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    df["site_status"] = np.select(
        [
            df["safe_site_score"] >= 70,
            df["safe_site_score"] >= 50,
        ],
        [
            "HIGH_SUITABILITY",
            "MEDIUM_SUITABILITY",
        ],
        default="LOW_SUITABILITY",
    )

    # --------------------------------------------------------
    # Selected final columns
    # --------------------------------------------------------

    output_columns = [
        "site_id",
        "site_name",
        "site_cluster",
        "village_name",
        "urban_local_body_name",
        "ward_name",
        "block_name",
        "district_name",

        "matched_settlement_id",
        "matched_address",

        "latitude",
        "longitude",

        "coordinate_confidence",
        "coordinate_match_method",

        "school_category_code",
        "school_type_code",

        "total_classrooms",
        "good_classrooms",
        "minor_repair_classrooms",
        "major_repair_classrooms",

        "normal_classroom_capacity",
        "temporary_capacity",
        "available_capacity",

        "building_score",
        "road_score",
        "water_score",
        "electricity_score",
        "land_score",
        "boundary_wall_score",
        "safety_score",

        "accessibility_score",
        "capacity_score",
        "infrastructure_score",
        "facility_suitability_score",
        "safe_site_score",

        "nearest_settlement_id",
        "nearest_settlement_name",
        "nearest_settlement_distance_km",

        "site_status",
    ]

    existing_columns = [
        column
        for column in output_columns
        if column in df.columns
    ]

    output = df[
        existing_columns
    ].copy()

    # Round scores/distances.
    score_columns = [
        "building_score",
        "road_score",
        "water_score",
        "electricity_score",
        "land_score",
        "boundary_wall_score",
        "safety_score",
        "accessibility_score",
        "capacity_score",
        "infrastructure_score",
        "facility_suitability_score",
        "safe_site_score",
        "nearest_settlement_distance_km",
    ]

    for column in score_columns:

        if column in output.columns:
            output[column] = pd.to_numeric(
                output[column],
                errors="coerce",
            ).round(3)

    return output


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("TRINETRA - SAFE SITE IDENTIFICATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    facilities = load_facilities()

    exposure = load_exposure()

    coordinates = load_coordinates()

    # --------------------------------------------------------
    # Detect fields
    # --------------------------------------------------------

    fields = identify_fields(
        facilities
    )

    # --------------------------------------------------------
    # Candidate facilities
    # --------------------------------------------------------

    print()
    print(
        "Calculating facility suitability..."
    )

    facilities = prepare_matching_fields(
        facilities,
        fields,
    )

    facilities = calculate_facility_scores(
        facilities,
        fields,
    )

    print()
    print(
        "Identifying candidate facilities..."
    )

    candidates = facilities[
        (
            facilities["good_classrooms"]
            > 0
        )
        &
        (
            facilities["temporary_capacity"]
            >= MIN_TEMPORARY_CAPACITY
        )
    ].copy()

    print(
        "Candidate facilities with usable "
        f"capacity: {len(candidates):,}"
    )

    # --------------------------------------------------------
    # Coordinate matching
    # --------------------------------------------------------

    candidates = match_facilities_to_coordinates(
        candidates,
        coordinates,
    )

    # --------------------------------------------------------
    # Proximity
    # --------------------------------------------------------

    candidates = calculate_proximity(
        candidates,
        coordinates,
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    output = create_output(
        candidates,
        fields,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    coordinate_count = int(
        output["latitude"]
        .notna()
        .sum()
    )

    no_coordinate_count = (
        len(output)
        - coordinate_count
    )

    total_capacity = int(
        output["temporary_capacity"]
        .sum()
    )

    high_count = int(
        (
            output["site_status"]
            == "HIGH_SUITABILITY"
        )
        .sum()
    )

    medium_count = int(
        (
            output["site_status"]
            == "MEDIUM_SUITABILITY"
        )
        .sum()
    )

    low_count = int(
        (
            output["site_status"]
            == "LOW_SUITABILITY"
        )
        .sum()
    )

    print()
    print("=" * 70)
    print("SAFE SITE MODEL COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Candidate safe sites       : "
        f"{len(output):,}"
    )

    print(
        f"Sites with coordinates     : "
        f"{coordinate_count:,}"
    )

    print(
        f"Sites without coordinates : "
        f"{no_coordinate_count:,}"
    )

    print(
        f"Total temporary capacity   : "
        f"{total_capacity:,}"
    )

    print(
        f"High suitability sites     : "
        f"{high_count:,}"
    )

    print(
        f"Medium suitability sites   : "
        f"{medium_count:,}"
    )

    print(
        f"Low suitability sites      : "
        f"{low_count:,}"
    )

    # --------------------------------------------------------
    # Matching confidence
    # --------------------------------------------------------

    print()
    print("Coordinate confidence:")

    confidence_counts = (
        output[
            "coordinate_confidence"
        ]
        .value_counts()
    )

    for confidence, count in (
        confidence_counts.items()
    ):
        print(
            f"  {confidence:<15}: "
            f"{count:,}"
        )

    # --------------------------------------------------------
    # Matching methods
    # --------------------------------------------------------

    print()
    print("Coordinate matching methods:")

    method_counts = (
        output[
            "coordinate_match_method"
        ]
        .value_counts()
    )

    for method, count in (
        method_counts.items()
    ):
        print(
            f"  {method:<30}: "
            f"{count:,}"
        )

    # --------------------------------------------------------
    # Top sites
    # --------------------------------------------------------

    print()
    print("Top candidate safe sites:")

    top_columns = [
        "site_id",
        "village_name",
        "temporary_capacity",
        "safe_site_score",
        "site_status",
        "coordinate_confidence",
        "coordinate_match_method",
    ]

    print(
        output[
            top_columns
        ]
        .sort_values(
            by=[
                "safe_site_score",
                "temporary_capacity",
            ],
            ascending=False,
        )
        .head(15)
        .to_string(index=False)
    )

    print()
    print("Output:")
    print(OUTPUT_FILE)

    print()
    print("Scoring:")
    print(
        "  Facility suitability : 40%"
    )
    print(
        "  Capacity             : 25%"
    )
    print(
        "  Accessibility        : 20%"
    )
    print(
        "  Infrastructure       : 15%"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()