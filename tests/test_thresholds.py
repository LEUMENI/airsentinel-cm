"""
Tests unitaires — Seuils officiels AirSentinel CM
Source : Seuils.docx — IndabaX Cameroon 2026
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.thresholds import (
    get_aqi_level_from_score,
    get_aqi_color,
    get_aqi_label,
    get_temp_class,
    get_temp_color,
    get_precip_class,
    get_precip_color,
    is_danger_level,
    AQI_SAFE_MAX,
    AQI_VIGILANCE_MAX,
    AQI_SCORE_SAFE_MAX,
    AQI_SCORE_VIGILANCE_MAX,
    TEMP_FRAIS_MAX,
    TEMP_TEMPERE_MAX,
    TEMP_CHAUD_MAX,
    PRECIP_TRES_SEC_MAX,
    PRECIP_SEC_MAX,
    PRECIP_MODERE_MAX,
    PRECIP_HUMIDE_MAX,
)


# ── Tests seuils PM2.5 ────────────────────────────────────────────

def test_aqi_safe_max_value():
    """PM2.5 Safe max doit être 12.7 µg/m³"""
    assert AQI_SAFE_MAX == 12.7

def test_aqi_vigilance_max_value():
    """PM2.5 Vigilance max doit être 22.2 µg/m³"""
    assert AQI_VIGILANCE_MAX == 22.2

def test_aqi_score_safe_max():
    """Score Safe max doit être 36.3"""
    assert AQI_SCORE_SAFE_MAX == 36.3

def test_aqi_score_vigilance_max():
    """Score Vigilance max doit être 63.4"""
    assert AQI_SCORE_VIGILANCE_MAX == 63.4

def test_get_aqi_level_safe():
    """Score 0 à 36.3 → SAFE"""
    assert get_aqi_level_from_score(0)    == "SAFE"
    assert get_aqi_level_from_score(20)   == "SAFE"
    assert get_aqi_level_from_score(36.3) == "SAFE"

def test_get_aqi_level_vigilance():
    """Score 36.4 à 63.4 → VIGILANCE"""
    assert get_aqi_level_from_score(36.4) == "VIGILANCE"
    assert get_aqi_level_from_score(50)   == "VIGILANCE"
    assert get_aqi_level_from_score(63.4) == "VIGILANCE"

def test_get_aqi_level_danger():
    """Score > 63.4 → DANGER"""
    assert get_aqi_level_from_score(63.5) == "DANGER"
    assert get_aqi_level_from_score(80)   == "DANGER"
    assert get_aqi_level_from_score(100)  == "DANGER"

def test_aqi_colors():
    """Couleurs officielles par niveau"""
    assert get_aqi_color("SAFE")      == "#007A5E"
    assert get_aqi_color("VIGILANCE") == "#FCD116"
    assert get_aqi_color("DANGER")    == "#CE1126"

def test_aqi_label_urgent():
    """DANGER doit afficher 'Urgent' (pas DANGER)"""
    assert get_aqi_label("DANGER", "fr") == "Urgent"
    assert get_aqi_label("SAFE",   "fr") == "Safe"

def test_is_danger_level():
    """is_danger_level retourne True seulement au-dessus de 63.4"""
    assert is_danger_level(63.4) == False
    assert is_danger_level(63.5) == True
    assert is_danger_level(100)  == True


# ── Tests température ─────────────────────────────────────────────

def test_temp_frais():
    """< 22°C → Frais → Bleu"""
    assert get_temp_class(15)   == "Frais"
    assert get_temp_class(21.9) == "Frais"
    assert get_temp_color(15)   == "#1A6FA6"

def test_temp_tempere():
    """22–24°C → Tempéré → Vert"""
    assert get_temp_class(22)   == "Tempéré"
    assert get_temp_class(24)   == "Tempéré"
    assert get_temp_color(23)   == "#007A5E"

def test_temp_chaud():
    """24–26°C → Chaud → Jaune"""
    assert get_temp_class(24.5) == "Chaud"
    assert get_temp_class(26)   == "Chaud"
    assert get_temp_color(25)   == "#FCD116"

def test_temp_tres_chaud():
    """> 26°C → Très chaud → Rouge"""
    assert get_temp_class(26.1) == "Très chaud"
    assert get_temp_class(40)   == "Très chaud"
    assert get_temp_color(35)   == "#CE1126"


# ── Tests précipitations ──────────────────────────────────────────

def test_precip_tres_sec():
    """< 2.5mm → Très sec → Rouge"""
    assert get_precip_class(0)   == "Très sec"
    assert get_precip_class(2.4) == "Très sec"
    assert get_precip_color(1)   == "#CE1126"

def test_precip_sec():
    """2.5–4.5mm → Sec → Jaune"""
    assert get_precip_class(2.5) == "Sec"
    assert get_precip_class(4.5) == "Sec"
    assert get_precip_color(3)   == "#FCD116"

def test_precip_modere():
    """4.5–6.5mm → Modéré → Orange"""
    assert get_precip_class(5)   == "Modéré"
    assert get_precip_class(6.5) == "Modéré"
    assert get_precip_color(5.5) == "#E07800"

def test_precip_humide():
    """6.5–8mm → Humide → Vert"""
    assert get_precip_class(7)   == "Humide"
    assert get_precip_class(8)   == "Humide"
    assert get_precip_color(7.5) == "#007A5E"

def test_precip_inondation():
    """> 8mm → Risque inondation → Bleu"""
    assert get_precip_class(8.1) == "Risque inondation"
    assert get_precip_class(30)  == "Risque inondation"
    assert get_precip_color(10)  == "#1A4D8F"
