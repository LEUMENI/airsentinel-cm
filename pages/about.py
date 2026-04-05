"""
AirSentinel CM - About Page
"""
import streamlit as st
import base64
import os

from utils.translations import t


TEAM_MEMBERS = [
    
    {
        "name": "Christy Alotse",
        "role": {"fr": "🔸Data Scientist 🔸Dans le Top 20 des 100 meilleurs étudiants camerounais - Edition 2025", "en": "🔸Data Scientist 🔸In the Top 20 of the 100 Best Cameroonian Students - 2025 Edition"},
        "photo": "profile_christy.png",
        "linkedin": "https://www.linkedin.com/in/christy-alotse/",
        "bio": {"fr": "Responsable de l’orchestration du projet, de la supervision des équipes, et de la validation des modèles et de l’application.",
                "en": "Responsible for project orchestration, team supervision, and validation of models and the application."}
    },
    {
        "name": "Danielle FOTSI",
        "role": {"fr": "Data scientist - Modèle Qualité de l'air", "en": "Software developer - Air Quality Model"},
        "photo": "profile_danielle.png",
        "linkedin": "https://www.linkedin.com/in/danielle-laura-nkonhawe-fotsi/",
        "bio": {"fr": "Data scientist - project manager. Développement et validation du modèle de prédiction de la qualité de l'air (XGBoost).",
                "en": "Data scientist - project manager. Development and validation of the air quality prediction model (XGBoost)."}
    },
    {
        "name": "Belgrade YONYA",
        "role": {"fr": "Data Scientist - modèle de vague de chaleur", "en": "Data Scientist - heat wave model"},
        "photo": "profile_belgrade.jpg",
        "linkedin": "https://www.linkedin.com/in/belgrade-yonya-29a1b9347/",
        "bio": {"fr": "Data Scientist spécialisé en analyse de données environnementales. Contribution à la validation des modèles et à l'analyse des données météorologiques camerounaises.",
                "en": "Data Scientist specialized in environmental data analysis. Contribution to model validation and analysis of Cameroonian meteorological data."}
    },
    {
        "name": "Lionel Leumeni",
        "role": {"fr": "Consultant IA & Data |  Co-Founder of AI & Automation French Speaking Africa Community | Founder of LTECH", "en": "AI & Data Consultant | Co-Founder of AI & Automation French Speaking Africa Community | Founder of LTECH"},
        "photo": "profile_leumeni.jpg",
        "linkedin": "www.linkedin.com/in/lionel-leumeni-582630226",
        "bio": {"fr": "Ingénieur logiciel. Responsable de l'architecture et du développement complet de AirSentinel CM.",
                "en": "Software engineer. Responsible for the architecture and complete development of AirSentinel CM."}
    }
    
]


