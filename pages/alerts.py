"""
AirSentinel CM - Alerts Page
"""
import streamlit as st
import pandas as pd
import io

from utils.translations import t, CAMEROON_CITIES
from utils.database import (create_alert, get_user_alerts, delete_alert,
                              get_all_alerts, log_activity)


def show_alerts():
    lang = st.session_state.lang
    user = st.session_state.user

    st.markdown("""
    <div class='tricolor-bar'></div>
    <h2 style='margin:0; font-weight:900;'>🔔 Alertes / Alerts</h2>
    <p style='color:#888; margin-top:4px;'>AirSentinel CM — Système d'alertes</p>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3= st.tabs([
        "➕ Créer alerte AQI",
        
        f"📋 {t('alert_my_alerts', lang)}",
        f"📨 {t('alert_notifications', lang)}",
    ])

    city_list = list(CAMEROON_CITIES.keys())

    with tab1:
        _create_alert_form(lang, city_list, user, alert_type="aqi")

    with tab2:
        _show_my_alerts(lang, user)

    with tab3:
        _show_notifications(lang, user)


def _create_alert_form(lang, city_list, user, alert_type):
    type_label = "AQI (Qualité de l'air)" if alert_type == "aqi" else "Vague de chaleur / Heatwave"
    icon = "🌫️" if alert_type == "aqi" else "🌡️"

    st.markdown(f"### {icon} Créer une alerte — {type_label}")

    col1, col2 = st.columns([2, 3])
    with col1:
        city = st.selectbox("Ville / City", city_list, key=f"alert_city_{alert_type}")

        if alert_type == "aqi":
            threshold = st.slider(
                t("alert_threshold", lang) + " — Score AQI (0-100)",
                min_value=0, max_value=100, value=66,
                help="L'alerte se déclenche quand le score AQI dépasse ce seuil"
            )
            # Live preview
            if threshold <= 33:
                badge = "🟢 SAFE"
                color = "#007A5E"
            elif threshold <= 66:
                badge = "🟡 VIGILANCE"
                color = "#FCD116"
            else:
                badge = "🔴 DANGER"
                color = "#CE1126"
        else:
            threshold = st.slider(
                t("alert_threshold", lang) + " — Probabilité vague (0-100%)",
                min_value=0, max_value=100, value=50,
                help="L'alerte se déclenche quand la probabilité de vague dépasse ce seuil"
            )
            if threshold <= 20:
                badge = "🟢 SAFE"
                color = "#007A5E"
            elif threshold <= 50:
                badge = "🟡 VIGILANCE"
                color = "#FCD116"
            else:
                badge = "🔴 DANGER"
                color = "#CE1126"

        st.markdown(f"""
        <div style='background:{color}; color:white; padding:10px 16px; border-radius:8px;
                    text-align:center; font-weight:700; margin-top:8px;'>
            Aperçu: {badge}<br>
            <small>Seuil: {threshold}{"%" if alert_type == "heatwave" else "/100"}</small>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🔔 {t('alert_create_btn', lang)}", key=f"create_btn_{alert_type}", use_container_width=True):
            create_alert(user["id"], city, alert_type, threshold)
            st.success(f"✅ {t('alert_created_ok', lang)}")
            st.rerun()

    with col2:
        st.markdown("""
        <div style='background:rgba(0,122,94,0.1); border:1px solid #007A5E; border-radius:10px; padding:16px;'>
            <b>💡 Comment fonctionnent les alertes / How alerts work</b><br><br>
            <b>FR:</b> Lorsque le score AQI ou la probabilité de vague de chaleur dépasse votre seuil,
            une notification est générée et transmise à l'administrateur pour validation avant diffusion.<br><br>
            <b>EN:</b> When the AQI score or heatwave probability exceeds your threshold,
            a notification is generated and sent to the administrator for validation before broadcasting.<br><br>
            <b>Flux d'alerte / Alert flow:</b><br>
            📊 Prédiction → 🔔 Alerte générée → 👑 Validation admin → 📱 Diffusion citoyens
        </div>
        """, unsafe_allow_html=True)

        # SMS message templates
        st.markdown("**📱 Messages types / Alert templates:**")
        if alert_type == "aqi":
            st.code("""🚨 AirSentinel CM - ALERTE QUALITÉ DE L'AIR
Ville: {city} | Score: {score}/100 | Niveau: {level}

⚠️ La qualité de l'air est dégradée.
Recommandations:
• Limitez les activités extérieures
• Portez un masque si nécessaire  
• Surveillez les personnes vulnérables
                
📍 Restez informé: airsentinel.cm""", language=None)
        else:
            st.code("""🌡️ AirSentinel CM - ALERTE VAGUE DE CHALEUR
Ville: {city} | Probabilité: {prob}% | Niveau: {level}

⚠️ Vague de chaleur probable dans 72h.
Recommandations:
• Hydratez-vous régulièrement
• Évitez le soleil entre 11h et 16h
• Surveillez personnes âgées et enfants
• Cherchez des endroits frais
                
📍 Restez informé: airsentinel.cm""", language=None)


def _show_my_alerts(lang, user):
    alerts = get_user_alerts(user["id"])
    if not alerts:
        st.info("📭 " + t("no_data", lang))
        return

    st.markdown(f"**{len(alerts)} alerte(s) configurée(s)**")

    for alert in alerts:
        type_icon = "🌫️" if alert["alert_type"] == "aqi" else "🌡️"
        type_label = "AQI" if alert["alert_type"] == "aqi" else "Vague de chaleur"
        validated_status = {0: "⏳ En attente", 1: "✅ Validée", -1: "❌ Rejetée"}

        col_info, col_btn = st.columns([5, 1])
        with col_info:
            st.markdown(f"""
            <div class='airsentinel-card' style='display:flex; align-items:center; gap:12px;'>
                <div style='font-size:28px;'>{type_icon}</div>
                <div>
                    <b>{alert['city']}</b> — {type_label}<br>
                    <small>Seuil: {alert['threshold']} | 
                    Statut: {validated_status.get(alert.get('validated', 0), '⏳')}<br>
                    Créée le: {alert['created_at'][:10]}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if st.button("🗑️", key=f"del_alert_{alert['id']}", help="Supprimer"):
                delete_alert(alert["id"], user["id"])
                st.success(t("alert_deleted_ok", lang))
                st.rerun()


def _show_notifications(lang, user):
    st.markdown("### 📲 Import & Simulation SMS")

    col_up, col_sim = st.columns(2)

    with col_up:
        st.markdown("""
        <div style='background:rgba(26,77,143,0.1); border:1px solid #1A4D8F;
                    border-radius:10px; padding:14px;'>
            <b>📁 Importer un fichier de numéros</b><br>
            <small>Format: CSV avec colonne 'phone' ou fichier texte
            (un numéro par ligne)</small>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("Fichier numéros / Phone numbers file",
                                     type=["csv", "txt"],
                                     help="CSV ou TXT avec numéros de téléphone")

        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                    phones = df.iloc[:, 0].astype(str).tolist()
                else:
                    content = uploaded.read().decode("utf-8")
                    phones = [l.strip() for l in content.splitlines() if l.strip()]

                st.session_state["sim_phones"] = phones
                st.success(f"✅ {len(phones)} numéro(s) chargé(s)")
                st.dataframe(pd.DataFrame(phones, columns=["Numéro"]), height=150)
            except Exception as e:
                st.error(f"Erreur: {e}")

    with col_sim:
        st.markdown("""
        <div style='background:rgba(206,17,38,0.1); border:1px solid #CE1126;
                    border-radius:10px; padding:14px;'>
            <b>📤 Simuler l'envoi de notifications</b><br>
            <small>Simulation des alertes SMS/WhatsApp aux citoyens</small>
        </div>
        """, unsafe_allow_html=True)

        phones = st.session_state.get("sim_phones", [])
        if phones:
            city_sim = st.selectbox("Ville concernée / Affected city", list(CAMEROON_CITIES.keys()), key="sim_city")
            msg_type = st.radio("Type de message", ["🌫️ Qualité de l'air"])

            if st.button("📤 Simuler l'envoi", use_container_width=True):
                log_activity(user["id"], "SMS_SIMULATION",
                             f"City: {city_sim}, {len(phones)} contacts")
                with st.expander("📋 Rapport de simulation / Simulation report", expanded=True):
                    st.markdown(f"**{len(phones)} messages simulés pour {city_sim}**")
                    for i, phone in enumerate(phones[:10]):
                        st.markdown(f"✅ `{phone}` — Message envoyé (simulation)")
                    if len(phones) > 10:
                        st.markdown(f"_... et {len(phones)-10} autres_")
                st.success(f"🎉 Simulation terminée: {len(phones)} notifications simulées!")
        else:
            st.info("📁 Importez d'abord un fichier de numéros.")
