# Dataset Source & Data Dictionary

The project uses the uploaded `ChargingRecords.csv` as the raw dataset. The supplied source package also contained R scripts (`Code.zip`) used to inspect the charging records.

Raw file columns observed in this copy: UserID, ChargerID, ChargerCompany, Location, ChargerType, StartDay, StartTime, EndDay, EndTime, StartDatetime, EndDatetime, Duration, Demand.

## Important data semantics
- `Demand` is treated as **kWh per charging session** for this project, consistent with the supplied R source code, which sums `Demand` and labels the resulting monthly measure as kWh.
- `Duration` is retained from the source. We also calculate `DurationComputedMin` from the supplied timestamps as a data-quality check.
- `ChargerCompany`: the supplied source comments interpret `1` as the own charging company and `0` as other charging companies.
- `UserID = 0`: the supplied source comments describe this as non-members / members of other EV charging companies; this project keeps that category as a transparent `UserType` label rather than inventing a more specific identity.

## Data quality handling
The raw file contains 72,856 rows. The pipeline removes 17 rows because their temporal fields are invalid for analysis (for example, EndDatetime earlier than StartDatetime). All cleaning decisions are recorded in `reports/data_quality_report.json`.

## Forecasting grain
The ML target is **hourly total charging demand (kWh) by Location**. The hourly table is completed to a full hourly grid per location, and missing activity is treated as zero demand.
