"""
AirSentinel CM - Interactive Map Page
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import random

from utils.translations import t
from utils.weather_api import CAMEROON_CITIES, CITIES, REGIONS
from utils.database import get_all_predictions_aqi, get_all_predictions_heatwave
from utils.styles import COLORS, RISK_COLORS


def show_map_page():
    lang = st.session_state.get("lang", "fr")
    dark = st.session_state.get("dark_mode", False)

    st.markdown(f"""
    <div class="page-header">
        <h1>🗺️ {t('map_title', lang)}</h1>
        <p>📍 40 villes • 10 régions | Open-Meteo API</p>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        region_filter = st.selectbox(
            t("filter_region", lang),
            [t("all_regions", lang)] + REGIONS,
            key="map_region"
        )
    with col_f2:
        risk_filter = st.selectbox(
            t("filter_risk", lang),
            [t("all_levels", lang), "SAFE", "VIGILANCE", "DANGER"],
            key="map_risk"
        )
    with col_f3:
        score_range = st.slider(
            t("filter_score", lang),
            min_value=0, max_value=100,
            value=(0, 100),
            key="map_score_range"
        )

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🌫️ {t('tab_aqi_map', lang)}",
        f"🌡️ {t('tab_temp_map', lang)}",
        f"💧 {t('tab_precip_map', lang)}",
        f"🌡️🔥 {t('tab_hw_map', lang)}",
    ])

    # Build city data
    city_data = _build_city_data()

    # Apply filters
    filtered_data = _apply_filters(city_data, region_filter, risk_filter, score_range,
                                   t("all_regions", lang), t("all_levels", lang))

    with tab1:
        _show_aqi_map(filtered_data, lang, dark)
    with tab2:
        _show_temp_map(filtered_data, lang, dark)
    with tab3:
        _show_precip_map(filtered_data, lang, dark)
    with tab4:
        _show_hw_map(filtered_data, lang, dark)

    # Summary table
    st.markdown("---")
    st.markdown(f'<div class="section-title">📋 {t("summary_table", lang)}</div>',
                unsafe_allow_html=True)
    _show_summary_table(filtered_data, lang)


def _build_city_data() -> dict:
    """Build city data from predictions + simulated data."""
    aqi_preds = get_all_predictions_aqi(limit=500)
    hw_preds = get_all_predictions_heatwave(limit=500)

    city_aqi = {}
    for p in aqi_preds:
        city = p.get("city", "")
        if city and city not in city_aqi:
            city_aqi[city] = p

    city_hw = {}
    for p in hw_preds:
        city = p.get("city", "")
        if city and city not in city_hw:
            city_hw[city] = p

    result = {}
    for city, info in CAMEROON_CITIES.items():
        if city in city_aqi:
            aqi_score = city_aqi[city].get("score", 0)
            aqi_risk = city_aqi[city].get("risk_level", "SAFE")
        else:
            aqi_score = round(random.uniform(5, 55), 1)
            aqi_risk = "SAFE" if aqi_score <= 33 else "VIGILANCE" if aqi_score <= 66 else "DANGER"

        if city in city_hw:
            hw_prob = city_hw[city].get("probability", 0)
            hw_pred = city_hw[city].get("prediction", 0)
        else:
            hw_prob = round(random.uniform(0.02, 0.35), 3)
            hw_pred = 1 if hw_prob >= 0.20 else 0

        # Simulated weather
        temp_max = round(random.uniform(22, 40), 1)
        precip = round(random.uniform(0, 20), 1)

        result[city] = {
            "lat": info["lat"],
            "lon": info["lon"],
            "region": info["region"],
            "aqi_score": aqi_score,
            "aqi_risk": aqi_risk,
            "hw_prob": hw_prob,
            "hw_pred": hw_pred,
            "hw_risk": "DANGER" if hw_pred == 1 else ("VIGILANCE" if hw_prob >= 0.10 else "SAFE"),
            "temp_max": temp_max,
            "precip": precip,
        }

    return result


