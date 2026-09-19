from pathlib import Path

import pandas as pd
import numpy as np


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_predictions.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_susceptibility.csv"
)


# =========================================================
# LOAD
# =========================================================

print("=" * 70)
print("BUILDING LANDSLIDE SUSCEPTIBILITY LAYER")
print("=" * 70)

df = pd.read_csv(
    INPUT_PATH
)

print(
    "\nRows:",
    len(df)
)


# =========================================================
# VALIDATE
# =========================================================

required_columns = [
    "cell_id",
    "lat",
    "lon",
    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation",
    "landslide_probability",
]


missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:

    raise ValueError(
        f"Missing required columns: {missing}"
    )


# =========================================================
# CLEAN PROBABILITY
# =========================================================

df["landslide_probability"] = (
    pd.to_numeric(
        df["landslide_probability"],
        errors="coerce"
    )
)

df = df.dropna(
    subset=[
        "landslide_probability"
    ]
).copy()


# =========================================================
# CLIP INVALID VALUES
# =========================================================

df["landslide_probability"] = (
    df["landslide_probability"]
    .clip(
        lower=0.0,
        upper=1.0
    )
)


# =========================================================
# AOI PERCENTILE
# =========================================================
#
# This is NOT a calibrated probability.
#
# It represents the relative position of a cell within
# the current model's susceptibility distribution.
# =========================================================

df["landslide_percentile"] = (
    df["landslide_probability"]
    .rank(
        method="average",
        pct=True
    )
    * 100
)


# =========================================================
# SUSCEPTIBILITY SCORE
# =========================================================
#
# 0–100 relative susceptibility score.
#
# 100 = highest predicted susceptibility in this AOI.
#
# It does NOT mean a 100% probability of landslide.
# =========================================================

df["landslide_susceptibility_score"] = (
    df["landslide_percentile"]
    .round(2)
)


# =========================================================
# LEVEL
# =========================================================
#
# Percentile-based classes.
#
# LOW:
#     bottom 50%
#
# MODERATE:
#     50th–90th percentile
#
# HIGH:
#     90th–99th percentile
#
# CRITICAL:
#     top 1%
# =========================================================

def susceptibility_level(percentile):

    if percentile >= 99:

        return "CRITICAL"

    elif percentile >= 90:

        return "HIGH"

    elif percentile >= 50:

        return "MODERATE"

    else:

        return "LOW"


df["landslide_susceptibility_level"] = (
    df["landslide_percentile"]
    .apply(
        susceptibility_level
    )
)


# =========================================================
# SOURCE
# =========================================================

df["susceptibility_source"] = (
    "Random Forest + DEM terrain"
)


# =========================================================
# FINAL COLUMNS
# =========================================================

output_columns = [
    "cell_id",
    "lat",
    "lon",

    "elevation",
    "slope",
    "aspect",
    "curvature",
    "flow_accumulation",

    "landslide_probability",

    "landslide_percentile",

    "landslide_susceptibility_score",

    "landslide_susceptibility_level",

    "susceptibility_source",
]


df = df[
    output_columns
]


# =========================================================
# SAVE
# =========================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# =========================================================
# SUMMARY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "LANDSLIDE SUSCEPTIBILITY COMPLETE"
)

print(
    "=" * 70
)

print(
    "\nRows:",
    len(df)
)


print(
    "\nSusceptibility distribution:"
)

print(
    df[
        "landslide_susceptibility_level"
    ]
    .value_counts()
    .to_string()
)


print(
    "\nScore statistics:"
)

print(
    df[
        "landslide_susceptibility_score"
    ]
    .describe()
    .round(2)
    .to_string()
)


print(
    "\nHighest susceptibility cells:"
)

print(
    df.nlargest(
        20,
        "landslide_susceptibility_score"
    )[
        [
            "cell_id",
            "lat",
            "lon",
            "landslide_probability",
            "landslide_susceptibility_score",
            "landslide_susceptibility_level",
        ]
    ]
    .to_string(
        index=False
    )
)


print(
    "\nSaved:"
)

print(
    OUTPUT_PATH
)

print(
    "\nDONE."
)