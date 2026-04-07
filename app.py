"""
AirSentinel CM -Main Streamlit Application
IndabaX Cameroon 2026 | InsightX D_Vas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from datetime import datetime

from utils.database import init_db, authenticate_user, create_user
from utils.styles import get_css
from utils.translations import t

# Page config -MUST be first Streamlit call
st.set_page_config(
    page_title="AirSentinel CM",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ─── MASQUER LA NAVIGATION NATIVE ─────────────────────────────────────────────
st.markdown("""
    <style>
        /* Cache la liste des fichiers .py du dossier pages/ */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Optionnel : remonte un peu ton logo si l'espace vide est trop grand */
        [data-testid="stSidebarNav"] + div {
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# ─── Init DB ─────────────────────────────────────────────────────────────────
init_db()

# ─── Session state defaults ──────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "lang" not in st.session_state:
    st.session_state.lang = "fr"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)


# ─── AUTH PAGE ───────────────────────────────────────────────────────────────
def show_auth_page():
    lang = st.session_state.lang

    col_l, col_m, col_r = st.columns([1, 1.6, 1])
    with col_m:
        st.markdown("""
        <div style='text-align:center; padding: 30px 0 10px 0;'>
            <div style='font-size:48px;'>🌿</div>
            <div style='font-size:30px; font-weight:900; color:#007A5E; letter-spacing:-1px;'>
                AirSentinel CM
            </div>
            <div class='tricolor-bar' style='margin:10px auto; width:200px;'></div>
            <div style='color:#666; font-size:14px; font-style:italic;'>
                Surveiller l'air. Protéger les populations.<br>
                Monitor the air. Protect the people.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Language selector
        l_col, r_col = st.columns(2)
        with l_col:
            if st.button("🇫🇷 Français", use_container_width=True,
                         type="primary" if lang == "fr" else "secondary"):
                st.session_state.lang = "fr"
                st.rerun()
        with r_col:
            if st.button("🇬🇧 English", use_container_width=True,
                         type="primary" if lang == "en" else "secondary"):
                st.session_state.lang = "en"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs([t("auth_login", lang), t("auth_register", lang)])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(t("auth_email", lang), placeholder="email@example.com")
                password = st.text_input(t("auth_password", lang), type="password")
                submitted = st.form_submit_button(t("auth_login_btn", lang), use_container_width=True)
                if submitted:
                    if not email or not password:
                        st.error("⚠️ Veuillez remplir tous les champs. / Please fill all fields.")
                    else:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error(t("auth_invalid", lang))

            st.markdown("""
            <div style='text-align:center; color:#888; font-size:12px; margin-top:12px;'>
                🔑 Compte démo admin / Demo admin account:<br>
                <b>admin@airsentinel.cm</b> / <b>admin123</b>
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    fullname = st.text_input(t("auth_fullname", lang))
                    organisation = st.text_input(t("auth_organisation", lang))
                with col2:
                    reg_email = st.text_input(t("auth_email", lang), key="reg_email")
                    phone = st.text_input(t("auth_phone", lang), placeholder="+237 6XX XXX XXX")
                pwd1 = st.text_input(t("auth_password", lang), type="password", key="p1")
                pwd2 = st.text_input(t("auth_confirm_pwd", lang), type="password", key="p2")
                reg_submitted = st.form_submit_button(t("auth_register_btn", lang), use_container_width=True)
                if reg_submitted:
                    errors = []
                    if not all([fullname, reg_email, pwd1, pwd2]):
                        errors.append("⚠️ Remplissez tous les champs obligatoires.")
                    if pwd1 != pwd2:
                        errors.append(t("auth_pwd_mismatch", lang))
                    if len(pwd1) < 6:
                        errors.append(t("auth_pwd_short", lang))
                    if errors:
                        for e in errors:
                            st.error(e)
                    else:
                        from utils.database import create_user
                        ok, msg = create_user(fullname, reg_email, pwd1, organisation, phone)
                        if ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def show_sidebar():
    lang = st.session_state.lang
    user = st.session_state.user
    dark = st.session_state.dark_mode

    with st.sidebar:
        # Logo + tricolor
        st.markdown("""
        <div class='tricolor-bar'></div>
        <div class='logo-text'>🌿 AirSentinel CM</div>
        <div class='logo-sub'>InsightX D_Vas • IndabaX 2026</div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # User info
        role_icon = "👑" if user["role"] == "admin" else "🔬"
        st.markdown(f"""
        <div style='font-size:13px; color:#007A5E; font-weight:700;'>
            {role_icon} {user['username']}
        </div>
        <div style='font-size:11px; color:#888; margin-bottom:8px;'>
            {user['role'].upper()} • {user.get('organisation', '')}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # Navigation
        pages = [
            ("📊", "dashboard", t("nav_dashboard", lang)),
            ("🌫️", "aqi", t("nav_aqi", lang)),
            ("🗺️", "map", t("nav_map", lang)),
            ("🔔", "alerts", t("nav_alerts", lang)),
            ("ℹ️", "about", t("nav_about", lang)),
            ("👤", "profile", t("nav_profile", lang)),
        ]
        if user["role"] == "admin":
            pages.append(("⚙️", "admin", t("nav_admin", lang)))

        for icon, page_key, label in pages:
            is_active = st.session_state.page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon} {label}", key=f"nav_{page_key}",
                         use_container_width=True, type=btn_type):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("---")

        # Theme toggle
        theme_label = "🌙 Thème sombre" if not dark else "☀️ Thème clair"
        if st.button(theme_label, use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()

        # Language
        l1, l2 = st.columns(2)
        with l1:
            if st.button("🇫🇷 FR", use_container_width=True,
                         type="primary" if lang == "fr" else "secondary"):
                st.session_state.lang = "fr"
                st.rerun()
        with l2:
            if st.button("🇬🇧 EN", use_container_width=True,
                         type="primary" if lang == "en" else "secondary"):
                st.session_state.lang = "en"
                st.rerun()

        st.markdown("---")
        # Logout
        if st.button(f"🚪 {t('nav_logout', lang)}", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()

        # Date
        st.markdown(f"""
        <div style='text-align:center; font-size:11px; color:#888; margin-top:8px;'>
            {datetime.now().strftime('%d %b %Y • %H:%M')}
        </div>
        """, unsafe_allow_html=True)


# ─── MAIN ROUTER ─────────────────────────────────────────────────────────────
def main():
    if not st.session_state.authenticated:
        show_auth_page()
        return

    # --- ÉTAPE 1 : Récupérer les variables nécessaires ---
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    
    # Définit les couleurs en fonction du mode (doit matcher tes fonctions de dashboard)
    if dark:
        paper, text, sub, brd = "#000000", "#FFFFFF", "#BBBBBB", "#262626"
    else:
        paper, text, sub, brd = "#FFFFFF", "#1A1D27", "#64748B", "#E2E8F0"

    # --- ÉTAPE 2 : Afficher la sidebar ---
    show_sidebar()

    page = st.session_state.page

    # --- ÉTAPE 3 : Router vers les pages ---
    if page == "dashboard":
        from pages.dashboard import show_dashboard
        # Maintenant dark, paper, etc. existent bien !
        show_dashboard()
        
    elif page == "aqi":
        from pages.aqi_prediction import show_aqi_prediction
        show_aqi_prediction()
        
    elif page == "map":
        from pages.interactive_map import show_map
        # Si ta page map a aussi besoin de styles, passe-les ici
        show_map()
        
    elif page == "alerts":
        from pages.alerts import show_alerts
        show_alerts()
        
    elif page == "about":
        from pages.about import show_about
        show_about()
        
    elif page == "profile":
        from pages.profile import show_profile
        show_profile()
        
    elif page == "admin" and st.session_state.user["role"] == "admin":
        from pages.admin import show_admin
        show_admin()
        
    else:
        from pages.dashboard import show_dashboard
        show_dashboard()

if __name__ == "__main__":
    main()
