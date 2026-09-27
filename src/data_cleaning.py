from pathlib import Path
import pandas as pd
import numpy as np
import json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "ChargingRecords.csv"
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
OUT.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)

EXPECTED = ["UserID","ChargerID","ChargerCompany","Location","ChargerType","StartDay","StartTime","EndDay","EndTime","StartDatetime","EndDatetime","Duration","Demand"]

def clean_data(input_path=RAW):
    df = pd.read_csv(input_path)
    if df.columns.tolist() != EXPECTED:
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")
    df["Location"] = df["Location"].astype(str).str.strip().str.lower()
    for c in ["UserID","ChargerID","ChargerCompany","ChargerType","Duration"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Demand"] = pd.to_numeric(df["Demand"], errors="coerce")
    df["StartDatetime"] = pd.to_datetime(df["StartDatetime"], errors="coerce")
    df["EndDatetime"] = pd.to_datetime(df["EndDatetime"], errors="coerce")
    df["DurationComputedMin"] = (df["EndDatetime"]-df["StartDatetime"]).dt.total_seconds()/60
    invalid = (df[["StartDatetime","EndDatetime","UserID","ChargerID","Duration","Demand"]].isna().any(axis=1)
               | (df["EndDatetime"] < df["StartDatetime"]) | (df["Demand"] < 0))
    clean = df.loc[~invalid].copy().reset_index(drop=True)
    clean.insert(0,"SessionID",np.arange(1,len(clean)+1))
    clean["StartDate"] = clean["StartDatetime"].dt.date.astype(str)
    clean["EndDate"] = clean["EndDatetime"].dt.date.astype(str)
    clean["StartHour"] = clean["StartDatetime"].dt.hour
    clean["DayOfWeek"] = clean["StartDatetime"].dt.dayofweek
    clean["DayName"] = clean["StartDatetime"].dt.day_name()
    clean["Month"] = clean["StartDatetime"].dt.month
    clean["Year"] = clean["StartDatetime"].dt.year
    clean["IsWeekend"] = clean["DayOfWeek"].isin([5,6]).astype(int)
    clean["TimePeriod"] = pd.cut(clean["StartHour"],bins=[-1,5,11,17,23],labels=["Night","Morning","Afternoon","Evening"]).astype(str)
    clean["ChargerCompanyType"] = np.where(clean["ChargerCompany"].eq(1),"Own company","Other company")
    clean["UserType"] = np.where(clean["UserID"].eq(0),"ID 0 / non-member-or-other-company-member","Known user")
    output = ["SessionID","UserID","ChargerID","ChargerCompany","ChargerCompanyType","Location","ChargerType","StartDay","StartTime","EndDay","EndTime","StartDatetime","EndDatetime","Duration","DurationComputedMin","Demand","StartDate","EndDate","StartHour","DayOfWeek","DayName","Month","Year","IsWeekend","TimePeriod","UserType"]
    clean[output].to_csv(OUT/"cleaned_charging_sessions.csv",index=False)
    report={"raw_rows":len(df),"clean_rows":len(clean),"rows_removed":len(df)-len(clean),"negative_duration_rows":int((df["Duration"]<0).sum()),"duplicate_rows":int(df.duplicated().sum()),"date_min":str(df["StartDatetime"].min()),"date_max":str(df["StartDatetime"].max())}
    (REPORTS/"data_quality_report.json").write_text(json.dumps(report,indent=2))
    return clean

if __name__ == "__main__":
    clean_data()