def _apply_filters(data, region_filter, risk_filter, score_range, all_regions_label, all_levels_label):
    filtered = {}
    for city, info in data.items():
        if region_filter != all_regions_label and info["region"] != region_filter:
            continue
        if risk_filter != all_levels_label and info["aqi_risk"] != risk_filter:
            continue
        if not (score_range[0] <= info["aqi_score"] <= score_range[1]):
            continue
        filtered[city] = info
    return filtered


def _create_base_map(dark: bool) -> folium.Map:
    tile = "CartoDB dark_matter" if dark else "CartoDB positron"
    m = folium.Map(
        location=[5.5, 12.5],
        zoom_start=5.5,
        tiles=tile,
        control_scale=True,
    )
    return m


def _add_city_marker(m, city, info, color, popup_html, radius=8, blink=False):
    """Add a circle marker to the folium map."""
    # Blinking effect via CSS for DANGER cities
    folium.CircleMarker(
        location=[info["lat"], info["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=2,
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=city,
    ).add_to(m)

    # Add blinking overlay for danger
    if blink:
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=radius + 4,
            color=color,
            fill=False,
            fill_opacity=0,
            weight=1.5,
            opacity=0.4,
        ).add_to(m)


def _show_aqi_map(city_data, lang, dark):
    m = _create_base_map(dark)

    for city, info in city_data.items():
        color = RISK_COLORS.get(info["aqi_risk"], "#007A5E")
        radius = 14 if info["aqi_risk"] == "DANGER" else (10 if info["aqi_risk"] == "VIGILANCE" else 7)
        blink = info["aqi_risk"] == "DANGER"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif; min-width:200px;">
            <b style="font-size:1rem; color:{color};">{city}</b><br>
            <span style="color:#666; font-size:0.8rem;">{info['region']}</span><hr style="margin:4px 0;">
            <b>Score IQA:</b> {info['aqi_score']:.1f}<br>
            <b>Niveau:</b> <span style="color:{color}; font-weight:bold;">{info['aqi_risk']}</span><br>
            <b>Temp. max:</b> {info['temp_max']:.1f}°C<br>
            <b>Précip.:</b> {info['precip']:.1f} mm
        </div>
        """
        _add_city_marker(m, city, info, color, popup_html, radius, blink)

    # Add legend
    legend_html = """
    <div style="position:fixed; bottom:20px; left:20px; z-index:1000;
                background:rgba(255,255,255,0.95); border-radius:10px;
                padding:10px 15px; box-shadow:0 2px 10px rgba(0,0,0,0.2);
                font-family:Arial,sans-serif; font-size:12px;">
        <b>Indice Qualité de l'Air</b><br>
        <span style="color:#007A5E;">●</span> SAFE (0–33)<br>
        <span style="color:#FCD116;">●</span> VIGILANCE (34–66)<br>
        <span style="color:#CE1126;">●</span> DANGER (67–100)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, use_container_width=True, height=480, returned_objects=[])


def _show_temp_map(city_data, lang, dark):
    m = _create_base_map(dark)

    for city, info in city_data.items():
        temp = info["temp_max"]
        if temp < 25:
            color = "#1A4D8F"
        elif temp < 30:
            color = "#007A5E"
        elif temp < 35:
            color = "#FCD116"
        else:
            color = "#CE1126"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif;">
            <b>{city}</b> ({info['region']})<hr style="margin:4px 0;">
            <b>Temp. max:</b> {temp:.1f}°C
        </div>
        """
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            weight=2,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {temp:.1f}°C",
        ).add_to(m)

    legend_html = """
    <div style="position:fixed; bottom:20px; left:20px; z-index:1000;
                background:rgba(255,255,255,0.95); border-radius:10px;
                padding:10px 15px; box-shadow:0 2px 10px rgba(0,0,0,0.2);
                font-family:Arial,sans-serif; font-size:12px;">
        <b>Température max (°C)</b><br>
        <span style="color:#1A4D8F;">●</span> &lt; 25°C<br>
        <span style="color:#007A5E;">●</span> 25–30°C<br>
        <span style="color:#FCD116;">●</span> 30–35°C<br>
        <span style="color:#CE1126;">●</span> &gt; 35°C
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, use_container_width=True, height=480, returned_objects=[])


