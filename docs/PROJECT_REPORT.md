# Project Report

## Objective
Build a practical forecasting POC that predicts hourly charging energy demand by location and exposes operational insights through Power BI.

## Data preparation
The raw CSV was inspected for type issues, missing timestamps, duplicates, negative duration, and negative demand. Invalid temporal records are removed from the modeling/analytics layer. The supplied source `Duration` is kept, while `DurationComputedMin` is added as a quality-check field based on the start/end timestamps.

## Data model
No Date dimension is used.

Tables:
- `dim_user`
- `dim_charger`
- `fact_charging_sessions`
- `fact_hourly_location_demand`
- `fact_model_predictions`

## Feature engineering
The target is `TotalDemandKWh` at the `Location x HourStart` grain.

Features:
- Hour
- DayOfWeek
- Month
- IsWeekend
- cyclic hour encoding (`HourSin`, `HourCos`)
- 1-hour lag
- 24-hour lag
- 168-hour lag
- 24-hour rolling mean (shifted to avoid leakage)
- 168-hour rolling mean (shifted to avoid leakage)

## Validation
The last 30 days are held out as test data. This is a chronological split instead of a random split so the evaluation better reflects forecasting.

## Model
- Baseline: same location, same hour one week earlier (`Lag168hKWh`)
- Main model: XGBoost regression

See `reports/model_metrics.json` for the exact run metrics.

## Business outputs
Power BI pages are designed around:
- executive KPI overview
- actual vs predicted demand
- seven-day forecast
- location and charger analysis
- time-of-day and weekday patterns

## Limitations
- The raw dataset has no weather, holidays, traffic, or real-time grid variables, so the model only uses information present in the source file and temporal lag features.
- MAPE can be unstable when actual demand is near zero; MAE and RMSE should be emphasized in discussion.
- The seven-day forecast is recursive, so forecast errors can propagate into later horizons.
