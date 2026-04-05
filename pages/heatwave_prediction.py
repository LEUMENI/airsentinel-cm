"""
AirSentinel CM - Heatwave Prediction Page
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date

from utils.translations import t, CAMEROON_CITIES, WMO_CODES
from utils.models import predict_heatwave, get_risk_color, get_risk_emoji
from utils.database import save_heatwave_prediction
from utils.weather_api import fetch_weather


def show_heatwave_prediction():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user = st.session_state.user
    paper_color = "#252836" if dark else "#FFFFFF"
    text_color = "#E8EAF6" if dark else "#1A1A2E"

    st.markdown("""
    <div class='tricolor-bar'></div>
    <h2 style='margin:0; font-weight:900;'>🌡️ Prédiction Vague de Chaleur</h2>
    <p style='color:#888; margin-top:4px;'>Heatwave Prediction -AirSentinel CM</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:linear-gradient(135deg,#CE1126,#FF6B35); border-radius:10px;
                padding:12px 18px; margin-bottom:16px; color:white; font-size:13px;'>
        <b>⚠️ Comment ça marche / How it works:</b><br>
        Le modèle prédit si une vague de chaleur est probable dans les 3 prochains jours (J+3),
        basé sur une régression logistique entraînée sur les données camerounaises 2020-2025.<br>
        <i>The model predicts whether a heatwave is likely in the next 3 days (D+3),
        based on logistic regression trained on Cameroonian data 2020-2025.</i>
    </div>
    """, unsafe_allow_html=True)

    # ── City & Date ───────────────────────────────────────────────────
    city_list = list(CAMEROON_CITIES.keys())
    col_city, col_date = st.columns([2, 1.5])
    with col_city:
        selected_city = st.selectbox(t("aqi_city", lang), city_list,
                                     index=city_list.index("Garoua") if "Garoua" in city_list else 0)
    with col_date:
        selected_date = st.date_input(t("aqi_date", lang), value=date.today())

    city_info = CAMEROON_CITIES[selected_city]

    # Real-time loader
    rt_col, _ = st.columns([2, 5])
    with rt_col:
        if st.button(f"🌐 {t('aqi_realtime_btn', lang)}", use_container_width=True, key="hw_rt"):
            with st.spinner(t("loading", lang)):
                result = fetch_weather(city_info["lat"], city_info["lon"],
                                       selected_date.isoformat())
                if result["success"]:
                    st.session_state["hw_rt_data"] = result["data"]
                    st.success(f"✅ {t('realtime_loaded', lang)}")
                else:
                    st.error(f"❌ {result.get('error', '')}")

    rt = st.session_state.get("hw_rt_data", {})

    # ── Form ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📝 Données d'entrée / Input data")

    with st.form("hw_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("**🌡️ Températures**")
            temp_max = st.number_input("Temp max (°C)", value=float(rt.get("temperature_2m_max", 38.0)),
                                       min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            temp_min = st.number_input("Temp min (°C)", value=float(rt.get("temperature_2m_min", 26.0)),
                                       min_value=5.0, max_value=45.0, step=0.1, format="%.1f")
            temp_mean = st.number_input("Temp moyenne (°C)", value=float(rt.get("temperature_2m_mean", 32.0)),
                                        min_value=10.0, max_value=50.0, step=0.1, format="%.1f")
            app_max = st.number_input("Ressentie max (°C)", value=float(rt.get("apparent_temperature_max", 42.0)),
                                      min_value=15.0, max_value=65.0, step=0.1, format="%.1f")
            app_min = st.number_input("Ressentie min (°C)", value=float(rt.get("apparent_temperature_min", 28.0)),
                                      min_value=5.0, max_value=55.0, step=0.1, format="%.1f")
            app_mean = st.number_input("Ressentie moy (°C)", value=float(rt.get("apparent_temperature_mean", 35.0)),
                                       min_value=10.0, max_value=60.0, step=0.1, format="%.1f")

        with c2:
            st.markdown("**📊 Historique températures / Temp history**")
            temp_threshold = st.number_input(
                "Seuil climatologique local (°C) / Local climate threshold",
                value=35.0, min_value=25.0, max_value=50.0, step=0.5, format="%.1f",
                help="90ème percentile local des températures max (issu des données historiques)"
            )
            temp_lag1 = st.number_input("Temp max J-1 (°C)", value=float(rt.get("temperature_2m_max", 37.0)) - 1,
                                        min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            temp_lag2 = st.number_input("Temp max J-2 (°C)", value=float(rt.get("temperature_2m_max", 37.0)) - 2,
                                        min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            temp_lag3 = st.number_input("Temp max J-3 (°C)", value=float(rt.get("temperature_2m_max", 37.0)) - 3,
                                        min_value=15.0, max_value=55.0, step=0.1, format="%.1f")
            st.markdown("""
            <div style='font-size:11px; color:#888; background:#1A2A3A; padding:8px; border-radius:6px;'>
            💡 Saisir les temperatures maximales observees les 3 jours precedents
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("**🌧️ Météo complémentaire**")
            precip = st.number_input("Précipitations (mm)", value=float(rt.get("precipitation_sum", 0.0)),
                                     min_value=0.0, max_value=200.0, step=0.1, format="%.1f")
            rain = st.number_input("Pluie (mm)", value=float(rt.get("rain_sum", 0.0)),
                                   min_value=0.0, max_value=200.0, step=0.1, format="%.1f")
            precip_h = st.number_input("Heures pluie", value=float(rt.get("precipitation_hours", 0.0)),
                                       min_value=0.0, max_value=24.0, step=0.5, format="%.1f")
            radiation = st.number_input("Rayonnement (MJ/m²)", value=float(rt.get("shortwave_radiation_sum", 28.0)),
                                        min_value=0.0, max_value=50.0, step=0.1, format="%.1f")
            et0 = st.number_input("ET0 (mm)", value=float(rt.get("et0_fao_evapotranspiration", 7.0)),
                                  min_value=0.0, max_value=30.0, step=0.1, format="%.1f")
            wind_speed = st.number_input("Vent max (km/h)", value=float(rt.get("wind_speed_10m_max", 8.0)),
                                         min_value=0.0, max_value=200.0, step=0.5, format="%.1f")
            sunrise_val = st.text_input("Lever soleil (HH:MM)", value=rt.get("sunrise", "06:00"), key="hw_sr")
            sunset_val = st.text_input("Coucher soleil (HH:MM)", value=rt.get("sunset", "18:30"), key="hw_ss")

        predict_btn = st.form_submit_button(f"🌡️ {t('hw_predict_btn', lang)}", use_container_width=True)

    # ── Prediction ────────────────────────────────────────────────────
    if predict_btn:
        input_dict = {
            "city": selected_city, "date": selected_date.isoformat(),
            "temperature_2m_max": temp_max, "temperature_2m_min": temp_min,
            "temperature_2m_mean": temp_mean,
            "apparent_temperature_max": app_max, "apparent_temperature_min": app_min,
            "apparent_temperature_mean": app_mean,
            "temp_threshold": temp_threshold,
            "temp_lag1": temp_lag1, "temp_lag2": temp_lag2, "temp_lag3": temp_lag3,
            "precipitation_sum": precip, "rain_sum": rain, "precipitation_hours": precip_h,
            "shortwave_radiation_sum": radiation, "et0_fao_evapotranspiration": et0,
            "wind_speed_10m_max": wind_speed,
            "sunrise": sunrise_val, "sunset": sunset_val,
            "daylight_duration": 43200, "sunshine_duration": 25000,
            "wind_gusts_10m_max": wind_speed * 1.5,
            "wind_direction_10m_dominant": 180.0,
        }

        with st.spinner("⚙️ Analyse en cours..."):
            try:
                result = predict_heatwave(input_dict)
                save_heatwave_prediction(
                    user["id"], selected_city, city_info["region"],
                    selected_date.isoformat(), result["probability"],
                    result["prediction"], result["risk_level"], input_dict
                )
                st.session_state["last_hw_result"] = {
                    **result, "city": selected_city,
                    "date": selected_date.isoformat(), "input": input_dict
                }
                st.success(f"✅ {t('prediction_saved', lang)}")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    # ── Results ───────────────────────────────────────────────────────
    if "last_hw_result" in st.session_state:
        res = st.session_state["last_hw_result"]
        prob = res["probability"]
        pred = res["prediction"]
        risk = res["risk_level"]
        risk_color = get_risk_color(risk)

        st.markdown("---")
        st.markdown("### 🌡️ Résultats / Results")

        r1, r2, r3 = st.columns([2, 2, 3])

        with r1:
            alert_text = "🚨 VAGUE DE CHALEUR PROBABLE" if pred == 1 else "✅ PAS DE VAGUE DÉTECTÉE"
            alert_sub = "HEATWAVE LIKELY" if pred == 1 else "NO HEATWAVE DETECTED"
            st.markdown(f"""
            <div style='background:{risk_color}; border-radius:12px; padding:24px;
                        text-align:center; color:white;
                        {"animation:blink 1.5s infinite;" if pred==1 else ""}'>
                <div style='font-size:44px; font-weight:900;'>{prob*100:.1f}%</div>
                <div style='font-size:12px; opacity:0.9;'>Probabilité / Probability</div>
                <div style='font-size:16px; font-weight:800; margin-top:10px;'>{alert_text}</div>
                <div style='font-size:11px; opacity:0.8;'>{alert_sub}</div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            # Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "ticksuffix": "%"},
                    "bar": {"color": risk_color},
                    "steps": [
                        {"range": [0, 20], "color": "#007A5E" if not dark else "#004D3E"},
                        {"range": [20, 50], "color": "#FCD116" if not dark else "#A08000"},
                        {"range": [50, 100], "color": "#CE1126" if not dark else "#8B000E"},
                    ],
                },
                number={"suffix": "%", "font": {"color": risk_color, "size": 32}}
            ))
            fig_gauge.update_layout(
                paper_bgcolor=paper_color, font=dict(color=text_color),
                margin=dict(l=20, r=20, t=30, b=20), height=200,
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        with r3:
            threshold_used = 20
            interpretations = {
                "SAFE": {
                    "fr": f"✅ Aucune vague de chaleur détectée (probabilité: {prob*100:.1f}% < seuil {threshold_used}%).\nConditions météo dans les normes. Population sans risque immédiat.",
                    "en": f"✅ No heatwave detected (probability: {prob*100:.1f}% < threshold {threshold_used}%).\nWeather conditions within normal range."
                },
                "VIGILANCE": {
                    "fr": f"⚠️ Risque modéré de vague de chaleur (probabilité: {prob*100:.1f}%).\nSurveillance accrue recommandée pour les personnes vulnérables.",
                    "en": f"⚠️ Moderate heatwave risk (probability: {prob*100:.1f}%).\nIncreased monitoring recommended for vulnerable people."
                },
                "DANGER": {
                    "fr": f"🚨 ALERTE -Vague de chaleur probable ! Probabilité: {prob*100:.1f}%\n• Hydratation intensive\n• Éviter le soleil 11h-16h\n• Surveiller personnes âgées et enfants\n• Alerter les autorités sanitaires",
                    "en": f"🚨 ALERT -Heatwave likely! Probability: {prob*100:.1f}%\n• Intensive hydration\n• Avoid sun 11am-4pm\n• Monitor elderly and children\n• Alert health authorities"
                }
            }
            msg = interpretations.get(risk, {}).get(lang, "")
            st.markdown(f"""
            <div style='background:{paper_color}; border:2px solid {risk_color};
                        border-radius:12px; padding:16px; white-space:pre-line; font-size:13px;'>
                <b>📍 {res['city']} -{res['date']}</b><br><br>{msg}
            </div>
            """, unsafe_allow_html=True)

        # Temperature history chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📈 Historique des températures / Temperature history")
        _show_temp_history(res["input"], paper_color, text_color, dark, risk_color)

        # Download
        d1, d2, _ = st.columns([1.5, 1.5, 4])
        with d1:
            try:
                from utils.pdf_report import generate_heatwave_report
                pdf_bytes = generate_heatwave_report(
                    res["city"], city_info["region"], res["date"],
                    res["probability"], res["prediction"], res["risk_level"],
                    res["input"], user["username"]
                )
                st.download_button("📄 Rapport PDF", data=pdf_bytes,
                                   file_name=f"hw_{res['city']}_{res['date']}.pdf",
                                   mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF: {e}")
        with d2:
            csv_data = pd.DataFrame([{**res["input"], "probability": prob,
                                       "prediction": pred, "risk_level": risk}])
            st.download_button("📊 Export CSV", data=csv_data.to_csv(index=False),
                               file_name=f"hw_{res['city']}_{res['date']}.csv",
                               mime="text/csv", use_container_width=True)


def _show_temp_history(input_data, paper_color, text_color, dark, risk_color):
    days = ["J-3", "J-2", "J-1", "J (aujourd'hui)"]
    temps = [
        input_data.get("temp_lag3", 30),
        input_data.get("temp_lag2", 31),
        input_data.get("temp_lag1", 33),
        input_data.get("temperature_2m_max", 38),
    ]
    threshold = input_data.get("temp_threshold", 35)

    colors = [risk_color if t >= threshold else "#007A5E" for t in temps]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days, y=temps, marker=dict(color=colors, opacity=0.85),
        text=[f"{v:.1f}°C" for v in temps], textposition="outside",
        textfont=dict(color=text_color),
    ))
    fig.add_hline(y=threshold, line_dash="dash", line_color="#CE1126",
                  annotation_text=f"Seuil local: {threshold:.1f}°C",
                  annotation_font_color="#CE1126")
    fig.update_layout(
        paper_bgcolor=paper_color, plot_bgcolor=paper_color,
        font=dict(color=text_color), height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,
                   gridcolor="#3D4154" if dark else "#EEEEEE"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
