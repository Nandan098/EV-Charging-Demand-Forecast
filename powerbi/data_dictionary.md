# Power BI Data Dictionary

## fact_hourly_location_demand
- `Location`: location category of the charging event.
- `HourStart`: hourly timestamp.
- `SessionCount`: charging sessions started in that location-hour.
- `TotalDemandKWh`: sum of source `Demand` for that location-hour.
- `AvgDemandPerSessionKWh`: mean source demand per session.
- `AvgSessionDurationMin`: mean source duration per session.

## model_predictions
- `ActualDemandKWh`: actual target in the test set.
- `BaselinePredKWh`: same-hour-last-week baseline prediction.
- `PredictedDemandKWh`: XGBoost prediction.
- `AbsoluteErrorKWh`: absolute prediction error.

## next_7_day_forecast
- `ForecastDemandKWh`: recursively generated hourly forecast for seven days after the last observed hour.

## dim_charger
One row per charger with source company flag, location, charger type, historical session count and demand.

## dim_user
One row per UserID. UserID 0 is kept as the special category described in the supplied source comments.
