from pathlib import Path
import math, joblib
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; MODELS=ROOT/'models'
FEATURES=['Hour','DayOfWeek','Month','IsWeekend','HourSin','HourCos','Lag1hKWh','Lag24hKWh','Lag168hKWh','Rolling24hKWh','Rolling168hKWh']

def forecast(days=7):
    df=pd.read_csv(OUT/'model_training_dataset.csv',parse_dates=['HourStart'])
    model=joblib.load(MODELS/'xgboost_charging_demand_full.joblib')
    feature_columns=model['feature_columns']; reg=model['model']
    base=pd.read_csv(OUT/'fact_hourly_location_demand.csv',parse_dates=['HourStart'])
    history=base[['Location','HourStart','TotalDemandKWh']].set_index(['Location','HourStart'])['TotalDemandKWh'].sort_index()
    locations=sorted(base['Location'].unique()); future_start=base['HourStart'].max()+pd.Timedelta(hours=1); future_hours=pd.date_range(future_start,periods=days*24,freq='h')
    rows=[]
    for loc in locations:
        series=history.loc[loc].copy()
        for ts in future_hours:
            hour=ts.hour; dow=ts.dayofweek; month=ts.month; is_weekend=int(dow>=5)
            lag1=float(series.get(ts-pd.Timedelta(hours=1),np.nan)); lag24=float(series.get(ts-pd.Timedelta(hours=24),np.nan)); lag168=float(series.get(ts-pd.Timedelta(hours=168),np.nan))
            prev24=series.loc[:ts-pd.Timedelta(hours=1)].tail(24); prev168=series.loc[:ts-pd.Timedelta(hours=1)].tail(168)
            if pd.isna(lag1) or pd.isna(lag24) or pd.isna(lag168) or len(prev24)<24 or len(prev168)<168:
                raise RuntimeError('Insufficient history to create recursive lag features.')
            row={'Location':loc,'Hour':hour,'DayOfWeek':dow,'Month':month,'IsWeekend':is_weekend,'HourSin':math.sin(2*math.pi*hour/24),'HourCos':math.cos(2*math.pi*hour/24),'Lag1hKWh':lag1,'Lag24hKWh':lag24,'Lag168hKWh':lag168,'Rolling24hKWh':float(prev24.mean()),'Rolling168hKWh':float(prev168.mean())}
            x=pd.DataFrame([row]); x=pd.get_dummies(x,columns=['Location'],dtype=float).reindex(columns=feature_columns,fill_value=0)
            pred=float(max(0,reg.predict(x)[0])); series.loc[ts]=pred
            rows.append({'Location':loc,'HourStart':ts,'Date':ts.date().isoformat(),'Hour':hour,'DayName':ts.day_name(),'IsWeekend':is_weekend,'ForecastDemandKWh':pred})
    out=pd.DataFrame(rows); out.to_csv(OUT/f'next_{days}_day_forecast.csv',index=False); out.to_csv(OUT/'next_7_day_forecast.csv',index=False)
    return out

if __name__=='__main__': forecast(7)
