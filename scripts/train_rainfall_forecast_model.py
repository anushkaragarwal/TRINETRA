from pathlib import Path
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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


DISTRICT_COL = "District"
DATE_COL = "Date"

DAILY_ACTUAL_COL = "Daily Actual"
DAILY_NORMAL_COL = "Daily Normal"
DAILY_DEPARTURE_COL = "Daily Departure Per"


def main():

    print("📥 Loading cleaned rainfall data...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[DATE_COL],
    )

    df = df.sort_values(
        by=[DISTRICT_COL, DATE_COL]
    ).copy()

    # -----------------------------------------------------
    # Target
    # -----------------------------------------------------

    # shift(-1) = next day's rainfall.

    df["target_rainfall_1d"] = (
        df.groupby(DISTRICT_COL)[DAILY_ACTUAL_COL]
        .shift(-1)
    )

    # -----------------------------------------------------
    # Lag features
    # -----------------------------------------------------

    for lag in [1, 3, 7]:

        df[f"rainfall_lag_{lag}d"] = (
            df.groupby(DISTRICT_COL)[DAILY_ACTUAL_COL]
            .shift(lag)
        )

    # -----------------------------------------------------
    # Rolling features
    # -----------------------------------------------------

    # Use only previous observations.
    # shift(1) prevents today's rainfall from leaking
    # directly into the rolling statistics.

    df["rolling_mean_3d"] = (
        df.groupby(DISTRICT_COL)[DAILY_ACTUAL_COL]
        .transform(
            lambda s: s.shift(1).rolling(
                window=3,
                min_periods=3,
            ).mean()
        )
    )

    df["rolling_std_3d"] = (
        df.groupby(DISTRICT_COL)[DAILY_ACTUAL_COL]
        .transform(
            lambda s: s.shift(1).rolling(
                window=3,
                min_periods=3,
            ).std()
        )
    )

    df["rolling_mean_7d"] = (
        df.groupby(DISTRICT_COL)[DAILY_ACTUAL_COL]
        .transform(
            lambda s: s.shift(1).rolling(
                window=7,
                min_periods=7,
            ).mean()
        )
    )

    # -----------------------------------------------------
    # Calendar features
    # -----------------------------------------------------

    df["day_of_year"] = (
        df[DATE_COL].dt.dayofyear
    )

    df["month"] = (
        df[DATE_COL].dt.month
    )

    # -----------------------------------------------------
    # Model features
    # -----------------------------------------------------

    feature_columns = [
        "rainfall_lag_1d",
        "rainfall_lag_3d",
        "rainfall_lag_7d",

        "rolling_mean_3d",
        "rolling_std_3d",
        "rolling_mean_7d",

        DAILY_NORMAL_COL,
        DAILY_DEPARTURE_COL,

        "day_of_year",
        "month",
    ]

    model_data = df.dropna(
        subset=(
            feature_columns
            + ["target_rainfall_1d"]
        )
    ).copy()

    print(
        "📊 Total usable rows:",
        len(model_data),
    )

    print(
        "🧠 Features:",
        feature_columns,
    )

    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    if len(model_data) < 10:

        raise RuntimeError(
            "Not enough historical rainfall data "
            "to train the forecast model. "
            f"Only {len(model_data)} usable rows are available."
        )

    # -----------------------------------------------------
    # Time-series split
    # -----------------------------------------------------

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
        "target_rainfall_1d"
    ]

    X_test = test[
        feature_columns
    ]

    y_test = test[
        "target_rainfall_1d"
    ]

    print(
        "📚 Training samples:",
        len(train),
    )

    print(
        "🧪 Test samples:",
        len(test),
    )

    # -----------------------------------------------------
    # Random Forest
    # -----------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    print(
        "\n🧠 Training next-day rainfall "
        "forecast model..."
    )

    model.fit(
        X_train,
        y_train,
    )

    # -----------------------------------------------------
    # Test predictions
    # -----------------------------------------------------

    test["predicted_rainfall_1d"] = (
        model.predict(X_test)
    )

    # Rainfall cannot physically be negative.

    test["predicted_rainfall_1d"] = (
        test["predicted_rainfall_1d"]
        .clip(lower=0)
    )

    # -----------------------------------------------------
    # Evaluation
    # -----------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        test["predicted_rainfall_1d"],
    )

    rmse = mean_squared_error(
        y_test,
        test["predicted_rainfall_1d"],
    ) ** 0.5

    r2 = r2_score(
        y_test,
        test["predicted_rainfall_1d"],
    )

    print(
        "\n📈 Rainfall forecast evaluation:"
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

    # -----------------------------------------------------
    # Latest test predictions
    # -----------------------------------------------------

    print(
        "\n🔎 Latest rainfall test forecasts:"
    )

    print(
        test[
            [
                DISTRICT_COL,
                DATE_COL,
                DAILY_ACTUAL_COL,
                "target_rainfall_1d",
                "predicted_rainfall_1d",
            ]
        ]
        .tail(15)
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Feature importance
    # -----------------------------------------------------

    print(
        "\n🧠 Feature importance:"
    )

    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": (
            model.feature_importances_
        ),
    }).sort_values(
        by="importance",
        ascending=False,
    )

    print(
        importance.to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # Operational next-day forecast
    # -----------------------------------------------------

    print(
        "\n🔮 Generating operational next-day forecast..."
    )

    # Latest available observation for each district.

    latest_rows = (
        df.sort_values(
            by=[DISTRICT_COL, DATE_COL]
        )
        .groupby(
            DISTRICT_COL,
            as_index=False
        )
        .tail(1)
        .copy()
    )

    # The latest row does not have a known target because
    # the next day's rainfall has not happened yet.

    latest_features = latest_rows[
        feature_columns
    ].copy()

    operational_predictions = (
        model.predict(latest_features)
    )

    operational_predictions = (
        pd.Series(
            operational_predictions,
            index=latest_rows.index,
        )
        .clip(lower=0)
    )

    latest_rows["predicted_rainfall_1d"] = (
        operational_predictions
    )

    latest_rows["forecast_date"] = (
        latest_rows[DATE_COL]
        + pd.Timedelta(days=1)
    )

    print(
        "\n🌧️ Operational next-day rainfall forecast:"
    )

    print(
        latest_rows[
            [
                DISTRICT_COL,
                DATE_COL,
                "forecast_date",
                DAILY_ACTUAL_COL,
                "predicted_rainfall_1d",
            ]
        ]
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        MODEL_PATH,
        "wb",
    ) as file:

        pickle.dump(
            {
                "model": model,
                "feature_columns": feature_columns,
            },
            file,
        )

    # -----------------------------------------------------
    # Save predictions
    # -----------------------------------------------------

    # Keep the historical test predictions and append
    # the operational next-day forecast.

    historical_predictions = test[
        [
            DISTRICT_COL,
            DATE_COL,
            DAILY_ACTUAL_COL,
            "target_rainfall_1d",
            "predicted_rainfall_1d",
        ]
    ].copy()

    operational_output = latest_rows[
        [
            DISTRICT_COL,
            DATE_COL,
            DAILY_ACTUAL_COL,
            "predicted_rainfall_1d",
        ]
    ].copy()

    operational_output["target_rainfall_1d"] = pd.NA

    operational_output = operational_output[
        [
            DISTRICT_COL,
            DATE_COL,
            DAILY_ACTUAL_COL,
            "target_rainfall_1d",
            "predicted_rainfall_1d",
        ]
    ]

    predictions_output = pd.concat(
        [
            historical_predictions,
            operational_output,
        ],
        ignore_index=True,
    )

    predictions_output = (
        predictions_output
        .drop_duplicates(
            subset=[
                DISTRICT_COL,
                DATE_COL,
            ],
            keep="last",
        )
        .sort_values(
            by=[
                DISTRICT_COL,
                DATE_COL,
            ]
        )
    )

    predictions_output.to_csv(
        PREDICTION_PATH,
        index=False,
    )

    print(
        f"\n✅ Forecast model saved: "
        f"{MODEL_PATH}"
    )

    print(
        f"✅ Predictions saved: "
        f"{PREDICTION_PATH}"
    )


if __name__ == "__main__":
    main()