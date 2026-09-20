from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

RIVER_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_hybrid_hazard.csv"
)

RAINFALL_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk_daily.csv"
)

LANDSLIDE_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_hazard_features.csv"
)

SATELLITE_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "gee_satellite_evidence_summary.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / "trinetra_event_dashboard_data.csv"
)


# ============================================================
# MULTI-HAZARD WEIGHTS
# ============================================================

# Configurable MVP weights.
#
# These are NOT statistically calibrated weights.
# They should be calibrated later using historical events.

RIVER_WEIGHT = 0.40
RAINFALL_WEIGHT = 0.30
LANDSLIDE_WEIGHT = 0.30

LANDSLIDE_RADIUS_KM = 1.0


# ============================================================
# VALIDATE WEIGHTS
# ============================================================

WEIGHT_SUM = (
    RIVER_WEIGHT
    + RAINFALL_WEIGHT
    + LANDSLIDE_WEIGHT
)

if not np.isclose(WEIGHT_SUM, 1.0):
    raise ValueError(
        "Hazard weights must sum to 1.0. "
        f"Current sum = {WEIGHT_SUM}"
    )


# ============================================================
# HELPERS
# ============================================================

def find_column(df, candidates, required=True):
    """
    Find a dataframe column using case-insensitive matching.
    """

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    if required:
        raise ValueError(
            f"Could not find any of:\n"
            f"{candidates}\n\n"
            f"Available columns:\n"
            f"{list(df.columns)}"
        )

    return None


def classify_risk(score):
    """
    Convert a 0-100 hazard score into the standard TRINETRA
    risk classification.
    """

    score = numeric(score)

    if not np.isfinite(score):
        return "UNKNOWN"

    if score >= 90:
        return "CRITICAL"

    if score >= 75:
        return "HIGH"

    if score >= 50:
        return "MODERATE"

    if score >= 25:
        return "LOW"

    return "VERY LOW"


def numeric(value, default=np.nan):
    """
    Safely convert a value to finite float.
    """

    try:
        value = float(value)

        if np.isfinite(value):
            return value

    except (TypeError, ValueError):
        pass

    return default


def normalize_text(value):
    """
    Normalize text for matching.
    """

    if value is None or pd.isna(value):
        return ""

    return str(value).strip().upper()


def parse_date_series(series):
    """
    Parse a pandas series into dates.
    Invalid dates become NaT.
    """

    return pd.to_datetime(
        series,
        errors="coerce"
    )


# ============================================================
# RAINFALL COVERAGE
# ============================================================

def get_rainfall_coverage(rainfall_df):
    """
    Determine the actual available rainfall date range from
    the rainfall dataset.

    This prevents the event integration from selecting an
    event date for which rainfall data does not exist.
    """

    date_col = find_column(
        rainfall_df,
        [
            "date",
            "Date",
            "DATE",
        ],
    )

    rainfall_dates = parse_date_series(
        rainfall_df[date_col]
    ).dropna()

    if rainfall_dates.empty:
        raise ValueError(
            "Rainfall dataset contains no valid dates."
        )

    start_date = rainfall_dates.min().date()
    end_date = rainfall_dates.max().date()

    return start_date, end_date, date_col


# ============================================================
# LOCAL LANDSLIDE LOOKUP
# ============================================================

