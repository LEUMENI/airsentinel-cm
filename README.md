# 🌿 AirSentinel CM

**Surveiller l'air. Protéger les populations.**  
*Monitor the air. Protect the people.*

> IndabaX Cameroon 2026 -Hackathon "L'IA au service de la résilience climatique et sanitaire"  
> Équipe **InsightX D_Vas**

---

## 📋 Description

AirSentinel CM est une application web d'intelligence artificielle qui prédit :
- **L'Indice de Qualité de l'Air (AQI/PM2.5)** via Gradient boosting (R²=0.85)
- **Les vagues de chaleur** via Régression Logistique (ROC-AUC=0.96)

pour **30 villes du Cameroun**, avec données météo en temps réel (Open-Meteo).

---

## 🚀 Installation et lancement local

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/airsentinel-cm.git
cd airsentinel-cm

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py
```

L'app s'ouvre sur http://localhost:8501

**Compte admin par défaut :**  
Email: `admin@airsentinel.cm` | Mot de passe: `admin123`

---

## 📁 Structure du projet

```
airsentinel_cm/
├── app.py                          # Point d'entrée principal
├── requirements.txt
├── models/
│   ├── modele_pm25_insightx_final.pkl   # Gradient boosting AQI (R²=0.85)
│   └── heatwave_model.pkl               # LogReg Heatwave (AUC=0.96)
├── assets/
│   └── profile_*.jpg/png           # Photos équipe
├── utils/
│   ├── database.py                 # SQLite (users, prédictions, alertes)
│   ├── models.py                   # Prédiction ML
│   ├── weather_api.py              # Open-Meteo API
│   ├── pdf_report.py               # Génération rapports PDF
│   ├── styles.py                   # CSS Dark/Light
│   └── translations.py             # FR/EN + données villes
└── pages/
    ├── dashboard.py                # KPIs + cartes + graphes
    ├── aqi_prediction.py           # Formulaire + prédiction AQI
    ├── heatwave_prediction.py      # Formulaire + prédiction vague
    ├── interactive_map.py          # Carte Folium interactive
    ├── alerts.py                   # Gestion alertes + SMS sim.
    ├── about.py                    # À propos + équipe
    ├── profile.py                  # Profil utilisateur
    └── admin.py                    # Administration (admin only)
```

---

## 🤖 Modèles ML

### Modèle AQI -Gradient boosting
- **Target** : PM2.5 proxy (µg/m³)
- **R² validation** : 0.861 | **R² holdout** : 0.857
- **MAE** : 1.62 µg/m³ | **RMSE** : 2.04 µg/m³
- **Top features** : rain_sum, precipitation_sum, precipitation_hours, time_month, time_cos, et0_fao_evapotranspiration, temperature_2m_max, temperature_2m_mean
- **Scaling** : score = min(100, PM2.5/35 × 100)

### Modèle Vague de chaleur -Régression Logistique
- **Target** : vague de chaleur dans J+3 (fenêtre 3 jours consécutifs > 90e percentile local)
- **ROC-AUC** : 0.9632 | **Recall classe 1** : 0.82
- **Seuil décision** : 0.20 (optimisé pour maximiser le rappel -sécurité sanitaire)
- **Définition** : ETCCDI -3 jours consécutifs avec Tmax > 90e percentile local

---

## 🎨 Code couleur

| Score | Niveau | Couleur |
|-------|--------|---------|
| 0 -33 | ✅ SAFE | #007A5E (vert) |
| 34 -66 | ⚠️ VIGILANCE | #FCD116 (jaune) |
| 67 -100 | 🚨 DANGER | #CE1126 (rouge) |

---

## 🌐 Déploiement Streamlit Cloud

1. Pusher le code sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le dépôt GitHub
4. Fichier principal : `app.py`
5. Cliquer **Deploy**

---

## 👥 Équipe InsightX D_Vas

| Membre | Rôle |
|--------|------|
| **Lionel Leumeni** | Software Engineer -Architecture & Développement |
| **Danielle** | Data Scientist -Modèle AQI (Gradient boosting) |
| **Christy** | Data Scientist -Modèle Vague de chaleur |
| **Belgrade** | Data Scientist -Analyse & Validation |

---

## 📄 Données

- **Dataset** : 87 240 observations • 30 villes • 10 régions • 2020–2025
- **Source** : Open-Meteo Historical Archive
- **Variables** : 22 variables météorologiques quotidiennes

---

*AirSentinel CM © 2026 -InsightX D_Vas -IndabaX Cameroon*