def _get_img_b64(filename):
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    path = os.path.join(assets_dir, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        ext = filename.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg", "jfif"] else f"image/{ext}"
        return f"data:{mime};base64,{base64.b64encode(data).decode()}"
    return ""


def show_about():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    card_bg = "#2D3147" if dark else "#FFFFFF"
    border = "#3D4154" if dark else "#E0E0E0"
    text_color = "#E8EAF6" if dark else "#1A1A2E"

    st.markdown("""
    <div class='tricolor-bar'></div>
    <h2 style='margin:0; font-weight:900;'>ℹ️ À propos -About AirSentinel CM</h2>
    """, unsafe_allow_html=True)

    # App presentation
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#007A5E,#005A44); border-radius:14px;
                padding:28px 32px; color:white; margin:16px 0;'>
        <div style='font-size:36px; font-weight:900; margin-bottom:4px;'>🌿 AirSentinel CM</div>
        <div style='font-size:16px; opacity:0.9; font-style:italic; margin-bottom:16px;'>
            Surveiller l'air. Protéger les populations. | Monitor the air. Protect the people.
        </div>
        <div style='font-size:13px; opacity:0.85; line-height:1.6;'>
            <b>FR:</b> AirSentinel CM est une application web d'intelligence artificielle développée dans le cadre du 
            Hackathon IndabaX Cameroon 2026, sous le thème «&nbsp;L'IA au service de la résilience climatique et sanitaire&nbsp;». 
            Elle prédit l'Indice de Qualité de l'Air et les vagues de chaleur pour 40 villes du Cameroun, 
            permettant aux autorités sanitaires d'anticiper les épisodes critiques.<br><br>
            <b>EN:</b> AirSentinel CM is an AI-powered web application developed for the IndabaX Cameroon 2026 Hackathon, 
            under the theme "AI for Climate and Health Resilience". It predicts the Air Quality Index and heatwaves 
            for 40 Cameroonian cities, enabling health authorities to anticipate critical episodes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Identity card
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class='airsentinel-card'>
            <b style='color:#007A5E; font-size:16px;'>📋 Fiche d'identité / Identity</b><br><br>
            <table style='width:100%; font-size:13px; border-collapse:collapse;'>
                <tr><td style='padding:4px 8px; color:#888;'>Nom / Name</td><td style='padding:4px 8px;'><b>AirSentinel CM</b></td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Équipe / Team</td><td style='padding:4px 8px;'><b>InsightX D_Vas</b></td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Hackathon</td><td style='padding:4px 8px;'>IndabaX Cameroon 2026</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Dataset</td><td style='padding:4px 8px;'>87&nbsp;240 obs • 40 villes • 10 régions • 2020–2025</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Langues / Languages</td><td style='padding:4px 8px;'>Français / English</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Déploiement</td><td style='padding:4px 8px;'>Streamlit Cloud</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class='airsentinel-card'>
            <b style='color:#1A4D8F; font-size:16px;'>🛠️ Stack Technique / Tech Stack</b><br><br>
            <table style='width:100%; font-size:13px; border-collapse:collapse;'>
                <tr><td style='padding:4px 8px; color:#888;'>Backend</td><td style='padding:4px 8px;'>Python 3.11 + Streamlit</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>ML -AQI</td><td style='padding:4px 8px;'>XGBoost (R²=0.86)</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>ML -Heatwave</td><td style='padding:4px 8px;'>Logistic Regression</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Viz</td><td style='padding:4px 8px;'>Plotly + Folium</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>Database</td><td style='padding:4px 8px;'>SQLite</td></tr>
                <tr><td style='padding:4px 8px; color:#888;'>API Météo</td><td style='padding:4px 8px;'>Open-Meteo (real-time)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ML Models
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🤖 Modèles de Machine Learning / ML Models")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""
        <div class='airsentinel-card' style='border-left:4px solid #007A5E;'>
            <b style='color:#007A5E; font-size:15px;'>🌫️ Modèle AQI -XGBoost</b><br><br>
            <b>Variables clés / Key features:</b>
            <ul style='font-size:12px; margin-top:6px;'>
                <li>precipitation_sum (précipitations totales)</li>
                <li>rain_sum (pluie)</li>
                <li>precipitation_hours (heures de pluie)</li>
                <li>et0_fao_evapotranspiration</li>
                <li>time_month, time_cos (cyclique)</li>
                <li>temperature_2m_max, temperature_2m_mean</li>
            </ul>
            <br>
            <b>Métriques de performance / Metrics:</b><br>
            <table style='font-size:12px; width:100%;'>
                <tr><td>R² validation</td><td><b style='color:#007A5E;'>0.861</b></td></tr>
                <tr><td>R² holdout</td><td><b style='color:#007A5E;'>0.857</b></td></tr>
                <tr><td>MAE holdout</td><td><b>1.62 µg/m³</b></td></tr>
                <tr><td>RMSE holdout</td><td><b>2.04 µg/m³</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown("""
        <div class='airsentinel-card' style='border-left:4px solid #CE1126;'>
            <b style='color:#CE1126; font-size:15px;'>🌡️ Modèle Vague de chaleur -Régression Logistique</b><br><br>
            <b>Définition vague de chaleur:</b><br>
            <small>3 jours consécutifs avec Temp max > 90ème percentile local (ETCCDI)</small><br><br>
            <b>Variables clés / Key features:</b>
            <ul style='font-size:12px; margin-top:6px;'>
                <li>temperature_2m_max + temp_threshold</li>
                <li>temp_lag1, temp_lag2, temp_lag3 (historique)</li>
                <li>hot_day (indicateur journée chaude)</li>
                <li>shortwave_radiation_sum</li>
                <li>city (encodage TargetEncoder)</li>
            </ul>
            <br>
            <b>Seuil de décision / Decision threshold: 0.20</b><br>
            <small>(Optimisé pour maximiser le rappel -sécurité sanitaire)</small>
        </div>
        """, unsafe_allow_html=True)

    # Color code
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎨 Code couleur / Color Code")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.markdown("""
        <div style='background:#007A5E; border-radius:10px; padding:16px; text-align:center; color:white;'>
            <div style='font-size:24px; font-weight:900;'>✅ SAFE</div>
            <div style='font-size:20px; font-weight:800;'>0 -33</div>
            <div style='font-size:12px; opacity:0.9; margin-top:6px;'>
                Qualité acceptable<br>Air quality acceptable
            </div>
        </div>
        """, unsafe_allow_html=True)
    with cc2:
        st.markdown("""
        <div style='background:#FCD116; border-radius:10px; padding:16px; text-align:center; color:#1A1A1A;'>
            <div style='font-size:24px; font-weight:900;'>⚠️ VIGILANCE</div>
            <div style='font-size:20px; font-weight:800;'>34 -66</div>
            <div style='font-size:12px; opacity:0.8; margin-top:6px;'>
                Qualité modérée -Personnes sensibles<br>Moderate -Sensitive people
            </div>
        </div>
        """, unsafe_allow_html=True)
    with cc3:
        st.markdown("""
        <div style='background:#CE1126; border-radius:10px; padding:16px; text-align:center; color:white; animation:blink 1.5s infinite;'>
            <div style='font-size:24px; font-weight:900;'>🚨 DANGER</div>
            <div style='font-size:20px; font-weight:800;'>67 -100</div>
            <div style='font-size:12px; opacity:0.9; margin-top:6px;'>
                Qualité dangereuse -Alertes sanitaires<br>Dangerous -Health alerts
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Team
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 👥 L'équipe InsightX D_Vas")
    st.markdown("""
    <div style='text-align:center; color:#888; font-size:13px; margin-bottom:20px;'>
        IndabaX Cameroon 2026 • Hackathon "L'IA au service de la résilience climatique et sanitaire"
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (col, member) in enumerate(zip(cols, TEAM_MEMBERS)):
        with col:
            img_src = _get_img_b64(member["photo"])
            img_html = f'<img src="{img_src}" style="width:100px; height:100px; object-fit:cover; border-radius:50%; border:3px solid #007A5E;">' if img_src else '<div style="width:100px; height:100px; border-radius:50%; background:#007A5E; display:flex; align-items:center; justify-content:center; font-size:36px; color:white;">👤</div>'

            st.markdown(f"""
            <div style='background:{card_bg}; border:1px solid {border}; border-radius:12px;
                        padding:20px; text-align:center;'>
                <div style='display:flex; justify-content:center; margin-bottom:12px;'>
                    {img_html}
                </div>
                <div style='font-weight:800; font-size:15px;'>{member['name']}</div>
                <div style='color:#007A5E; font-size:12px; margin:4px 0;'>{member['role'][lang]}</div>
                <div style='font-size:11px; color:#888; line-height:1.4;'>{member['bio'][lang][:120]}...</div>
                <a href='{member['linkedin']}' target='_blank'
                   style='display:inline-block; margin-top:10px; background:#0077B5; color:white;
                          padding:4px 12px; border-radius:6px; text-decoration:none; font-size:11px;'>
                    LinkedIn 🔗
                </a>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; color:#888; font-size:12px; border-top:1px solid #333; padding-top:16px;'>
        🌿 <b>AirSentinel CM</b> • InsightX D_Vas • IndabaX Cameroon 2026<br>
        Développé avec ❤️ pour le Cameroun • Made with ❤️ for Cameroon<br>
        <span style='color:#007A5E;'>Python</span> •
        <span style='color:#FCD116;'>Streamlit</span> •
        <span style='color:#CE1126;'>XGBoost</span> •
        <span style='color:#1A4D8F;'>Folium</span> •
        <span style='color:#007A5E;'>Open-Meteo</span>
    </div>
    """, unsafe_allow_html=True)
