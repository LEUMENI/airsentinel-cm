"""
AirSentinel CM - Admin Page
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

from utils.translations import t
from utils.database import (get_all_users, toggle_user_status, promote_user_to_admin,
                              get_all_predictions_aqi, get_all_predictions_heatwave,
                              get_all_alerts, validate_alert, get_activity_logs,
                              get_dashboard_stats)
from utils.models import get_risk_color


def show_admin():
    lang = st.session_state.lang
    dark = st.session_state.dark_mode
    user = st.session_state.user
    paper_color = "#252836" if dark else "#FFFFFF"
    text_color = "#E8EAF6" if dark else "#1A1A2E"
    card_bg = "#2D3147" if dark else "#FFFFFF"
    border = "#3D4154" if dark else "#E0E0E0"

    st.markdown("""
    <div class='tricolor-bar'></div>
    <h2 style='margin:0; font-weight:900;'>⚙️ Administration -AirSentinel CM</h2>
    <p style='color:#CE1126; font-weight:700; margin-top:4px;'>
        👑 Accès réservé aux administrateurs / Admin access only
    </p>
    """, unsafe_allow_html=True)

    # ── Global KPIs ───────────────────────────────────────────────────
    stats = get_dashboard_stats()
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "👥", stats["total_users"], "Utilisateurs", "#1A4D8F"),
        (k2, "🔬", stats["total_predictions"], "Prédictions totales", "#007A5E"),
        (k3, "🌫️", stats["total_aqi"], "Prédictions AQI", "#007A5E"),
        (k4, "🌡️", stats["total_hw"], "Prédictions vague", "#CE1126"),
        (k5, "🔔", stats["active_alerts"], "Alertes actives", "#FCD116"),
    ]
    for col, icon, val, label, color in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card' style='border-top-color:{color};'>
                <div style='font-size:18px;'>{icon}</div>
                <div class='kpi-value' style='color:{color}; font-size:1.8rem;'>{val}</div>
                <div class='kpi-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"👥 {t('admin_users', lang)}",
        f"📊 {t('admin_stats', lang)}",
        f"🔬 {t('admin_predictions', lang)}",
        f"✅ {t('admin_alerts_validation', lang)}",
        f"📋 {t('admin_logs', lang)}",
    ])

    # ── TAB 1: Users ──────────────────────────────────────────────────
    with tab1:
        _show_users_tab(lang, user, card_bg, border, text_color, paper_color, dark)

    # ── TAB 2: Stats ──────────────────────────────────────────────────
    with tab2:
        _show_stats_tab(lang, paper_color, text_color, dark)

    # ── TAB 3: Predictions ────────────────────────────────────────────
    with tab3:
        _show_predictions_tab(lang, paper_color, text_color)

    # ── TAB 4: Alert validation ───────────────────────────────────────
    with tab4:
        _show_alerts_validation_tab(lang, user, card_bg, border)

    # ── TAB 5: Logs ───────────────────────────────────────────────────
    with tab5:
        _show_logs_tab(lang, paper_color, text_color)


def _show_users_tab(lang, current_user, card_bg, border, text_color, paper_color, dark):
    st.markdown("### 👥 Gestion des utilisateurs / User management")

    users = get_all_users()
    if not users:
        st.info(t("no_data", lang))
        return

    # Filters
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        role_f = st.selectbox("Rôle / Role", ["Tous / All", "admin", "user"])
    with f2:
        status_f = st.selectbox("Statut / Status", ["Tous / All", "Actif / Active", "Inactif / Inactive"])
    with f3:
        search_f = st.text_input("🔍 Rechercher / Search (nom ou email)", placeholder="...")

    filtered_users = users
    if role_f != "Tous / All":
        filtered_users = [u for u in filtered_users if u["role"] == role_f]
    if status_f == "Actif / Active":
        filtered_users = [u for u in filtered_users if u.get("is_active", 1) == 1]
    elif status_f == "Inactif / Inactive":
        filtered_users = [u for u in filtered_users if u.get("is_active", 1) == 0]
    if search_f:
        search_lower = search_f.lower()
        filtered_users = [u for u in filtered_users
                          if search_lower in u.get("username", "").lower()
                          or search_lower in u.get("email", "").lower()]

    st.markdown(f"**{len(filtered_users)} utilisateur(s) trouvé(s)**")
    st.markdown("---")

    for u in filtered_users:
        is_active = u.get("is_active", 1)
        is_admin = u["role"] == "admin"
        role_icon = "👑" if is_admin else "🔬"
        status_badge = (f"<span style='background:#007A5E;color:white;padding:2px 8px;border-radius:10px;font-size:11px;'>✅ Actif</span>"
                        if is_active else
                        f"<span style='background:#CE1126;color:white;padding:2px 8px;border-radius:10px;font-size:11px;'>❌ Inactif</span>")

        col_info, col_actions = st.columns([5, 2])
        with col_info:
            st.markdown(f"""
            <div style='background:{card_bg}; border:1px solid {border}; border-radius:10px;
                        padding:12px 16px; margin-bottom:6px;'>
                <div style='display:flex; align-items:center; gap:10px;'>
                    <span style='font-size:24px;'>{role_icon}</span>
                    <div>
                        <b style='font-size:14px;'>{u['username']}</b>
                        <span style='margin-left:8px;'>{status_badge}</span>
                        <span style='margin-left:8px; font-size:11px; color:#888;'>{u['role'].upper()}</span><br>
                        <small style='color:#888;'>{u['email']} | {u.get('organisation', '—')} | {u.get('phone', '—')}</small><br>
                        <small style='color:#666;'>Inscrit le: {u.get('created_at', '')[:10]}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_actions:
            # Don't allow actions on self
            if u["id"] != current_user["id"]:
                a1, a2 = st.columns(2)
                with a1:
                    toggle_label = "🚫 Désact." if is_active else "✅ Activer"
                    if st.button(toggle_label, key=f"toggle_{u['id']}", use_container_width=True):
                        toggle_user_status(u["id"])
                        st.rerun()
                with a2:
                    if not is_admin:
                        if st.button("👑 Admin", key=f"promote_{u['id']}", use_container_width=True):
                            promote_user_to_admin(u["id"])
                            st.rerun()
                    else:
                        st.markdown("<small style='color:#888;'>Admin</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small style='color:#888;'>Vous-même / Yourself</small>",
                            unsafe_allow_html=True)


