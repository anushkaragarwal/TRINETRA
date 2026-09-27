"""
TRINETRA - MASTER PIPELINE RUNNER

Runs the complete canonical TRINETRA data/model pipeline
in dependency order.

Usage:

    python scripts/run_full_pipeline.py

The pipeline stops immediately if any stage fails.
"""

from pathlib import Path
import subprocess
import sys
import time


# ============================================================
# ROOT
# ============================================================

ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# CONFIGURATION
# ============================================================

PYTHON = sys.executable


# ============================================================
# PIPELINE STEPS
# ============================================================

PIPELINE = [

    # --------------------------------------------------------
    # RIVER PIPELINE
    # --------------------------------------------------------

    (
        "RIVER 1/6 - Fetch fresh CWC/NWDP data",
        "scripts/fetch_river.py",
    ),

    (
        "RIVER 2/6 - Process river data",
        "scripts/process_river.py",
    ),

    (
        "RIVER 3/6 - Train river anomaly model",
        "scripts/train_river_anomaly_model.py",
    ),

    (
        "RIVER 4/6 - Train river forecast model",
        "scripts/train_river_forecast_model.py",
    ),

    (
        "RIVER 5/6 - Calculate river risk score",
        "scripts/risk_score.py",
    ),

    (
        "RIVER 6/6 - Build river hybrid hazard",
        "scripts/build_hybrid_hazard.py",
    ),


    # --------------------------------------------------------
    # RAINFALL PIPELINE
    # --------------------------------------------------------

    (
        "RAINFALL 1/5 - Fetch fresh rainfall data",
        "scripts/fetch_rainfall.py",
    ),

    (
        "RAINFALL 2/5 - Process rainfall data",
        "scripts/process_rainfall.py",
    ),

    (
        "RAINFALL 3/5 - Train rainfall anomaly model",
        "scripts/train_rainfall_anomaly_model.py",
    ),

    (
        "RAINFALL 4/5 - Train rainfall forecast model",
        "scripts/train_rainfall_forecast_model.py",
    ),

    (
        "RAINFALL 5/5 - Calculate rainfall risk",
        "scripts/rainfall_risk_score.py",
    ),


    # --------------------------------------------------------
    # TERRAIN / DEM PIPELINE
    # --------------------------------------------------------

    (
        "TERRAIN 1/3 - Build terrain features",
        "src/dem/terrain_features.py",
    ),

    (
        "TERRAIN 2/3 - Calculate terrain risk",
        "src/dem/terrain_risk.py",
    ),

    (
        "TERRAIN 3/3 - Build terrain hazard layer",
        "src/dem/terrain_hazard.py",
    ),


    # --------------------------------------------------------
    # LANDSLIDE PIPELINE
    # --------------------------------------------------------

    (
        "LANDSLIDE - Build landslide hazard layer",
        "src/landslides/build_landslide_hazard.py",
    ),


    # --------------------------------------------------------
    # FINAL TRINETRA INTEGRATION
    # --------------------------------------------------------

    (
        "FINAL - Build TRINETRA event dashboard output",
        "scripts/build_final_trinetra_event_output.py",
    ),
]


# ============================================================
# OUTPUTS TO VALIDATE
# ============================================================

EXPECTED_OUTPUTS = [

    # River
    ROOT / "data/river/raw/cwc_uttarakhand_raw.csv",
    ROOT / "data/river/processed/river_features.csv",
    ROOT / "data/river/processed/river_anomaly_scores.csv",
    ROOT / "data/river/processed/river_forecast_predictions.csv",
    ROOT / "data/river/processed/river_risk.csv",
    ROOT / "data/river/processed/river_hybrid_hazard.csv",

    # Rainfall
    ROOT / "data/rainfall/raw/rainfall_hourly_raw.csv",
    ROOT / "data/rainfall/processed/rainfall_features.csv",
    ROOT / "data/rainfall/processed/rainfall_anomaly_scores.csv",
    ROOT / "data/rainfall/processed/rainfall_forecast_predictions.csv",
    ROOT / "data/rainfall/processed/rainfall_risk.csv",

    # Terrain
    ROOT / "data/features/terrain_features.csv",
    ROOT / "data/features/terrain_risk.csv",
    ROOT / "data/features/terrain_hazard_features.csv",

    # Landslide
    ROOT / "data/features/landslide_hazard_features.csv",

    # Final
    ROOT / "data/outputs/trinetra_event_dashboard_data.csv",
]


# ============================================================
# HELPERS
# ============================================================

def print_header(text):
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)


def run_step(number, total, description, script):

    print_header(
        f"STEP {number}/{total}: {description}"
    )

    script_path = ROOT / script

    if not script_path.exists():
        raise FileNotFoundError(
            f"Required script not found:\n{script_path}"
        )

    print(f"Script : {script_path}")
    print(f"Python : {PYTHON}")
    print()

    start = time.time()

    result = subprocess.run(
        [
            PYTHON,
            str(script_path),
        ],
        cwd=ROOT,
        check=False,
    )

    elapsed = time.time() - start

    if result.returncode != 0:

        print()
        print("=" * 80)
        print("PIPELINE FAILED")
        print("=" * 80)

        print(f"Step     : {description}")
        print(f"Script   : {script}")
        print(f"Exit code: {result.returncode}")
        print(f"Time     : {elapsed:.2f} seconds")

        raise RuntimeError(
            f"Pipeline stopped at: {description}"
        )

    print()
    print(
        f"✅ Completed in {elapsed:.2f} seconds"
    )


def validate_outputs():

    print_header(
        "FINAL OUTPUT VALIDATION"
    )

    missing = []

    for path in EXPECTED_OUTPUTS:

        if path.exists():

            size_mb = (
                path.stat().st_size
                / (1024 * 1024)
            )

            print(
                f"✅ {path.relative_to(ROOT)} "
                f"({size_mb:.2f} MB)"
            )

        else:

            print(
                f"❌ MISSING: "
                f"{path.relative_to(ROOT)}"
            )

            missing.append(path)

    if missing:

        raise RuntimeError(
            "Pipeline completed, but some expected "
            "output files are missing."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print_header(
        "🚀 TRINETRA MASTER PIPELINE"
    )

    print(
        "This will rebuild the dynamic data/model pipeline "
        "from fresh API data."
    )

    print()
    print(
        f"Repository root:\n{ROOT}"
    )

    print()
    print(
        f"Total pipeline stages: {len(PIPELINE)}"
    )

    start_all = time.time()

    try:

        total = len(PIPELINE)

        for index, (description, script) in enumerate(
            PIPELINE,
            start=1,
        ):

            run_step(
                index,
                total,
                description,
                script,
            )

        validate_outputs()

    except Exception as error:

        print()
        print("=" * 80)
        print("❌ TRINETRA PIPELINE FAILED")
        print("=" * 80)
        print(str(error))
        print()

        sys.exit(1)

    elapsed_all = (
        time.time() - start_all
    )

    print_header(
        "🎉 TRINETRA PIPELINE COMPLETED SUCCESSFULLY"
    )

    print(
        f"Total execution time: "
        f"{elapsed_all / 60:.2f} minutes"
    )

    print()
    print(
        "Fresh data → processing → ML models → "
        "risk scores → hazard layers → final integration"
    )

    print()
    print(
        "Final output:"
    )

    print(
        ROOT
        / "data"
        / "outputs"
        / "trinetra_event_dashboard_data.csv"
    )

    print()


if __name__ == "__main__":
    main()
    