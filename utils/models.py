"""
AirSentinel CM - ML Model Loading and Prediction Utilities
XGBoost (AQI/PM2.5) + Logistic Regression (Heatwave)
"""
import pickle
import numpy as np
import pandas as pd
import warnings
import os
import math
from datetime import datetime

warnings.filterwarnings("ignore")

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
_pm25_bundle = None
_hw_bundle = None


# ─── encode_datetime must be in __main__ for PM2.5 pkl unpickling ────────────
def _register_encode_datetime():
    import __main__
    if not hasattr(__main__, "encode_datetime"):
        def encode_datetime(df):
            df = df.copy()
            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"])
                days = (df["time"] - pd.Timestamp("2020-01-01")).dt.days
                df["time_sin"] = np.sin(2 * np.pi * days / 365.25)
                df["time_cos"] = np.cos(2 * np.pi * days / 365.25)
                df["time_month"] = df["time"].dt.month
                df["time_year"] = df["time"].dt.year
                df["time_dayofweek"] = df["time"].dt.dayofweek
                df = df.drop(columns=["time"])
            return df
        __main__.encode_datetime = encode_datetime


def load_pm25_model():
    global _pm25_bundle
    if _pm25_bundle is None:
        _register_encode_datetime()
        path = os.path.join(MODELS_DIR, "modele_pm25_insightx_final.pkl")
        with open(path, "rb") as f:
            _pm25_bundle = pickle.load(f)
    return _pm25_bundle


def load_heatwave_model():
    global _hw_bundle
    if _hw_bundle is None:
        path = os.path.join(MODELS_DIR, "heatwave_model.pkl")
        with open(path, "rb") as f:
            _hw_bundle = pickle.load(f)
    return _hw_bundle


# ─── PM2.5 / AQI helpers ─────────────────────────────────────────────────────

