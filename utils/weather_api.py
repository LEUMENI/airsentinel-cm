"""
AirSentinel CM - Open-Meteo Real-time Weather API
Fetches data automatically and returns all model features
"""
import requests
from datetime import datetime, date, timedelta

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARS = [
    "temperature_2m_max","temperature_2m_min","temperature_2m_mean",
    "apparent_temperature_max","apparent_temperature_min","apparent_temperature_mean",
    "sunrise","sunset","daylight_duration","sunshine_duration",
    "precipitation_sum","rain_sum","precipitation_hours",
    "wind_speed_10m_max","wind_gusts_10m_max","wind_direction_10m_dominant",
    "shortwave_radiation_sum","et0_fao_evapotranspiration","weather_code",
]


def fetch_weather(lat: float, lon: float, target_date: str = None) -> dict:
    """
    Fetch weather data for a location/date.
    Returns {"success": bool, "data": dict, "error": str}
    """
    if target_date is None:
        target_date = date.today().isoformat()
    target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()
    today = date.today()

    try:
        if target_dt < today - timedelta(days=2):
            url = OPEN_METEO_ARCHIVE_URL
            params = {"latitude": lat, "longitude": lon,
                      "start_date": target_date, "end_date": target_date,
                      "daily": ",".join(DAILY_VARS), "timezone": "Africa/Douala"}
        else:
            url = OPEN_METEO_URL
            fdate = max(target_dt, today)
            params = {"latitude": lat, "longitude": lon,
                      "start_date": fdate.isoformat(),
                      "end_date": (fdate + timedelta(days=1)).isoformat(),
                      "daily": ",".join(DAILY_VARS), "timezone": "Africa/Douala"}

        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})
        idx = 0

        def safe(key, default=0.0):
            vals = daily.get(key, [])
            return vals[idx] if (vals and idx < len(vals) and vals[idx] is not None) else default

        def parse_time(val):
            if val and "T" in str(val):
                return str(val).split("T")[1][:5]
            return val or "06:00"

        result = {
            "temperature_2m_max":        safe("temperature_2m_max", 30.0),
            "temperature_2m_min":        safe("temperature_2m_min", 20.0),
            "temperature_2m_mean":       safe("temperature_2m_mean", 25.0),
            "apparent_temperature_max":  safe("apparent_temperature_max", 32.0),
            "apparent_temperature_min":  safe("apparent_temperature_min", 22.0),
            "apparent_temperature_mean": safe("apparent_temperature_mean", 27.0),
            "sunrise":                   parse_time(safe("sunrise", "2024-01-01T06:00")),
            "sunset":                    parse_time(safe("sunset",  "2024-01-01T18:00")),
            "daylight_duration":         safe("daylight_duration", 43200),
            "sunshine_duration":         safe("sunshine_duration", 25000),
            "precipitation_sum":         safe("precipitation_sum", 0.0),
            "rain_sum":                  safe("rain_sum", 0.0),
            "precipitation_hours":       safe("precipitation_hours", 0.0),
            "wind_speed_10m_max":        safe("wind_speed_10m_max", 10.0),
            "wind_gusts_10m_max":        safe("wind_gusts_10m_max", 15.0),
            "wind_direction_10m_dominant": safe("wind_direction_10m_dominant", 180.0),
            "shortwave_radiation_sum":   safe("shortwave_radiation_sum", 20.0),
            "et0_fao_evapotranspiration":safe("et0_fao_evapotranspiration", 5.0),
            "weather_code":              int(safe("weather_code", 3)),
        }
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e), "data": {}}


def fetch_weather_3days(lat: float, lon: float) -> list:
    """
    Fetch last 3 days temperatures for heatwave lag features.
    Returns list of [temp_lag3, temp_lag2, temp_lag1] (oldest first)
    """
    try:
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=3)
        params = {"latitude": lat, "longitude": lon,
                  "start_date": start.isoformat(), "end_date": end.isoformat(),
                  "daily": "temperature_2m_max", "timezone": "Africa/Douala"}
        resp = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=10)
        resp.raise_for_status()
        temps = resp.json().get("daily", {}).get("temperature_2m_max", [])
        if len(temps) >= 3:
            return [temps[-3], temps[-2], temps[-1]]
        return [30.0, 30.0, 30.0]
    except Exception:
        return [30.0, 30.0, 30.0]


def fetch_all_cities_realtime(cities_dict: dict) -> dict:
    """
    Fetch today's weather for all cities in parallel (for dashboard auto-alerts).
    Returns {city_name: {weather data}, ...}
    """
    from datetime import date as dt
    results = {}
    today = dt.today().isoformat()
    for city, info in cities_dict.items():
        r = fetch_weather(info["lat"], info["lon"], today)
        if r["success"]:
            results[city] = r["data"]
    return results


def fetch_historical_for_dashboard(lat: float, lon: float, days: int = 30) -> list:
    """Last N days of weather for dashboard charts."""
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days)
    try:
        params = {"latitude": lat, "longitude": lon,
                  "start_date": start.isoformat(), "end_date": end.isoformat(),
                  "daily": "temperature_2m_max,temperature_2m_mean,precipitation_sum,et0_fao_evapotranspiration,shortwave_radiation_sum",
                  "timezone": "Africa/Douala"}
        resp = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=12)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})
        dates = daily.get("time", [])
        return [{"date": d,
                 "temp_max":  daily.get("temperature_2m_max", [None]*len(dates))[i],
                 "temp_mean": daily.get("temperature_2m_mean", [None]*len(dates))[i],
                 "precip":    daily.get("precipitation_sum", [None]*len(dates))[i],
                 "et0":       daily.get("et0_fao_evapotranspiration", [None]*len(dates))[i],
                 "radiation": daily.get("shortwave_radiation_sum", [None]*len(dates))[i]}
                for i, d in enumerate(dates)]
    except Exception:
        return []
