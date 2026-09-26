from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_features.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "terrain_risk.csv"
)


# ---------------------------------------------------------
# PERCENTILE HELPERS
# ---------------------------------------------------------

def percentile_thresholds(series):
    """
    Calculate local terrain percentile thresholds.
    """
    clean = series.dropna()

    return {
        "p50": clean.quantile(0.50),
        "p75": clean.quantile(0.75),
        "p90": clean.quantile(0.90),
    }


# ---------------------------------------------------------
# SLOPE SCORE
#
# Formula sheet:
# <15  -> 10
# <25  -> 40
# <35  -> 70
# <45  -> 90
# >=45 -> 100
# ---------------------------------------------------------

def score_slope(value):

    if value < 15:
        return 10
    elif value < 25:
        return 40
    elif value < 35:
        return 70
    elif value < 45:
        return 90
    else:
        return 100


# ---------------------------------------------------------
# TWI SCORE
#
# Formula sheet specifies corridor-specific thresholds.
# Since no fixed numeric TWI thresholds are supplied,
# use local percentile thresholds.
#
# p50 -> 15
# p75 -> 45
# p90 -> 75
# >p90 -> 90
# ---------------------------------------------------------

def score_twi(value, thresholds):

    if value <= thresholds["p50"]:
        return 15
    elif value <= thresholds["p75"]:
        return 45
    elif value <= thresholds["p90"]:
        return 75
    else:
        return 90


# ---------------------------------------------------------
# SPI SCORE
#
# p50 -> 15
# p75 -> 45
# p90 -> 75
# >p90 -> 90
# ---------------------------------------------------------

def score_spi(value, thresholds):

    if value <= thresholds["p50"]:
        return 15
    elif value <= thresholds["p75"]:
        return 45
    elif value <= thresholds["p90"]:
        return 75
    else:
        return 90


# ---------------------------------------------------------
# CURVATURE SCORE
#
# Formula sheet:
#
# curvature < -0.5 -> 80
# curvature >  0.5 -> 40
# otherwise        -> 55
# ---------------------------------------------------------

def score_curvature(value):

    if value < -0.5:
        return 80
    elif value > 0.5:
        return 40
    else:
        return 55


# ---------------------------------------------------------
# RUGGEDNESS SCORE
#
# p50 -> 15
# p75 -> 45
# p90 -> 75
# >p90 -> 90
# ---------------------------------------------------------

def score_ruggedness(value, thresholds):

    if value <= thresholds["p50"]:
        return 15
    elif value <= thresholds["p75"]:
        return 45
    elif value <= thresholds["p90"]:
        return 75
    else:
        return 90


# ---------------------------------------------------------
# COMMON RISK CATEGORY
# ---------------------------------------------------------

def risk_category(score):

    if score < 30:
        return "LOW"

    elif score < 60:
        return "MODERATE"

    elif score < 80:
        return "HIGH"

    else:
        return "CRITICAL"


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("Loading terrain features...")

    terrain = pd.read_csv(INPUT_PATH)

    print(f"Rows loaded: {len(terrain):,}")

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "twi",
        "spi",
        "ruggedness",
    ]

    missing = [
        column
        for column in required_columns
        if column not in terrain.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # -----------------------------------------------------
    # CLEAN NUMERIC DATA
    # -----------------------------------------------------

    numeric_columns = [
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "twi",
        "spi",
        "ruggedness",
    ]

    for column in numeric_columns:

        terrain[column] = pd.to_numeric(
            terrain[column],
            errors="coerce"
        )

    terrain = terrain.dropna(
        subset=numeric_columns
    ).copy()

    print(
        f"Rows after cleaning: {len(terrain):,}"
    )

    # -----------------------------------------------------
    # LOCAL PERCENTILE THRESHOLDS
    # -----------------------------------------------------

    twi_thresholds = percentile_thresholds(
        terrain["twi"]
    )

    spi_thresholds = percentile_thresholds(
        terrain["spi"]
    )

    ruggedness_thresholds = percentile_thresholds(
        terrain["ruggedness"]
    )

    print("\n========== TERRAIN THRESHOLDS ==========")

    print(
        "TWI:",
        twi_thresholds
    )

    print(
        "SPI:",
        spi_thresholds
    )

    print(
        "Ruggedness:",
        ruggedness_thresholds
    )

    # -----------------------------------------------------
    # COMPONENT SCORES
    # -----------------------------------------------------

    terrain["slope_score"] = (
        terrain["slope"]
        .apply(score_slope)
    )

    terrain["twi_score"] = terrain["twi"].apply(
        lambda x: score_twi(
            x,
            twi_thresholds
        )
    )

    terrain["spi_score"] = terrain["spi"].apply(
        lambda x: score_spi(
            x,
            spi_thresholds
        )
    )

    terrain["curvature_score"] = (
        terrain["curvature"]
        .apply(score_curvature)
    )

    terrain["ruggedness_score"] = (
        terrain["ruggedness"]
        .apply(
            lambda x: score_ruggedness(
                x,
                ruggedness_thresholds
            )
        )
    )

    # -----------------------------------------------------
    # TERRAIN RISK FORMULA
    #
    # T =
    # 0.35*SLOPE
    # + 0.20*TWI
    # + 0.20*SPI
    # + 0.15*CURVATURE
    # + 0.10*RUGGEDNESS
    # -----------------------------------------------------

    terrain["terrain_risk_score"] = (
        0.35 * terrain["slope_score"]
        + 0.20 * terrain["twi_score"]
        + 0.20 * terrain["spi_score"]
        + 0.15 * terrain["curvature_score"]
        + 0.10 * terrain["ruggedness_score"]
    ).round(2)

    # -----------------------------------------------------
    # COMMON RISK CATEGORY
    # -----------------------------------------------------

    terrain["terrain_risk_level"] = (
        terrain["terrain_risk_score"]
        .apply(risk_category)
    )

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    output_columns = [
        "cell_id",
        "lat",
        "lon",
        "elevation",
        "slope",
        "aspect",
        "curvature",
        "flow_accumulation",
        "twi",
        "spi",
        "ruggedness",
        "slope_score",
        "twi_score",
        "spi_score",
        "curvature_score",
        "ruggedness_score",
        "terrain_risk_score",
        "terrain_risk_level",
    ]

    terrain = terrain[
        output_columns
    ]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    terrain.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("TERRAIN RISK COMPLETE")
    print("=" * 60)

    print(
        f"Rows: {len(terrain):,}"
    )

    print(
        f"Risk score range: "
        f"{terrain['terrain_risk_score'].min():.2f} "
        f"to "
        f"{terrain['terrain_risk_score'].max():.2f}"
    )

    print("\nRisk distribution:")

    print(
        terrain["terrain_risk_level"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nComponent score ranges:")

    for column in [
        "slope_score",
        "twi_score",
        "spi_score",
        "curvature_score",
        "ruggedness_score",
    ]:

        print(
            f"{column}: "
            f"{terrain[column].min():.2f} "
            f"to "
            f"{terrain[column].max():.2f}"
        )

    print("\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()