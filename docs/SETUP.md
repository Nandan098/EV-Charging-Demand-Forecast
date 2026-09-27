# Setup & Run Guide

## 1. Folder
Open a terminal in the `EV_Charging_Demand_Forecasting_Project` root folder.

## 2. Python environment

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Run the complete project
```bash
python src/run_pipeline.py
```

This performs:
- data cleaning
- dimension creation (User and Charger only; no Date dimension)
- EDA summaries and charts
- hourly feature extraction
- chronological model training/evaluation
- full-model refit
- recursive 7-day forecast
- SQLite database creation
- SQL result CSV generation

## 4. Run pieces separately
```bash
python src/data_cleaning.py
python src/create_dimensions.py
python src/eda.py
python src/feature_engineering.py
python src/train_model.py
python src/forecast_next_7_days.py
python src/run_sql_analysis.py
```

## 5. Power BI
Open Power BI Desktop and import the CSV files described in `powerbi/README.md`.

Recommended first import set:
- `outputs/fact_hourly_location_demand.csv`
- `outputs/model_predictions.csv`
- `outputs/next_7_day_forecast.csv`
- `outputs/dim_charger.csv`
- `outputs/dim_user.csv`

Add `outputs/cleaned_charging_sessions.csv` only when you need session-level drill-through.

## 6. SQLite
The database is at:
`database/ev_charging.db`

The SQL scripts are in:
- `sql/schema.sql`
- `sql/analysis.sql`

## 7. Main output files
- `outputs/cleaned_charging_sessions.csv` — cleaned session fact
- `outputs/fact_hourly_location_demand.csv` — hourly modeling/BI table
- `outputs/model_training_dataset.csv` — training-ready features
- `outputs/model_predictions.csv` — holdout predictions
- `outputs/next_7_day_forecast.csv` — recursive 7-day forecast
- `reports/model_metrics.csv` — baseline vs XGBoost metrics
- `reports/feature_importance.csv` — feature importance
- `reports/*.png` — EDA/model plots
