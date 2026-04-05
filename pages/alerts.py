"""
AirSentinel CM - Alerts Page
Temps réel automatique + simulation WhatsApp/SMS concret
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.translations import t, CAMEROON_CITIES
from utils.database import (create_alert, get_user_alerts, delete_alert,
                              get_all_alerts, log_activity)
from utils.models import predict_aqi, predict_heatwave, get_risk_color, CITY_THRESHOLDS
from utils.weather_api import fetch_weather, fetch_weather_3days


def show_alerts():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user = st.session_state.user
    paper_color = "#2C2C2E" if dark else "#FFFFFF"
    text_color  = "#F2F2F7" if dark else "#2C2C2E"
    subtext     = "#AEAEB2" if dark else "#636366"
    border      = "#3A3A3C" if dark else "#D4CDB8"

    st.markdown(f"""
    <div class='section-header'>
        <h3>{'🔔 Alertes -Système de surveillance' if lang=='fr' else '🔔 Alerts -Monitoring system'}</h3>
        <p>{'Alertes automatiques basées sur les données temps réel Open-Meteo' if lang=='fr'
            else 'Automatic alerts based on Open-Meteo real-time data'}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚡ " + ("Scan temps réel" if lang=="fr" else "Real-time scan"),
        "➕ " + ("Créer alerte AQI" if lang=="fr" else "Create AQI alert"),
        "🌡️ " + ("Créer alerte Vague" if lang=="fr" else "Create Heatwave alert"),
        "📋 " + ("Mes alertes" if lang=="fr" else "My alerts"),
        "📱 WhatsApp " + ("simulation" if lang=="fr" else "simulation"),
    ])

    city_list = list(CAMEROON_CITIES.keys())

    with tab1:
        _show_realtime_scan(lang, user, paper_color, text_color, subtext, border, dark)
    with tab2:
        _create_alert_form(lang, city_list, user, paper_color, subtext, border, "aqi")
    with tab3:
        _create_alert_form(lang, city_list, user, paper_color, subtext, border, "heatwave")
    with tab4:
        _show_my_alerts(lang, user, paper_color, text_color, subtext, border)
    with tab5:
        _show_whatsapp_demo(lang, user, paper_color, text_color, subtext, border, dark)