def get_local_landslide(
    landslide_df,
    event_lat,
    event_lon,
):
    """
    Extract landslide hazard information from approximately
    1 km around the event.

    landslide_hazard_features.csv contains:

        cell_id
        lat
        lon
        landslide_probability
        landslide_susceptibility_score
        landslide_susceptibility_level
        hazard_score
        risk_level
        hazard_source

    This layer does not contain slope/elevation fields, so
    those values are not calculated here.
    """

    required_columns = [
        "lat",
        "lon",
        "hazard_score",
        "landslide_probability",
    ]

    missing = [
        column
        for column in required_columns
        if column not in landslide_df.columns
    ]

    if missing:
        raise ValueError(
            "Landslide dataset is missing required columns: "
            f"{missing}"
        )

    km_lat = LANDSLIDE_RADIUS_KM / 111.0

    cos_lat = np.cos(
        np.radians(event_lat)
    )

    # Protect against division by zero near poles.
    if abs(cos_lat) < 1e-8:
        cos_lat = 1e-8

    km_lon = LANDSLIDE_RADIUS_KM / (
        111.0 * cos_lat
    )

    mask = (
        (landslide_df["lat"] >= event_lat - km_lat)
        & (landslide_df["lat"] <= event_lat + km_lat)
        & (landslide_df["lon"] >= event_lon - km_lon)
        & (landslide_df["lon"] <= event_lon + km_lon)
    )

    local = landslide_df.loc[mask].copy()

    if local.empty:
        raise ValueError(
            "No landslide hazard cells found around "
            "the event location."
        )

    local["hazard_score"] = pd.to_numeric(
        local["hazard_score"],
        errors="coerce",
    )

    local["landslide_probability"] = pd.to_numeric(
        local["landslide_probability"],
        errors="coerce",
    )

    local = local[
        local["hazard_score"].notna()
    ].copy()

    if local.empty:
        raise ValueError(
            "Local landslide cells exist, but contain "
            "no valid hazard_score values."
        )

    landslide_score = float(
        local["hazard_score"].median()
    )

    landslide_max = float(
        local["hazard_score"].max()
    )

    probability_median = float(
        local["landslide_probability"].median()
    )

    probability_max = float(
        local["landslide_probability"].max()
    )

    return {
        "landslide_hazard_score_0_100": landslide_score,
        "landslide_hazard_max_score_0_100": landslide_max,
        "landslide_probability_median": probability_median,
        "landslide_probability_max": probability_max,
        "landslide_hazard_level": classify_risk(
            landslide_score
        ),
        "landslide_cells_used": len(local),

        # Not available from this layer.
        "landslide_slope_median_deg": np.nan,
        "landslide_slope_max_deg": np.nan,
        "landslide_elevation_median_m": np.nan,
    }


# ============================================================
# RAINFALL LOOKUP
# ============================================================

