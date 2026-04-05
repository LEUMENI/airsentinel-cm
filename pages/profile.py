"""
AirSentinel CM - Profile Page
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.translations import t
from utils.database import (get_user_predictions_aqi, get_user_predictions_heatwave,
                              update_user_profile, change_user_password, get_dashboard_stats)
from utils.models import get_risk_color


def show_profile():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user = st.session_state.user
    paper_color = "#252836" if dark else "#FFFFFF"
    text_color = "#E8EAF6" if dark else "#1A1A2E"
    card_bg = "#2D3147" if dark else "#FFFFFF"
    border = "#3D4154" if dark else "#E0E0E0"

    st.markdown("""
    <div class='tricolor-bar'></div>
    <h2 style='margin:0; font-weight:900;'>👤 Mon Profil -My Profile</h2>
    """, unsafe_allow_html=True)

    # ── Header card ───────────────────────────────────────────────────
    role_icon = "👑" if user["role"] == "admin" else "🔬"
    role_label = "Administrateur / Administrator" if user["role"] == "admin" else "Chercheur / Researcher"
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#007A5E,#1A4D8F); border-radius:14px;
                padding:24px 28px; color:white; margin-bottom:20px; display:flex; align-items:center;'>
        <div style='font-size:60px; margin-right:20px;'>{role_icon}</div>
        <div>
            <div style='font-size:24px; font-weight:900;'>{user['username']}</div>
            <div style='font-size:14px; opacity:0.85;'>{user.get('email', '')}</div>
            <div style='font-size:13px; opacity:0.8; margin-top:4px;'>
                {role_label} • {user.get('organisation', 'IndabaX Cameroon')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        f"📋 {t('profile_info', lang) if 'profile_info' in dir() else 'Informations'}",
        f"📊 {t('profile_stats', lang)}",
        f"🔐 {t('profile_security', lang)}",
    ])

    # ── Tab 1: Info ───────────────────────────────────────────────────
    with tab1:
        st.markdown("### ✏️ Modifier mes informations / Edit my information")

        with st.form("profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Nom complet / Full name",
                                         value=user.get("username", ""))
                new_org = st.text_input(t("auth_organisation", lang),
                                        value=user.get("organisation", ""))
            with c2:
                new_phone = st.text_input(t("auth_phone", lang),
                                          value=user.get("phone", ""),
                                          placeholder="+237 6XX XXX XXX")
                st.text_input(t("auth_email", lang),
                              value=user.get("email", ""),
                              disabled=True,
                              help="L'email ne peut pas être modifié / Email cannot be changed")

            save_btn = st.form_submit_button(f"💾 {t('profile_save', lang)}", use_container_width=True)

            if save_btn:
                ok, msg = update_user_profile(user["id"], new_name, new_org, new_phone)
                if ok:
                    st.session_state.user["username"] = new_name
                    st.session_state.user["organisation"] = new_org
                    st.session_state.user["phone"] = new_phone
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        # Account info
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:{card_bg}; border:1px solid {border}; border-radius:10px; padding:16px;'>
            <b>📅 Informations du compte / Account information</b><br><br>
            <table style='font-size:13px; width:100%; border-collapse:collapse;'>
                <tr>
                    <td style='padding:5px 12px; color:#888;'>Membre depuis / Member since</td>
                    <td style='padding:5px 12px;'><b>{user.get('created_at', 'N/A')[:10]}</b></td>
                    <td style='padding:5px 12px; color:#888;'>Dernière connexion / Last login</td>
                    <td style='padding:5px 12px;'><b>{user.get('last_login', 'N/A')[:10] if user.get('last_login') else 'N/A'}</b></td>
                </tr>
                <tr>
                    <td style='padding:5px 12px; color:#888;'>Rôle / Role</td>
                    <td style='padding:5px 12px;'><b>{role_label}</b></td>
                    <td style='padding:5px 12px; color:#888;'>Téléphone / Phone</td>
                    <td style='padding:5px 12px;'><b>{user.get('phone', 'Non renseigné')}</b></td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 2: Stats ──────────────────────────────────────────────────
    with tab2:
        aqi_preds = get_user_predictions_aqi(user["id"])
        hw_preds = get_user_predictions_heatwave(user["id"])

        total = len(aqi_preds) + len(hw_preds)
        cities_analyzed = len(set([p.get("city", "") for p in aqi_preds + hw_preds]))

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        kpis = [
            (k1, "🔬", total, "Total prédictions", "#007A5E"),
            (k2, "🌫️", len(aqi_preds), "Prédictions AQI", "#1A4D8F"),
            (k3, "🌡️", len(hw_preds), "Prédictions vague", "#CE1126"),
            (k4, "🗺️", cities_analyzed, "Villes analysées", "#FCD116"),
        ]
        for col, icon, val, label, color in kpis:
            with col:
                st.markdown(f"""
                <div class='kpi-card' style='border-top-color:{color};'>
                    <div style='font-size:22px;'>{icon}</div>
                    <div class='kpi-value' style='color:{color};'>{val}</div>
                    <div class='kpi-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if aqi_preds:
            col_chart, col_table = st.columns([1, 2])

            with col_chart:
                # Risk distribution pie
                counts = {"SAFE": 0, "VIGILANCE": 0, "DANGER": 0}
                for p in aqi_preds:
                    counts[p.get("risk_level", "SAFE")] = counts.get(p.get("risk_level", "SAFE"), 0) + 1

                fig = go.Figure(go.Pie(
                    labels=list(counts.keys()),
                    values=list(counts.values()),
                    marker=dict(colors=["#007A5E", "#FCD116", "#CE1126"]),
                    hole=0.45,
                    textinfo="label+percent",
                    textfont=dict(color=text_color, size=11),
                ))
                fig.update_layout(
                    title=dict(text="Répartition AQI", font=dict(color=text_color, size=13)),
                    paper_bgcolor=paper_color, font=dict(color=text_color),
                    margin=dict(l=10, r=10, t=40, b=10), height=240, showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with col_table:
                # Recent predictions table
                st.markdown("**🕒 Mes 10 dernières prédictions AQI**")
                if aqi_preds:
                    df = pd.DataFrame(aqi_preds[:10])[
                        ["city", "region", "date_pred", "score", "risk_level"]
                    ]
                    df.columns = ["Ville", "Région", "Date", "Score", "Niveau"]

                    def style_risk(val):
                        c = {"SAFE": "background-color:#007A5E;color:white",
                             "VIGILANCE": "background-color:#FCD116;color:#333",
                             "DANGER": "background-color:#CE1126;color:white"}
                        return c.get(val, "")

                    styled = df.style.map(style_risk, subset=["Niveau"])
                    st.dataframe(styled, use_container_width=True, hide_index=True, height=220)

            # Cities bar chart
            if cities_analyzed > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**📊 Score moyen par ville analysée**")
                city_scores = {}
                for p in aqi_preds:
                    city = p.get("city", "")
                    if city:
                        if city not in city_scores:
                            city_scores[city] = []
                        city_scores[city].append(p.get("score", 0))

                cities = list(city_scores.keys())
                avg_scores = [sum(v)/len(v) for v in city_scores.values()]
                colors = [get_risk_color("DANGER" if s > 66 else ("VIGILANCE" if s > 33 else "SAFE"))
                          for s in avg_scores]

                fig2 = go.Figure(go.Bar(
                    x=cities, y=avg_scores,
                    marker=dict(color=colors, opacity=0.85),
                    text=[f"{s:.1f}" for s in avg_scores], textposition="outside",
                    textfont=dict(color=text_color),
                ))
                fig2.add_hline(y=33, line_dash="dot", line_color="#007A5E", opacity=0.5)
                fig2.add_hline(y=66, line_dash="dot", line_color="#CE1126", opacity=0.5)
                fig2.update_layout(
                    paper_bgcolor=paper_color, plot_bgcolor=paper_color,
                    font=dict(color=text_color), height=250,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(range=[0, 115], showgrid=True,
                               gridcolor="#3D4154" if dark else "#EEEEEE"),
                    xaxis=dict(showgrid=False),
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Aucune prédiction effectuée pour le moment. / No predictions yet.")
            st.markdown("""
            <div style='text-align:center; padding:30px; color:#888;'>
                <div style='font-size:48px;'>🔬</div>
                <div>Commencez par faire une prédiction AQI ou vague de chaleur !</div>
                <div>Start by making an AQI or heatwave prediction!</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 3: Security ───────────────────────────────────────────────
    with tab3:
        st.markdown("### 🔐 Changer le mot de passe / Change password")

        col_form, col_tips = st.columns([1.5, 2])

        with col_form:
            with st.form("pwd_form"):
                old_pwd = st.text_input("Ancien mot de passe / Old password", type="password")
                new_pwd1 = st.text_input("Nouveau mot de passe / New password", type="password")
                new_pwd2 = st.text_input("Confirmer / Confirm new password", type="password")

                change_btn = st.form_submit_button("🔑 Changer le mot de passe", use_container_width=True)

                if change_btn:
                    if not all([old_pwd, new_pwd1, new_pwd2]):
                        st.error("⚠️ Remplissez tous les champs.")
                    elif new_pwd1 != new_pwd2:
                        st.error(t("auth_pwd_mismatch", lang))
                    elif len(new_pwd1) < 6:
                        st.error(t("auth_pwd_short", lang))
                    else:
                        ok, msg = change_user_password(user["id"], old_pwd, new_pwd1)
                        if ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")

        with col_tips:
            st.markdown(f"""
            <div style='background:{card_bg}; border:1px solid {border}; border-radius:10px; padding:16px;'>
                <b>🛡️ Conseils de sécurité / Security tips</b><br><br>
                <div style='font-size:13px; line-height:1.6;'>
                    ✅ Utilisez au moins 8 caractères / Use at least 8 characters<br>
                    ✅ Mélangez majuscules et minuscules / Mix uppercase and lowercase<br>
                    ✅ Incluez des chiffres et symboles / Include numbers and symbols<br>
                    ✅ N'utilisez pas votre nom ou email / Avoid using your name or email<br>
                    ✅ Ne partagez pas votre mot de passe / Never share your password<br><br>
                    <b>Exemples de mots de passe forts / Strong password examples:</b><br>
                    <code>Cam3roun#2026!</code> &nbsp; <code>Air$ent1nel@CM</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Sessions / Activity
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:{card_bg}; border:1px solid {border}; border-radius:10px; padding:16px;'>
            <b>📅 Activité du compte / Account activity</b><br><br>
            <table style='font-size:13px; width:100%;'>
                <tr>
                    <td style='color:#888; padding:4px 8px;'>Compte créé le</td>
                    <td style='padding:4px 8px;'><b>{user.get('created_at', 'N/A')[:16]}</b></td>
                </tr>
                <tr>
                    <td style='color:#888; padding:4px 8px;'>Dernière connexion</td>
                    <td style='padding:4px 8px;'><b>{user.get('last_login', 'N/A')[:16] if user.get('last_login') else 'N/A'}</b></td>
                </tr>
                <tr>
                    <td style='color:#888; padding:4px 8px;'>Statut du compte</td>
                    <td style='padding:4px 8px;'>
                        <span style='background:#007A5E; color:white; padding:2px 10px; border-radius:10px;'>
                            ✅ Actif / Active
                        </span>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
