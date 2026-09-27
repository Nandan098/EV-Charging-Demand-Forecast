from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"outputs"

def build_dims():
    c=pd.read_csv(OUT/"cleaned_charging_sessions.csv")
    ch=(c.sort_values("SessionID").groupby("ChargerID",as_index=False).agg(ChargerCompany=("ChargerCompany","first"),ChargerCompanyType=("ChargerCompanyType","first"),Location=("Location","first"),ChargerType=("ChargerType","first"),TotalSessions=("SessionID","count"),TotalDemandKWh=("Demand","sum")))
    ch.to_csv(OUT/"dim_charger.csv",index=False)
    c[["UserID","UserType"]].drop_duplicates().sort_values("UserID").to_csv(OUT/"dim_user.csv",index=False)

if __name__=="__main__": build_dims()
