from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; REPORTS=ROOT/'reports'
REPORTS.mkdir(exist_ok=True)

def run_eda():
    df=pd.read_csv(OUT/'cleaned_charging_sessions.csv', parse_dates=['StartDatetime','EndDatetime'])
    # Summary tables
    location=(df.groupby('Location',as_index=False)
        .agg(Sessions=('SessionID','count'),TotalDemandKWh=('Demand','sum'),AvgDemandKWh=('Demand','mean'),AvgDurationMin=('Duration','mean'),UniqueChargers=('ChargerID','nunique'))
        .sort_values('TotalDemandKWh',ascending=False))
    location.to_csv(REPORTS/'eda_location_summary.csv',index=False)
    hour=(df.groupby(['StartHour'],as_index=False)
        .agg(Sessions=('SessionID','count'),TotalDemandKWh=('Demand','sum'),AvgDemandKWh=('Demand','mean'))
        .sort_values('StartHour'))
    hour.to_csv(REPORTS/'eda_hour_summary.csv',index=False)
    weekday=(df.groupby(['DayOfWeek','DayName'],as_index=False)
        .agg(Sessions=('SessionID','count'),TotalDemandKWh=('Demand','sum'),AvgDemandKWh=('Demand','mean'))
        .sort_values('DayOfWeek'))
    weekday.to_csv(REPORTS/'eda_weekday_summary.csv',index=False)
    duration=(df['Duration'].describe()).to_frame('DurationMinutes')
    duration.to_csv(REPORTS/'eda_duration_describe.csv')
    demand=(df['Demand'].describe()).to_frame('DemandKWh')
    demand.to_csv(REPORTS/'eda_demand_describe.csv')

    # Charts
    plt.figure(figsize=(10,5)); plt.bar(location['Location'],location['TotalDemandKWh']); plt.xticks(rotation=55,ha='right'); plt.title('Total Charging Demand by Location'); plt.ylabel('Demand (kWh)'); plt.tight_layout(); plt.savefig(REPORTS/'eda_demand_by_location.png',dpi=180); plt.close()
    plt.figure(figsize=(9,5)); plt.plot(hour['StartHour'],hour['TotalDemandKWh'],marker='o',markersize=3); plt.title('Total Charging Demand by Start Hour'); plt.xlabel('Hour'); plt.ylabel('Demand (kWh)'); plt.xticks(range(0,24,2)); plt.tight_layout(); plt.savefig(REPORTS/'eda_demand_by_hour.png',dpi=180); plt.close()
    return location,hour,weekday

if __name__=='__main__': run_eda()