def _show_realtime_scan(lang, user, paper_color, text_color, subtext, border, dark):
    """Scan automatique temps réel d'une ville."""
    st.markdown(f"""
    <div class='as-card'>
        <b>{'⚡ Déclenchement automatique d\'alertes' if lang=='fr' else '⚡ Automatic alert triggering'}</b><br>
        <small style='color:{subtext};'>
            {'Sélectionnez une ville, cliquez "Scanner". L\'application récupère les données météo en temps réel, '
             'exécute les deux modèles ML, et déclenche les alertes automatiquement si les seuils sont dépassés.'
             if lang=='fr' else
             'Select a city, click "Scan". The application fetches real-time weather data, '
             'runs both ML models, and automatically triggers alerts if thresholds are exceeded.'}
        </small>
    </div>
    """, unsafe_allow_html=True)

    city_list = list(CAMEROON_CITIES.keys())
    sc1, sc2, sc3, sc4 = st.columns([2, 1, 1, 1])
    with sc1:
        scan_city = st.selectbox("🏙️ Ville à scanner" if lang=="fr" else "🏙️ City to scan",
                                  city_list, key="scan_city")
    with sc2:
        aqi_thresh = st.number_input("Seuil AQI", value=50, min_value=0, max_value=100, key="scan_aqi_t")
    with sc3:
        hw_thresh = st.number_input("Seuil HW (%)", value=30, min_value=0, max_value=100, key="scan_hw_t")
    with sc4:
        st.markdown("<br>", unsafe_allow_html=True)
        scan_btn = st.button("🔍 Scanner maintenant" if lang=="fr" else "🔍 Scan now",
                              use_container_width=True, key="scan_btn")

    if scan_btn:
        city_info = CAMEROON_CITIES[scan_city]
        with st.spinner(f"⚡ Scan temps réel de {scan_city}..." if lang=="fr" else f"⚡ Real-time scan of {scan_city}..."):
            # 1. Fetch weather
            today = datetime.now().strftime("%Y-%m-%d")
            weather = fetch_weather(city_info["lat"], city_info["lon"], today)
            lags    = fetch_weather_3days(city_info["lat"], city_info["lon"])

            if not weather["success"]:
                st.error(f"❌ Open-Meteo: {weather.get('error','')}")
                return

            wd = weather["data"]
            threshold = CITY_THRESHOLDS.get(scan_city, 36.0)

            # 2. Run AQI model
            aqi_input = {**wd, "city": scan_city, "date": today}
            try:
                aqi_res = predict_aqi(aqi_input)
            except Exception as e:
                aqi_res = {"score": 0, "pm25_raw": 0, "risk_level": "SAFE"}

            # 3. Run Heatwave model
            hw_input = {**wd, "city": scan_city, "date": today,
                        "temp_threshold": threshold,
                        "temp_lag1": lags[2] if len(lags)>=3 else wd.get("temperature_2m_max",30)-1,
                        "temp_lag2": lags[1] if len(lags)>=3 else wd.get("temperature_2m_max",30)-2,
                        "temp_lag3": lags[0] if len(lags)>=3 else wd.get("temperature_2m_max",30)-3}
            try:
                hw_res = predict_heatwave(hw_input)
            except Exception as e:
                hw_res = {"probability": 0, "prediction": 0, "risk_level": "SAFE"}

            # 4. Display results
            st.markdown(f"""
            <div style='background:{paper_color}; border:1px solid {border}; border-radius:10px; padding:16px; margin:12px 0;'>
                <b style='font-size:14px;'>📊 {'Résultats du scan pour' if lang=='fr' else 'Scan results for'} {scan_city}</b>
                <div style='font-size:11px; color:{subtext}; margin-bottom:10px;'>{today} · Open-Meteo</div>
                <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
                    <div style='background:{"#1C2C1C" if dark else "#F0FFF4"}; border:1px solid {"#2A4A2A" if dark else "#C3E6CB"};
                                border-radius:8px; padding:12px; border-left:4px solid {get_risk_color(aqi_res["risk_level"])};'>
                        <div style='font-size:11px; color:{subtext};'>🌫️ Proxy PM2.5</div>
                        <div style='font-size:22px; font-weight:800; color:{get_risk_color(aqi_res["risk_level"])};
                                    font-family:"JetBrains Mono",monospace;'>{aqi_res["score"]:.1f}/100</div>
                        <div style='font-size:12px;'>PM2.5 estimé: <b>{aqi_res["pm25_raw"]:.2f} µg/m³</b></div>
                        <span class='badge-{aqi_res["risk_level"].lower()}'>{aqi_res["risk_level"]}</span>
                    </div>
                    <div style='background:{"#2C1C1C" if dark else "#FFF8F0"}; border:1px solid {"#4A2A2A" if dark else "#FFD6A5"};
                                border-radius:8px; padding:12px; border-left:4px solid {get_risk_color(hw_res["risk_level"])};'>
                        <div style='font-size:11px; color:{subtext};'>🌡️ {'Vague de chaleur' if lang=='fr' else 'Heatwave'}</div>
                        <div style='font-size:22px; font-weight:800; color:{get_risk_color(hw_res["risk_level"])};
                                    font-family:"JetBrains Mono",monospace;'>{hw_res["probability"]*100:.1f}%</div>
                        <div style='font-size:12px;'>Tmax: <b>{wd.get("temperature_2m_max",0):.1f}°C</b> / P90: <b>{threshold}°C</b></div>
                        <span class='badge-{hw_res["risk_level"].lower()}'>{hw_res["risk_level"]}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 5. Auto-trigger alerts
            triggered = []
            if aqi_res["score"] >= aqi_thresh:
                create_alert(user["id"], scan_city, "aqi", aqi_thresh)
                triggered.append(f"🌫️ AQI {aqi_res['score']:.1f} ≥ seuil {aqi_thresh}")
            if hw_res["probability"] * 100 >= hw_thresh:
                create_alert(user["id"], scan_city, "heatwave", hw_thresh)
                triggered.append(f"🌡️ HW {hw_res['probability']*100:.1f}% ≥ seuil {hw_thresh}%")

            if triggered:
                for tr in triggered:
                    st.warning(f"⚡ {'Alerte automatique déclenchée' if lang=='fr' else 'Automatic alert triggered'}: {tr}")
                log_activity(user["id"], "AUTO_ALERT", f"City:{scan_city} AQI:{aqi_res['score']:.1f} HW:{hw_res['probability']:.2f}")
            else:
                st.success(f"✅ {'Aucune alerte -seuils non dépassés.' if lang=='fr' else 'No alert -thresholds not exceeded.'}")

    # Recent scans table
    st.markdown("<br>", unsafe_allow_html=True)
    alerts = get_user_alerts(user["id"])
    if alerts:
        st.markdown(f"<div class='form-label-custom'>{'📋 Alertes récentes' if lang=='fr' else '📋 Recent alerts'}</div>", unsafe_allow_html=True)
        df = pd.DataFrame(alerts[:10])
        if not df.empty:
            st.dataframe(df[["city", "alert_type", "threshold", "created_at"]].rename(columns={
                "city": "Ville", "alert_type": "Type", "threshold": "Seuil", "created_at": "Date"
            }), use_container_width=True, hide_index=True)


def _create_alert_form(lang, city_list, user, paper_color, subtext, border, alert_type):
    icon = "🌫️" if alert_type == "aqi" else "🌡️"
    type_label = ("Proxy PM2.5 / Qualité de l'air" if lang=="fr" else "Proxy PM2.5 / Air Quality") if alert_type == "aqi" else ("Vague de chaleur" if lang=="fr" else "Heatwave")

    st.markdown(f"""
    <div class='section-header' style='margin-top:8px;'>
        <h3>{icon} {'Créer une alerte —' if lang=='fr' else 'Create alert —'} {type_label}</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])
    with col1:
        city = st.selectbox("Ville" if lang=="fr" else "City", city_list, key=f"ac_{alert_type}")
        if alert_type == "aqi":
            thresh = st.slider("Seuil AQI (0–100)" if lang=="fr" else "AQI threshold (0–100)",
                               0, 100, 50, key=f"at_{alert_type}")
            rc = get_risk_color("DANGER" if thresh > 66 else ("VIGILANCE" if thresh > 33 else "SAFE"))
            lvl = "DANGER" if thresh > 66 else ("VIGILANCE" if thresh > 33 else "SAFE")
        else:
            thresh = st.slider("Seuil probabilité (0–100%)" if lang=="fr" else "Probability threshold (0–100%)",
                               0, 100, 30, key=f"at_{alert_type}")
            rc = get_risk_color("DANGER" if thresh > 50 else ("VIGILANCE" if thresh > 20 else "SAFE"))
            lvl = "DANGER" if thresh > 50 else ("VIGILANCE" if thresh > 20 else "SAFE")

        st.markdown(f"""
        <div style='background:{rc}18; border:1px solid {rc}; border-radius:8px;
                    padding:10px; text-align:center; margin-top:8px;'>
            <span class='badge-{lvl.lower()}'>{lvl}</span>
            <div style='font-size:12px; color:{subtext}; margin-top:4px;'>
                {'Seuil' if lang=='fr' else 'Threshold'}: <b>{thresh}{'%' if alert_type=='heatwave' else '/100'}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🔔 {'Créer l\'alerte' if lang=='fr' else 'Create alert'}", key=f"create_{alert_type}", use_container_width=True):
            create_alert(user["id"], city, alert_type, thresh)
            st.success("✅ Alerte créée !" if lang=="fr" else "✅ Alert created!")
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class='as-card'>
            <b>{'💡 Comment fonctionnent les alertes' if lang=='fr' else '💡 How alerts work'}</b><br><br>
            <div style='font-size:13px; line-height:1.7;'>
                {'🔄 <b>Flux automatique</b> : Scan temps réel → Modèle ML → Score → Comparaison seuil → Alerte<br>'
                 '👑 <b>Validation admin</b> : Chaque alerte est validée avant diffusion publique<br>'
                 '📱 <b>Diffusion</b> : SMS et WhatsApp aux citoyens de la ville concernée'
                 if lang=='fr' else
                 '🔄 <b>Automatic flow</b>: Real-time scan → ML Model → Score → Threshold → Alert<br>'
                 '👑 <b>Admin validation</b>: Each alert is validated before public broadcast<br>'
                 '📱 <b>Broadcast</b>: SMS and WhatsApp to citizens of the concerned city'}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _show_my_alerts(lang, user, paper_color, text_color, subtext, border):
    alerts = get_user_alerts(user["id"])
    if not alerts:
        st.info("📭 " + ("Aucune alerte configurée." if lang=="fr" else "No alerts configured."))
        return

    st.markdown(f"**{len(alerts)} alerte(s)**")
    for alert in alerts:
        icon = "🌫️" if alert["alert_type"] == "aqi" else "🌡️"
        validated = {0: "⏳ En attente" if lang=="fr" else "⏳ Pending",
                     1: "✅ Validée" if lang=="fr" else "✅ Validated",
                     -1: "❌ Rejetée" if lang=="fr" else "❌ Rejected"}.get(alert.get("validated", 0), "⏳")
        col_i, col_b = st.columns([5, 1])
        with col_i:
            st.markdown(f"""
            <div class='as-card' style='padding:10px 14px;'>
                {icon} <b>{alert['city']}</b> -{alert['alert_type']}
                &nbsp;|&nbsp; {'Seuil' if lang=='fr' else 'Threshold'}: <b>{alert['threshold']}</b>
                &nbsp;|&nbsp; {validated}
                <br><small style='color:{subtext};'>{alert.get('created_at','')[:16]}</small>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            if st.button("🗑️", key=f"del_{alert['id']}", help="Supprimer"):
                delete_alert(alert["id"], user["id"])
                st.rerun()


def _show_whatsapp_demo(lang, user, paper_color, text_color, subtext, border, dark):
    """Exemple concret de réception d'alerte WhatsApp par un utilisateur."""
    st.markdown(f"""
    <div class='section-header'>
        <h3>📱 {'Simulation -Alerte WhatsApp citoyen' if lang=='fr' else 'Simulation -Citizen WhatsApp alert'}</h3>
        <p>{'Exemple concret d\'une alerte reçue par un citoyen de Garoua' if lang=='fr'
            else 'Concrete example of an alert received by a citizen of Garoua'}</p>
    </div>
    """, unsafe_allow_html=True)

    col_demo, col_phone = st.columns([2, 3])

    with col_demo:
        scenario = st.selectbox(
            "Scénario de démonstration" if lang=="fr" else "Demo scenario",
            ["🌡️ Vague de chaleur -Garoua DANGER",
             "🌫️ Qualité de l'air -Maroua VIGILANCE",
             "✅ Tout normal -Yaoundé SAFE"]
        )

        city_for_demo = st.selectbox(
            "Ville destinataire" if lang=="fr" else "Recipient city",
            list(CAMEROON_CITIES.keys()),
            key="wa_city_input"   # ← clé unique pour le widget
        )

        phone_demo = st.text_input(
            "Numéro WhatsApp" if lang=="fr" else "WhatsApp number",
            value="+237 690 000 000",
            key="wa_phone_input"  # ← clé unique pour le widget (différente de wa_phone)
        )

        if st.button(
            "📤 Envoyer simulation" if lang=="fr" else "📤 Send simulation",
            use_container_width=True,
            key="wa_send"
        ):
            log_activity(user["id"], "WHATSAPP_SIMULATION",
                         f"City:{city_for_demo} Phone:{phone_demo}")
            # On sauvegarde dans des clés DIFFÉRENTES des clés des widgets
            st.session_state["wa_sent"]     = True
            st.session_state["wa_scenario"] = scenario
            st.session_state["wa_saved_phone"] = phone_demo   # ← clé différente
            st.session_state["wa_saved_city"]  = city_for_demo # ← clé différente
            st.rerun()

        # Import fichier
        st.markdown("---")
        st.markdown(
            f"<p class='form-label-custom'>{'📁 Diffusion en masse' if lang=='fr' else '📁 Mass broadcast'}</p>",
            unsafe_allow_html=True
        )
        uploaded = st.file_uploader(
            "CSV/TXT numéros" if lang=="fr" else "CSV/TXT numbers",
            type=["csv","txt"],
            key="wa_upload"
        )
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    phones = pd.read_csv(uploaded).iloc[:,0].astype(str).tolist()
                else:
                    phones = [l.strip() for l in uploaded.read().decode().splitlines() if l.strip()]
                st.session_state["mass_phones"] = phones
                st.success(f"✅ {len(phones)} numéro(s) importé(s)")
            except Exception as e:
                st.error(f"Erreur: {e}")

        if st.session_state.get("mass_phones"):
            nb = len(st.session_state["mass_phones"])
            if st.button(f"📤 Simuler diffusion ({nb} destinataires)", use_container_width=True):
                st.success(f"🎉 {nb} messages WhatsApp simulés !")
                log_activity(user["id"], "MASS_WHATSAPP_SIM",
                             f"{nb} contacts, city:{city_for_demo}")

    with col_phone:
        if st.session_state.get("wa_sent"):
            sc       = st.session_state.get("wa_scenario", "")
            # On lit depuis les clés de SAUVEGARDE, pas les clés des widgets
            city_wa  = st.session_state.get("wa_saved_city",  "Garoua")
            phone_wa = st.session_state.get("wa_saved_phone", "+237 690 000 000")
            now_str  = datetime.now().strftime("%H:%M")

            if "Vague" in sc or "Heatwave" in sc or "DANGER" in sc:
                msg_fr = f"""🚨 *ALERTE VAGUE DE CHALEUR -AirSentinel CM*

📍 *Ville:* {city_wa}
🌡️ *Niveau:* DANGER
📊 *Probabilité:* 87.3%

⚠️ *Recommandations urgentes:*
- Restez à l'intérieur entre 11h et 16h
- Hydratez-vous toutes les heures
- Surveillez les personnes âgées et les enfants
- Appelez le SAMU si malaise: 15

📱 _Alerte générée automatiquement par AirSentinel CM_
🌿 _InsightX D_Vas -IndabaX Cameroon 2026_"""
                msg_en = f"""🚨 *HEATWAVE ALERT -AirSentinel CM*

📍 *City:* {city_wa}
🌡️ *Level:* DANGER
📊 *Probability:* 87.3%

⚠️ *Urgent recommendations:*
- Stay indoors between 11am and 4pm
- Hydrate every hour
- Monitor elderly and children
- Call emergency if heatstroke: 15

📱 _Automatically generated by AirSentinel CM_
🌿 _InsightX D_Vas -IndabaX Cameroon 2026_"""
                bg_strip = "#B91C1C"

            elif "Qualité" in sc or "Air Quality" in sc:
                msg_fr = f"""⚠️ *ALERTE QUALITÉ DE L'AIR -AirSentinel CM*

📍 *Ville:* {city_wa}
🌫️ *Proxy PM2.5:* 58.4/100
📊 *Niveau:* VIGILANCE

📌 *Recommandations:*
- Personnes sensibles: limitez les activités extérieures
- Portez un masque si vous avez des problèmes respiratoires
- Aérez vos locaux aux heures fraîches (matin/soir)

📱 _Alerte générée automatiquement par AirSentinel CM_
🌿 _InsightX D_Vas -IndabaX Cameroon 2026_"""
                msg_en = f"""⚠️ *AIR QUALITY ALERT -AirSentinel CM*

📍 *City:* {city_wa}
🌫️ *Proxy PM2.5:* 58.4/100
📊 *Level:* VIGILANCE

📌 *Recommendations:*
- Sensitive groups: limit outdoor activities
- Wear a mask if you have respiratory issues
- Ventilate rooms during cool hours (morning/evening)

📱 _Automatically generated by AirSentinel CM_
🌿 _InsightX D_Vas -IndabaX Cameroon 2026_"""
                bg_strip = "#B8860B"

            else:
                msg_fr = f"""✅ *BONNE NOUVELLE -AirSentinel CM*

📍 *Ville:* {city_wa}
🌿 *Qualité de l'air:* SAFE (12.3/100)
🌡️ *Vague de chaleur:* Aucun risque (4.2%)

😊 La qualité de l'air est bonne aujourd'hui.
Profitez des espaces verts en toute sécurité !

📱 _Rapport quotidien -AirSentinel CM_
🌿 _InsightX D_Vas -IndabaX Cameroon 2026_"""
                msg_en = f"""✅ *GOOD NEWS -AirSentinel CM*

📍 *City:* {city_wa}
🌿 *Air quality:* SAFE (12.3/100)
🌡️ *Heatwave:* No risk (4.2%)

😊 Air quality is good today.
Enjoy outdoor spaces safely!

📱 _Daily report -AirSentinel CM_
🌿 _InsightX D_Vas -IndabaX Cameroon 2026_"""
                bg_strip = "#007A5E"

            msg = msg_fr if lang == "fr" else msg_en
            msg_html = msg.replace("\n", "<br>").replace("*", "<b>", 1)
            for _ in range(20):
                msg_html = msg_html.replace("*", "</b>", 1) if "<b>" in msg_html else msg_html.replace("*","",1)

            st.markdown(f"""
            <div style='display:flex; justify-content:center;'>
              <div style='width:310px;'>
                <div style='background:{"#1A1A1A" if dark else "#2C2C2C"}; border-radius:36px;
                            padding:12px; box-shadow:0 8px 32px rgba(0,0,0,0.4);
                            border:3px solid {"#3A3A3A" if dark else "#555"};'>
                  <div style='display:flex; justify-content:space-between; padding:4px 16px;
                              font-size:11px; color:#CCC; margin-bottom:4px;'>
                    <span>Cameroun Mobile</span><span>{now_str}</span>
                  </div>
                  <div style='background:{bg_strip}; border-radius:8px 8px 0 0;
                              padding:10px 14px; display:flex; align-items:center; gap:8px;'>
                    <div style='width:32px; height:32px; border-radius:50%; background:white;
                                display:flex; align-items:center; justify-content:center;
                                font-size:18px;'>🌿</div>
                    <div>
                      <div style='color:white; font-weight:700; font-size:13px;'>AirSentinel CM</div>
                      <div style='color:rgba(255,255,255,0.8); font-size:10px;'>en ligne · {now_str}</div>
                    </div>
                  </div>
                  <div class='whatsapp-container' style='min-height:280px; padding:14px;'>
                    <div class='whatsapp-bubble'>
                      {msg_html}
                      <div class='whatsapp-time'>{now_str} ✓✓</div>
                    </div>
                  </div>
                  <div style='background:{"#2C2C2E" if dark else "#F0F0F0"}; border-radius:0 0 8px 8px;
                              padding:8px 12px; display:flex; align-items:center; gap:8px;'>
                    <div style='flex:1; background:{"#3A3A3C" if dark else "white"};
                                border-radius:20px; padding:6px 12px; font-size:11px;
                                color:{subtext};'>Aa</div>
                    <div style='background:#25D366; border-radius:50%; width:32px; height:32px;
                                display:flex; align-items:center; justify-content:center;
                                font-size:14px;'>🎤</div>
                  </div>
                </div>
                <div style='text-align:center; margin-top:10px; font-size:11px; color:{subtext};'>
                  📱 Envoyé à: <b>{phone_wa}</b>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='text-align:center; padding:40px 20px; color:{subtext};'>
                <div style='font-size:48px; margin-bottom:12px;'>📱</div>
                <div style='font-size:14px;'>
                    {'Configurez un scénario et cliquez "Envoyer simulation" pour voir un exemple concret d\'alerte WhatsApp.' if lang=='fr'
                     else 'Configure a scenario and click "Send simulation" to see a concrete WhatsApp alert example.'}
                </div>
            </div>
            """, unsafe_allow_html=True)