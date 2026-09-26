from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

FEATURES_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_features.csv"
)

FORECAST_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_forecast_predictions.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_risk.csv"
)

REFERENCE_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_reference_thresholds.csv"
)


# ============================================================
# COLUMNS
# ============================================================

TIME_COL = "Data Acquisition Time"
STATION_COL = "Station"

COL_1H = "rainfall_mm_1h"
COL_6H = "rainfall_mm_6h"
COL_24H = "rainfall_mm_24h"
COL_15D = "antecedent_rainfall_mm_15d"

FORECAST_COL = "predicted_rainfall_6h"


# ============================================================
# SCORING FUNCTIONS
# ============================================================

def score_1h(value):
    """
    1-hour rainfall intensity score.

    <10       -> 10
    10-<30    -> 40
    30-<60    -> 70
    60-<100   -> 85
    >=100     -> 100
    """

    if pd.isna(value):
        return np.nan

    if value < 10:
        return 10.0
    elif value < 30:
        return 40.0
    elif value < 60:
        return 70.0
    elif value < 100:
        return 85.0
    else:
        return 100.0


def score_accumulation(
    value,
    q75,
    q90,
    q95
):
    """
    6-hour / 24-hour accumulation score.

    <= q75 -> 20
    <= q90 -> 50
    <= q95 -> 75
    > q95  -> 95
    """

    if pd.isna(value):
        return np.nan

    if value <= q75:
        return 20.0
    elif value <= q90:
        return 50.0
    elif value <= q95:
        return 75.0
    else:
        return 95.0


def score_antecedent(
    value,
    q75,
    q90,
    q95
):
    """
    15-day antecedent rainfall / wetness-proxy score.

    <= q75 -> 15
    <= q90 -> 45
    <= q95 -> 70
    > q95  -> 90
    """

    if pd.isna(value):
        return np.nan

    if value <= q75:
        return 15.0
    elif value <= q90:
        return 45.0
    elif value <= q95:
        return 70.0
    else:
        return 90.0


def score_forecast(
    value,
    q75,
    q90,
    q95
):
    """
    Next-6-hour rainfall forecast score.

    <= q75 -> 10
    <= q90 -> 40
    <= q95 -> 70
    > q95  -> 100

    Missing forecast remains unavailable.
    """

    if pd.isna(value):
        return np.nan

    if value <= q75:
        return 10.0
    elif value <= q90:
        return 40.0
    elif value <= q95:
        return 70.0
    else:
        return 100.0


def risk_category(score):
    """
    Rainfall risk category.

    <30       LOW
    30-<60    MODERATE
    60-<80    HIGH
    >=80      CRITICAL
    """

    if pd.isna(score):
        return "PARTIAL"

    if score < 30:
        return "LOW"
    elif score < 60:
        return "MODERATE"
    elif score < 80:
        return "HIGH"
    else:
        return "CRITICAL"


# ============================================================
# LOAD RAINFALL FEATURES
# ============================================================

print("Loading rainfall features...")

df = pd.read_csv(
    FEATURES_PATH,
    parse_dates=[TIME_COL]
)

print(
    f"Records: {len(df)}"
)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

for col in [
    COL_1H,
    COL_6H,
    COL_24H,
    COL_15D,
]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# ============================================================
# LOAD FORECAST PREDICTIONS
# ============================================================

print(
    "\nLoading 6-hour rainfall forecasts..."
)

if FORECAST_PATH.exists():

    forecast_df = pd.read_csv(
        FORECAST_PATH,
        parse_dates=[TIME_COL]
    )

    print(
        f"Forecast records: {len(forecast_df)}"
    )

    if FORECAST_COL not in forecast_df.columns:

        raise ValueError(
            f"Required forecast column "
            f"'{FORECAST_COL}' not found."
        )

    forecast_df[FORECAST_COL] = pd.to_numeric(
        forecast_df[FORECAST_COL],
        errors="coerce"
    )

    # Keep only the forecast information needed
    # to merge with rainfall observations.
    forecast_df = forecast_df[
        [
            STATION_COL,
            TIME_COL,
            FORECAST_COL
        ]
    ].drop_duplicates(
        subset=[
            STATION_COL,
            TIME_COL
        ],
        keep="last"
    )

    df = df.merge(
        forecast_df,
        on=[
            STATION_COL,
            TIME_COL
        ],
        how="left"
    )

