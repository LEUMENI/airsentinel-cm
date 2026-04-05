"""
AirSentinel CM - Interactive Map Page
Carte sobre unifiée lisible en mode clair/sombre
Style Belgrade pour vagues de chaleur
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.graph_objects as go
import random

from utils.translations import CAMEROON_CITIES, REGIONS
from utils.models import CITY_THRESHOLDS
from utils.thresholds import (
    get_aqi_level_from_score, get_aqi_color,
    get_temp_color, get_temp_label,
    get_precip_color, get_precip_class,
    AQI_SCORE_SAFE_MAX, AQI_SCORE_VIGILANCE_MAX,
    HW_COLORS, is_danger_level,
)
from utils.database import create_alert, log_activity, get_admin_emails


def _mock_scores(seed=42):
    random.seed(seed)
    scores = {}
    for city, info in CAMEROON_CITIES.items():
        s = random.uniform(5, 80)
        if info["region"] in ["Extreme-Nord", "Nord"]:
            s = random.uniform(45, 90)
        hw = random.uniform(0, 0.85)
        if info["region"] in ["Extreme-Nord", "Nord"]:
            hw = random.uniform(0.4, 0.95)
        scores[city] = {**info, "score": round(s, 1), "hw_prob": round(hw, 3),
                        "temp": round(random.uniform(22, 42), 1),
                        "precip": round(random.uniform(0, 30), 1)}
    return scores


def show_map():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user  = st.session_state.user 
    paper = "#2C2C2E" if dark else "#FFFFFF"
    text  = "#F2F2F7" if dark else "#2C2C2E"
    sub   = "#AEAEB2" if dark else "#636366"
    brd   = "#3A3A3C" if dark else "#D4CDB8"

    st.markdown(f"""
    <div class='section-header'>
        <h3>{'🗺️ Carte Interactive -Cameroun' if lang=='fr' else '🗺️ Interactive Map -Cameroon'}</h3>
        <p>{'Visualisation géospatiale des indices de qualité de l\'air et des vagues de chaleur' if lang=='fr'
            else 'Geospatial visualization of air quality indices and heatwaves'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Filtres
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        region_f = st.selectbox("Région" if lang=="fr" else "Region",
                                 ["Toutes" if lang=="fr" else "All"] + REGIONS)
    with f2:
        risk_f = st.selectbox("Niveau de risque" if lang=="fr" else "Risk level",
                               ["Tous" if lang=="fr" else "All", "SAFE", "VIGILANCE", "DANGER"])
    with f3:
        score_range = st.slider("Plage score AQI" if lang=="fr" else "AQI score range",
                                 0, 100, (0, 100))

    city_data = _mock_scores()

    # ── Alertes automatiques ─────────────────────────────────────────
    danger_cities = [(c, d) for c, d in city_data.items()
                    if d["score"] > AQI_SCORE_VIGILANCE_MAX]

    if danger_cities:
        if "map_alerts_sent" not in st.session_state:
            st.session_state["map_alerts_sent"] = set()

        new_alerts = []
        for city, data in danger_cities:
            key = f"{city}_{data['score']:.0f}"
            if key not in st.session_state["map_alerts_sent"]:
                create_alert(user["id"], city, "aqi",
                            AQI_SCORE_VIGILANCE_MAX,
                            score=data["score"], risk_level="DANGER")
                new_alerts.append((city, data["score"]))
                st.session_state["map_alerts_sent"].add(key)

        if new_alerts:
            try:
                from utils.email_service import send_alert_to_admin
                admin_emails = get_admin_emails()
                for admin_email in admin_emails:
                    for city, score in new_alerts:
                        send_alert_to_admin(admin_email, city, score, "DANGER", "aqi")
            except Exception:
                pass

            cities_str = ", ".join([f"**{c}** ({s:.0f}/100)" for c, s in new_alerts[:5]])
            st.warning(f"⚡ **{len(new_alerts)} alerte(s) URGENT** : {cities_str} — Admin notifié.")


    # Apply filters
    filtered = {c: d for c, d in city_data.items()
                if (region_f in ["Toutes", "All"] or d["region"] == region_f)
                and (risk_f in ["Tous", "All"] or
                     (risk_f == "SAFE" and d["score"] <= 33) or
                     (risk_f == "VIGILANCE" and 33 < d["score"] <= 66) or
                     (risk_f == "DANGER" and d["score"] > 66))
                and score_range[0] <= d["score"] <= score_range[1]}

    tab1, tab2, tab3, tab4 = st.tabs([
        f"🌫️ {'Proxy PM2.5' if lang=='fr' else 'Proxy PM2.5'}",
        f"🔥 {'Vagues de chaleur' if lang=='fr' else 'Heatwaves'}",
        f"🌡️ {'Températures' if lang=='fr' else 'Temperatures'}",
        f"🌧️ {'Précipitations' if lang=='fr' else 'Precipitation'}",
        
    ])

    with tab1:
        _folium_map(filtered, "aqi", dark, lang)
    with tab2:
        _folium_map(filtered, "temp", dark, lang)
    with tab3:
        _folium_map(filtered, "precip", dark, lang)
    with tab4:
        _folium_map_heatwave_belgrade(filtered, dark, lang, paper, text, sub, brd)

    st.markdown("---")
    st.markdown(f"<div class='form-label-custom'>{'📋 Tableau récapitulatif' if lang=='fr' else '📋 Summary table'}</div>", unsafe_allow_html=True)

    if filtered:
        df = pd.DataFrame([{
            "Ville": c,
            "Région": d["region"],
            "Proxy PM2.5": d["score"],
            "Vague (%)": f"{d['hw_prob']*100:.0f}%",
            "Temp (°C)": d["temp"],
            "Préc. (mm)": d["precip"],
            "Niveau": "DANGER" if d["score"] > 66 else ("VIGILANCE" if d["score"] > 33 else "SAFE"),
        } for c, d in filtered.items()])

        def style_level(val):
            colors = {"SAFE": "background-color:#007A5E;color:white",
                      "VIGILANCE": "background-color:#B8860B;color:white",
                      "DANGER": "background-color:#B91C1C;color:white"}
            return colors.get(val, "")

        styled = df.style.map(style_level, subset=["Niveau"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Graphique régions
        region_df = df.groupby("Région")["Proxy PM2.5"].mean().round(1).reset_index()
        colors_r = [get_aqi_color(get_aqi_level_from_score(v))
            for v in region_df["Proxy PM2.5"]]
        fig = go.Figure(go.Bar(
            x=region_df["Proxy PM2.5"], y=region_df["Région"],
            orientation="h",
            marker=dict(color=colors_r, opacity=0.85),
            text=region_df["Proxy PM2.5"].astype(str),
            textposition="outside", textfont=dict(color=text),
        ))
        fig.add_vline(x=33, line_dash="dot", line_color="#007A5E", opacity=0.6,
                      annotation_text="Safe", annotation_font_color="#007A5E")
        fig.add_vline(x=66, line_dash="dot", line_color="#B91C1C", opacity=0.6,
                      annotation_text="Danger", annotation_font_color="#B91C1C")
        fig.update_layout(
            paper_bgcolor=paper, plot_bgcolor=paper, font=dict(color=text),
            height=280, margin=dict(l=10, r=60, t=20, b=10),
            xaxis=dict(range=[0, 115], showgrid=False),
            yaxis=dict(showgrid=False),
            title=dict(text="Proxy PM2.5 moyen par région" if lang=="fr" else "Average Proxy PM2.5 by region",
                       font=dict(color=text, size=13)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _folium_map(city_data, map_type, dark, lang):
    """Carte Folium sobre -fond unique lisible clair/sombre."""
    tile = "CartoDB dark_matter" if dark else "CartoDB positron"
    m = folium.Map(location=[5.5, 12.3], zoom_start=6, tiles=tile,
                   prefer_canvas=True)

    for city, data in city_data.items():
        score = data["score"]
        temp  = data["temp"]
        precip= data["precip"]

        if map_type == "aqi":
            val = score
            color = "#007A5E" if val <= 33 else ("#B8860B" if val <= 66 else "#B91C1C")
            radius = max(6, val / 6)
            popup_html = f"""
            <div style='font-family:Inter,sans-serif; padding:6px; min-width:140px;'>
                <b style='color:{color}; font-size:14px;'>{city}</b><br>
                <span style='color:#666; font-size:11px;'>{data['region']}</span><br>
                <b>Proxy PM2.5: {val:.1f}/100</b><br>
                PM2.5: ~{val*35/100:.1f} µg/m³<br>
                <span style='background:{color}; color:white; padding:1px 8px;
                             border-radius:10px; font-size:10px; font-weight:700;'>
                    {'DANGER' if val > 66 else ('VIGILANCE' if val > 33 else 'SAFE')}
                </span>
            </div>"""
            danger = val > 66

        elif map_type == "temp":
            val = temp
            ratio = min(1, max(0, (val - 22) / 20))
            r_c = min(255, int(ratio * 200 + 55))
            b_c = max(0, int((1-ratio) * 180))
            color = f"#{r_c:02x}5A{b_c:02x}"
            radius = 7
            popup_html = f"<b>{city}</b><br>Température: <b>{val:.1f}°C</b>"
            danger = val > 38

        elif map_type == "precip":
            val = precip
            ratio = min(1, val / 30)
            b_c = min(255, int(ratio * 200 + 55))
            color = f"#1A5A{b_c:02x}"
            radius = max(5, val / 3)
            popup_html = f"<b>{city}</b><br>Précipitations: <b>{val:.1f} mm</b>"
            danger = False

        # Marqueur avec effet pulse pour danger
        if danger:
            icon_html = f"""
            <div style='position:relative;'>
              <div style='background:{color}; width:{int(radius)*2}px; height:{int(radius)*2}px;
                          border-radius:50%; border:2px solid white; opacity:0.9;
                          animation:pulse 2s infinite;'></div>
              <style>@keyframes pulse{{
                0%,100%{{transform:scale(1);opacity:0.9;}}
                50%{{transform:scale(1.4);opacity:0.5;}}
              }}</style>
            </div>"""
            folium.Marker(
                [data["lat"], data["lon"]],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.DivIcon(html=icon_html,
                                     icon_size=(int(radius)*2, int(radius)*2),
                                     icon_anchor=(int(radius), int(radius)))
            ).add_to(m)
        else:
            folium.CircleMarker(
                [data["lat"], data["lon"]], radius=radius,
                color="white", weight=1.5, fill=True,
                fill_color=color, fill_opacity=0.85,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=city,
            ).add_to(m)

    st_folium(m, width=None, height=480, returned_objects=[])


def _folium_map_heatwave_belgrade(city_data, dark, lang, paper, text, sub, brd):
    """
    Carte vagues de chaleur style Belgrade:
    - Fond sobre (carto positron/dark)
    - Cercles proportionnels à la probabilité
    - Palette sobre: vert→doré→rouge profond
    - Tooltips détaillés avec seuil P90
    """
    tile = "CartoDB dark_matter" if dark else "CartoDB positron"
    m = folium.Map(location=[5.5, 12.3], zoom_start=6, tiles=tile,
                   prefer_canvas=True)

    for city, data in city_data.items():
        prob  = data["hw_prob"]
        temp  = data["temp"]
        thr   = CITY_THRESHOLDS.get(city, 36.0)
        above = temp > thr

        # Palette sobre Belgrade
        if prob <= 0.20:
            color = "#2D7A5E"   # vert foncé sobre
            level = "SAFE"
        elif prob <= 0.50:
            color = "#9A7000"   # doré sobre
            level = "VIGILANCE"
        else:
            color = "#9A1515"   # rouge profond sobre
            level = "DANGER"

        radius = max(6, int(prob * 28))

        popup_html = f"""
        <div style='font-family:Inter,sans-serif; padding:8px; min-width:180px;'>
            <b style='color:{color}; font-size:13px;'>{city}</b>
            <div style='color:#666; font-size:10px; margin-bottom:6px;'>{data['region']}</div>
            <table style='width:100%; font-size:11px; border-collapse:collapse;'>
                <tr><td style='color:#888;'>Probabilité vague</td>
                    <td style='font-weight:700; color:{color};'>{prob*100:.0f}%</td></tr>
                <tr><td style='color:#888;'>Tmax aujourd'hui</td>
                    <td><b>{temp:.1f}°C</b></td></tr>
                <tr><td style='color:#888;'>Seuil P90 local</td>
                    <td><b>{thr:.1f}°C</b></td></tr>
                <tr><td style='color:#888;'>Statut</td>
                    <td>{'🔥 Au-dessus' if above else '✅ Normal'}</td></tr>
            </table>
            <div style='margin-top:6px; background:{color}; color:white;
                        padding:2px 8px; border-radius:10px; font-size:10px;
                        font-weight:700; display:inline-block;'>{level}</div>
        </div>"""

        # Cercles proportionnels
        folium.CircleMarker(
            [data["lat"], data["lon"]], radius=radius,
            color="white" if dark else "#F0F0F0", weight=1,
            fill=True, fill_color=color, fill_opacity=0.80,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{city}: {prob*100:.0f}% ({level})",
        ).add_to(m)

        # Croix pour les villes au-dessus du seuil
        if above:
            folium.Marker(
                [data["lat"] + 0.15, data["lon"]],
                icon=folium.DivIcon(
                    html=f'<div style="color:{color}; font-size:10px; font-weight:900;">▲</div>',
                    icon_size=(12, 12), icon_anchor=(6, 6)
                )
            ).add_to(m)

    # Légende manuelle
    legend_html = f"""
    <div style='position:fixed; bottom:30px; left:30px; z-index:999;
                background:{"rgba(28,28,30,0.92)" if dark else "rgba(255,255,255,0.92)"};
                color:{"#F2F2F7" if dark else "#2C2C2E"};
                padding:14px 18px; border-radius:10px;
                border:1px solid {"#3A3A3C" if dark else "#D4CDB8"};
                font-family:Inter,sans-serif; font-size:11px;
                box-shadow:0 4px 16px rgba(0,0,0,0.2);'>
        <div style='font-weight:700; margin-bottom:8px;'>
            {'🌡️ Risque Vague de Chaleur' if lang=='fr' else '🌡️ Heatwave Risk'}
        </div>
        <div style='display:flex; align-items:center; gap:8px; margin-bottom:4px;'>
            <div style='width:12px; height:12px; border-radius:50%; background:#2D7A5E;'></div>
            <span>SAFE (≤ 20%)</span>
        </div>
        <div style='display:flex; align-items:center; gap:8px; margin-bottom:4px;'>
            <div style='width:16px; height:16px; border-radius:50%; background:#9A7000;'></div>
            <span>VIGILANCE (20–50%)</span>
        </div>
        <div style='display:flex; align-items:center; gap:8px; margin-bottom:6px;'>
            <div style='width:20px; height:20px; border-radius:50%; background:#9A1515;'></div>
            <span>DANGER (> 50%)</span>
        </div>
        <div style='font-size:10px; color:{"#AEAEB2" if dark else "#636366"};'>
            ▲ = T > P90 local<br>
            {'Taille ∝ probabilité' if lang=='fr' else 'Size ∝ probability'}
        </div>
    </div>"""

    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=None, height=500, returned_objects=[])

    # Graphique complémentaire style Belgrade
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='form-label-custom'>{'📊 Probabilité vague de chaleur par ville (Top 15)' if lang=='fr' else '📊 Heatwave probability by city (Top 15)'}</div>", unsafe_allow_html=True)

    sorted_cities = sorted(city_data.items(), key=lambda x: x[1]["hw_prob"], reverse=True)[:15]
    cities_names = [c for c, _ in sorted_cities]
    probs_vals   = [d["hw_prob"] * 100 for _, d in sorted_cities]
    temps_vals   = [d["temp"] for _, d in sorted_cities]
    thrs         = [CITY_THRESHOLDS.get(c, 36.0) for c, _ in sorted_cities]

    bar_colors2 = ["#9A1515" if p > 50 else ("#9A7000" if p > 20 else "#2D7A5E") for p in probs_vals]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=cities_names, x=probs_vals, orientation="h", name="Prob. vague",
        marker=dict(color=bar_colors2, opacity=0.85,
                    line=dict(color="#1C1C1E" if dark else "#F7F5F0", width=0.5)),
        text=[f"{v:.0f}%" for v in probs_vals],
        textposition="outside", textfont=dict(color=text, size=10),
    ))
    fig.add_vline(x=20, line_dash="dot", line_color="#9A7000", opacity=0.7,
                  annotation_text="20%", annotation_font_color="#9A7000")
    fig.add_vline(x=50, line_dash="dot", line_color="#9A1515", opacity=0.7,
                  annotation_text="50%", annotation_font_color="#9A1515")
    fig.update_layout(
        paper_bgcolor=paper, plot_bgcolor=paper, font=dict(color=text),
        height=340, margin=dict(l=10, r=60, t=20, b=10),
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor=brd, gridwidth=0.5,
                   ticksuffix="%"),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