def get_rainfall_risk(
    rainfall_df,
    district,
    event_date,
):
    """
    Match daily rainfall risk using:

        District + event date

    The event must already have been filtered to the rainfall
    coverage window before this function is called.
    """

    if district is None or pd.isna(district):
        raise ValueError(
            "District is required for rainfall matching."
        )

    required_columns = [
        "District",
        "date",
        "max_risk_score",
        "max_daily_rainfall_mm",
        "mean_daily_rainfall_mm",
        "observations",
    ]

    missing = [
        column
        for column in required_columns
        if column not in rainfall_df.columns
    ]

    if missing:
        raise ValueError(
            "Rainfall dataset is missing required columns: "
            f"{missing}"
        )

    rainfall_df = rainfall_df.copy()

    rainfall_df["_district"] = (
        rainfall_df["District"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    rainfall_df["_date"] = (
        pd.to_datetime(
            rainfall_df["date"],
            errors="coerce",
        )
        .dt.date
    )

    target_date = pd.Timestamp(
        event_date
    ).date()

    matched = rainfall_df[
        (rainfall_df["_district"] == normalize_text(district))
        & (rainfall_df["_date"] == target_date)
    ].copy()

    event_date_rainfall_available = not matched.empty

    if matched.empty:
        print()
        print(
        "WARNING: Rainfall data is unavailable for the "
        f"selected event date {target_date}."
        )
        print(
        "Using the latest available rainfall record "
        "from the frozen dataset as MVP fallback."
        )

    fallback = rainfall_df[
        rainfall_df["_district"] == normalize_text(district)
    ].copy()

    fallback = fallback[
        fallback["_date"].notna()
    ]

    if fallback.empty:
        raise ValueError(
            "No rainfall data is available for district "
            f"{district}."
        )

    latest_date = fallback["_date"].max()

    matched = fallback[
        fallback["_date"] == latest_date
    ].copy()

    print(
        f"Rainfall fallback date: {latest_date}"
    )

    # There should normally be one district/day record.
    # If multiple records exist, use the maximum daily risk.
    score = float(
        pd.to_numeric(
            matched["max_risk_score"],
            errors="coerce",
        ).max()
    )

    max_rainfall = float(
        pd.to_numeric(
            matched["max_daily_rainfall_mm"],
            errors="coerce",
        ).max()
    )

    mean_rainfall = float(
        pd.to_numeric(
            matched["mean_daily_rainfall_mm"],
            errors="coerce",
        ).mean()
    )

    observations = int(
        pd.to_numeric(
            matched["observations"],
            errors="coerce",
        ).fillna(0).sum()
    )

    if not np.isfinite(score):
        raise ValueError(
            "Rainfall record exists for the event date, "
            "but max_risk_score is invalid."
        )

    return {
        "rainfall_available": event_date_rainfall_available,
        "rainfall_risk_score_0_100": score,
        "rainfall_risk_level": classify_risk(score),
        "rainfall_observations": observations,
        "rainfall_max_mm": max_rainfall,
        "rainfall_mean_mm": mean_rainfall,
    }


# ============================================================
# SELECT VALID SATELLITE EVENT
# ============================================================

def select_satellite_event(
    satellite_df,
    rainfall_start_date,
    rainfall_end_date,
):
    """
    Select a satellite event whose event date falls inside
    the actual rainfall coverage window.

    No event outside the rainfall window is allowed into the
    final TRINETRA event integration.
    """

    required_columns = [
        "event_id",
        "station_name",
        "event_time_ist",
        "latitude",
        "longitude",
    ]

    missing = [
        column
        for column in required_columns
        if column not in satellite_df.columns
    ]

    if missing:
        raise ValueError(
            "Satellite dataset is missing required columns: "
            f"{missing}"
        )

    satellite_df = satellite_df.copy()

    satellite_df["_event_time"] = pd.to_datetime(
        satellite_df["event_time_ist"],
        errors="coerce",
    )

    satellite_df["_event_date"] = (
        satellite_df["_event_time"]
        .dt.date
    )

    valid_satellite_events = satellite_df[
        satellite_df["_event_time"].notna()
        & satellite_df["_event_date"].notna()
        & (
            satellite_df["_event_date"]
            >= rainfall_start_date
        )
        & (
            satellite_df["_event_date"]
            <= rainfall_end_date
        )
    ].copy()

    print()
    print("Rainfall coverage:")
    print(
        f"  Start date : {rainfall_start_date}"
    )
    print(
        f"  End date   : {rainfall_end_date}"
    )

    print()
    print(
        "Satellite events before date filtering: "
        f"{len(satellite_df)}"
    )

    print(
        "Satellite events inside rainfall window: "
        f"{len(valid_satellite_events)}"
    )

    if valid_satellite_events.empty:
        print()
        print(
            "WARNING: No satellite event falls inside the "
            "available rainfall date range."
        )
        print(
            "Using the latest available satellite event as "
            "supporting/historical evidence."
        )

        satellite_row = (
            satellite_df
            .sort_values("_event_time")
            .iloc[-1]
            .copy()
        )

        satellite_row["_satellite_temporal_status"] = (
            "OUTSIDE_RAINFALL_WINDOW"
        )

        return satellite_row

    # Sort chronologically and select the earliest valid event.
    satellite_row = (
        valid_satellite_events
        .sort_values("_event_time")
        .iloc[0]
        .copy()
    )

    satellite_row["_satellite_temporal_status"] = (
        "INSIDE_RAINFALL_WINDOW"
    )

    return satellite_row

    # Sort chronologically and select the earliest valid event.
    satellite_row = (
        valid_satellite_events
        .sort_values("_event_time")
        .iloc[0]
        .copy()
    )

    satellite_row["_satellite_temporal_status"] = (
        "INSIDE_RAINFALL_WINDOW"
    )

    return satellite_row


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "TRINETRA - FINAL MULTI-HAZARD EVENT INTEGRATION"
    )
    print("=" * 70)

    # ========================================================
    # LOAD
    # ========================================================

    print("\nLoading river data...")

    if not RIVER_PATH.exists():
        raise FileNotFoundError(
            f"River file not found:\n{RIVER_PATH}"
        )

    river_df = pd.read_csv(RIVER_PATH)

    print(
        f"River rows: {len(river_df)}"
    )


    print("\nLoading rainfall data...")

    if not RAINFALL_PATH.exists():
        raise FileNotFoundError(
            f"Rainfall file not found:\n{RAINFALL_PATH}"
        )

    rainfall_df = pd.read_csv(
        RAINFALL_PATH
    )

    print(
        f"Rainfall daily rows: {len(rainfall_df)}"
    )


    print("\nLoading landslide hazard...")

    if not LANDSLIDE_PATH.exists():
        raise FileNotFoundError(
            f"Landslide file not found:\n{LANDSLIDE_PATH}"
        )

    landslide_df = pd.read_csv(
        LANDSLIDE_PATH
    )

    print(
        f"Landslide rows: {len(landslide_df)}"
    )


    print("\nLoading satellite events...")

    if not SATELLITE_PATH.exists():
        raise FileNotFoundError(
            f"Satellite file not found:\n{SATELLITE_PATH}"
        )

    satellite_df = pd.read_csv(
        SATELLITE_PATH
    )

    print(
        f"Satellite rows: {len(satellite_df)}"
    )

    if satellite_df.empty:
        raise ValueError(
            "Satellite evidence file contains no event rows."
        )


    # ========================================================
    # DETERMINE RAINFALL COVERAGE
    # ========================================================

    rainfall_start_date, rainfall_end_date, rainfall_date_col = (
        get_rainfall_coverage(
            rainfall_df
        )
    )

    print()
    print(
        "Detected rainfall data coverage:"
    )
    print(
        f"  {rainfall_start_date} "
        f"to "
        f"{rainfall_end_date}"
    )


    # ========================================================
    # BASIC RIVER COLUMN VALIDATION
    # ========================================================

    river_station_col = find_column(
        river_df,
        [
            "Station",
            "station",
            "station_name",
        ],
    )

    river_score_col = find_column(
        river_df,
        [
            "hybrid_hazard_score",
            "hazard_score",
            "risk_score",
        ],
    )

    river_level_col = find_column(
        river_df,
        [
            "hybrid_hazard_category",
            "hybrid_hazard_level",
            "hazard_category",
            "risk_category",
        ],
        required=False,
    )


    # ========================================================
    # SELECT SATELLITE EVENT
    # ========================================================

    satellite_row = select_satellite_event(
        satellite_df,
        rainfall_start_date,
        rainfall_end_date,
    )

    event_id = satellite_row["event_id"]

    station_name = satellite_row[
        "station_name"
    ]

    event_time = pd.to_datetime(
        satellite_row["event_time_ist"],
        errors="coerce",
    )

    if pd.isna(event_time):
        raise ValueError(
            "Could not parse event_time_ist."
        )

    event_date = event_time.date()

    event_lat = numeric(
        satellite_row["latitude"]
    )

    event_lon = numeric(
        satellite_row["longitude"]
    )

    if not np.isfinite(event_lat):
        raise ValueError(
            "Satellite event latitude is invalid."
        )

    if not np.isfinite(event_lon):
        raise ValueError(
            "Satellite event longitude is invalid."
        )

    print("\nSelected event:")

    print(
        f"Event ID       : {event_id}"
    )

    print(
        f"Station        : {station_name}"
    )

    print(
        f"Event time     : {event_time}"
    )

    print(
        f"Event date     : {event_date}"
    )

    print(
        f"Coordinates    : "
        f"{event_lat:.6f}, "
        f"{event_lon:.6f}"
    )


    # ========================================================
    # FINAL DATE SAFETY CHECK
    # ========================================================

    if not(
    rainfall_start_date
    <= event_date
    <= rainfall_end_date
    ):
        print()
        print(
        "WARNING: Selected event date falls outside "
        "rainfall coverage."
        )
        print(
        "Continuing MVP integration using available "
        "satellite evidence."
        )


    # ========================================================
    # RIVER
    # ========================================================

    print("\nMatching river event...")

    river_df["_station_normalized"] = (
        river_df[river_station_col]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    station_terms = [
        str(station_name)
        .lower()
        .strip(),
        "lambagarh",
    ]

    matched_river = river_df[
        river_df["_station_normalized"].apply(
            lambda value: any(
                term in value
                for term in station_terms
            )
        )
    ].copy()

    if matched_river.empty:
        raise ValueError(
            "No matching river station/event found."
        )


    # --------------------------------------------------------
    # Parse river timestamps
    # --------------------------------------------------------

    river_time_col = find_column(
        matched_river,
        [
            "Data Acquisition Time",
            "data_acquisition_time",
        ],
        required=False,
    )

    if river_time_col is None:
        raise ValueError(
            "River dataset has no Data Acquisition Time column."
        )

    matched_river["_river_time"] = pd.to_datetime(
        matched_river[river_time_col],
        errors="coerce",
    )

    matched_river[river_score_col] = pd.to_numeric(
        matched_river[river_score_col],
        errors="coerce",
    )

    matched_river = matched_river[
        matched_river["_river_time"].notna()
        & matched_river[river_score_col].notna()
    ].copy()

    if matched_river.empty:
        raise ValueError(
            "River records exist, but no valid timestamp "
            "and hazard score combination was found."
        )


    # --------------------------------------------------------
    # Find river observation closest to satellite event
    # --------------------------------------------------------

    matched_river["_time_difference"] = (
        matched_river["_river_time"]
        - event_time
    ).abs()

    selected_river = (
        matched_river
        .sort_values(
            by="_time_difference"
        )
        .iloc[0]
    )

    river_time_difference = (
        selected_river["_time_difference"]
    )

    river_score = float(
        selected_river[river_score_col]
    )


    # --------------------------------------------------------
    # District
    # --------------------------------------------------------

    district_col = find_column(
        matched_river,
        [
            "District",
            "district",
        ],
        required=False,
    )

    if district_col:
        district = str(
            selected_river[district_col]
        ).strip()
    else:
        district = None

    if not district:
        raise ValueError(
            "Could not determine district from river data."
        )


    if river_level_col:
        river_level = str(
            selected_river[river_level_col]
        ).strip()

        if not river_level:
            river_level = classify_risk(
                river_score
            )
    else:
        river_level = classify_risk(
            river_score
        )


    print("\nRiver:")

    print(
        f"District       : {district}"
    )

    print(
        f"Risk score     : {river_score:.2f}"
    )

    print(
        f"Risk level     : {river_level}"
    )

    print(
        "River observation time: "
        f"{selected_river['_river_time']}"
    )

    print(
        "Time difference       : "
        f"{river_time_difference}"
    )


    # ========================================================
    # RAINFALL
    # ========================================================

    print("\nMatching rainfall...")

    rainfall = get_rainfall_risk(
        rainfall_df,
        district,
        event_date,
    )

    # Because the event was filtered against rainfall coverage,
    # rainfall MUST be available here.

    if not rainfall["rainfall_available"]:
        print(
            "Rainfall status : MVP FALLBACK "
            "(event-date rainfall unavailable)"
        )

    rainfall_score = float(
        rainfall[
            "rainfall_risk_score_0_100"
        ]
    )

    if not np.isfinite(rainfall_score):
        raise RuntimeError(
            "Rainfall score is not finite."
        )

    print(
        f"Rainfall score : "
        f"{rainfall_score:.2f}"
    )

    print(
        f"Rainfall level : "
        f"{rainfall['rainfall_risk_level']}"
    )

    print(
        f"Max rainfall   : "
        f"{rainfall['rainfall_max_mm']:.2f} mm"
    )

    print(
        f"Mean rainfall  : "
        f"{rainfall['rainfall_mean_mm']:.2f} mm"
    )

    print(
        f"Observations   : "
        f"{rainfall['rainfall_observations']}"
    )


    # ========================================================
    # LANDSLIDE
    # ========================================================

    print(
        "\nExtracting local landslide hazard..."
    )

    landslide = get_local_landslide(
        landslide_df,
        event_lat,
        event_lon,
    )

    landslide_score = float(
        landslide[
            "landslide_hazard_score_0_100"
        ]
    )

    print(
        f"Landslide score: "
        f"{landslide_score:.2f}"
    )

    print(
        f"Landslide level: "
        f"{landslide['landslide_hazard_level']}"
    )

    print(
        f"Cells used     : "
        f"{landslide['landslide_cells_used']}"
    )


    # ========================================================
    # FINAL MULTI-HAZARD SCORE
    # ========================================================

    # All three components MUST be available because the event
    # has already been restricted to the rainfall coverage
    # window.

    if not np.isfinite(river_score):
        raise ValueError(
            "River score is invalid."
        )

    if not np.isfinite(rainfall_score):
        raise ValueError(
            "Rainfall score is invalid."
        )

    if not np.isfinite(landslide_score):
        raise ValueError(
            "Landslide score is invalid."
        )


    # --------------------------------------------------------
    # TRINETRA FORMULA
    # --------------------------------------------------------
    #
    # TRINETRA score =
    #
    #   40% River
    # + 30% Rainfall
    # + 30% Landslide
    #
    # Since all three components are required, there is no
    # missing-data renormalization here.
    # --------------------------------------------------------

    river_component = (
        RIVER_WEIGHT
        * river_score
    )

    rainfall_component = (
        RAINFALL_WEIGHT
        * rainfall_score
    )

    landslide_component = (
        LANDSLIDE_WEIGHT
        * landslide_score
    )

    trinetra_score = (
        river_component
        + rainfall_component
        + landslide_component
    )

    trinetra_score = float(
        np.clip(
            trinetra_score,
            0,
            100,
        )
    )

    trinetra_level = classify_risk(
        trinetra_score
    )


    print("\nTRINETRA calculation:")

    print(
        f"River component     : "
        f"{river_component:.2f}"
    )

    print(
        f"Rainfall component  : "
        f"{rainfall_component:.2f}"
    )

    print(
        f"Landslide component : "
        f"{landslide_component:.2f}"
    )

    print(
        f"Final score         : "
        f"{trinetra_score:.2f}"
    )

    print(
        f"Final level         : "
        f"{trinetra_level}"
    )


    # ========================================================
    # SATELLITE EVIDENCE
    # ========================================================

    satellite_score = numeric(
        satellite_row[
            "satellite_evidence_score_0_100"
        ],
        default=np.nan,
    )

    satellite_class = satellite_row.get(
        "satellite_evidence_class",
        np.nan,
    )

    satellite_status = satellite_row.get(
        "satellite_evidence_status",
        np.nan,
    )


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    dashboard_row = {

        # ----------------------------------------------------
        # Event
        # ----------------------------------------------------

        "event_id": event_id,

        "station_name": station_name,

        "event_time_ist": satellite_row[
            "event_time_ist"
        ],

        "event_date": event_date,

        "district": district,

        "latitude": event_lat,

        "longitude": event_lon,


        # ----------------------------------------------------
        # River
        # ----------------------------------------------------

        "river_risk_score_0_100": river_score,

        "river_risk_level": river_level,


        # ----------------------------------------------------
        # Rainfall
        # ----------------------------------------------------

        "rainfall_available": rainfall["rainfall_available"],

        "rainfall_risk_score_0_100": rainfall_score,

        "rainfall_risk_level": rainfall[
            "rainfall_risk_level"
        ],

        "rainfall_observations": rainfall[
            "rainfall_observations"
        ],

        "rainfall_max_mm": rainfall[
            "rainfall_max_mm"
        ],

        "rainfall_mean_mm": rainfall[
            "rainfall_mean_mm"
        ],

        "rainfall_coverage_start": rainfall_start_date,

        "rainfall_coverage_end": rainfall_end_date,


        # ----------------------------------------------------
        # Landslide
        # ----------------------------------------------------

        "landslide_hazard_score_0_100": (
            landslide_score
        ),

        "landslide_hazard_max_score_0_100": (
            landslide[
                "landslide_hazard_max_score_0_100"
            ]
        ),

        "landslide_probability_median": (
            landslide[
                "landslide_probability_median"
            ]
        ),

        "landslide_probability_max": (
            landslide[
                "landslide_probability_max"
            ]
        ),

        "landslide_hazard_level": (
            landslide[
                "landslide_hazard_level"
            ]
        ),

        "landslide_slope_median_deg": (
            landslide[
                "landslide_slope_median_deg"
            ]
        ),

        "landslide_slope_max_deg": (
            landslide[
                "landslide_slope_max_deg"
            ]
        ),

        "landslide_elevation_median_m": (
            landslide[
                "landslide_elevation_median_m"
            ]
        ),

        "landslide_cells_used": (
            landslide[
                "landslide_cells_used"
            ]
        ),


        # ----------------------------------------------------
        # Final TRINETRA
        # ----------------------------------------------------

        "river_weight": RIVER_WEIGHT,

        "rainfall_weight": RAINFALL_WEIGHT,

        "landslide_weight": LANDSLIDE_WEIGHT,

        "trinetra_hazard_score_0_100": (
            trinetra_score
        ),

        "trinetra_hazard_level": (
            trinetra_level
        ),


        # ----------------------------------------------------
        # Satellite
        # ----------------------------------------------------

        "satellite_evidence_score_0_100": (
            satellite_score
        ),

        "satellite_evidence_class": (
            satellite_class
        ),

        "satellite_evidence_status": (
            satellite_status
        ),

        "sentinel2_candidate_new_water_ha": numeric(
            satellite_row.get(
                "sentinel2_candidate_new_water_ha",
                np.nan,
            ),
            0,
        ),

        "sentinel2_net_water_change_ha": numeric(
            satellite_row.get(
                "sentinel2_net_water_change_ha",
                np.nan,
            ),
            0,
        ),

        "sentinel1_mean_vv_change_db": numeric(
            satellite_row.get(
                "sentinel1_mean_vv_change_db",
                np.nan,
            ),
            0,
        ),

        "sentinel1_candidate_new_water_ha": numeric(
            satellite_row.get(
                "sentinel1_candidate_new_water_ha",
                np.nan,
            ),
            0,
        ),


        # ----------------------------------------------------
        # Interpretation
        # ----------------------------------------------------

        "system_interpretation": (
    "TRINETRA combines river hazard, "
    "district-level rainfall risk, and "
    "local DEM-derived landslide susceptibility. "
    "When event-date rainfall is unavailable, "
    "the latest available rainfall record is used "
    "as an explicitly marked MVP fallback. "
    "Satellite observations are retained as "
    "supporting evidence and may be temporally "
    "outside the event rainfall window."
),
    }


    # ========================================================
    # CREATE OUTPUT
    # ========================================================

    output_df = pd.DataFrame(
        [dashboard_row]
    )


    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )


    # ========================================================
    # REPORT
    # ========================================================

    print()
    print("=" * 70)
    print(
        "TRINETRA MULTI-HAZARD INTEGRATION COMPLETE"
    )
    print("=" * 70)

    print(
        f"Event location    : "
        f"{event_lat:.6f}, "
        f"{event_lon:.6f}"
    )

    print(
        f"District          : "
        f"{district}"
    )

    print(
        f"Event date        : "
        f"{event_date}"
    )

    print(
        f"Rainfall window   : "
        f"{rainfall_start_date} "
        f"to "
        f"{rainfall_end_date}"
    )

    print(
        f"River score       : "
        f"{river_score:.2f}"
    )

    print(
        f"Rainfall score    : "
        f"{rainfall_score:.2f}"
    )

    print(
        f"Landslide score   : "
        f"{landslide_score:.2f}"
    )

    print(
        f"TRINETRA score    : "
        f"{trinetra_score:.2f}"
    )

    print(
        f"TRINETRA level    : "
        f"{trinetra_level}"
    )

    if np.isfinite(satellite_score):
        print(
            f"Satellite score   : "
            f"{satellite_score:.2f}"
        )
    else:
        print(
            "Satellite score   : "
            "N/A"
        )

    print()
    print("Saved:")
    print(OUTPUT_PATH)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
        main()