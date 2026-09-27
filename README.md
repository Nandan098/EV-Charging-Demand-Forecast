# EV Charging Demand Forecasting & Operations Intelligence

An end-to-end Data Analyst / Data Science portfolio project built from the uploaded EV charging transaction dataset. The project intentionally does **not** use a Date dimension table, FastAPI, or Streamlit. The BI layer is designed for **Power BI**.

## Business objective
Forecast hourly EV charging energy demand by location and surface operational insights such as peak hours, demand patterns, station/charger contribution, and forecast performance.

## Dataset
- Raw rows: **72,856**
- Clean rows: **72,839**
- Locations: **14**
- Chargers: **2,118**
- Users: **2,337**
- Coverage from the source file: **2021-09-30 17:14:00 to 2022-09-30 23:11:00**

See `docs/DATASET.md` for source semantics and cleaning details.

## Tech stack
Python, Pandas, NumPy, SQL (SQLite), XGBoost, scikit-learn, Matplotlib, Power BI, Git/GitHub.

## Project architecture
```text
Raw CSV
  -> Python data cleaning
  -> SQL database
  -> SQL business analysis
  -> hourly feature extraction
  -> time-based train/test split
  -> XGBoost forecasting
  -> model predictions
  -> Power BI dashboard
```

## Database model (no DimDate)
```text
dim_user  --------- fact_charging_sessions -------- dim_charger
                              
                              +---- fact_hourly_location_demand
                              +---- fact_model_predictions
```

## Main project components
### 1. Data cleaning
`src/data_cleaning.py` loads and cleans the raw file, standardizes types, creates derived calendar fields, flags business categories, and writes a clean fact dataset.

### 2. SQL analysis
`sql/schema.sql` creates the database tables. `sql/analysis.sql` contains KPI, monthly trend, peak-hour, location, charger, weekday, time-period, company-mix, user-mix, and location peak-hour queries. CSV results are written to `outputs/sql_results/`.

### 3. Feature engineering
`src/feature_engineering.py` builds an hourly Location x Hour table and derives lag and rolling features: 1-hour, 24-hour, 168-hour lags plus 24-hour and 168-hour rolling averages.

### 4. Model training
`src/train_model.py` compares a same-hour-last-week baseline with XGBoost using a **chronological last-30-days test split**. No random train/test split is used.

### 5. Power BI
The `powerbi/` folder contains the exact recommended data sources, relationships, DAX measures, page design, and refresh steps. Import the provided CSVs into Power BI Desktop.

## Run the full pipeline
From the project root:

```bash
pip install -r requirements.txt
python src/run_pipeline.py
```

The pipeline is designed to be repeatable. It rebuilds the cleaned data, features, model artifacts, predictions, SQLite database, and report files from the raw CSV.

## Power BI dashboard pages
1. **Executive Overview** – total sessions, total demand, unique chargers, peak hour, demand trend.
2. **Demand Trend & Forecast** – actual vs predicted demand, 7-day forecast, error KPIs.
3. **Location & Charger Analysis** – location demand, charger contribution, company mix, top chargers.
4. **Time Pattern Analysis** – hour-of-day, weekday, weekend vs weekday, time-period patterns.

## Model target and evaluation
Target: `TotalDemandKWh` at hourly Location grain.

The test set is the last 30 calendar days of the available hourly data. Metrics produced are MAE, RMSE, R², and non-zero MAPE. See `reports/model_metrics.json`.

## Interview story
**Problem:** Charging demand varies by time and location.

**Approach:** Clean transactions, aggregate to hourly location demand, engineer temporal and lag features, train a time-aware forecasting model, and publish the results through a Power BI dashboard.

**Business output:** Identify peak charging periods, compare location demand, and provide a short-term forecast to support operational planning.

## Repository structure
```text
EV_Charging_Demand_Forecasting_Project/
├── raw/
├── source_material/
├── src/
├── sql/
├── database/
├── outputs/
│   ├── sql_results/
│   └── ...
├── models/
├── reports/
├── powerbi/
├── notebooks/
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

## Power BI note
A native `.pbix` file cannot be generated in this environment. The project therefore includes Power BI-ready CSVs plus the exact model, DAX measures, page layout, and data dictionary in `powerbi/`. After opening Power BI Desktop, import the listed CSVs and build the four pages as specified.