def _show_precip_map(city_data, lang, dark):
    m = _create_base_map(dark)

    for city, info in city_data.items():
        precip = info["precip"]
        if precip < 1:
            color = "#CE1126"
        elif precip < 5:
            color = "#FCD116"
        elif precip < 15:
            color = "#007A5E"
        else:
            color = "#1A4D8F"

        radius = max(6, min(14, int(precip / 3) + 6))
        popup_html = f"""
        <div style="font-family:Arial,sans-serif;">
            <b>{city}</b> ({info['region']})<hr style="margin:4px 0;">
            <b>Précipitations:</b> {precip:.1f} mm
        </div>
        """
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {precip:.1f} mm",
        ).add_to(m)

    legend_html = """
    <div style="position:fixed; bottom:20px; left:20px; z-index:1000;
                background:rgba(255,255,255,0.95); border-radius:10px;
                padding:10px 15px; box-shadow:0 2px 10px rgba(0,0,0,0.2);
                font-family:Arial,sans-serif; font-size:12px;">
        <b>Précipitations (mm)</b><br>
        <span style="color:#CE1126;">●</span> &lt; 1 mm<br>
        <span style="color:#FCD116;">●</span> 1–5 mm<br>
        <span style="color:#007A5E;">●</span> 5–15 mm<br>
        <span style="color:#1A4D8F;">●</span> &gt; 15 mm
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, use_container_width=True, height=480, returned_objects=[])


def _show_hw_map(city_data, lang, dark):
    m = _create_base_map(dark)

    for city, info in city_data.items():
        hw_risk = info["hw_risk"]
        color = RISK_COLORS.get(hw_risk, "#007A5E")
        prob_pct = info["hw_prob"] * 100
        radius = 14 if hw_risk == "DANGER" else (10 if hw_risk == "VIGILANCE" else 7)
        blink = hw_risk == "DANGER"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif; min-width:200px;">
            <b style="color:{color};">{city}</b><br>
            <span style="color:#666; font-size:0.8rem;">{info['region']}</span><hr style="margin:4px 0;">
            <b>Probabilité vague:</b> {prob_pct:.0f}%<br>
            <b>Détection:</b> {'⚠️ Oui' if info['hw_pred'] == 1 else '✅ Non'}<br>
            <b>Niveau:</b> <span style="color:{color};">{hw_risk}</span>
        </div>
        """
        _add_city_marker(m, city, info, color, popup_html, radius, blink)

    legend_html = """
    <div style="position:fixed; bottom:20px; left:20px; z-index:1000;
                background:rgba(255,255,255,0.95); border-radius:10px;
                padding:10px 15px; box-shadow:0 2px 10px rgba(0,0,0,0.2);
                font-family:Arial,sans-serif; font-size:12px;">
        <b>Indice Vague de Chaleur</b><br>
        <span style="color:#007A5E;">●</span> SAFE (&lt;10%)<br>
        <span style="color:#FCD116;">●</span> VIGILANCE (10–20%)<br>
        <span style="color:#CE1126;">●</span> DANGER (&gt;20%)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, use_container_width=True, height=480, returned_objects=[])


def _show_summary_table(city_data, lang):
    rows = []
    for city, info in city_data.items():
        rows.append({
            t("city", lang): city,
            t("region", lang): info["region"],
            "Score IQA": f"{info['aqi_score']:.1f}",
            "Niveau IQA": info["aqi_risk"],
            "Prob. Chaleur": f"{info['hw_prob']:.0%}",
            "Niveau Chaleur": info["hw_risk"],
            "Temp. max (°C)": f"{info['temp_max']:.1f}",
            "Précip. (mm)": f"{info['precip']:.1f}",
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # CSV export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇️ {t('export_csv', lang)}",
            data=csv,
            file_name="airsentinel_cities_summary.csv",
            mime="text/csv",
        )
