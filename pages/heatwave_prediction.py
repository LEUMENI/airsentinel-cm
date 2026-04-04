"""
AirSentinel CM - Heatwave Prediction Page
Style cartographique inspiré de Belgrade — sobre et lisible
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

from utils.translations import t, CAMEROON_CITIES
from utils.models import predict_heatwave, get_risk_color, get_risk_emoji, CITY_THRESHOLDS
from utils.database import save_heatwave_prediction
from utils.weather_api import fetch_weather, fetch_weather_3days


def show_heatwave_prediction():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user = st.session_state.user
    paper_color = "#2C2C2E" if dark else "#FFFFFF"
    text_color  = "#F2F2F7" if dark else "#2C2C2E"
    subtext     = "#AEAEB2" if dark else "#636366"
    border      = "#3A3A3C" if dark else "#D4CDB8"
    card_bg     = "#2C2C2E" if dark else "#FFFFFF"

    st.markdown(f"""
    <div class='section-header'>
        <h3>{'🌡️ Prédiction Vague de Chaleur' if lang=='fr' else '🌡️ Heatwave Prediction'}</h3>
        <p>{'Modèle Régression Logistique — Seuil 0.20 — Définition ETCCDI (3 jours consécutifs > P90 local)' if lang=='fr'
            else 'Logistic Regression model — Threshold 0.20 — ETCCDI definition (3 consecutive days > local P90)'}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Ville & Date ──────────────────────────────────────────────────
    city_list = list(CAMEROON_CITIES.keys())
    col_city, col_date = st.columns([2, 1.5])
    with col_city:
        selected_city = st.selectbox(
            "🏙️ Ville" if lang == "fr" else "🏙️ City",
            city_list,
            index=city_list.index("Garoua") if "Garoua" in city_list else 0
        )
    with col_date:
        selected_date = st.date_input("📅 Date", value=date.today())

    city_info = CAMEROON_CITIES[selected_city]
    auto_threshold = CITY_THRESHOLDS.get(selected_city, 36.0)

    # Infos ville
    st.markdown(f"""
    <div class='info-strip'>
        📍 <b>{selected_city}</b> — {city_info['region']} &nbsp;|&nbsp;
        Lat: {city_info['lat']:.2f}°N, Lon: {city_info['lon']:.2f}°E &nbsp;|&nbsp;
        {'Seuil P90 local' if lang=='fr' else 'Local P90 threshold'}: <b>{auto_threshold:.1f}°C</b>
    </div>
    """, unsafe_allow_html=True)

    # ── Chargement auto ───────────────────────────────────────────────
    col_rt, col_info = st.columns([2, 4])
    with col_rt:
        rt_label = "🌐 Charger données temps réel" if lang == "fr" else "🌐 Load real-time data"
        if st.button(rt_label, use_container_width=True, key="hw_rt"):
            with st.spinner("Récupération Open-Meteo + historique 3j..." if lang == "fr" else "Fetching Open-Meteo + 3-day history..."):
                result = fetch_weather(city_info["lat"], city_info["lon"], selected_date.isoformat())
                lags   = fetch_weather_3days(city_info["lat"], city_info["lon"])
                if result["success"]:
                    st.session_state["hw_rt"] = result["data"]
                    st.session_state["hw_lags"] = lags
                    st.success("✅ Données + historique 3j chargés !" if lang == "fr" else "✅ Data + 3-day history loaded!")
                else:
                    st.error(f"❌ {result.get('error','')}")
    with col_info:
        st.markdown(f"""
        <div style='padding:8px 12px; background:{paper_color}; border:1px solid {border};
                    border-radius:6px; font-size:12px; color:{subtext}; margin-top:4px;'>
            {'⚡ Le chargement récupère aussi automatiquement les températures J-1, J-2, J-3 pour les lags.' if lang=='fr'
             else '⚡ Loading also automatically fetches D-1, D-2, D-3 temperatures for lag features.'}
        </div>
        """, unsafe_allow_html=True)

    rt   = st.session_state.get("hw_rt", {})
    lags = st.session_state.get("hw_lags", [auto_threshold - 2, auto_threshold - 1, auto_threshold])

    # ── Formulaire ────────────────────────────────────────────────────
    st.markdown("---")
    with st.form("hw_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"<p class='form-label-custom'>{'🌡️ Températures' if lang=='fr' else '🌡️ Temperatures'}</p>", unsafe_allow_html=True)
            temp_max  = st.number_input("Temp max (°C)", value=float(rt.get("temperature_2m_max", 35.0)), min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            temp_min  = st.number_input("Temp min (°C)", value=float(rt.get("temperature_2m_min", 24.0)), min_value=5.0, max_value=45.0, step=0.1, format="%.1f")
            temp_mean = st.number_input("Temp moyenne (°C)", value=float(rt.get("temperature_2m_mean", 29.0)), min_value=10.0, max_value=50.0, step=0.1, format="%.1f")
            app_max   = st.number_input("Ressentie max (°C)", value=float(rt.get("apparent_temperature_max", 38.0)), min_value=15.0, max_value=65.0, step=0.1, format="%.1f")
            app_min   = st.number_input("Ressentie min (°C)", value=float(rt.get("apparent_temperature_min", 26.0)), min_value=5.0, max_value=55.0, step=0.1, format="%.1f")
            app_mean  = st.number_input("Ressentie moy (°C)", value=float(rt.get("apparent_temperature_mean", 32.0)), min_value=10.0, max_value=60.0, step=0.1, format="%.1f")

        with c2:
            st.markdown(f"<p class='form-label-custom'>{'📅 Historique & Seuil' if lang=='fr' else '📅 History & Threshold'}</p>", unsafe_allow_html=True)
            temp_threshold = st.number_input(
                f"{'Seuil climatologique P90 (°C)' if lang=='fr' else 'Climatological P90 threshold (°C)'}",
                value=auto_threshold, min_value=25.0, max_value=50.0, step=0.5, format="%.1f",
                help="90ème percentile local — pré-rempli automatiquement selon la ville" if lang == "fr" else "Local 90th percentile — auto-filled by city"
            )
            temp_lag1 = st.number_input("Temp max J-1 (°C)", value=float(lags[2] if len(lags)>=3 else temp_max - 1), min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            temp_lag2 = st.number_input("Temp max J-2 (°C)", value=float(lags[1] if len(lags)>=3 else temp_max - 2), min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            temp_lag3 = st.number_input("Temp max J-3 (°C)", value=float(lags[0] if len(lags)>=3 else temp_max - 3), min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            radiation = st.number_input("Rayonnement (MJ/m²)", value=float(rt.get("shortwave_radiation_sum", 22.0)), min_value=0.0, max_value=50.0, step=0.1, format="%.1f")

        with c3:
            st.markdown(f"<p class='form-label-custom'>{'🌧️ Précipitations & Vent' if lang=='fr' else '🌧️ Precipitation & Wind'}</p>", unsafe_allow_html=True)
            prec_sum  = st.number_input("Précipitations (mm)", value=float(rt.get("precipitation_sum", 0.0)), min_value=0.0, max_value=200.0, step=0.1, format="%.1f")
            rain_sum  = st.number_input("Pluie (mm)", value=float(rt.get("rain_sum", 0.0)), min_value=0.0, max_value=200.0, step=0.1, format="%.1f")
            prec_h    = st.number_input("Heures pluie", value=float(rt.get("precipitation_hours", 0.0)), min_value=0.0, max_value=24.0, step=0.5, format="%.1f")
            et0       = st.number_input("ET0 (mm)", value=float(rt.get("et0_fao_evapotranspiration", 6.0)), min_value=0.0, max_value=30.0, step=0.1, format="%.1f")
            wind_speed= st.number_input("Vent max (km/h)", value=float(rt.get("wind_speed_10m_max", 8.0)), min_value=0.0, max_value=200.0, step=0.5, format="%.1f")
            wind_gusts= st.number_input("Rafales (km/h)", value=float(rt.get("wind_gusts_10m_max", 12.0)), min_value=0.0, max_value=300.0, step=0.5, format="%.1f")
            wind_dir  = st.number_input("Direction (°)", value=float(rt.get("wind_direction_10m_dominant", 90.0)), min_value=0.0, max_value=360.0, step=1.0, format="%.0f")
            sunrise_v = st.text_input("Lever (HH:MM)", value=rt.get("sunrise", "06:00"), key="hw_sr")
            sunset_v  = st.text_input("Coucher (HH:MM)", value=rt.get("sunset", "18:30"), key="hw_ss")

        btn_label = "🌡️ Analyser le risque vague de chaleur" if lang == "fr" else "🌡️ Analyze heatwave risk"
        predict_btn = st.form_submit_button(btn_label, use_container_width=True)

    # ── Prédiction ────────────────────────────────────────────────────
    if predict_btn:
        input_dict = {
            "city": selected_city, "date": selected_date.isoformat(),
            "temperature_2m_max": temp_max, "temperature_2m_min": temp_min,
            "temperature_2m_mean": temp_mean,
            "apparent_temperature_max": app_max, "apparent_temperature_min": app_min,
            "apparent_temperature_mean": app_mean,
            "temp_threshold": temp_threshold,
            "temp_lag1": temp_lag1, "temp_lag2": temp_lag2, "temp_lag3": temp_lag3,
            "precipitation_sum": prec_sum, "rain_sum": rain_sum, "precipitation_hours": prec_h,
            "shortwave_radiation_sum": radiation, "et0_fao_evapotranspiration": et0,
            "wind_speed_10m_max": wind_speed, "wind_gusts_10m_max": wind_gusts,
            "wind_direction_10m_dominant": wind_dir,
            "sunrise": sunrise_v, "sunset": sunset_v,
            "daylight_duration": float(rt.get("daylight_duration", 43200)),
            "sunshine_duration": float(rt.get("sunshine_duration", 25000)),
        }
        with st.spinner("⚙️ Analyse vague de chaleur..." if lang=="fr" else "⚙️ Analyzing heatwave..."):
            try:
                result = predict_heatwave(input_dict)
                save_heatwave_prediction(user["id"], selected_city, city_info["region"],
                                         selected_date.isoformat(), result["probability"],
                                         result["prediction"], result["risk_level"], input_dict)
                st.session_state["last_hw"] = {
                    **result, "city": selected_city,
                    "date": selected_date.isoformat(), "input": input_dict
                }
                st.success("✅ Prédiction enregistrée." if lang=="fr" else "✅ Prediction saved.")
            except Exception as e:
                st.error(f"❌ {e}")

    # ── Résultats ─────────────────────────────────────────────────────
    if "last_hw" in st.session_state:
        res  = st.session_state["last_hw"]
        prob = res["probability"]
        pred = res["prediction"]
        risk = res["risk_level"]
        rc   = get_risk_color(risk)

        st.markdown("---")
        st.markdown(f"""
        <div class='section-header'>
            <h3>{'🌡️ Résultats — Vague de Chaleur' if lang=='fr' else '🌡️ Results — Heatwave'}</h3>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3 = st.columns([2, 2, 3])

        with r1:
            alert_txt = ("🚨 VAGUE PROBABLE" if lang=="fr" else "🚨 LIKELY HEATWAVE") if pred == 1 else ("✅ PAS DE VAGUE" if lang=="fr" else "✅ NO HEATWAVE")
            badge_cls = f"badge-{risk.lower()}"
            st.markdown(f"""
            <div class='as-card' style='text-align:center; border-left:4px solid {rc};'>
                <div style='font-size:3rem; font-weight:900; color:{rc};
                            font-family:"JetBrains Mono",monospace;'>{prob*100:.1f}%</div>
                <div style='font-size:11px; color:{subtext}; margin:2px 0 8px;'>
                    {'Probabilité de vague de chaleur J+3' if lang=='fr' else 'Heatwave probability D+3'}</div>
                <span class='{badge_cls}'>{alert_txt}</span>
                <div style='font-size:11px; color:{subtext}; margin-top:8px;'>
                    📍 {res['city']} · {res['date']}<br>
                    {'Seuil décision' if lang=='fr' else 'Decision threshold'}: 0.20
                </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            # Gauge sobre style Belgrade
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                gauge={
                    "axis": {"range": [0, 100], "ticksuffix": "%",
                             "tickcolor": text_color, "tickfont": {"color": text_color}},
                    "bar": {"color": rc, "thickness": 0.3},
                    "steps": [
                        {"range": [0, 20],   "color": "#005A44" if dark else "#E8F5E9"},
                        {"range": [20, 50],  "color": "#7A5A00" if dark else "#FFF3CD"},
                        {"range": [50, 100], "color": "#7A1010" if dark else "#FDECEA"},
                    ],
                    "threshold": {"line": {"color": text_color, "width": 2}, "value": 20},
                    "bordercolor": border,
                },
                number={"suffix": "%", "font": {"color": rc, "size": 28, "family": "JetBrains Mono"}}
            ))
            fig_g.update_layout(
                paper_bgcolor=paper_color, font=dict(color=text_color),
                margin=dict(l=15, r=15, t=25, b=10), height=200,
            )
            st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

        with r3:
            interp = {
                "SAFE": {
                    "fr": f"✅ Aucune vague de chaleur prévue.\nProbabilité: {prob*100:.1f}% (< seuil 20%)\nConditions météorologiques dans les normes saisonnières.",
                    "en": f"✅ No heatwave expected.\nProbability: {prob*100:.1f}% (< 20% threshold)\nWeather conditions within seasonal norms."
                },
                "VIGILANCE": {
                    "fr": f"⚠️ Risque modéré de vague de chaleur.\nProbabilité: {prob*100:.1f}%\nSurveillance accrue recommandée.\nPersonnes vulnérables : hydratation intensive.",
                    "en": f"⚠️ Moderate heatwave risk.\nProbability: {prob*100:.1f}%\nIncreased monitoring recommended.\nVulnerable people: intensive hydration."
                },
                "DANGER": {
                    "fr": f"🚨 ALERTE — Vague de chaleur probable !\nProbabilité: {prob*100:.1f}%\n• Hydratez-vous toutes les heures\n• Évitez le soleil 11h–16h\n• Surveillez personnes âgées et enfants\n• Contactez les services sanitaires",
                    "en": f"🚨 ALERT — Heatwave likely!\nProbability: {prob*100:.1f}%\n• Hydrate every hour\n• Avoid sun 11am–4pm\n• Monitor elderly and children\n• Contact health services"
                }
            }
            msg = interp.get(risk, {}).get(lang, "")
            st.markdown(f"""
            <div class='as-card' style='border-left:4px solid {rc}; white-space:pre-line;
                        font-size:13px; line-height:1.6;'>
                {msg}
            </div>
            """, unsafe_allow_html=True)

        # ── Graphique historique températures (style Belgrade) ───────
        st.markdown(f"<br><div class='form-label-custom'>{'📈 Historique des températures vs seuil P90' if lang=='fr' else '📈 Temperature history vs P90 threshold'}</div>", unsafe_allow_html=True)
        _show_temp_history_belgrade(res["input"], paper_color, text_color, subtext, border, dark, rc, lang)

        # Downloads
        d1, d2, _ = st.columns([1.5, 1.5, 4])
        with d1:
            try:
                from utils.pdf_report import generate_heatwave_report
                pdf = generate_heatwave_report(res["city"], city_info["region"], res["date"],
                                               prob, pred, risk, res["input"], user["username"])
                st.download_button("📄 Rapport PDF", data=pdf,
                                   file_name=f"hw_{res['city']}_{res['date']}.pdf",
                                   mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF: {e}")
        with d2:
            csv = pd.DataFrame([{**res["input"], "probability": prob,
                                   "prediction": pred, "risk_level": risk}])
            st.download_button("📊 Export CSV", data=csv.to_csv(index=False),
                               file_name=f"hw_{res['city']}_{res['date']}.csv",
                               mime="text/csv", use_container_width=True)


def _show_temp_history_belgrade(inp, paper_color, text_color, subtext, border, dark, risk_color, lang):
    """Style cartographique sobre inspiré de Belgrade."""
    threshold = inp.get("temp_threshold", 36.0)
    days = ["J-3", "J-2", "J-1", "J (auj.)" if lang == "fr" else "D (today)"]
    temps = [
        inp.get("temp_lag3", threshold - 3),
        inp.get("temp_lag2", threshold - 2),
        inp.get("temp_lag1", threshold - 1),
        inp.get("temperature_2m_max", threshold),
    ]

    # Couleurs sobre par statut
    bar_colors = []
    for t in temps:
        if t >= threshold:
            bar_colors.append(risk_color)  # rouge danger
        elif t >= threshold - 2:
            bar_colors.append("#B8860B")   # vigilance doré
        else:
            bar_colors.append("#6B7355")   # kaki safe

    fig = go.Figure()

    # Zone de seuil (fond sobre)
    fig.add_hrect(y0=threshold, y1=max(temps) + 3,
                  fillcolor=risk_color, opacity=0.06, line_width=0,
                  annotation_text="Zone DANGER" if lang=="fr" else "DANGER Zone",
                  annotation_position="top right",
                  annotation_font=dict(color=risk_color, size=10))

    # Barres
    fig.add_trace(go.Bar(
        x=days, y=temps,
        marker=dict(color=bar_colors, opacity=0.85,
                    line=dict(color=paper_color, width=1)),
        text=[f"<b>{v:.1f}°C</b>" for v in temps],
        textposition="outside",
        textfont=dict(color=text_color, size=12),
        width=0.5,
    ))

    # Ligne de seuil P90
    fig.add_hline(y=threshold, line_dash="dash", line_color="#B8860B", line_width=2,
                  annotation_text=f"P90 = {threshold:.1f}°C",
                  annotation_font=dict(color="#B8860B", size=11),
                  annotation_position="right")

    fig.update_layout(
        paper_bgcolor=paper_color, plot_bgcolor=paper_color,
        font=dict(color=text_color, family="Inter"),
        height=240, margin=dict(l=10, r=80, t=20, b=10),
        xaxis=dict(showgrid=False, showline=True, linecolor=border, tickfont=dict(color=text_color)),
        yaxis=dict(showgrid=True, gridcolor=border, gridwidth=0.5,
                   ticksuffix="°C", tickfont=dict(color=text_color),
                   range=[min(temps) - 5, max(temps) + 8]),
        bargap=0.4,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
