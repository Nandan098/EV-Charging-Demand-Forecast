
-- QUERY: overall_kpis
SELECT
  COUNT(*) AS total_sessions,
  COUNT(DISTINCT UserID) AS unique_users,
  COUNT(DISTINCT ChargerID) AS unique_chargers,
  COUNT(DISTINCT Location) AS locations,
  ROUND(SUM(Demand),2) AS total_demand_kwh,
  ROUND(AVG(Demand),2) AS avg_session_demand_kwh,
  ROUND(AVG(Duration),2) AS avg_session_duration_min
FROM fact_charging_sessions;

-- QUERY: monthly_demand
SELECT Year, Month,
       COUNT(*) AS sessions,
       ROUND(SUM(Demand),2) AS demand_kwh,
       ROUND(AVG(Demand),2) AS avg_session_demand_kwh
FROM fact_charging_sessions
GROUP BY Year, Month
ORDER BY Year, Month;

-- QUERY: peak_hours
SELECT Hour,
       SUM(SessionCount) AS sessions,
       ROUND(SUM(TotalDemandKWh),2) AS demand_kwh,
       ROUND(AVG(TotalDemandKWh),2) AS avg_location_hour_demand_kwh
FROM fact_hourly_location_demand
GROUP BY Hour
ORDER BY demand_kwh DESC;

-- QUERY: location_performance
SELECT Location,
       COUNT(*) AS sessions,
       ROUND(SUM(Demand),2) AS demand_kwh,
       ROUND(AVG(Demand),2) AS avg_session_demand_kwh,
       ROUND(AVG(Duration),2) AS avg_duration_min
FROM fact_charging_sessions
GROUP BY Location
ORDER BY demand_kwh DESC;

-- QUERY: top_chargers
SELECT c.ChargerID, c.Location, c.ChargerCompanyType,
       c.ChargerType, c.TotalSessions, ROUND(c.TotalDemandKWh,2) AS TotalDemandKWh
FROM dim_charger c
ORDER BY c.TotalDemandKWh DESC
LIMIT 20;

-- QUERY: weekday_pattern
SELECT DayName,
       SUM(SessionCount) AS sessions,
       ROUND(SUM(TotalDemandKWh),2) AS demand_kwh,
       ROUND(AVG(TotalDemandKWh),2) AS avg_location_hour_demand_kwh
FROM fact_hourly_location_demand
GROUP BY DayOfWeek, DayName
ORDER BY DayOfWeek;

-- QUERY: time_period_pattern
SELECT TimePeriod,
       SUM(SessionCount) AS sessions,
       ROUND(SUM(TotalDemandKWh),2) AS demand_kwh
FROM fact_hourly_location_demand
GROUP BY TimePeriod
ORDER BY demand_kwh DESC;

-- QUERY: company_mix
SELECT ChargerCompanyType,
       COUNT(*) AS sessions,
       ROUND(SUM(Demand),2) AS demand_kwh,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM fact_charging_sessions),2) AS session_share_pct
FROM fact_charging_sessions
GROUP BY ChargerCompanyType;

-- QUERY: user_mix
SELECT UserType,
       COUNT(*) AS sessions,
       COUNT(DISTINCT UserID) AS users,
       ROUND(SUM(Demand),2) AS demand_kwh
FROM fact_charging_sessions
GROUP BY UserType;

-- QUERY: location_peak_hour
WITH ranked AS (
 SELECT Location, Hour, SUM(TotalDemandKWh) AS demand_kwh,
        ROW_NUMBER() OVER(PARTITION BY Location ORDER BY SUM(TotalDemandKWh) DESC) AS rn
 FROM fact_hourly_location_demand
 GROUP BY Location, Hour
)
SELECT Location, Hour, ROUND(demand_kwh,2) AS demand_kwh
FROM ranked
WHERE rn=1
ORDER BY demand_kwh DESC;
