
DROP TABLE IF EXISTS fact_model_predictions;
DROP TABLE IF EXISTS fact_hourly_location_demand;
DROP TABLE IF EXISTS fact_charging_sessions;
DROP TABLE IF EXISTS dim_charger;
DROP TABLE IF EXISTS dim_user;

CREATE TABLE dim_charger (
    ChargerID INTEGER PRIMARY KEY,
    ChargerCompany INTEGER,
    ChargerCompanyType TEXT,
    Location TEXT,
    ChargerType INTEGER,
    TotalSessions INTEGER,
    TotalDemandKWh REAL
);

CREATE TABLE dim_user (
    UserID INTEGER PRIMARY KEY,
    UserType TEXT
);

CREATE TABLE fact_charging_sessions (
    SessionID INTEGER PRIMARY KEY,
    UserID INTEGER,
    ChargerID INTEGER,
    ChargerCompany INTEGER,
    ChargerCompanyType TEXT,
    Location TEXT,
    ChargerType INTEGER,
    StartDay TEXT,
    StartTime TEXT,
    EndDay TEXT,
    EndTime TEXT,
    StartDatetime TEXT,
    EndDatetime TEXT,
    Duration REAL,
    DurationComputedMin REAL,
    Demand REAL,
    StartDate TEXT,
    EndDate TEXT,
    StartHour INTEGER,
    DayOfWeek INTEGER,
    DayName TEXT,
    Month INTEGER,
    Year INTEGER,
    IsWeekend INTEGER,
    TimePeriod TEXT,
    UserType TEXT,
    FOREIGN KEY (UserID) REFERENCES dim_user(UserID),
    FOREIGN KEY (ChargerID) REFERENCES dim_charger(ChargerID)
);

CREATE TABLE fact_hourly_location_demand (
    Location TEXT,
    HourStart TEXT,
    Date TEXT,
    Year INTEGER,
    Month INTEGER,
    MonthName TEXT,
    Hour INTEGER,
    DayOfWeek INTEGER,
    DayName TEXT,
    IsWeekend INTEGER,
    TimePeriod TEXT,
    SessionCount INTEGER,
    TotalDemandKWh REAL,
    AvgDemandPerSessionKWh REAL,
    AvgSessionDurationMin REAL,
    ActiveChargerStarts INTEGER,
    PRIMARY KEY (Location, HourStart)
);

CREATE TABLE fact_model_predictions (
    Location TEXT,
    HourStart TEXT,
    Date TEXT,
    Hour INTEGER,
    DayName TEXT,
    IsWeekend INTEGER,
    ActualDemandKWh REAL,
    BaselinePredKWh REAL,
    PredictedDemandKWh REAL,
    AbsoluteErrorKWh REAL,
    Split TEXT
);
