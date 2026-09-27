from pathlib import Path
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_features.csv"
)

MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "river_forecast_model.pkl"

PREDICTION_PATH = (
    ROOT
    / "data"
    / "river"
    / "processed"
    / "river_forecast_predictions.csv"
)

DISCHARGE_COL = (
    "Telemetry Hourly River Water Discharge (m3/sec)"
)

TIME_COL = "Data Acquisition Time"


def main():
    print("📥 Loading cleaned river data...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[TIME_COL],
    )

    df = df.sort_values(
        by=["Station", TIME_COL]
    ).copy()

    # 15-minute frequency:
    # 4 rows = 1 hour ahead prediction target.
    df["target_discharge_1h"] = (
        df.groupby("Station")[DISCHARGE_COL]
        .shift(-4)
    )

    # Previous discharge levels:
    # lag_1 = 15 minutes ago, lag_4 = 1 hour ago,
    # lag_8 = 2 hours ago, lag_12 = 3 hours ago.
    for lag in [1, 4, 8, 12]:
        df[f"discharge_lag_{lag}"] = (
            df.groupby("Station")[DISCHARGE_COL]
            .shift(lag)
        )

    # Rolling measurements based only on previous readings.
    df["rolling_mean_1h"] = (
        df.groupby("Station")[DISCHARGE_COL]
        .transform(
            lambda s: s.shift(1).rolling(
                window=4,
                min_periods=4,
            ).mean()
        )
    )

    df["rolling_std_1h"] = (
        df.groupby("Station")[DISCHARGE_COL]
        .transform(
            lambda s: s.shift(1).rolling(
                window=4,
                min_periods=4,
            ).std()
        )
    )

    df["hour_of_day"] = df[TIME_COL].dt.hour
    df["month"] = df[TIME_COL].dt.month

    feature_columns = [
        "discharge_lag_1",
        "discharge_lag_4",
        "discharge_lag_8",
        "discharge_lag_12",
        "rolling_mean_1h",
        "rolling_std_1h",
        "hour_of_day",
        "month",
    ]

    model_data = df.dropna(
        subset=feature_columns + ["target_discharge_1h"]
    ).copy()

    print("📊 Total usable rows:", len(model_data))
    print("🧠 Features:", feature_columns)

    # Time-series split: never random split for time data.
    # Train on first 80%, test on most recent 20%.
    split_index = int(len(model_data) * 0.80)

    train = model_data.iloc[:split_index].copy()
    test = model_data.iloc[split_index:].copy()

    X_train = train[feature_columns]
    y_train = train["target_discharge_1h"]

    X_test = test[feature_columns]
    y_test = test["target_discharge_1h"]

    print("📚 Training samples:", len(train))
    print("🧪 Test samples:", len(test))

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    print("🧠 Training 1-hour discharge forecast model...")
    model.fit(X_train, y_train)

    test["predicted_discharge_1h"] = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        test["predicted_discharge_1h"],
    )

    rmse = mean_squared_error(
        y_test,
        test["predicted_discharge_1h"],
    ) ** 0.5

    r2 = r2_score(
        y_test,
        test["predicted_discharge_1h"],
    )

    print("\n📈 Forecast evaluation:")
    print(f"MAE  : {mae:.2f} m³/s")
    print(f"RMSE : {rmse:.2f} m³/s")
    print(f"R²   : {r2:.3f}")

    print("\n🔎 Latest 15 forecasts:")
    print(
        test[
            [
                "Station",
                TIME_COL,
                DISCHARGE_COL,
                "target_discharge_1h",
                "predicted_discharge_1h",
            ]
        ]
        .tail(15)
        .to_string(index=False)
    )

    print("\n🧠 Feature importance:")
    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_,
    }).sort_values(
        by="importance",
        ascending=False,
    )

    print(
        importance.to_string(
            index=False
        )
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(
            {
                "model": model,
                "feature_columns": feature_columns,
            },
            file,
        )

    output_columns = [
        "Station",
        TIME_COL,
        DISCHARGE_COL,
        "target_discharge_1h",
        "predicted_discharge_1h",
    ]

    test[output_columns].to_csv(
        PREDICTION_PATH,
        index=False,
    )

    print(f"\n✅ Forecast model saved: {MODEL_PATH}")
    print(f"✅ Predictions saved: {PREDICTION_PATH}")


if __name__ == "__main__":
    main()