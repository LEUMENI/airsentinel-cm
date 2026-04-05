"""
AirSentinel CM - Global CSS Styles (OLED Dark & High Contrast)
FIX FINAL : Visibilité des listes de sélection (Selectbox) et Calendriers
"""

def get_css(dark_mode=False):
    if dark_mode:
        bg          = "#000000"   # Noir Absolu
        sidebar_bg  = "#050505"
        card_bg     = "#0A0A0A"
        text        = "#FFFFFF"   # Blanc Pur
        subtext     = "#BBBBBB"
        border      = "#262626"   # Bordures un peu plus visibles
        input_bg    = "#111111"
        accent      = "#7C3AED"   # Violet
        accent_glow = "rgba(124, 58, 237, 0.4)"
        # Spécifique pour les listes déroulantes et calendriers
        popover_bg  = "#0A0A0A"
    else:
        bg          = "#FFFFFF"
        sidebar_bg  = "#F8FAFC"
        card_bg     = "#FFFFFF"
        text        = "#0F172A"
        subtext     = "#64748B"
        border      = "#E2E8F0"
        input_bg    = "#F1F5F9"
        accent      = "#4F46E5"
        accent_glow = "rgba(79, 70, 229, 0.1)"
        popover_bg  = "#FFFFFF"

    SAFE, VIGILANCE, DANGER = "#007A5E", "#FCD116", "#CE1126"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

/* ── 1. FOND ET TEXTE GLOBAL ── */
[data-testid="stAppViewContainer"], .main, .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
}}

/* Force la couleur sur TOUS les textes */
h1, h2, h3, h4, h5, h6, p, span, div, label, li {{
    color: {text} !important;
}}

/* ── 2. FIX CRITIQUE : SELECTBOX & CALENDRIERS (POPOVERS) ── */

/* Le fond du menu déroulant (quand il est ouvert) */
div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"] {{
    background-color: {popover_bg} !important;
    border: 1px solid {border} !important;
}}

/* Les options à l'intérieur de la liste (ex: Yaoundé, Douala) */
li[role="option"] {{
    background-color: {popover_bg} !important;
    color: {text} !important;
    transition: background 0.2s;
}}

/* L'option sur laquelle on passe la souris */
li[role="option"]:hover, li[aria-selected="true"] {{
    background-color: {accent} !important;
    color: #FFFFFF !important;
}}

/* FIX CALENDRIER (Date Input) */
div[data-baseweb="calendar"] {{
    background-color: {popover_bg} !important;
    color: {text} !important;
}}

/* Boutons des jours dans le calendrier */
div[data-baseweb="calendar"] button {{
    color: {text} !important;
    background-color: transparent !important;
}}

/* Jour sélectionné ou survolé dans le calendrier */
div[data-baseweb="calendar"] button[aria-selected="true"], 
div[data-baseweb="calendar"] button:hover {{
    background-color: {accent} !important;
    color: #FFFFFF !important;
}}

/* ── 3. CHAMPS DE SAISIE (INPUTS) ── */
input, textarea, [data-baseweb="select"] > div {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}

/* ── 4. BOUTONS (FIX SURVOL ET VISIBILITÉ) ── */
.stButton > button {{
    background-color: {accent} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: auto;
    transition: all 0.3s ease;
}}

.stButton > button:hover {{
    box-shadow: 0 0 15px {accent_glow} !important;
    transform: translateY(-1px);
    color: #FFFFFF !important; /* Maintient le texte blanc au survol */
}}

/* ── 5. SIDEBAR ── */
[data-testid="stSidebarNav"] {{ display: none !important; }}

section[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {border} !important;
}}

section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: {subtext} !important;
    justify-content: flex-start !important;
    border-radius: 12px !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {accent_glow} !important;
    color: {accent} !important;
}}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: {accent} !important;
    color: white !important;
}}

/* ── 6. CARTES & KPIs ── */
.as-card, [data-testid="metric-container"] {{
    background-color: {card_bg} !important;
    border: 1px solid {border} !important;
    border-radius: 20px !important;
}}

[data-testid="stMetricValue"] {{
    color: {accent} !important;
    font-weight: 800 !important;
}}

/* ── 7. SIGNATURE CAMEROUN ── */
.tricolor-bar {{
    height: 6px;
    background: linear-gradient(to right, {SAFE} 33%, {VIGILANCE} 33% 66%, {DANGER} 66%);
    border-radius: 100px;
    margin: 20px 0;
}}
</style>
"""