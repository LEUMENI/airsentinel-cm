"""
AirSentinel CM - Authentication Page (Login / Register)
"""
import streamlit as st
from utils.database import authenticate_user, create_user
from utils.translations import t


def show_auth_page():
    lang = st.session_state.get("lang", "fr")
    dark = st.session_state.get("dark_mode", False)

    # Centered layout
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        # Logo & branding
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem 0;">
            <div style="font-size: 3rem;">🛡️</div>
            <h1 style="font-family:'Sora',sans-serif; font-size:2rem; font-weight:700;
                       color:#007A5E; margin:0.3rem 0 0 0;">AirSentinel CM</h1>
            <p style="color:#888; font-size:0.9rem; font-style:italic; margin:0.2rem 0 0 0;">
                Surveiller l'air. Protéger les populations.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Cameroon stripe
        st.markdown("""
        <div style="height:5px; background:linear-gradient(to right,
            #007A5E 33.33%, #FCD116 33.33% 66.66%, #CE1126 66.66%);
            border-radius:3px; margin:0.5rem 0 1.5rem 0;"></div>
        """, unsafe_allow_html=True)

        # IndabaX badge
        st.markdown("""
        <div style="text-align:center; margin-bottom:1.5rem;">
            <span style="background:rgba(0,122,94,0.12); border:1px solid #007A5E;
                         color:#007A5E; padding:0.3rem 1rem; border-radius:20px;
                         font-size:0.8rem; font-weight:600;">
                🏆 IndabaX Cameroon 2026 -InsightX D_Vas
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Login / Register tabs
        tab_login, tab_register = st.tabs([
            f"🔐 {t('login', lang)}",
            f"✨ {t('register', lang)}"
        ])

        with tab_login:
            _show_login_form(lang)

        with tab_register:
            _show_register_form(lang)


def _show_login_form(lang):
    st.markdown(f"<p style='color:#888; font-size:0.9rem; margin-bottom:1rem;'>{t('welcome_back', lang)}</p>",
                unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input(t("email", lang), placeholder="votre@email.com")
        password = st.text_input(t("password", lang), type="password", placeholder="••••••••")
        submitted = st.form_submit_button(
            f"🔐 {t('login_btn', lang)}",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if not email or not password:
            st.error(t("email_required", lang))
        else:
            user = authenticate_user(email.strip(), password)
            if user:
                st.session_state["user"] = user
                st.session_state["authenticated"] = True
                st.session_state["page"] = "dashboard"
                st.success(f"✅ {t('welcome_back', lang)}, **{user['username']}** !")
                st.rerun()
            else:
                st.error(f"❌ {t('login_error', lang)}")

    # Demo credentials hint
    st.markdown("""
    <div style="margin-top:1rem; padding:0.8rem; background:rgba(0,122,94,0.08);
                border-radius:8px; font-size:0.8rem; color:#555;">
        <b>🔑 Démo Admin :</b> admin@airsentinel.cm / admin123
    </div>
    """, unsafe_allow_html=True)


def _show_register_form(lang):
    st.markdown(f"<p style='color:#888; font-size:0.9rem; margin-bottom:1rem;'>{t('no_account', lang)}</p>",
                unsafe_allow_html=True)

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input(t("full_name", lang), placeholder="Jean Dupont")
        with col2:
            organisation = st.text_input(t("organisation", lang), placeholder="MINSANTE, ONG...")

        email = st.text_input(t("email", lang), placeholder="votre@email.com")
        phone = st.text_input(t("phone", lang), placeholder="+237 6XX XXX XXX")

        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input(t("password", lang), type="password", placeholder="Min. 6 caractères")
        with col4:
            confirm = st.text_input(t("confirm_password", lang), type="password", placeholder="Répétez")

        submitted = st.form_submit_button(
            f"✨ {t('register_btn', lang)}",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        errors = []
        if not username:
            errors.append(t("name_required", lang))
        if not email:
            errors.append(t("email_required", lang))
        if len(password) < 6:
            errors.append(t("password_too_short", lang))
        if password != confirm:
            errors.append(t("password_mismatch", lang))

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            success, msg = create_user(username, email, password, organisation, phone, role="user")
            if success:
                st.success(f"✅ {t('register_success', lang)}")
            else:
                st.error(f"❌ {msg}")

    st.markdown("""
    <div style="margin-top:0.8rem; padding:0.7rem; background:rgba(26,77,143,0.08);
                border-radius:8px; font-size:0.78rem; color:#555;">
        <b>ℹ️ Note :</b> Les comptes administrateurs sont créés manuellement par un super-administrateur.
    </div>
    """, unsafe_allow_html=True)
