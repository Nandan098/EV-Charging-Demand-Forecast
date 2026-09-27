from pathlib import Path
import sqlite3, re
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"outputs"; DB=ROOT/"database"/"ev_charging.db"; SQL=ROOT/"sql"
DB.parent.mkdir(exist_ok=True)
SCHEMA=(SQL/"schema.sql").read_text(); ANALYSIS=(SQL/"analysis.sql").read_text()

def build_db():
    if DB.exists(): DB.unlink()
    conn=sqlite3.connect(DB); conn.executescript(SCHEMA)
    pd.read_csv(OUT/"dim_charger.csv").to_sql("dim_charger",conn,if_exists="append",index=False)
    pd.read_csv(OUT/"dim_user.csv").to_sql("dim_user",conn,if_exists="append",index=False)
    pd.read_csv(OUT/"cleaned_charging_sessions.csv").to_sql("fact_charging_sessions",conn,if_exists="append",index=False)
    pd.read_csv(OUT/"fact_hourly_location_demand.csv").to_sql("fact_hourly_location_demand",conn,if_exists="append",index=False)
    p=pd.read_csv(OUT/"model_predictions.csv").rename(columns={"TotalDemandKWh":"ActualDemandKWh"})
    p[["Location","HourStart","Date","Hour","DayName","IsWeekend","ActualDemandKWh","BaselinePredKWh","PredictedDemandKWh","AbsoluteErrorKWh","Split"]].to_sql("fact_model_predictions",conn,if_exists="append",index=False)
    conn.commit()
    outdir=OUT/"sql_results"; outdir.mkdir(exist_ok=True)
    chunks=re.split(r"-- QUERY:\s*",ANALYSIS)[1:]
    for ch in chunks:
        name,query=ch.split("\n",1); query=query.strip()
        if query:
            pd.read_sql_query(query,conn).to_csv(outdir/f"{name.strip()}.csv",index=False)
    conn.close()

if __name__=="__main__": build_db()