def _encode_datetime_pm25(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
        days = (df["time"] - pd.Timestamp("2020-01-01")).dt.days
        df["time_sin"] = np.sin(2 * np.pi * days / 365.25)
        df["time_cos"] = np.cos(2 * np.pi * days / 365.25)
        df["time_month"] = df["time"].dt.month
        df["time_year"] = df["time"].dt.year
        df["time_dayofweek"] = df["time"].dt.dayofweek
        df = df.drop(columns=["time"])
    return df


def _encode_sunrise_sunset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["sunrise", "sunset"]:
        if col in df.columns:
            def to_minutes(val):
                try:
                    if isinstance(val, str):
                        parts = val.strip().split(":")
                        return int(parts[0]) * 60 + int(parts[1])
                    if hasattr(val, "hour"):
                        return val.hour * 60 + val.minute
                    return float(val)
                except Exception:
                    return 360 if col == "sunrise" else 1080
            mins = df[col].apply(to_minutes)
            df[f"{col}_sin"] = np.sin(2 * np.pi * mins / 1440)
            df[f"{col}_cos"] = np.cos(2 * np.pi * mins / 1440)
            df = df.drop(columns=[col])
    return df


RAW_COLS_PM25 = [
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
    "sunrise_sin", "sunrise_cos", "sunset_sin", "sunset_cos",
    "daylight_duration", "sunshine_duration",
    "precipitation_sum", "rain_sum", "precipitation_hours",
    "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
    "shortwave_radiation_sum", "et0_fao_evapotranspiration",
    "city", "region", "latitude", "longitude", "weather_code_label",
    "time_sin", "time_cos", "time_month", "time_year", "time_dayofweek",
]


def _build_pm25_input(d: dict) -> pd.DataFrame:
    from utils.translations import CAMEROON_CITIES
    city = d.get("city", "Yaounde")
    city_info = CAMEROON_CITIES.get(city, {"lat": 3.87, "lon": 11.52, "region": "Centre"})
    wmo_code = int(d.get("weather_code", 3))
    wmo_map = {
        0: "Ciel dégagé", 1: "Peu nuageux", 2: "Partiellement nuageux", 3: "Couvert",
        45: "Brouillard", 48: "Brouillard givrant",
        51: "Bruine légère", 53: "Bruine modérée", 55: "Bruine dense",
        61: "Pluie légère", 63: "Pluie modérée", 65: "Pluie forte",
        80: "Averses légères", 81: "Averses modérées", 82: "Averses violentes",
        95: "Orage", 96: "Orage+grêle légère", 99: "Orage+grêle forte",
    }
    row = {
        "time": pd.to_datetime(d.get("date", datetime.now().strftime("%Y-%m-%d"))),
        "temperature_2m_max": float(d.get("temperature_2m_max", 30.0)),
        "temperature_2m_min": float(d.get("temperature_2m_min", 20.0)),
        "temperature_2m_mean": float(d.get("temperature_2m_mean", 25.0)),
        "apparent_temperature_max": float(d.get("apparent_temperature_max", 32.0)),
        "apparent_temperature_min": float(d.get("apparent_temperature_min", 22.0)),
        "apparent_temperature_mean": float(d.get("apparent_temperature_mean", 27.0)),
        "sunrise": d.get("sunrise", "06:00"),
        "sunset": d.get("sunset", "18:00"),
        "daylight_duration": float(d.get("daylight_duration", 43200)),
        "sunshine_duration": float(d.get("sunshine_duration", 25000)),
        "precipitation_sum": float(d.get("precipitation_sum", 0.0)),
        "rain_sum": float(d.get("rain_sum", 0.0)),
        "precipitation_hours": float(d.get("precipitation_hours", 0.0)),
        "wind_speed_10m_max": float(d.get("wind_speed_10m_max", 10.0)),
        "wind_gusts_10m_max": float(d.get("wind_gusts_10m_max", 15.0)),
        "wind_direction_10m_dominant": float(d.get("wind_direction_10m_dominant", 180.0)),
        "shortwave_radiation_sum": float(d.get("shortwave_radiation_sum", 20.0)),
        "et0_fao_evapotranspiration": float(d.get("et0_fao_evapotranspiration", 5.0)),
        "city": city,
        "region": city_info["region"],
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "weather_code_label": wmo_map.get(wmo_code, "Couvert"),
    }
    return pd.DataFrame([row])


def predict_aqi(input_dict: dict) -> dict:
    """Predict PM2.5/AQI score. Returns score (0-100), pm25_raw, risk_level."""
    bundle = load_pm25_model()
    model = bundle["modele"]
    preprocessor = bundle["preprocessor"]
    top_feat_idx = bundle["top_feat_idx"]

    df = _build_pm25_input(input_dict)
    df = _encode_datetime_pm25(df)
    df = _encode_sunrise_sunset(df)

    for col in RAW_COLS_PM25:
        if col not in df.columns:
            df[col] = 0

    X = preprocessor.transform(df[RAW_COLS_PM25])
    pm25_raw = float(model.predict(X[:, top_feat_idx])[0])
    score = min(100.0, max(0.0, (pm25_raw / 35.0) * 100.0))

    return {
        "score": round(score, 2),
        "pm25_raw": round(pm25_raw, 2),
        "risk_level": get_risk_level(score),
    }


# ─── Heatwave helpers ─────────────────────────────────────────────────────────

# Precomputed city temp_thresholds from training data (90th percentile)
# These are approximate values based on the dataset
CITY_THRESHOLDS = {
    "Abong-Mbang": 31.8, "Akonolinga": 32.4, "Bafoussam": 30.2, "Bamenda": 28.9,
    "Batouri": 33.2, "Bertoua": 33.5, "Douala": 33.1, "Dschang": 29.5,
    "Ebolowa": 32.0, "Foumban": 31.8, "Garoua": 41.2, "Guider": 41.5,
    "Kousseri": 43.8, "Maroua": 42.5, "Mbalmayo": 32.2, "Mbengwi": 29.0,
    "Mbouda": 30.1, "Meiganga": 35.0, "Mokolo": 41.0, "Ngaoundere": 34.2,
    "Nkongsamba": 32.0, "Poli": 40.5, "Sangmelima": 31.5, "Tibati": 33.8,
    "Tignere": 34.5, "Touboro": 40.8, "Wum": 30.5, "Yagoua": 42.0,
    "Yaounde": 31.8, "Yokadouma": 33.0,
}


def _build_heatwave_input(d: dict) -> pd.DataFrame:
    """Build feature row matching the model trained on the dataset."""
    from utils.translations import CAMEROON_CITIES
    city = d.get("city", "Yaounde")
    city_info = CAMEROON_CITIES.get(city, {"lat": 3.87, "lon": 11.52, "region": "Centre"})

    date_obj = pd.to_datetime(d.get("date", datetime.now().strftime("%Y-%m-%d")))
    doy = date_obj.day_of_year
    time_sin = math.sin(2 * math.pi * doy / 365)
    time_cos = math.cos(2 * math.pi * doy / 365)

    def time_to_min(val, default):
        try:
            if isinstance(val, str):
                p = val.split(":")
                return int(p[0]) * 60 + int(p[1])
            return default
        except Exception:
            return default

    sr_min = time_to_min(d.get("sunrise", "06:00"), 360)
    ss_min = time_to_min(d.get("sunset", "18:00"), 1080)

    temp_max = float(d.get("temperature_2m_max", 30.0))
    temp_threshold = float(d.get("temp_threshold",
                                  CITY_THRESHOLDS.get(city, 36.0)))
    temp_lag1 = float(d.get("temp_lag1", temp_max - 1))
    temp_lag2 = float(d.get("temp_lag2", temp_max - 2))
    temp_lag3 = float(d.get("temp_lag3", temp_max - 3))

    hot_day = int(temp_max > temp_threshold)
    # heatwave = 1 if last 3 days were all hot (simplified: use lags)
    heatwave = int(
        (temp_max > temp_threshold) and
        (temp_lag1 > temp_threshold) and
        (temp_lag2 > temp_threshold)
    )

    row = {
        "temperature_2m_max": temp_max,
        "temperature_2m_min": float(d.get("temperature_2m_min", 20.0)),
        "temperature_2m_mean": float(d.get("temperature_2m_mean", 25.0)),
        "apparent_temperature_max": float(d.get("apparent_temperature_max", 32.0)),
        "apparent_temperature_min": float(d.get("apparent_temperature_min", 22.0)),
        "apparent_temperature_mean": float(d.get("apparent_temperature_mean", 27.0)),
        "daylight_duration": float(d.get("daylight_duration", 43200)),
        "sunshine_duration": float(d.get("sunshine_duration", 25000)),
        "precipitation_sum": float(d.get("precipitation_sum", 0.0)),
        "rain_sum": float(d.get("rain_sum", 0.0)),
        "precipitation_hours": float(d.get("precipitation_hours", 0.0)),
        "wind_speed_10m_max": float(d.get("wind_speed_10m_max", 10.0)),
        "wind_gusts_10m_max": float(d.get("wind_gusts_10m_max", 15.0)),
        "wind_direction_10m_dominant": float(d.get("wind_direction_10m_dominant", 180.0)),
        "shortwave_radiation_sum": float(d.get("shortwave_radiation_sum", 20.0)),
        "et0_fao_evapotranspiration": float(d.get("et0_fao_evapotranspiration", 5.0)),
        "city": city,
        "region": city_info["region"],
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "temp_threshold": temp_threshold,
        "hot_day": hot_day,
        "heatwave": heatwave,
        "temp_lag1": temp_lag1,
        "temp_lag2": temp_lag2,
        "temp_lag3": temp_lag3,
        "time_month": date_obj.month,
        "time_year": date_obj.year,
        "time_dayofweek": date_obj.dayofweek,
        "time_sin": time_sin,
        "time_cos": time_cos,
        "sunrise_sin": math.sin(2 * math.pi * sr_min / 1440),
        "sunrise_cos": math.cos(2 * math.pi * sr_min / 1440),
        "sunset_sin": math.sin(2 * math.pi * ss_min / 1440),
        "sunset_cos": math.cos(2 * math.pi * ss_min / 1440),
    }
    return pd.DataFrame([row])


def predict_heatwave(input_dict: dict) -> dict:
    """Predict heatwave probability. Returns probability, prediction, risk_level."""
    bundle = load_heatwave_model()
    preprocessor = bundle["preprocessor"]
    scaler       = bundle["scaler"]
    model        = bundle["model"]
    threshold    = bundle.get("threshold", 0.20)
    feat_names   = bundle.get("feature_names_enc", [])

    df = _build_heatwave_input(input_dict)

    # Ensure all expected columns exist
    for col in feat_names:
        if col not in df.columns:
            df[col] = 0

    # Keep only expected columns in order
    if feat_names:
        df = df[feat_names]

    X = preprocessor.transform(df)
    X_sc = scaler.transform(X)
    proba = float(model.predict_proba(X_sc)[0][1])
    prediction = int(proba > threshold)

    risk_level = "DANGER" if prediction == 1 else ("VIGILANCE" if proba > 0.1 else "SAFE")
    return {
        "probability": round(proba, 4),
        "prediction": prediction,
        "risk_level": risk_level,
        "score": round(proba * 100, 2),
    }


# ─── Shared helpers ───────────────────────────────────────────────────────────

def get_risk_level(score: float) -> str:
    if score <= 33:
        return "SAFE"
    elif score <= 66:
        return "VIGILANCE"
    return "DANGER"


def get_risk_color(level: str) -> str:
    return {"SAFE": "#007A5E", "VIGILANCE": "#FCD116", "DANGER": "#CE1126"}.get(level, "#007A5E")


def get_risk_emoji(level: str) -> str:
    return {"SAFE": "✅", "VIGILANCE": "⚠️", "DANGER": "🚨"}.get(level, "✅")
