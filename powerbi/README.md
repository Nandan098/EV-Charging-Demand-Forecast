# Power BI Setup

This project intentionally uses **Power BI** as the presentation layer. There is no FastAPI, Streamlit, or Date dimension table.

## Import these CSVs
Use **Get Data -> Text/CSV** and import:

- `outputs/fact_hourly_location_demand.csv`
- `outputs/model_predictions.csv`
- `outputs/next_7_day_forecast.csv`
- `outputs/cleaned_charging_sessions.csv`
- `outputs/dim_charger.csv`
- `outputs/dim_user.csv`

For a lighter Power BI model, start with the first five files and add `cleaned_charging_sessions.csv` only when you need session-level drill-through.

## Relationships (no DimDate)
- `fact_charging_sessions[ChargerID]` -> `dim_charger[ChargerID]` (Many-to-One, single direction)
- `fact_charging_sessions[UserID]` -> `dim_user[UserID]` (Many-to-One, single direction)

`fact_hourly_location_demand`, `model_predictions`, and `next_7_day_forecast` are analytical tables at their own grains. Do not force a many-to-many relationship between them. Use their own date/hour fields on visuals.

## Suggested report pages
### Page 1 — Executive Overview
Cards: Total Sessions, Total Demand (kWh), Avg Session Demand (kWh), Unique Chargers.
Charts: monthly demand line, demand by location bar chart, top 10 chargers bar chart.

### Page 2 — Demand Trend & Forecast
Line chart: Actual vs Predicted from `model_predictions`.
Line chart: 7-day forecast from `next_7_day_forecast`.
Cards: MAE, RMSE, MAPE, Forecast Horizon.

### Page 3 — Location & Charger Analysis
Matrix: Location -> ChargerID with sessions and demand.
Bar chart: Demand by location.
Stacked column: Own company vs Other company.

### Page 4 — Time Pattern Analysis
Line chart: demand by hour.
Column chart: demand by weekday.
Column chart: demand by TimePeriod.
Slicers: Location, Month, DayName, IsWeekend.