def _show_stats_tab(lang, paper_color, text_color, dark):
    st.markdown("### 📊 Statistiques d'utilisation / Usage statistics")

    aqi_preds = get_all_predictions_aqi(limit=1000)
    hw_preds = get_all_predictions_heatwave(limit=1000)
    all_preds = aqi_preds + hw_preds

    if not all_preds:
        # Generate mock stats for demo
        st.info("📊 Données démo / Demo data (aucune prédiction réelle)")
        all_preds = _generate_mock_predictions()

    # Predictions per day (last 30 days)
    from datetime import date
    today = date.today()
    days_30 = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]

    pred_per_day = {d: 0 for d in days_30}
    for p in all_preds:
        created = (p.get("created_at") or "")[:10]
        if created in pred_per_day:
            pred_per_day[created] += 1

    col1, col2 = st.columns([3, 2])

    with col1:
        fig1 = go.Figure(go.Bar(
            x=list(pred_per_day.keys()),
            y=list(pred_per_day.values()),
            marker=dict(color="#007A5E", opacity=0.8),
        ))
        fig1.update_layout(
            title=dict(text="📈 Prédictions par jour -30 derniers jours", font=dict(color=text_color)),
            paper_bgcolor=paper_color, plot_bgcolor=paper_color,
            font=dict(color=text_color), height=280,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(showgrid=False, tickangle=45),
            yaxis=dict(showgrid=True, gridcolor="#3D4154" if dark else "#EEEEEE"),
        )
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # Risk distribution
        counts = {"SAFE": 0, "VIGILANCE": 0, "DANGER": 0}
        for p in all_preds:
            lvl = p.get("risk_level", "SAFE")
            counts[lvl] = counts.get(lvl, 0) + 1

        fig2 = go.Figure(go.Pie(
            labels=list(counts.keys()),
            values=list(counts.values()),
            marker=dict(colors=["#007A5E", "#FCD116", "#CE1126"]),
            hole=0.45, textinfo="label+percent",
            textfont=dict(color=text_color, size=11),
        ))
        fig2.update_layout(
            title=dict(text="🎯 Distribution des niveaux", font=dict(color=text_color)),
            paper_bgcolor=paper_color, font=dict(color=text_color),
            margin=dict(l=10, r=10, t=40, b=10), height=280, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Predictions by city
    city_counts = {}
    for p in aqi_preds:
        city = p.get("city", "")
        city_counts[city] = city_counts.get(city, 0) + 1

    if city_counts:
        sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        cities, counts_val = zip(*sorted_cities)

        fig3 = go.Figure(go.Bar(
            x=list(counts_val), y=list(cities), orientation="h",
            marker=dict(color="#1A4D8F", opacity=0.8),
            text=list(counts_val), textposition="outside",
            textfont=dict(color=text_color),
        ))
        fig3.update_layout(
            title=dict(text="🏙️ Prédictions AQI par ville (Top 15)", font=dict(color=text_color)),
            paper_bgcolor=paper_color, plot_bgcolor=paper_color,
            font=dict(color=text_color), height=400,
            margin=dict(l=10, r=60, t=40, b=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


def _show_predictions_tab(lang, paper_color, text_color):
    st.markdown("### 🔬 Historique global des prédictions / Global prediction history")

    sub1, sub2 = st.tabs(["🌫️ AQI", "🌡️ Vague de chaleur"])

    with sub1:
        preds = get_all_predictions_aqi(limit=500)
        if not preds:
            st.info(t("no_data", lang))
        else:
            df = pd.DataFrame(preds)
            disp_cols = ["username", "city", "region", "date_pred", "score", "risk_level", "created_at"]
            available = [c for c in disp_cols if c in df.columns]
            df = df[available]
            col_labels = {"username": "Utilisateur", "city": "Ville", "region": "Région",
                          "date_pred": "Date prédiction", "score": "Score AQI",
                          "risk_level": "Niveau de risque", "created_at": "Créé le"}
            df = df.rename(columns={k: v for k, v in col_labels.items() if k in df.columns})

            def style_risk(val):
                c = {"SAFE": "background-color:#007A5E;color:white",
                     "VIGILANCE": "background-color:#FCD116;color:#333",
                     "DANGER": "background-color:#CE1126;color:white"}
                return c.get(val, "")

            styled = df.style.map(style_risk, subset=["Niveau de risque"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False)
            st.download_button(
                f"📥 {t('admin_export_csv', lang)}",
                data=csv,
                file_name=f"airsentinel_aqi_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    with sub2:
        preds_hw = get_all_predictions_heatwave(limit=500)
        if not preds_hw:
            st.info(t("no_data", lang))
        else:
            df_hw = pd.DataFrame(preds_hw)
            disp_cols = ["username", "city", "region", "date_pred",
                         "probability", "prediction", "risk_level", "created_at"]
            available = [c for c in disp_cols if c in df_hw.columns]
            df_hw = df_hw[available]
            if "probability" in df_hw.columns:
                df_hw["probability"] = df_hw["probability"].apply(lambda x: f"{float(x)*100:.1f}%")

            def style_risk2(val):
                c = {"SAFE": "background-color:#007A5E;color:white",
                     "VIGILANCE": "background-color:#FCD116;color:#333",
                     "DANGER": "background-color:#CE1126;color:white"}
                return c.get(val, "")

            if "risk_level" in df_hw.columns:
                styled_hw = df_hw.style.map(style_risk2, subset=["risk_level"])
                st.dataframe(styled_hw, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_hw, use_container_width=True, hide_index=True)

            csv_hw = df_hw.to_csv(index=False)
            st.download_button(
                f"📥 {t('admin_export_csv', lang)}",
                data=csv_hw,
                file_name=f"airsentinel_heatwave_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )


def _show_alerts_validation_tab(lang, current_user, card_bg, border):
    st.markdown("### ✅ Validation des alertes / Alert validation")
    st.markdown("""
    <div style='background:rgba(206,17,38,0.1); border:1px solid #CE1126; border-radius:8px;
                padding:10px 14px; margin-bottom:16px; font-size:13px;'>
        <b>⚠️ Responsabilité / Responsibility:</b>
        En validant une alerte, vous autorisez sa diffusion auprès des citoyens de la ville concernée.<br>
        By validating an alert, you authorize its broadcast to the citizens of the concerned city.
    </div>
    """, unsafe_allow_html=True)

    alerts = get_all_alerts()
    pending = [a for a in alerts if a.get("validated", 0) == 0 and a.get("active", 1) == 1]
    confirmed = [a for a in alerts if a.get("validated", 0) == 1]
    rejected = [a for a in alerts if a.get("validated", 0) == -1]

    st.markdown(f"**⏳ En attente: {len(pending)} | ✅ Validées: {len(confirmed)} | ❌ Rejetées: {len(rejected)}**")

    if not pending and not confirmed and not rejected:
        st.info("📭 Aucune alerte pour le moment / No alerts yet.")
        return

    if pending:
        st.markdown("#### ⏳ Alertes en attente de validation")
        for alert in pending:
            type_icon = "🌫️" if alert["alert_type"] == "aqi" else "🌡️"
            type_label = "AQI" if alert["alert_type"] == "aqi" else "Vague de chaleur"

            col_info, col_v, col_r = st.columns([4, 1, 1])
            with col_info:
                st.markdown(f"""
                <div style='background:{card_bg}; border:1px solid {border}; border-radius:8px; padding:10px 14px;'>
                    {type_icon} <b>{alert.get('city', '—')}</b> -{type_label}<br>
                    <small>Seuil: {alert['threshold']} | Par: {alert.get('username', '—')} | 
                    Créée: {alert.get('created_at', '')[:10]}</small>
                </div>
                """, unsafe_allow_html=True)
            with col_v:
                if st.button("✅", key=f"val_{alert['id']}", use_container_width=True,
                             help="Valider / Confirm"):
                    validate_alert(alert["id"], current_user["id"], 1)
                    st.success("✅ Alerte validée!")
                    st.rerun()
            with col_r:
                if st.button("❌", key=f"rej_{alert['id']}", use_container_width=True,
                             help="Rejeter / Reject"):
                    validate_alert(alert["id"], current_user["id"], -1)
                    st.warning("❌ Alerte rejetée.")
                    st.rerun()

    if confirmed:
        with st.expander(f"✅ Alertes validées ({len(confirmed)})"):
            for alert in confirmed[:10]:
                st.markdown(f"✅ **{alert.get('city', '—')}** -{alert['alert_type']} | "
                            f"Seuil: {alert['threshold']} | "
                            f"Validée le: {alert.get('validated_at', '')[:10] if alert.get('validated_at') else 'N/A'}")

    if rejected:
        with st.expander(f"❌ Alertes rejetées ({len(rejected)})"):
            for alert in rejected[:10]:
                st.markdown(f"❌ **{alert.get('city', '—')}** -{alert['alert_type']} | "
                            f"Seuil: {alert['threshold']}")


def _show_logs_tab(lang, paper_color, text_color):
    st.markdown("### 📋 Journaux d'activité / Activity logs")

    logs = get_activity_logs(limit=200)
    if not logs:
        st.info(t("no_data", lang))
        return

    # Filters
    f1, f2 = st.columns([2, 3])
    with f1:
        action_types = list(set([l.get("action", "") for l in logs]))
        action_filter = st.selectbox("Type d'action / Action type",
                                     ["Toutes / All"] + sorted(action_types))
    with f2:
        user_search = st.text_input("🔍 Filtrer par utilisateur / Filter by user", "")

    filtered_logs = logs
    if action_filter != "Toutes / All":
        filtered_logs = [l for l in filtered_logs if l.get("action") == action_filter]
    if user_search:
        filtered_logs = [l for l in filtered_logs
                         if user_search.lower() in l.get("username", "").lower()]

    df_logs = pd.DataFrame(filtered_logs)
    if not df_logs.empty:
        disp_cols = ["created_at", "username", "action", "details"]
        available = [c for c in disp_cols if c in df_logs.columns]
        df_logs = df_logs[available]
        col_labels = {"created_at": "Date/Heure", "username": "Utilisateur",
                      "action": "Action", "details": "Détails"}
        df_logs = df_logs.rename(columns={k: v for k, v in col_labels.items() if k in df_logs.columns})
        st.dataframe(df_logs, use_container_width=True, hide_index=True, height=400)

        csv_logs = df_logs.to_csv(index=False)
        st.download_button(
            f"📥 {t('admin_export_csv', lang)}",
            data=csv_logs,
            file_name=f"airsentinel_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info(t("no_data", lang))


def _generate_mock_predictions():
    """Generate mock prediction data for demo purposes."""
    from utils.translations import CAMEROON_CITIES
    random.seed(42)
    preds = []
    cities = list(CAMEROON_CITIES.keys())
    levels = ["SAFE", "VIGILANCE", "DANGER"]
    weights = [0.45, 0.35, 0.20]

    today = datetime.now()
    for i in range(50):
        d = today - timedelta(days=random.randint(0, 29))
        city = random.choice(cities)
        score = random.uniform(5, 90)
        level = "DANGER" if score > 66 else ("VIGILANCE" if score > 33 else "SAFE")
        preds.append({
            "city": city, "region": CAMEROON_CITIES[city]["region"],
            "score": round(score, 1), "risk_level": level,
            "created_at": d.strftime("%Y-%m-%d %H:%M:%S"),
            "date_pred": d.strftime("%Y-%m-%d"),
            "username": "demo_user",
        })
    return preds
