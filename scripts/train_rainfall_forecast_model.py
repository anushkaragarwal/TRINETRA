from pathlib import Path
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_features.csv"
)

MODEL_DIR = ROOT / "models"

MODEL_PATH = (
    MODEL_DIR
    / "rainfall_forecast_model.pkl"
)

PREDICTION_PATH = (
    ROOT
    / "data"
    / "rainfall"
    / "processed"
    / "rainfall_forecast_predictions.csv"
)


# ============================================================
# COLUMNS
# ============================================================

TIME_COL = "Data Acquisition Time"
STATION_COL = "Station"

RAIN_1H = "rainfall_mm_1h"
RAIN_15D = "antecedent_rainfall_mm_15d"


# ============================================================
# BUILD NEXT 6-HOUR TARGET
# ============================================================

def build_future_6h_target(station_df):
    """
    Build the target:

        rainfall during the next 6 hours.

    Missing observations are NOT treated as zero.

    A target is valid only when six actual future
    hourly observations exist inside the next 6 hours.
    """

    station_df = (
        station_df
        .sort_values(TIME_COL)
        .copy()
    )

    times = station_df[TIME_COL].to_numpy()
    rainfall = station_df[RAIN_1H].to_numpy()

    targets = np.full(
        len(station_df),
        np.nan
    )

    for i in range(len(station_df)):

        current_time = times[i]

        future_values = []

        for j in range(i + 1, len(station_df)):

            delta_hours = (
                times[j] - current_time
            ) / np.timedelta64(1, "h")

            if delta_hours > 6:
                break

            if (
                delta_hours > 0
                and not pd.isna(rainfall[j])
            ):
                future_values.append(
                    rainfall[j]
                )

        # Exactly six future hourly observations
        # are required for a valid target.
        if len(future_values) == 6:
            targets[i] = sum(future_values)

    station_df[
        "forecast_target_6h"
    ] = targets

    return station_df


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading rainfall features...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Rainfall feature file not found:\n"
            f"{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[TIME_COL]
    )

    print(
        f"Raw records: {len(df)}"
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = (
        df
        .sort_values(
            [STATION_COL, TIME_COL]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    df[RAIN_1H] = pd.to_numeric(
        df[RAIN_1H],
        errors="coerce"
    )

    df[RAIN_15D] = pd.to_numeric(
        df[RAIN_15D],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Build target station-wise
    # --------------------------------------------------------

    station_results = []

    for station, station_df in df.groupby(
        STATION_COL,
        sort=False
    ):

        print(
            f"Building 6h target: {station}"
        )

        station_result = (
            build_future_6h_target(
                station_df
            )
        )

        station_results.append(
            station_result
        )

    df = pd.concat(
        station_results,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Calendar features
    # --------------------------------------------------------

    df["hour"] = (
        df[TIME_COL].dt.hour
    )

    df["day_of_year"] = (
        df[TIME_COL].dt.dayofyear
    )

    df["month"] = (
        df[TIME_COL].dt.month
    )

    # --------------------------------------------------------
    # Forecast features
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # Do not use rainfall_mm_6h or rainfall_mm_24h here.
    #
    # Those features are frequently unavailable because
    # the source API has large temporal gaps.
    #
    # The model therefore uses features that can actually
    # exist at the current/latest observation.
    # --------------------------------------------------------

    feature_columns = [
        RAIN_1H,
        RAIN_15D,
        "hour",
        "day_of_year",
        "month",
    ]

    print("\nModel features:")

    for feature in feature_columns:
        print(
            f"  - {feature}"
        )

    # --------------------------------------------------------
    # Training data
    # --------------------------------------------------------

    model_data = (
        df
        .dropna(
            subset=(
                feature_columns
                + ["forecast_target_6h"]
            )
        )
        .copy()
    )

    print(
        "\nValid 6-hour targets:",
        df[
            "forecast_target_6h"
        ].notna().sum()
    )

    print(
        "Usable training rows:",
        len(model_data)
    )

    if len(model_data) < 20:

        raise RuntimeError(
            "\nNot enough valid training samples.\n"
            f"Only {len(model_data)} rows available."
        )

    # --------------------------------------------------------
    # Chronological split
    # --------------------------------------------------------

    model_data = (
        model_data
        .sort_values(TIME_COL)
        .reset_index(drop=True)
    )

    split_index = int(
        len(model_data) * 0.80
    )

    train = (
        model_data
        .iloc[:split_index]
        .copy()
    )

    test = (
        model_data
        .iloc[split_index:]
        .copy()
    )

    X_train = train[
        feature_columns
    ]

    y_train = train[
        "forecast_target_6h"
    ]

    X_test = test[
        feature_columns
    ]

    y_test = test[
        "forecast_target_6h"
    ]

    print(
        "\nTraining samples:",
        len(train)
    )

    print(
        "Testing samples:",
        len(test)
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    print(
        "\nTraining next-6-hour rainfall "
        "forecast model..."
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Test prediction
    # --------------------------------------------------------

    test[
        "predicted_rainfall_6h"
    ] = model.predict(
        X_test
    )

    test[
        "predicted_rainfall_6h"
    ] = (
        test[
            "predicted_rainfall_6h"
        ]
        .clip(lower=0)
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        test[
            "predicted_rainfall_6h"
        ]
    )

    rmse = mean_squared_error(
        y_test,
        test[
            "predicted_rainfall_6h"
        ]
    ) ** 0.5

    r2 = r2_score(
        y_test,
        test[
            "predicted_rainfall_6h"
        ]
    )

    print(
        "\n======================================"
    )

    print(
        "6-HOUR RAINFALL FORECAST EVALUATION"
    )

    print(
        "======================================"
    )

    print(
        f"MAE  : {mae:.2f} mm"
    )

    print(
        f"RMSE : {rmse:.2f} mm"
    )

    print(
        f"R²   : {r2:.3f}"
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": (
            model.feature_importances_
        )
    }).sort_values(
        "importance",
        ascending=False
    )

    print(
        "\nFeature importance:"
    )

    print(
        importance.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Operational forecast
    # --------------------------------------------------------

    print(
        "\nGenerating operational "
        "6-hour forecast..."
    )

    latest_rows = (
        df
        .sort_values(
            [STATION_COL, TIME_COL]
        )
        .groupby(
            STATION_COL,
            as_index=False
        )
        .tail(1)
        .copy()
    )

    operational_data = (
        latest_rows
        .dropna(
            subset=feature_columns
        )
        .copy()
    )

    if len(operational_data) > 0:

        operational_data[
            "forecast_rainfall_mm_6h"
        ] = (
            model.predict(
                operational_data[
                    feature_columns
                ]
            )
        )

        operational_data[
            "forecast_rainfall_mm_6h"
        ] = (
            operational_data[
                "forecast_rainfall_mm_6h"
            ]
            .clip(lower=0)
        )

        print(
            "\nOperational forecasts:"
        )

        print(
            operational_data[
                [
                    STATION_COL,
                    TIME_COL,
                    "forecast_rainfall_mm_6h"
                ]
            ].to_string(
                index=False
            )
        )

    else:

        operational_data[
            "forecast_rainfall_mm_6h"
        ] = np.nan

        print(
            "No station has enough valid "
            "current features for forecasting."
        )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        MODEL_PATH,
        "wb"
    ) as file:

        pickle.dump(
            {
                "model": model,
                "feature_columns": feature_columns,
                "target": (
                    "forecast_rainfall_mm_6h"
                )
            },
            file
        )

    # --------------------------------------------------------
    # Save predictions
    # --------------------------------------------------------

    historical_predictions = test[
        [
            STATION_COL,
            TIME_COL,
            "forecast_target_6h",
            "predicted_rainfall_6h"
        ]
    ].copy()

    historical_predictions[
        "prediction_type"
    ] = "historical_test"

    operational_predictions = (
        operational_data[
            [
                STATION_COL,
                TIME_COL,
                "forecast_rainfall_mm_6h"
            ]
        ]
        .rename(
            columns={
                "forecast_rainfall_mm_6h":
                    "predicted_rainfall_6h"
            }
        )
    )

    operational_predictions[
        "forecast_target_6h"
    ] = np.nan

    operational_predictions[
        "prediction_type"
    ] = "operational"

    predictions = pd.concat(
        [
            historical_predictions,
            operational_predictions[
                [
                    STATION_COL,
                    TIME_COL,
                    "forecast_target_6h",
                    "predicted_rainfall_6h",
                    "prediction_type"
                ]
            ]
        ],
        ignore_index=True
    )

    predictions.to_csv(
        PREDICTION_PATH,
        index=False
    )

    print(
        f"\nModel saved:"
    )

    print(
        MODEL_PATH
    )

    print(
        f"\nPredictions saved:"
    )

    print(
        PREDICTION_PATH
    )


if __name__ == "__main__":
    main()