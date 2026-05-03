"""
Tests unitaires — Modèles ML AirSentinel CM
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


def _base_aqi_input(city="Yaounde"):
    return {
        "city": city, "date": "2025-04-01", "weather_code": 3,
        "temperature_2m_max": 30.0, "temperature_2m_min": 20.0,
        "temperature_2m_mean": 25.0, "precipitation_sum": 5.0,
        "rain_sum": 5.0, "precipitation_hours": 2.0,
        "et0_fao_evapotranspiration": 5.0, "shortwave_radiation_sum": 22.0,
        "wind_speed_10m_max": 12.0, "wind_gusts_10m_max": 18.0,
        "wind_direction_10m_dominant": 180.0,
        "apparent_temperature_max": 34.0, "apparent_temperature_min": 24.0,
        "apparent_temperature_mean": 29.0,
        "sunrise": "06:10", "sunset": "18:15",
        "daylight_duration": 43800.0, "sunshine_duration": 25000.0,
    }


def test_predict_aqi_returns_dict():
    """predict_aqi doit retourner un dictionnaire"""
    from utils.models import predict_aqi
    result = predict_aqi(_base_aqi_input())
    assert isinstance(result, dict)


def test_predict_aqi_has_required_keys():
    """predict_aqi doit avoir score, pm25_raw, risk_level"""
    from utils.models import predict_aqi
    result = predict_aqi(_base_aqi_input())
    assert "score"      in result
    assert "pm25_raw"   in result
    assert "risk_level" in result


def test_predict_aqi_score_range():
    """Le score doit être entre 0 et 100"""
    from utils.models import predict_aqi
    result = predict_aqi(_base_aqi_input())
    assert 0 <= result["score"] <= 100


def test_predict_aqi_risk_level_valid():
    """risk_level doit être SAFE, VIGILANCE ou DANGER"""
    from utils.models import predict_aqi
    result = predict_aqi(_base_aqi_input())
    assert result["risk_level"] in ["SAFE", "VIGILANCE", "DANGER"]


def test_predict_aqi_multiple_cities():
    """Le modèle fonctionne pour plusieurs villes"""
    from utils.models import predict_aqi
    cities = ["Yaounde", "Maroua", "Douala", "Garoua", "Bamenda"]
    for city in cities:
        result = predict_aqi(_base_aqi_input(city))
        assert 0 <= result["score"] <= 100, f"Score invalide pour {city}"


def test_predict_aqi_risk_coherent_with_thresholds():
    """Le risk_level doit être cohérent avec les seuils officiels"""
    from utils.models import predict_aqi
    from utils.thresholds import get_aqi_level_from_score
    result = predict_aqi(_base_aqi_input())
    expected = get_aqi_level_from_score(result["score"])
    assert result["risk_level"] == expected


def test_get_risk_color():
    """get_risk_color retourne une couleur hex valide"""
    from utils.models import get_risk_color
    for level in ["SAFE", "VIGILANCE", "DANGER"]:
        color = get_risk_color(level)
        assert color.startswith("#")
        assert len(color) == 7
