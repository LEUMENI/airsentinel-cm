"""
AirSentinel CM - Dashboard
Couleurs sobres, KPIs, cartes, graphes, nomenclature Proxy PM2.5
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

from utils.database import get_dashboard_stats, get_all_predictions_aqi
from utils.translations import t, CAMEROON_CITIES
from utils.thresholds import (
    AQI_SCORE_SAFE_MAX, AQI_SCORE_VIGILANCE_MAX,
    get_aqi_color, get_aqi_level_from_score
)


def show_dashboard():
    lang  = st.session_state.lang
    dark  = st.session_state.dark_mode
    paper = "#2C2C2E" if dark else "#FFFFFF"
    text  = "#F2F2F7" if dark else "#2C2C2E"
    sub   = "#AEAEB2" if dark else "#636366"
    brd   = "#3A3A3C" if dark else "#D4CDB8"
    kaki  = "#6B7355" if dark else "#4A5240"

    st.markdown(f"""
    <div class='section-header'>
        <h3>{'📊 Tableau de bord - AirSentinel CM' if lang=='fr' else '📊 Dashboard - AirSentinel CM'}</h3>
        <p>{'Vue d\'ensemble de la surveillance de la qualité de l\'air au Cameroun' if lang=='fr'
            else 'Overview of air quality monitoring in Cameroon'}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────
    stats = get_dashboard_stats()
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "🔬", stats["total_predictions"],  "Total prédictions" if lang=="fr" else "Total predictions", kaki),
        (k2, "👥", stats["total_users"],         "Utilisateurs"      if lang=="fr" else "Users",             "#4A6090"),
        (k3, "🔔", stats["active_alerts"],       "Alertes actives"   if lang=="fr" else "Active alerts",
         "#9A1515" if stats["active_alerts"] > 0 else "#4A5240"),
        (k4, "📅", stats["predictions_today"],   "Aujourd'hui"       if lang=="fr" else "Today",             "#4A5240"),
    ]
    for col, icon, val, label, color in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card' style='border-left-color:{color};'>
                <div style='font-size:20px;'>{icon}</div>
                <div class='kpi-value' style='color:{color};'>{val}</div>
                <div class='kpi-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LIGNE 1 : Carte + Camembert ───────────────────────────────────
    col_top_l, col_top_r = st.columns(2)

    with col_top_l:
        st.markdown(f"<div class='form-label-custom'>{'🗺️ Carte Proxy PM2.5 - Cameroun' if lang=='fr' else '🗺️ Proxy PM2.5 Map - Cameroon'}</div>",
                    unsafe_allow_html=True)
        _show_aqi_map_plotly(dark, paper, text, sub, brd, lang)

    with col_top_r:
        st.markdown(f"<div class='form-label-custom'>{'🍩 Distribution des niveaux de risque' if lang=='fr' else '🍩 Risk level distribution'}</div>",
                    unsafe_allow_html=True)
        _show_risk_pie(dark, paper, text, lang)

    # ── LIGNE 2 : Évolution + Score par région ────────────────────────
    col_bot_l, col_bot_r = st.columns(2)

    with col_bot_l:
        st.markdown(f"<div class='form-label-custom'>{'📈 Évolution Proxy PM2.5 - 30 derniers jours' if lang=='fr' else '📈 Proxy PM2.5 Evolution - Last 30 days'}</div>",
                    unsafe_allow_html=True)
        _show_evolution(dark, paper, text, brd, lang)

    with col_bot_r:
        st.markdown(f"<div class='form-label-custom'>{'📊 Score moyen par région' if lang=='fr' else '📊 Average score by region'}</div>",
                    unsafe_allow_html=True)
        _show_region_bars(dark, paper, text, brd, lang)

    # ── Dernières prédictions ─────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"<div class='form-label-custom'>{'🕒 10 dernières prédictions Proxy PM2.5' if lang=='fr' else '🕒 Last 10 Proxy PM2.5 predictions'}</div>",
                unsafe_allow_html=True)
    preds = get_all_predictions_aqi(limit=10)
    if preds:
        df = pd.DataFrame(preds)
        cols_show = [c for c in ["city","region","date_pred","score","risk_level","username","created_at"]
                     if c in df.columns]
        df = df[cols_show]
        col_map = {
            "city": "Ville", "region": "Région", "date_pred": "Date",
            "score": "Proxy PM2.5", "risk_level": "Niveau",
            "username": "Utilisateur", "created_at": "Enregistré le"
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        def style_r(val):
            c = {"SAFE":      "background-color:#007A5E;color:white",
                 "VIGILANCE": "background-color:#B8860B;color:white",
                 "DANGER":    "background-color:#B91C1C;color:white"}
            return c.get(val, "")

        if "Niveau" in df.columns:
            st.dataframe(df.style.map(style_r, subset=["Niveau"]),
                         use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune prédiction." if lang=="fr" else "No predictions yet.")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_city_scores():
    random.seed(42)
    out = {}
    for city, info in CAMEROON_CITIES.items():
        s = random.uniform(5, 80)
        if info["region"] in ["Extreme-Nord", "Nord"]:
            s = random.uniform(45, 90)
        out[city] = {**info, "score": round(s, 1)}
    return out


def _show_aqi_map_plotly(dark, paper, text, sub, brd, lang):
    scores = _mock_city_scores()
    lats, lons, names, vals, hovers = [], [], [], [], []

    for city, d in scores.items():
        s = d["score"]
        lats.append(d["lat"]); lons.append(d["lon"])
        names.append(city);    vals.append(s)
        pm25 = round(s / 100 * 35, 2)
        level = get_aqi_level_from_score(s)
        label = {"SAFE": "Safe", "VIGILANCE": "Vigilance", "DANGER": "Urgent"}.get(level, level)
        hovers.append(f"<b>{city}</b><br>{d['region']}<br>Proxy PM2.5: {s:.1f}/100<br>PM2.5: ~{pm25} µg/m³<br>{label}")

    fig = go.Figure()
    for lvl, lc, lb in [
        ("SAFE",      "#007A5E", f"Safe (0–{AQI_SCORE_SAFE_MAX})"),
        ("VIGILANCE", "#B8860B", f"Vigilance ({AQI_SCORE_SAFE_MAX}–{AQI_SCORE_VIGILANCE_MAX})"),
        ("DANGER",    "#B91C1C", f"Urgent (>{AQI_SCORE_VIGILANCE_MAX})"),
    ]:
        mask = [i for i, v in enumerate(vals)
                if get_aqi_level_from_score(v) == lvl]
        if mask:
            fig.add_trace(go.Scattergeo(
                lat=[lats[i] for i in mask],
                lon=[lons[i] for i in mask],
                mode="markers",
                marker=dict(
                    size=[max(8, vals[i] / 5) for i in mask],
                    color=lc, opacity=0.85,
                    line=dict(color="#F7F5F0" if not dark else "#1C1C1E", width=1)
                ),
                hovertext=[hovers[i] for i in mask],
                hoverinfo="text",
                name=lb,
            ))

    fig.update_layout(
        geo=dict(
            scope="africa", center=dict(lat=5.5, lon=12.3), projection_scale=8,
            showland=True,       landcolor="#2A3020"  if dark else "#EEF0E8",
            showocean=True,      oceancolor="#1A2030" if dark else "#E8EEF5",
            showcoastlines=True, coastlinecolor="#555" if dark else "#CCCCCC",
            showcountries=True,  countrycolor="#666"  if dark else "#BBBBBB",
            showframe=False,     bgcolor=paper,
        ),
        paper_bgcolor=paper, plot_bgcolor=paper,
        font=dict(color=text, family="Inter"), height=280,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor=paper, bordercolor=brd, borderwidth=1,
                    font=dict(size=10, color=text)),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _show_risk_pie(dark, paper, text, lang):
    preds  = get_all_predictions_aqi(limit=500)
    counts = {"SAFE": 45, "VIGILANCE": 35, "DANGER": 20}
    if preds:
        counts = {"SAFE": 0, "VIGILANCE": 0, "DANGER": 0}
        for p in preds:
            lvl = p.get("risk_level", "SAFE")
            counts[lvl] = counts.get(lvl, 0) + 1

    fig = go.Figure(go.Pie(
        labels=list(counts.keys()),
        values=list(counts.values()),
        marker=dict(colors=["#007A5E", "#B8860B", "#B91C1C"]),
        hole=0.5, textinfo="label+percent",
        textfont=dict(color=text, size=11),
        insidetextorientation="radial",
    ))
    fig.update_layout(
        paper_bgcolor=paper, font=dict(color=text),
        margin=dict(l=10, r=10, t=10, b=10),
        height=210, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _show_region_bars(dark, paper, text, brd, lang):
    regions = ["Adamaoua","Centre","Est","Extreme-Nord","Littoral","Nord","Nord-Ouest","Ouest"]
    random.seed(77)
    scores = [random.uniform(20, 80) for _ in regions]
    # Seuils officiels
    colors = [get_aqi_color(get_aqi_level_from_score(s)) for s in scores]

    fig = go.Figure(go.Bar(
        x=scores, y=regions, orientation="h",
        marker=dict(color=colors, opacity=0.85),
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(color=text),
    ))
    fig.update_layout(
        paper_bgcolor=paper, plot_bgcolor=paper, font=dict(color=text),
        margin=dict(l=10, r=40, t=5, b=5), height=200,
        xaxis=dict(range=[0, 110], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _show_evolution(dark, paper, text, brd, lang):
    days  = 30
    base  = datetime.now() - timedelta(days=days)
    dates = [base + timedelta(days=i) for i in range(days)]
    region_seeds = {"Centre": 38, "Nord": 62, "Littoral": 32, "Extreme-Nord": 68}
    kaki_colors  = {
        "Centre":       "#6B7355",
        "Nord":         "#B8860B",
        "Littoral":     "#4A7A6A",
        "Extreme-Nord": "#9A4A1A",
    }

    fig = go.Figure()
    for region, seed in region_seeds.items():
        random.seed(seed)
        vals = [max(0, min(100, seed + random.gauss(0, 7))) for _ in range(days)]
        fig.add_trace(go.Scatter(
            x=dates, y=vals, name=region, mode="lines",
            line=dict(color=kaki_colors[region], width=2),
        ))

    # Seuils officiels sur le graphique
    fig.add_hline(y=AQI_SCORE_SAFE_MAX,
                  line_dash="dot", line_color="#007A5E", opacity=0.5,
                  annotation_text=f"Safe ({AQI_SCORE_SAFE_MAX})",
                  annotation_font_color="#007A5E")
    fig.add_hline(y=AQI_SCORE_VIGILANCE_MAX,
                  line_dash="dot", line_color="#CE1126", opacity=0.5,
                  annotation_text=f"Urgent ({AQI_SCORE_VIGILANCE_MAX})",
                  annotation_font_color="#CE1126")

    fig.update_layout(
        paper_bgcolor=paper, plot_bgcolor=paper, font=dict(color=text),
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor=brd, gridwidth=0.5),
        yaxis=dict(showgrid=True, gridcolor=brd, gridwidth=0.5, range=[0, 105]),
        legend=dict(bgcolor=paper, bordercolor=brd, borderwidth=1,
                    font=dict(size=10, color=text)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})