else:

    print(
        "Forecast file not found."
    )

    # Forecast remains unavailable.
    df[FORECAST_COL] = np.nan


# ============================================================
# FROZEN STATION-SPECIFIC REFERENCE THRESHOLDS
# ============================================================
#
# The formula specification calls for frozen,
# station-specific reference percentiles.
#
# If the reference file already exists, reuse it.
# Otherwise create it once from the currently available
# historical processed rainfall data.
#
# This prevents thresholds from changing every time the
# operational risk script is executed.
# ============================================================

REFERENCE_FEATURES = [
    COL_6H,
    COL_24H,
    COL_15D,
]


def build_reference_thresholds():

    rows = []

    for station, station_df in df.groupby(
        STATION_COL
    ):

        row = {
            STATION_COL: station
        }

        for feature in REFERENCE_FEATURES:

            values = station_df[
                feature
            ].dropna()

            if len(values) == 0:

                row[f"{feature}_q75"] = np.nan
                row[f"{feature}_q90"] = np.nan
                row[f"{feature}_q95"] = np.nan

            else:

                row[f"{feature}_q75"] = (
                    values.quantile(0.75)
                )

                row[f"{feature}_q90"] = (
                    values.quantile(0.90)
                )

                row[f"{feature}_q95"] = (
                    values.quantile(0.95)
                )

        rows.append(row)

    return pd.DataFrame(rows)


if REFERENCE_PATH.exists():

    print(
        "\nLoading frozen rainfall "
        "reference thresholds..."
    )

    reference_df = pd.read_csv(
        REFERENCE_PATH
    )

else:

    print(
        "\nCreating frozen rainfall "
        "reference thresholds..."
    )

    reference_df = (
        build_reference_thresholds()
    )

    REFERENCE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    reference_df.to_csv(
        REFERENCE_PATH,
        index=False
    )

    print(
        f"Reference thresholds saved to:"
    )

    print(
        REFERENCE_PATH
    )


# ============================================================
# MERGE REFERENCE THRESHOLDS
# ============================================================

df = df.merge(
    reference_df,
    on=STATION_COL,
    how="left"
)


# ============================================================
# COMPONENT SCORES
# ============================================================

# ------------------------------------------------------------
# 1-HOUR
# ------------------------------------------------------------

df["rainfall_score_1h"] = (
    df[COL_1H]
    .apply(score_1h)
)


# ------------------------------------------------------------
# 6-HOUR
# ------------------------------------------------------------

df["rainfall_score_6h"] = [
    score_accumulation(
        value,
        q75,
        q90,
        q95
    )
    for value, q75, q90, q95
    in zip(
        df[COL_6H],
        df[f"{COL_6H}_q75"],
        df[f"{COL_6H}_q90"],
        df[f"{COL_6H}_q95"]
    )
]


# ------------------------------------------------------------
# 24-HOUR
# ------------------------------------------------------------

df["rainfall_score_24h"] = [
    score_accumulation(
        value,
        q75,
        q90,
        q95
    )
    for value, q75, q90, q95
    in zip(
        df[COL_24H],
        df[f"{COL_24H}_q75"],
        df[f"{COL_24H}_q90"],
        df[f"{COL_24H}_q95"]
    )
]


# ------------------------------------------------------------
# 15-DAY ANTECEDENT
# ------------------------------------------------------------

df["rainfall_score_15d"] = [
    score_antecedent(
        value,
        q75,
        q90,
        q95
    )
    for value, q75, q90, q95
    in zip(
        df[COL_15D],
        df[f"{COL_15D}_q75"],
        df[f"{COL_15D}_q90"],
        df[f"{COL_15D}_q95"]
    )
]


# ------------------------------------------------------------
# 6-HOUR FORECAST
# ------------------------------------------------------------
#
# Forecast is compared against historical 6-hour
# rainfall reference thresholds.
# ------------------------------------------------------------

