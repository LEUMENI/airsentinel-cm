"""
AirSentinel CM — Main Application
IndabaX Cameroon 2026 | InsightX D_Vas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from datetime import datetime

from utils.database import init_db, authenticate_user, create_user
from utils.styles import get_css

st.set_page_config(
    page_title="AirSentinel CM",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

if "authenticated"  not in st.session_state: st.session_state.authenticated = False
if "user"           not in st.session_state: st.session_state.user = None
if "lang"           not in st.session_state: st.session_state.lang = "fr"
if "dark_mode"      not in st.session_state: st.session_state.dark_mode = False
if "page"           not in st.session_state: st.session_state.page = "dashboard"
if "wa_sent"        not in st.session_state: st.session_state.wa_sent = False
if "mass_phones"    not in st.session_state: st.session_state.mass_phones = []

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)


def show_auth():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    paper = "#2C2C2E" if dark else "#FFFFFF"
    text  = "#F2F2F7" if dark else "#2C2C2E"
    sub   = "#AEAEB2" if dark else "#636366"

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown(f"""
        <div style='text-align:center; padding:32px 0 16px;'>
            <div style='font-size:52px; margin-bottom:4px;'>🌿</div>
            <div style='font-size:28px; font-weight:900; color:{"#A3B08A" if dark else "#4A5240"};
                        letter-spacing:-1px; font-family:Inter,sans-serif;'>
                AirSentinel CM
            </div>
            <div style='height:3px; background:linear-gradient(to right,#4A5240,#B8860B,#9A4A1A);
                        border-radius:2px; margin:10px auto; width:180px;'></div>
            <div style='color:{sub}; font-size:13px; font-style:italic; margin-top:4px;'>
                Surveiller l'air. Protéger les populations.<br>
                Monitor the air. Protect the people.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Langue
        lc, rc = st.columns(2)
        with lc:
            if st.button("🇫🇷 Français", use_container_width=True,
                         type="primary" if lang=="fr" else "secondary"):
                st.session_state.lang = "fr"; st.rerun()
        with rc:
            if st.button("🇬🇧 English", use_container_width=True,
                         type="primary" if lang=="en" else "secondary"):
                st.session_state.lang = "en"; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs([
            "🔑 Connexion" if lang=="fr" else "🔑 Login",
            "✏️ Créer un compte" if lang=="fr" else "✏️ Register"
        ])

        with tab_login:
            with st.form("lf"):
                email = st.text_input("E-mail", placeholder="email@exemple.cm")
                pwd   = st.text_input("Mot de passe" if lang=="fr" else "Password", type="password")
                sub_btn = st.form_submit_button("Se connecter" if lang=="fr" else "Sign in",
                                                 use_container_width=True)
                if sub_btn:
                    if not email or not pwd:
                        st.error("Veuillez remplir tous les champs." if lang=="fr" else "Please fill all fields.")
                    else:
                        user = authenticate_user(email, pwd)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error("Email ou mot de passe incorrect." if lang=="fr" else "Incorrect email or password.")

            st.markdown(f"""
            <div style='text-align:center; color:{sub}; font-size:11px; margin-top:10px;'>
                Compte démo : <b>admin@airsentinel.cm</b> / <b>admin123</b>
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            with st.form("rf"):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Nom complet" if lang=="fr" else "Full name")
                    org  = st.text_input("Organisation")
                with c2:
                    reg_email = st.text_input("E-mail", key="re")
                    phone     = st.text_input("Téléphone" if lang=="fr" else "Phone", placeholder="+237 6XX XXX XXX")
                p1 = st.text_input("Mot de passe" if lang=="fr" else "Password", type="password", key="rp1")
                p2 = st.text_input("Confirmer" if lang=="fr" else "Confirm", type="password", key="rp2")
                reg_btn = st.form_submit_button("Créer mon compte" if lang=="fr" else "Create account",
                                                 use_container_width=True)
                if reg_btn:
                    errs = []
                    if not all([name, reg_email, p1, p2]):
                        errs.append("Champs obligatoires manquants." if lang=="fr" else "Required fields missing.")
                    if p1 != p2: errs.append("Mots de passe différents." if lang=="fr" else "Passwords don't match.")
                    if len(p1) < 6: errs.append("Min. 6 caractères." if lang=="fr" else "Min. 6 characters.")
                    for e in errs:
                        st.error(e)
                    if not errs:
                        ok, msg = create_user(name, reg_email, p1, org, phone)
                        (st.success if ok else st.error)(f"{'✅' if ok else '❌'} {msg}")


def show_sidebar():
    lang = st.session_state.lang
    user = st.session_state.user
    dark = st.session_state.dark_mode
    sub  = "#AEAEB2" if dark else "#636366"
    kaki = "#A3B08A" if dark else "#4A5240"

    with st.sidebar:
        st.markdown(f"""
        <div style='padding:12px 0 8px;'>
            <div class='logo-text'>🌿 AirSentinel CM</div>
            <div class='logo-tagline'>InsightX D_Vas • IndabaX 2026</div>
        </div>
        <div style='height:2px; background:linear-gradient(to right,#4A5240,#B8860B,#9A4A1A);
                    border-radius:2px; margin-bottom:12px;'></div>
        """, unsafe_allow_html=True)

        role_icon = "👑" if user["role"] == "admin" else "🔬"
        st.markdown(f"""
        <div style='font-size:13px; font-weight:700; color:{kaki};'>{role_icon} {user['username']}</div>
        <div style='font-size:11px; color:{sub}; margin-bottom:10px;'>
            {user['role'].upper()} • {user.get('organisation','') or '—'}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        pages = [
            ("📊", "dashboard", "Tableau de bord" if lang=="fr" else "Dashboard"),
            ("🌫️", "aqi", "Proxy PM2.5" if lang=="fr" else "Proxy PM2.5"),
            ("🌡️", "heatwave", "Vague de chaleur" if lang=="fr" else "Heatwave"),
            ("🗺️", "map", "Carte interactive" if lang=="fr" else "Interactive map"),
            ("🔔", "alerts", "Alertes" if lang=="fr" else "Alerts"),
            ("ℹ️", "about", "À propos" if lang=="fr" else "About"),
            ("👤", "profile", "Mon profil" if lang=="fr" else "My profile"),
        ]
        if user["role"] == "admin":
            pages.append(("⚙️", "admin", "Administration"))

        for icon, pk, label in pages:
            is_active = st.session_state.page == pk
            if st.button(f"{icon} {label}", key=f"nav_{pk}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = pk; st.rerun()

        st.markdown("---")

        # Thème
        theme_lbl = "☀️ Mode clair" if dark else "🌙 Mode sombre"
        if st.button(theme_lbl, use_container_width=True):
            st.session_state.dark_mode = not dark; st.rerun()

        # Langue
        lc, rc = st.columns(2)
        with lc:
            if st.button("🇫🇷 FR", use_container_width=True,
                         type="primary" if lang=="fr" else "secondary"):
                st.session_state.lang = "fr"; st.rerun()
        with rc:
            if st.button("🇬🇧 EN", use_container_width=True,
                         type="primary" if lang=="en" else "secondary"):
                st.session_state.lang = "en"; st.rerun()

        st.markdown("---")
        if st.button(f"🚪 {'Déconnexion' if lang=='fr' else 'Logout'}", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()

        st.markdown(f"""
        <div style='text-align:center; font-size:10px; color:{sub}; margin-top:8px;'>
            {datetime.now().strftime('%d %b %Y · %H:%M')}
        </div>
        """, unsafe_allow_html=True)


def main():
    if not st.session_state.authenticated:
        show_auth(); return

    show_sidebar()
    page = st.session_state.page

    if   page == "dashboard": from pages.dashboard import show_dashboard; show_dashboard()
    elif page == "aqi":       from pages.aqi_prediction import show_aqi_prediction; show_aqi_prediction()
    elif page == "heatwave":  from pages.heatwave_prediction import show_heatwave_prediction; show_heatwave_prediction()
    elif page == "map":       from pages.interactive_map import show_map; show_map()
    elif page == "alerts":    from pages.alerts import show_alerts; show_alerts()
    elif page == "about":     from pages.about import show_about; show_about()
    elif page == "profile":   from pages.profile import show_profile; show_profile()
    elif page == "admin" and st.session_state.user["role"] == "admin":
        from pages.admin import show_admin; show_admin()
    else:
        from pages.dashboard import show_dashboard; show_dashboard()


if __name__ == "__main__":
    main()
