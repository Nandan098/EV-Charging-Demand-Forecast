from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from xgboost import XGBRegressor


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

OUT = ROOT / "outputs"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"

MODELS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "Hour",
    "DayOfWeek",
    "Month",
    "IsWeekend",
    "HourSin",
    "HourCos",
    "Lag1hKWh",
    "Lag24hKWh",
    "Lag168hKWh",
    "Rolling24hKWh",
    "Rolling168hKWh"
]


# ============================================================
# METRIC FUNCTION
# ============================================================

def calculate_metrics(y_true, y_pred):

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    non_zero = y_true != 0

    if non_zero.any():
        mape = np.mean(
            np.abs(
                (y_true[non_zero] - y_pred[non_zero])
                / y_true[non_zero]
            )
        ) * 100
    else:
        mape = np.nan

    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(
            mean_squared_error(y_true, y_pred) ** 0.5
        ),
        "R2": float(r2_score(y_true, y_pred)),
        "MAPE_nonzero_pct": float(mape)
    }


# ============================================================
# TRAINING
# ============================================================

def train():

    # --------------------------------------------------------
    # Load prepared modeling dataset
    # --------------------------------------------------------

    df = pd.read_csv(
        OUT / "model_training_dataset.csv",
        parse_dates=["HourStart"]
    )

    # IMPORTANT:
    # Sort chronologically before time-series CV
    df = (
        df
        .sort_values(["HourStart", "Location"])
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # Chronological train/test split
    # Last 30 days = untouched test set
    # --------------------------------------------------------

    cutoff = (
        df["HourStart"].max()
        - pd.Timedelta(days=30)
    )

    train_df = df[
        df["HourStart"] < cutoff
    ].copy()

    test_df = df[
        df["HourStart"] >= cutoff
    ].copy()


    # --------------------------------------------------------
    # One-hot encode Location
    # --------------------------------------------------------

    X_all = pd.get_dummies(
        df[["Location"] + FEATURES],
        columns=["Location"],
        dtype=float
    )

    X_train = (
        X_all.loc[train_df.index]
        .reset_index(drop=True)
    )

    X_test = (
        X_all.loc[test_df.index]
        .reset_index(drop=True)
    )

    y_train = (
        train_df["TotalDemandKWh"]
        .reset_index(drop=True)
    )

    y_test = (
        test_df["TotalDemandKWh"]
        .reset_index(drop=True)
    )


    # ========================================================
    # RANDOM SEARCH HYPERPARAMETER SPACE
    # ========================================================

    param_distributions = {

        "n_estimators": [
            100, 150, 200, 250, 300, 400
        ],

        "max_depth": [
            2, 3, 4, 5, 6
        ],

        "learning_rate": [
            0.01, 0.03, 0.05,
            0.08, 0.10
        ],

        "min_child_weight": [
            3, 5, 7, 10
        ],

        "subsample": [
            0.60, 0.70, 0.80, 0.90
        ],

        "colsample_bytree": [
            0.60, 0.70, 0.80, 0.90
        ],

        "gamma": [
            0, 0.1, 0.3, 0.5, 1.0
        ],

        "reg_alpha": [
            0, 0.01, 0.1, 0.5, 1.0
        ],

        "reg_lambda": [
            1, 2, 5, 10
        ]
    }


    # ========================================================
    # BASE XGBOOST MODEL
    # ========================================================

    base_model = XGBRegressor(

        objective="reg:squarederror",

        random_state=42,

        # One thread per model because
        # RandomizedSearchCV itself is parallelized
        n_jobs=1,

        tree_method="hist"
    )


    # ========================================================
    # TIME SERIES CROSS VALIDATION
    # ========================================================

    tscv = TimeSeriesSplit(
        n_splits=3
    )


    # ========================================================
    # RANDOMIZED SEARCH
    # ========================================================

    random_search = RandomizedSearchCV(

        estimator=base_model,

        param_distributions=param_distributions,

        # Number of random parameter combinations
        n_iter=10,

        # Optimize MAE
        scoring="neg_mean_absolute_error",

        # Time-aware CV
        cv=tscv,

        random_state=42,

        # Parallel search
        n_jobs=4,

        verbose=1,

        refit=True,

        return_train_score=True
    )


    # ========================================================
    # RUN HYPERPARAMETER SEARCH
    # ========================================================

    random_search.fit(
        X_train,
        y_train
    )


    # Best tuned model
    best_model = random_search.best_estimator_


    # ========================================================
    # TEST SET PREDICTIONS
    # ========================================================

    test_predictions = np.clip(
        best_model.predict(X_test),
        0,
        None
    )


    # Same-hour-last-week baseline
    baseline_predictions = np.clip(
        test_df["Lag168hKWh"].to_numpy(),
        0,
        None
    )


    # ========================================================
    # PERFORMANCE METRICS
    # ========================================================

    baseline_metrics = calculate_metrics(
        y_test,
        baseline_predictions
    )

    tuned_test_metrics = calculate_metrics(
        y_test,
        test_predictions
    )


    # Training metrics
    train_predictions = np.clip(
        best_model.predict(X_train),
        0,
        None
    )

    tuned_train_metrics = calculate_metrics(
        y_train,
        train_predictions
    )


    # Best CV MAE
    best_cv_mae = float(
        -random_search.best_score_
    )


    # ========================================================
    # SAVE METRICS
    # ========================================================

    metrics = {

        "target":
            "Hourly total charging demand (kWh) by location",

        "cv": {
            "method":
                "RandomizedSearchCV + TimeSeriesSplit",

            "n_splits": 3,

            "n_iter": 10,

            "scoring":
                "neg_mean_absolute_error",

            "best_cv_mae":
                best_cv_mae
        },

        "train_start":
            str(train_df["HourStart"].min()),

        "train_end":
            str(train_df["HourStart"].max()),

        "test_start":
            str(test_df["HourStart"].min()),

        "test_end":
            str(test_df["HourStart"].max()),

        "baseline_same_hour_last_week":
            baseline_metrics,

        "xgboost_tuned_train":
            tuned_train_metrics,

        "xgboost_tuned_test":
            tuned_test_metrics,

        "best_params":
            random_search.best_params_
    }


    # JSON report
    (
        REPORTS / "model_metrics_tuned.json"
    ).write_text(
        json.dumps(
            metrics,
            indent=2
        )
    )


    # CSV report
    pd.DataFrame([

        {
            "Model":
                "Same hour last week baseline",

            **baseline_metrics
        },

        {
            "Model":
                "XGBoost tuned - train",

            **tuned_train_metrics
        },

        {
            "Model":
                "XGBoost tuned - test",

            **tuned_test_metrics
        }

    ]).to_csv(
        REPORTS / "model_metrics_tuned.csv",
        index=False
    )


    # ========================================================
    # SAVE ALL RANDOM SEARCH RESULTS
    # ========================================================

    (
        pd.DataFrame(
            random_search.cv_results_
        )
        .sort_values("rank_test_score")
        .to_csv(
            REPORTS /
            "random_search_cv_results.csv",
            index=False
        )
    )


    # Best hyperparameters
    pd.DataFrame(
        [random_search.best_params_]
    ).to_csv(
        REPORTS /
        "best_hyperparameters.csv",
        index=False
    )


    # ========================================================
    # SAVE TEST PREDICTIONS
    # ========================================================

    predictions = test_df[
        [
            "Location",
            "HourStart",
            "Date",
            "Hour",
            "DayName",
            "IsWeekend",
            "TotalDemandKWh"
        ]
    ].copy()

    predictions[
        "BaselinePredKWh"
    ] = baseline_predictions

    predictions[
        "PredictedDemandKWh"
    ] = test_predictions

    predictions[
        "AbsoluteErrorKWh"
    ] = np.abs(
        predictions["TotalDemandKWh"]
        -
        predictions["PredictedDemandKWh"]
    )

    predictions[
        "Split"
    ] = "Test (last 30 days) - tuned XGBoost"

    predictions.to_csv(
        OUT /
        "model_predictions_tuned.csv",
        index=False
    )


    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    pd.DataFrame({

        "Feature":
            X_train.columns,

        "Importance":
            best_model.feature_importances_

    }).sort_values(
        "Importance",
        ascending=False
    ).to_csv(
        REPORTS /
        "feature_importance_tuned.csv",
        index=False
    )


    # ========================================================
    # SAVE FINAL MODEL
    # ========================================================

    joblib.dump(

        {
            "model":
                best_model,

            "feature_columns":
                X_train.columns.tolist(),

            "feature_numeric":
                FEATURES,

            "best_params":
                random_search.best_params_
        },

        MODELS /
        "xgboost_charging_demand_tuned.joblib"
    )


    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print("\n" + "=" * 60)
    print("BEST HYPERPARAMETERS")
    print("=" * 60)

    print(
        random_search.best_params_
    )


    print("\n" + "=" * 60)
    print("CV MAE")
    print("=" * 60)

    print(
        f"{best_cv_mae:.4f} kWh"
    )


    print("\n" + "=" * 60)
    print("TEST PERFORMANCE")
    print("=" * 60)

    print(
        pd.DataFrame([
            {
                "Model":
                    "Baseline",
                **baseline_metrics
            },
            {
                "Model":
                    "Tuned XGBoost",
                **tuned_test_metrics
            }
        ])
    )


if __name__ == "__main__":
    train()