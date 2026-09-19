from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "dem_landslide_integrated_features.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "features"
    / "landslide_hazard_features.csv"
)


def risk_level(score):

    if score >= 99:
        return "CRITICAL"

    elif score >= 90:
        return "HIGH"

    elif score >= 50:
        return "MODERATE"

    return "LOW"


def main():

    print("=" * 65)
    print("BUILDING LANDSLIDE HAZARD LAYER")
    print("=" * 65)

    # ---------------------------------------------------------
    # Load integrated data
    # ---------------------------------------------------------

    print("\nLoading DEM + landslide data...")

    df = pd.read_csv(INPUT_PATH)

    print("Rows:", len(df))

    # ---------------------------------------------------------
    # Required columns
    # ---------------------------------------------------------

    required_columns = [
        "cell_id",
        "lat",
        "lon",
        "landslide_probability",
        "landslide_susceptibility_score",
        "landslide_susceptibility_level",
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

    # ---------------------------------------------------------
    # Numeric conversion
    # ---------------------------------------------------------

    numeric_columns = [
        "lat",
        "lon",
        "landslide_probability",
        "landslide_susceptibility_score",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=numeric_columns
    ).copy()

    # ---------------------------------------------------------
    # Standardized hazard score
    # ---------------------------------------------------------
    #
    # The existing susceptibility score is already 0-100.
    # We therefore do NOT create another mathematical model.
    #

    df["hazard_score"] = (
        df["landslide_susceptibility_score"]
        .clip(0, 100)
        .round(2)
    )

    # ---------------------------------------------------------
    # Standardized risk level
    # ---------------------------------------------------------

    df["risk_level"] = (
        df["landslide_susceptibility_level"]
    )

    # ---------------------------------------------------------
    # Hazard source
    # ---------------------------------------------------------

    df["hazard_source"] = "LANDSLIDE_AI"

    # ---------------------------------------------------------
    # Final output
    # ---------------------------------------------------------

    output_columns = [
        "cell_id",
        "lat",
        "lon",

        "landslide_probability",
        "landslide_susceptibility_score",
        "landslide_susceptibility_level",

        "hazard_score",
        "risk_level",

        "hazard_source",
    ]

    output = df[
        output_columns
    ].copy()

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    print("\n" + "=" * 65)
    print("LANDSLIDE HAZARD LAYER COMPLETE")
    print("=" * 65)

    print("Rows:", len(output))

    print("\nHazard score statistics:")
    print(
        output["hazard_score"]
        .describe()
        .to_string()
    )

    print("\nRisk-level distribution:")
    print(
        output["risk_level"]
        .value_counts()
        .to_string()
    )

    print("\nHazard source:")
    print(
        output["hazard_source"]
        .value_counts()
        .to_string()
    )

    print("\nSaved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
