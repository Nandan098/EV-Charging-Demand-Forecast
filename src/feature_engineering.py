from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"outputs"

def build_features(clean_path=OUT/"cleaned_charging_sessions.csv"):
    clean=pd.read_csv(clean_path,parse_dates=["StartDatetime","EndDatetime"])
    agg=(clean.assign(HourStart=clean["StartDatetime"].dt.floor("h"))
        .groupby(["Location","HourStart"],as_index=False)
        .agg(SessionCount=("SessionID","count"),TotalDemandKWh=("Demand","sum"),AvgDemandPerSessionKWh=("Demand","mean"),AvgSessionDurationMin=("Duration","mean"),ActiveChargerStarts=("ChargerID","nunique")))
    locs=sorted(clean["Location"].unique()); all_hours=pd.date_range(clean["StartDatetime"].min().floor("h"),clean["StartDatetime"].max().ceil("h"),freq="h")
    grid=pd.MultiIndex.from_product([locs,all_hours],names=["Location","HourStart"]).to_frame(index=False)
    hourly=grid.merge(agg,on=["Location","HourStart"],how="left")
    for c in ["SessionCount","TotalDemandKWh","AvgDemandPerSessionKWh","AvgSessionDurationMin","ActiveChargerStarts"]: hourly[c]=hourly[c].fillna(0)
    hourly["Date"]=hourly["HourStart"].dt.date.astype(str); hourly["Year"]=hourly["HourStart"].dt.year; hourly["Month"]=hourly["HourStart"].dt.month; hourly["MonthName"]=hourly["HourStart"].dt.strftime("%b"); hourly["Hour"]=hourly["HourStart"].dt.hour; hourly["DayOfWeek"]=hourly["HourStart"].dt.dayofweek; hourly["DayName"]=hourly["HourStart"].dt.day_name(); hourly["IsWeekend"]=hourly["DayOfWeek"].isin([5,6]).astype(int)
    hourly["TimePeriod"]=pd.cut(hourly["Hour"],bins=[-1,5,11,17,23],labels=["Night","Morning","Afternoon","Evening"]).astype(str)
    hourly["HourSin"]=np.sin(2*np.pi*hourly["Hour"]/24); hourly["HourCos"]=np.cos(2*np.pi*hourly["Hour"]/24)
    hourly=hourly.sort_values(["Location","HourStart"]).reset_index(drop=True)
    g=hourly.groupby("Location")["TotalDemandKWh"]
    hourly["Lag1hKWh"]=g.shift(1); hourly["Lag24hKWh"]=g.shift(24); hourly["Lag168hKWh"]=g.shift(168)
    hourly["Rolling24hKWh"]=hourly.groupby("Location")["TotalDemandKWh"].transform(lambda s:s.shift(1).rolling(24,min_periods=24).mean())
    hourly["Rolling168hKWh"]=hourly.groupby("Location")["TotalDemandKWh"].transform(lambda s:s.shift(1).rolling(168,min_periods=168).mean())
    base=["Location","HourStart","Date","Year","Month","MonthName","Hour","DayOfWeek","DayName","IsWeekend","TimePeriod","SessionCount","TotalDemandKWh","AvgDemandPerSessionKWh","AvgSessionDurationMin","ActiveChargerStarts"]
    hourly[base].to_csv(OUT/"fact_hourly_location_demand.csv",index=False)
    model=hourly[base+["HourSin","HourCos","Lag1hKWh","Lag24hKWh","Lag168hKWh","Rolling24hKWh","Rolling168hKWh"]].dropna(subset=["Lag168hKWh","Rolling168hKWh"])
    model.to_csv(OUT/"model_training_dataset.csv",index=False)
    return hourly,model

if __name__=="__main__": build_features()