df["rainfall_score_forecast_6h"] = [
    score_forecast(
        value,
        q75,
        q90,
        q95
    )
    for value, q75, q90, q95
    in zip(
        df[FORECAST_COL],
        df[f"{COL_6H}_q75"],
        df[f"{COL_6H}_q90"],
        df[f"{COL_6H}_q95"]
    )
]


# ============================================================
# COMPLETE RAINFALL SCORE
# ============================================================

COMPONENTS = [
    "rainfall_score_1h",
    "rainfall_score_6h",
    "rainfall_score_24h",
    "rainfall_score_15d",
    "rainfall_score_forecast_6h",
]

all_components_available = (
    df[COMPONENTS]
    .notna()
    .all(axis=1)
)


# ============================================================
# WEIGHTED RAINFALL HAZARD W
# ============================================================

df["rainfall_risk_score"] = np.nan

df.loc[
    all_components_available,
    "rainfall_risk_score"
] = (
    0.35 * df.loc[
        all_components_available,
        "rainfall_score_1h"
    ]
    + 0.20 * df.loc[
        all_components_available,
        "rainfall_score_6h"
    ]
    + 0.15 * df.loc[
        all_components_available,
        "rainfall_score_24h"
    ]
    + 0.20 * df.loc[
        all_components_available,
        "rainfall_score_15d"
    ]
    + 0.10 * df.loc[
        all_components_available,
        "rainfall_score_forecast_6h"
    ]
)


# ============================================================
# STATUS
# ============================================================

df["rainfall_risk_status"] = np.where(
    all_components_available,
    "COMPLETE",
    "PARTIAL"
)


# ============================================================
# RISK CATEGORY
# ============================================================

df["rainfall_risk_category"] = (
    df["rainfall_risk_score"]
    .apply(risk_category)
)


# ============================================================
# EXTREME RAINFALL FLAG
# ============================================================

df["extreme_rainfall_flag"] = (
    df[COL_1H] >= 100
)


# ============================================================
# EXTREME RAINFALL STATUS
# ============================================================

df["rainfall_alert_status"] = np.select(
    [
        df[COL_1H] >= 100,
        df[COL_1H] >= 70,
        df[COL_1H] >= 40,
    ],
    [
        "CLOUDBURST_THRESHOLD_REACHED",
        "CLOUDBURST_WATCH",
        "HEAVY_RAINFALL_ALERT",
    ],
    default="NORMAL"
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print(
    "\n======================================"
)

print(
    "RAINFALL RISK PROCESSING COMPLETE"
)

print(
    "======================================"
)

print(
    f"Records: {len(df)}"
)


print(
    "\nComponent availability:"
)

for col in [
    COL_1H,
    COL_6H,
    COL_24H,
    COL_15D,
    FORECAST_COL,
]:

    print(
        f"{col}: "
        f"{df[col].notna().sum()}/{len(df)}"
    )


print(
    "\nComponent score availability:"
)

for col in COMPONENTS:

    print(
        f"{col}: "
        f"{df[col].notna().sum()}/{len(df)}"
    )


print(
    "\nRisk status:"
)

print(
    df[
        "rainfall_risk_status"
    ]
    .value_counts(
        dropna=False
    )
    .to_string()
)


print(
    "\nRisk category:"
)

print(
    df[
        "rainfall_risk_category"
    ]
    .value_counts(
        dropna=False
    )
    .to_string()
)


print(
    "\nExtreme rainfall:"
)

print(
    df[
        "extreme_rainfall_flag"
    ]
    .value_counts()
    .to_string()
)


print(
    "\nAlert status:"
)

print(
    df[
        "rainfall_alert_status"
    ]
    .value_counts()
    .to_string()
)


print(
    "\nComplete rainfall scores:"
)

complete = df[
    df["rainfall_risk_score"].notna()
]

if len(complete) > 0:

    print(
        complete[
            [
                STATION_COL,
                TIME_COL,
                "rainfall_risk_score",
                "rainfall_risk_category",
                "rainfall_alert_status",
            ]
        ]
        .tail(20)
        .to_string(
            index=False
        )
    )

else:

    print(
        "No complete rainfall scores "
        "available."
    )


print(
    f"\nSaved to:"
)

print(
    OUTPUT_PATH
)

print(
    f"\nFrozen reference thresholds:"
)

print(
    REFERENCE_PATH
)