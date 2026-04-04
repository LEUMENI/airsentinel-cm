"""
AirSentinel CM - Proxy PM2.5 Prediction Page
Formulaire avec exactement les 8 top features du modèle + variables support
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date

from utils.translations import t, CAMEROON_CITIES, WMO_CODES
from utils.models import predict_aqi, get_risk_color, get_risk_emoji
from utils.database import save_aqi_prediction
from utils.weather_api import fetch_weather, fetch_weather_3days


# Top 8 features du modèle (confirmées par le notebook)
TOP_FEATURES = [
    "rain_sum", "precipitation_sum", "precipitation_hours",
    "time_month", "time_cos", "et0_fao_evapotranspiration",
    "temperature_2m_max", "temperature_2m_mean"
]

FEATURE_LABELS = {
    "fr": {
        "rain_sum": "Pluie (mm)",
        "precipitation_sum": "Précipitations totales (mm)",
        "precipitation_hours": "Durée des précipitations (h)",
        "time_month": "Mois (1–12)",
        "time_cos": "Encodage cyclique mois (cos)",
        "et0_fao_evapotranspiration": "Évapotranspiration ET0 (mm)",
        "temperature_2m_max": "Température maximale (°C)",
        "temperature_2m_mean": "Température moyenne (°C)",
    },
    "en": {
        "rain_sum": "Rain (mm)",
        "precipitation_sum": "Total precipitation (mm)",
        "precipitation_hours": "Precipitation duration (h)",
        "time_month": "Month (1–12)",
        "time_cos": "Cyclical month encoding (cos)",
        "et0_fao_evapotranspiration": "Evapotranspiration ET0 (mm)",
        "temperature_2m_max": "Maximum temperature (°C)",
        "temperature_2m_mean": "Mean temperature (°C)",
    }
}


def show_aqi_prediction():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user = st.session_state.user
    paper_color = "#2C2C2E" if dark else "#FFFFFF"
    text_color  = "#F2F2F7" if dark else "#2C2C2E"
    subtext     = "#AEAEB2" if dark else "#636366"
    border      = "#3A3A3C" if dark else "#D4CDB8"

    st.markdown(f"""
    <div class='section-header'>
        <h3>{'🌫️ Prédiction Proxy PM2.5 — Qualité de l\'air' if lang=='fr' else '🌫️ Proxy PM2.5 Prediction — Air Quality'}</h3>
        <p>{'AirSentinel CM • Modèle XGBoost entraîné sur données camerounaises 2020–2025' if lang=='fr' else 'AirSentinel CM • XGBoost model trained on 2020–2025 Cameroonian data'}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Info box modèle ───────────────────────────────────────────────
    st.markdown(f"""
    <div class='info-strip'>
        <b>{'Modèle' if lang=='fr' else 'Model'}:</b> XGBoost &nbsp;|&nbsp;
        <b>R²:</b> 0.861 (validation) · 0.857 (holdout) &nbsp;|&nbsp;
        <b>MAE:</b> 1.64 µg/m³ &nbsp;|&nbsp;
        <b>{'8 variables sélectionnées' if lang=='fr' else '8 selected features'}</b>
    </div>
    """, unsafe_allow_html=True)

    # ── Ville & Date ──────────────────────────────────────────────────
    city_list = list(CAMEROON_CITIES.keys())
    col_city, col_date = st.columns([2, 1.5])
    with col_city:
        lbl = "🏙️ Ville" if lang == "fr" else "🏙️ City"
        selected_city = st.selectbox(lbl, city_list,
                                     index=city_list.index("Yaounde") if "Yaounde" in city_list else 0)
    with col_date:
        lbl2 = "📅 Date d'analyse" if lang == "fr" else "📅 Analysis date"
        selected_date = st.date_input(lbl2, value=date.today())

    city_info = CAMEROON_CITIES[selected_city]

    # ── Bouton chargement automatique ────────────────────────────────
    col_rt, col_info = st.columns([2, 4])
    with col_rt:
        rt_label = "🌐 Charger données météo temps réel" if lang == "fr" else "🌐 Load real-time weather data"
        if st.button(rt_label, use_container_width=True):
            with st.spinner("Connexion Open-Meteo..." if lang == "fr" else "Connecting to Open-Meteo..."):
                result = fetch_weather(city_info["lat"], city_info["lon"], selected_date.isoformat())
                if result["success"]:
                    st.session_state["aqi_rt"] = result["data"]
                    st.success("✅ Données chargées automatiquement !" if lang == "fr" else "✅ Data loaded automatically!")
                else:
                    st.error(f"❌ {result.get('error','Erreur API')}")
    with col_info:
        st.markdown(f"""
        <div style='padding:8px 12px; background:{paper_color}; border:1px solid {border};
                    border-radius:6px; font-size:12px; color:{subtext}; margin-top:4px;'>
            {'📍 Les données sont récupérées automatiquement depuis Open-Meteo pour la ville et la date sélectionnées.' if lang=='fr'
             else '📍 Data is automatically retrieved from Open-Meteo for the selected city and date.'}
        </div>
        """, unsafe_allow_html=True)

    rt = st.session_state.get("aqi_rt", {})

    # ── Formulaire ────────────────────────────────────────────────────
    st.markdown("---")
    fl = FEATURE_LABELS[lang]
    header = "📝 Variables du modèle (8 features sélectionnées)" if lang == "fr" else "📝 Model variables (8 selected features)"
    st.markdown(f"<div class='form-label-custom'>{header}</div>", unsafe_allow_html=True)

    with st.form("aqi_form"):
        # Ligne 1 — Les 3 variables précipitations (les + importantes)
        st.markdown(f"<p style='font-size:12px; color:{subtext}; margin-bottom:6px;'>{'💧 Précipitations (variables les plus influentes)' if lang=='fr' else '💧 Precipitation (most influential features)'}</p>", unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        with p1:
            rain_sum = st.number_input(fl["rain_sum"],
                value=float(rt.get("rain_sum", 0.0)), min_value=0.0, max_value=500.0, step=0.1, format="%.1f")
        with p2:
            prec_sum = st.number_input(fl["precipitation_sum"],
                value=float(rt.get("precipitation_sum", 0.0)), min_value=0.0, max_value=500.0, step=0.1, format="%.1f")
        with p3:
            prec_h = st.number_input(fl["precipitation_hours"],
                value=float(rt.get("precipitation_hours", 0.0)), min_value=0.0, max_value=24.0, step=0.5, format="%.1f")

        # Ligne 2 — Températures
        st.markdown(f"<p style='font-size:12px; color:{subtext}; margin:8px 0 6px;'>{'🌡️ Températures' if lang=='fr' else '🌡️ Temperatures'}</p>", unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            temp_max = st.number_input(fl["temperature_2m_max"],
                value=float(rt.get("temperature_2m_max", 30.0)), min_value=-10.0, max_value=55.0, step=0.1, format="%.1f")
        with t2:
            temp_mean = st.number_input(fl["temperature_2m_mean"],
                value=float(rt.get("temperature_2m_mean", 25.0)), min_value=-10.0, max_value=55.0, step=0.1, format="%.1f")

        # Ligne 3 — ET0
        st.markdown(f"<p style='font-size:12px; color:{subtext}; margin:8px 0 6px;'>🌿 Évapotranspiration</p>", unsafe_allow_html=True)
        e1, e2 = st.columns(2)
        with e1:
            et0 = st.number_input(fl["et0_fao_evapotranspiration"],
                value=float(rt.get("et0_fao_evapotranspiration", 5.0)), min_value=0.0, max_value=30.0, step=0.1, format="%.1f")
        with e2:
            # time_cos est calculé automatiquement depuis la date — affiché en lecture seule
            import math
            doy = selected_date.timetuple().tm_yday
            auto_cos = round(math.cos(2 * math.pi * doy / 365.25), 4)
            st.number_input(fl["time_cos"] + " (auto)",
                value=auto_cos, disabled=True, format="%.4f",
                help="Calculé automatiquement depuis la date" if lang == "fr" else "Automatically computed from date")

        # Variables support (non affichées dans le top8 mais nécessaires au pipeline)
        with st.expander("⚙️ " + ("Variables support (optionnelles)" if lang == "fr" else "Support variables (optional)")):
            s1, s2, s3 = st.columns(3)
            with s1:
                temp_min = st.number_input("Temp min (°C)", value=float(rt.get("temperature_2m_min", 20.0)), min_value=-10.0, max_value=50.0, step=0.1, format="%.1f")
                app_max  = st.number_input("Ressentie max (°C)", value=float(rt.get("apparent_temperature_max", 32.0)), min_value=-10.0, max_value=60.0, step=0.1, format="%.1f")
                app_min  = st.number_input("Ressentie min (°C)", value=float(rt.get("apparent_temperature_min", 22.0)), min_value=-10.0, max_value=55.0, step=0.1, format="%.1f")
                app_mean = st.number_input("Ressentie moy (°C)", value=float(rt.get("apparent_temperature_mean", 27.0)), min_value=-10.0, max_value=58.0, step=0.1, format="%.1f")
            with s2:
                wind_speed  = st.number_input("Vent max (km/h)", value=float(rt.get("wind_speed_10m_max", 10.0)), min_value=0.0, max_value=200.0, step=0.5, format="%.1f")
                wind_gusts  = st.number_input("Rafales (km/h)", value=float(rt.get("wind_gusts_10m_max", 15.0)), min_value=0.0, max_value=300.0, step=0.5, format="%.1f")
                wind_dir    = st.number_input("Direction vent (°)", value=float(rt.get("wind_direction_10m_dominant", 180.0)), min_value=0.0, max_value=360.0, step=1.0, format="%.0f")
                radiation   = st.number_input("Rayonnement (MJ/m²)", value=float(rt.get("shortwave_radiation_sum", 20.0)), min_value=0.0, max_value=50.0, step=0.1, format="%.1f")
            with s3:
                sunrise_val = st.text_input("Lever soleil (HH:MM)", value=rt.get("sunrise", "06:10"))
                sunset_val  = st.text_input("Coucher soleil (HH:MM)", value=rt.get("sunset", "18:15"))
                daylight    = st.number_input("Durée lumière (s)", value=float(rt.get("daylight_duration", 43800)), min_value=0.0, max_value=86400.0, step=100.0, format="%.0f")
                sunshine    = st.number_input("Soleil brillant (s)", value=float(rt.get("sunshine_duration", 25000)), min_value=0.0, max_value=86400.0, step=100.0, format="%.0f")

            wmo_list = list(WMO_CODES.values())
            wmo_label = st.selectbox("Code météo WMO", wmo_list)
            wmo_code = [k for k, v in WMO_CODES.items() if v == wmo_label][0]

        btn_label = "🔍 Calculer Proxy PM2.5" if lang == "fr" else "🔍 Calculate Proxy PM2.5"
        predict_btn = st.form_submit_button(btn_label, use_container_width=True)

    # ── Prédiction ────────────────────────────────────────────────────
    if predict_btn:
        input_dict = {
            "city": selected_city, "date": selected_date.isoformat(),
            "weather_code": wmo_code if 'wmo_code' in dir() else 3,
            "rain_sum": rain_sum, "precipitation_sum": prec_sum,
            "precipitation_hours": prec_h, "temperature_2m_max": temp_max,
            "temperature_2m_mean": temp_mean, "et0_fao_evapotranspiration": et0,
            "temperature_2m_min": temp_min if 'temp_min' in dir() else temp_max - 8,
            "apparent_temperature_max": app_max if 'app_max' in dir() else temp_max + 2,
            "apparent_temperature_min": app_min if 'app_min' in dir() else temp_max - 6,
            "apparent_temperature_mean": app_mean if 'app_mean' in dir() else temp_mean + 2,
            "wind_speed_10m_max": wind_speed if 'wind_speed' in dir() else 10.0,
            "wind_gusts_10m_max": wind_gusts if 'wind_gusts' in dir() else 15.0,
            "wind_direction_10m_dominant": wind_dir if 'wind_dir' in dir() else 180.0,
            "shortwave_radiation_sum": radiation if 'radiation' in dir() else 20.0,
            "sunrise": sunrise_val if 'sunrise_val' in dir() else "06:10",
            "sunset": sunset_val if 'sunset_val' in dir() else "18:15",
            "daylight_duration": daylight if 'daylight' in dir() else 43800.0,
            "sunshine_duration": sunshine if 'sunshine' in dir() else 25000.0,
        }
        with st.spinner("⚙️ Calcul Proxy PM2.5 en cours..."):
            try:
                result = predict_aqi(input_dict)
                save_aqi_prediction(user["id"], selected_city, city_info["region"],
                                    selected_date.isoformat(), result["score"],
                                    result["risk_level"], input_dict)
                st.session_state["last_aqi"] = {
                    **result, "city": selected_city,
                    "date": selected_date.isoformat(), "input": input_dict
                }
                st.success("✅ Prédiction enregistrée." if lang == "fr" else "✅ Prediction saved.")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    # ── Résultats ─────────────────────────────────────────────────────
    if "last_aqi" in st.session_state:
        res = st.session_state["last_aqi"]
        score = res["score"]
        risk  = res["risk_level"]
        rc    = get_risk_color(risk)
        emoji = get_risk_emoji(risk)

        st.markdown("---")
        st.markdown(f"""
        <div class='section-header'>
            <h3>{'📊 Résultats Proxy PM2.5' if lang=='fr' else '📊 Proxy PM2.5 Results'}</h3>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3 = st.columns([2, 2, 3])

        with r1:
            badge_class = f"badge-{risk.lower()}"
            st.markdown(f"""
            <div class='as-card' style='text-align:center; border-left:4px solid {rc};'>
                <div style='font-size:3.5rem; font-weight:900; color:{rc};
                            font-family:"JetBrains Mono",monospace; line-height:1;'>{score:.1f}</div>
                <div style='font-size:13px; color:{subtext}; margin:4px 0;'>Proxy PM2.5 Score / 100</div>
                <div style='margin:8px 0;'><span class='{badge_class}'>{emoji} {risk}</span></div>
                <div style='font-size:12px; color:{subtext};'>PM2.5 estimé: <b>{res['pm25_raw']:.2f} µg/m³</b></div>
                <div style='font-size:11px; color:{subtext}; margin-top:4px;'>📍 {res['city']} · {res['date']}</div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": text_color,
                             "tickfont": {"color": text_color}},
                    "bar": {"color": rc, "thickness": 0.25},
                    "steps": [
                        {"range": [0, 33],   "color": "#007A5E" if not dark else "#004D3E"},
                        {"range": [33, 66],  "color": "#B8860B" if not dark else "#7A5A00"},
                        {"range": [66, 100], "color": "#B91C1C" if not dark else "#7A1010"},
                    ],
                    "bordercolor": border,
                },
                number={"font": {"color": rc, "size": 32, "family": "JetBrains Mono"},
                        "suffix": "/100"}
            ))
            fig_gauge.update_layout(
                paper_bgcolor=paper_color, font=dict(color=text_color),
                margin=dict(l=20, r=20, t=30, b=10), height=200,
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        with r3:
            interp = {
                "SAFE": {
                    "fr": "✅ Qualité de l'air acceptable.\nPM2.5 estimé en dessous du seuil OMS (15 µg/m³/j).\nAucune restriction recommandée.",
                    "en": "✅ Acceptable air quality.\nEstimated PM2.5 below WHO threshold (15 µg/m³/d).\nNo restrictions recommended."
                },
                "VIGILANCE": {
                    "fr": "⚠️ Qualité de l'air modérément dégradée.\nPM2.5 entre les seuils OMS et OMS intermédiaire.\nPersonnes sensibles : limiter les activités prolongées en extérieur.",
                    "en": "⚠️ Moderately degraded air quality.\nPM2.5 between WHO thresholds.\nSensitive groups: limit prolonged outdoor activities."
                },
                "DANGER": {
                    "fr": "🚨 DANGER — PM2.5 élevé détecté !\nÉviter toute activité extérieure prolongée.\nPortez un masque FFP2 si nécessaire.\nAlertez les autorités sanitaires locales.",
                    "en": "🚨 DANGER — High PM2.5 detected!\nAvoid prolonged outdoor activities.\nWear FFP2 mask if necessary.\nAlert local health authorities."
                }
            }
            msg = interp.get(risk, {}).get(lang, "")
            st.markdown(f"""
            <div class='as-card' style='border-left:4px solid {rc}; white-space:pre-line; font-size:13px; line-height:1.6;'>
                {msg}
            </div>
            """, unsafe_allow_html=True)

        # Feature importance
        st.markdown(f"<br><div class='form-label-custom'>{'🔍 Contribution des 8 variables sélectionnées' if lang=='fr' else '🔍 Contribution of the 8 selected features'}</div>", unsafe_allow_html=True)
        fl2 = FEATURE_LABELS[lang]
        feat_vals = {
            fl2["rain_sum"]: res["input"].get("rain_sum", 0),
            fl2["precipitation_sum"]: res["input"].get("precipitation_sum", 0),
            fl2["precipitation_hours"]: res["input"].get("precipitation_hours", 0),
            fl2["et0_fao_evapotranspiration"]: res["input"].get("et0_fao_evapotranspiration", 0),
            fl2["temperature_2m_max"]: res["input"].get("temperature_2m_max", 0),
            fl2["temperature_2m_mean"]: res["input"].get("temperature_2m_mean", 0),
        }
        max_v = max(abs(v) for v in feat_vals.values()) or 1
        bar_colors = ["#6B7355" if v >= 0 else "#B91C1C" for v in feat_vals.values()]
        fig_feat = go.Figure(go.Bar(
            x=[abs(v)/max_v*100 for v in feat_vals.values()],
            y=list(feat_vals.keys()), orientation="h",
            marker=dict(color=bar_colors, opacity=0.85),
            text=[f"{v:.2f}" for v in feat_vals.values()],
            textposition="outside", textfont=dict(color=text_color, size=11),
        ))
        fig_feat.update_layout(
            paper_bgcolor=paper_color, plot_bgcolor=paper_color,
            font=dict(color=text_color), height=260,
            margin=dict(l=10, r=80, t=10, b=10),
            xaxis=dict(showgrid=False, range=[0, 130]),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_feat, use_container_width=True, config={"displayModeBar": False})

        # Downloads
        d1, d2, _ = st.columns([1.5, 1.5, 4])
        with d1:
            try:
                from utils.pdf_report import generate_aqi_report
                pdf = generate_aqi_report(res["city"], city_info["region"], res["date"],
                                          res["score"], res["risk_level"], res["pm25_raw"],
                                          res["input"], user["username"])
                st.download_button("📄 Rapport PDF", data=pdf,
                                   file_name=f"pm25_{res['city']}_{res['date']}.pdf",
                                   mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF: {e}")
        with d2:
            csv = pd.DataFrame([{**res["input"], "score": res["score"],
                                   "risk_level": res["risk_level"], "pm25_raw": res["pm25_raw"]}])
            st.download_button("📊 Export CSV", data=csv.to_csv(index=False),
                               file_name=f"pm25_{res['city']}_{res['date']}.csv",
                               mime="text/csv", use_container_width=True)
