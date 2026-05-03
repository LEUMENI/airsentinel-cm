# 🌿 AirSentinel CM

> **Surveiller l'air. Protéger les populations.**
> *Monitor the air. Protect the people.*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://airsentinel-cm.streamlit.app)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![IndabaX Cameroon 2026](https://img.shields.io/badge/IndabaX-Cameroon%202026-orange.svg)]()

---

## 📌 Présentation

**AirSentinel CM** est une application web d'intelligence artificielle de surveillance de la qualité de l'air au Cameroun, développée par l'équipe **InsightX D_Vas** dans le cadre du **Hackathon IndabaX Cameroon 2026** sous le thème *"L'IA au service de la résilience climatique et sanitaire"*.

L'application prédit en temps réel :
- Le **Proxy PM2.5** (particules fines estimées) via un modèle **XGBoost** (R² = 0.861)
- Le **risque de vague de chaleur** à J+3 via une **Régression Logistique** (ROC-AUC = 0.963)

pour **30 villes du Cameroun** couvrant les **10 régions administratives**.

---

## 🖼️ Aperçu

| Tableau de bord | Carte interactive | Prédiction PM2.5 |
|---|---|---|
| KPIs + carte + graphes | 4 couches : PM2.5, temp, précip, vagues | Formulaire + jauge + rapport PDF |

---

## 🏗️ Architecture

```
airsentinel_cm/
├── app.py                        # Point d'entrée — Auth + Router + Sidebar
├── requirements.txt              # Dépendances Python
├── .python-version               # Python 3.11
├── .streamlit/
│   ├── config.toml               # Configuration Streamlit
│   └── secrets.toml              # Variables sensibles (non versionné)
├── pages/
│   ├── dashboard.py              # Tableau de bord — KPIs + cartes
│   ├── aqi_prediction.py         # Prédiction Proxy PM2.5
│   ├── interactive_map.py        # Carte Folium interactive (4 couches)
│   ├── alerts.py                 # Système d'alertes + WhatsApp simulation
│   ├── admin.py                  # Administration (rôle admin)
│   ├── profile.py                # Profil utilisateur
│   └── about.py                  # À propos — équipe + modèles
├── utils/
│   ├── database.py               # Couche SQLite — CRUD
│   ├── models.py                 # Chargement + prédiction ML
│   ├── thresholds.py             # Seuils officiels (Seuils.docx)
│   ├── translations.py           # Bilingue FR/EN + 30 villes
│   ├── weather_api.py            # Client Open-Meteo (temps réel)
│   ├── email_service.py          # SMTP — alertes + rappels admin
│   └── styles.py                 # CSS global (thèmes clair/sombre)
├── models/
│   ├── modele_pm25_insightx_final.pkl   # XGBoost Proxy PM2.5
│   └── heatwave_model.pkl               # LogReg vagues de chaleur
├── assets/                       # Photos équipe
└── tests/
    ├── test_models.py            # Tests modèles ML
    ├── test_thresholds.py        # Tests seuils officiels
    └── test_database.py          # Tests base de données
```

---

## 🚀 Installation et lancement

### Prérequis
- Python 3.11
- Git

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/LEUMENI/airsentinel-cm.git
cd airsentinel-cm

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
streamlit run app.py
```

L'application s'ouvre sur **http://localhost:8501**

**Compte démo admin :**
```
Email    : admin@airsentinel.cm
Password : admin123
```

---

## ⚙️ Configuration email (optionnel)

Créez `.streamlit/secrets.toml` :

```toml
SMTP_HOST  = "smtp.gmail.com"
SMTP_PORT  = "587"
SMTP_USER  = "votre.email@gmail.com"
SMTP_PASS  = "votre_app_password"
FROM_EMAIL = "votre.email@gmail.com"
FROM_NAME  = "AirSentinel CM"
```

---

## 🤖 Modèles ML

### Proxy PM2.5 — XGBoost

| Métrique | Valeur |
|---|---|
| R² (validation) | 0.8511 |
| R² (holdout) | 0.8535 |
| MAE | 1.89 µg/m³ |
| RMSE | 2.44 µg/m³ |
| Dataset | 87 240 observations (2020–2025) |
| Features | 18 variables météorologiques |

**Seuils officiels PM2.5 :**
| Niveau | PM2.5 | Score |
|---|---|---|
| 🟢 Safe | ≤ 12.7 µg/m³ | ≤ 36.3 |
| 🟡 Vigilance | ≤ 22.2 µg/m³ | ≤ 63.4 |
| 🔴 Urgent | > 22.2 µg/m³ | > 63.4 |

### Vagues de chaleur — Régression Logistique

| Métrique | Valeur |
|---|---|
| ROC-AUC | 0.963 |
| Recall (classe 1) | 0.82 |
| Seuil décision | 0.20 |
| Définition | ETCCDI — 3 jours consécutifs > P90 local |

---

## 🗺️ Couverture géographique

30 villes — 10 régions administratives du Cameroun :

| Région | Villes couvertes |
|---|---|
| Adamaoua | Ngaoundéré, Meiganga, Tibati, Tignere |
| Centre | Yaoundé, Mbalmayo, Akonolinga |
| Est | Bertoua, Batouri, Yokadouma |
| Extrême-Nord | Maroua, Kousseri, Yagoua, Mokolo |
| Littoral | Douala, Nkongsamba |
| Nord | Garoua, Guider, Poli, Touboro |
| Nord-Ouest | Bamenda, Wum, Mbengwi |
| Ouest | Bafoussam, Dschang, Foumban, Mbouda |
| Sud | Ebolowa, Sangmelima |
| Sud-Ouest | Dschang |

---

## 📊 Données

- **Source météo temps réel :** [Open-Meteo API](https://open-meteo.com/) (gratuit, sans clé API)
- **Historique :** 2020–2025 — données quotidiennes
- **Variables :** Température, précipitations, rayonnement, évapotranspiration, vent

---

## 🛡️ Sécurité

- Mots de passe hachés (SHA-256)
- Variables sensibles dans `secrets.toml` (hors Git)
- Validation des entrées utilisateur
- Rôles : `user` / `admin`
- Journaux d'activité complets

---

## 👥 Équipe InsightX D_Vas

## 👥 Équipe InsightX D_Vas

| Membre | Rôle |
|--------|------|
| **Lionel Leumeni** | Software Engineer -Architecture & Développement |
| **Danielle FOTSI** | Data scientist - Modèle Qualité de l'air |
| **Christy Alotse** | Responsable de l’orchestration du projet, de la supervision des équipes |
| **Belgrade YONYA** | Data Scientist - modèle de vague de chaleur |

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE).

---

## 🏆 Hackathon IndabaX Cameroon 2026

Thème : *"L'IA au service de la résilience climatique et sanitaire"*

**AirSentinel CM** - Finaliste - Mai 2026
