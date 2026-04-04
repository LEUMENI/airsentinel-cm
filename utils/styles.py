"""
AirSentinel CM - Global CSS Styles
Couleurs sobres (kaki/beige/blanc) + vert/rouge/jaune uniquement pour alertes
Bootstrap 5 + Google Fonts
"""

def get_css(dark_mode=False):
    # ── Palette sobre ──────────────────────────────────────────────
    if dark_mode:
        bg        = "#1C1C1E"
        bg2       = "#2C2C2E"
        card_bg   = "#2C2C2E"
        sidebar_bg= "#1C1C1E"
        text      = "#F2F2F7"
        subtext   = "#AEAEB2"
        border    = "#3A3A3C"
        input_bg  = "#3A3A3C"
        nav_active= "#4A5240"   # kaki sombre
        nav_hover = "#3D4435"
        kaki      = "#8A9471"
        beige     = "#5C5640"
        btn_bg    = "#4A5240"
        btn_hover = "#5A6350"
        heading   = "#D4C9A8"   # beige clair
        link      = "#A3B08A"
    else:
        bg        = "#F7F5F0"   # beige très clair
        bg2       = "#FFFFFF"
        card_bg   = "#FFFFFF"
        sidebar_bg= "#EEEAE2"   # beige sidebar
        text      = "#2C2C2E"
        subtext   = "#636366"
        border    = "#D4CDB8"   # beige border
        input_bg  = "#FFFFFF"
        nav_active= "#4A5240"   # kaki
        nav_hover = "#5A6350"
        kaki      = "#6B7355"
        beige     = "#A09070"
        btn_bg    = "#4A5240"
        btn_hover = "#5A6350"
        heading   = "#3C3A30"
        link      = "#6B7355"

    # Alertes — couleurs fixes indépendantes du thème
    SAFE_BG     = "#007A5E"
    VIGILANCE_BG= "#B8860B"   # doré foncé (lisible sur fond clair ET sombre)
    DANGER_BG   = "#B91C1C"   # rouge sobre

    return f"""
<style>
/* ── Bootstrap 5 ── */
@import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css');
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Variables globales ── */
:root {{
  --bg:        {bg};
  --bg2:       {bg2};
  --card:      {card_bg};
  --sidebar:   {sidebar_bg};
  --text:      {text};
  --subtext:   {subtext};
  --border:    {border};
  --input-bg:  {input_bg};
  --kaki:      {kaki};
  --beige:     {beige};
  --btn:       {btn_bg};
  --btn-hover: {btn_hover};
  --heading:   {heading};
  --link:      {link};
  --nav-active:{nav_active};
  --safe:      {SAFE_BG};
  --vigilance: {VIGILANCE_BG};
  --danger:    {DANGER_BG};
}}

/* ── Reset global ── */
html, body, [class*="css"] {{
  font-family: 'Inter', system-ui, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}}

/* ── Main container ── */
.main .block-container {{
  background-color: var(--bg) !important;
  padding: 1.5rem 2rem !important;
  max-width: 1400px;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background-color: var(--sidebar) !important;
  border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] * {{
  color: var(--text) !important;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{
  font-family: 'Inter', sans-serif !important;
  font-weight: 700 !important;
  color: var(--heading) !important;
  letter-spacing: -0.3px;
}}

/* ── Buttons ── */
.stButton > button {{
  background-color: var(--btn) !important;
  color: #F7F5F0 !important;
  border: 1px solid var(--btn) !important;
  border-radius: 6px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 0.45rem 1.2rem !important;
  transition: background 0.18s, transform 0.12s !important;
  letter-spacing: 0.2px;
}}
.stButton > button:hover {{
  background-color: var(--btn-hover) !important;
  border-color: var(--btn-hover) !important;
  transform: translateY(-1px) !important;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stTextArea textarea {{
  background-color: var(--input-bg) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  font-family: 'Inter', sans-serif !important;
}}
.stSelectbox > div > div > div {{
  color: var(--text) !important;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 14px !important;
}}
[data-testid="metric-container"] > div {{
  color: var(--text) !important;
}}

/* ── Tabs ── */
button[data-baseweb="tab"] {{
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  color: var(--subtext) !important;
  font-size: 13px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
  border-bottom-color: var(--kaki) !important;
  color: var(--text) !important;
  font-weight: 700 !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}}

/* ── Alerts (Streamlit built-in) ── */
.stAlert {{ border-radius: 6px !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--kaki); }}

/* ── Custom components ── */

/* KPI Card sobre */
.kpi-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
  text-align: center;
  border-left: 4px solid var(--kaki);
  transition: box-shadow 0.2s;
}}
.kpi-card:hover {{ box-shadow: 0 3px 12px rgba(0,0,0,0.12); }}
.kpi-value {{
  font-size: 2rem;
  font-weight: 800;
  color: var(--kaki);
  line-height: 1.1;
  font-family: 'JetBrains Mono', monospace;
}}
.kpi-label {{
  font-size: 0.78rem;
  color: var(--subtext);
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

/* Risk badges */
.badge-safe {{
  display:inline-block;
  background:{SAFE_BG};
  color:white;
  padding:3px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:700;
  letter-spacing:0.5px;
}}
.badge-vigilance {{
  display:inline-block;
  background:{VIGILANCE_BG};
  color:white;
  padding:3px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:700;
  letter-spacing:0.5px;
}}
.badge-danger {{
  display:inline-block;
  background:{DANGER_BG};
  color:white;
  padding:3px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:700;
  letter-spacing:0.5px;
  animation: pulse-danger 1.8s infinite;
}}
@keyframes pulse-danger {{
  0%,100% {{ opacity:1; box-shadow:0 0 0 0 rgba(185,28,28,0.4); }}
  50%      {{ opacity:0.85; box-shadow:0 0 0 6px rgba(185,28,28,0); }}
}}

/* Section header bar */
.section-header {{
  border-left: 4px solid var(--kaki);
  padding-left: 12px;
  margin-bottom: 16px;
}}
.section-header h3 {{
  margin:0;
  font-size:1rem;
  font-weight:700;
  color: var(--heading) !important;
}}
.section-header p {{
  margin:2px 0 0 0;
  font-size:12px;
  color: var(--subtext);
}}

/* Card generic */
.as-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 14px;
}}

/* Logo */
.logo-text {{
  font-size: 20px;
  font-weight: 800;
  color: var(--heading);
  letter-spacing: -0.5px;
}}
.logo-tagline {{
  font-size: 10px;
  color: var(--subtext);
  text-transform: uppercase;
  letter-spacing: 1px;
}}

/* Info box (replaces tricolor bar) */
.info-strip {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 18px;
  font-size: 12px;
  color: var(--subtext);
}}

/* WhatsApp mock */
.whatsapp-bubble {{
  background: #25D366;
  color: white;
  border-radius: 12px 12px 3px 12px;
  padding: 10px 14px;
  font-size: 13px;
  max-width: 320px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  font-family: 'Inter', sans-serif;
  line-height: 1.5;
}}
.whatsapp-time {{
  font-size: 10px;
  opacity: 0.75;
  text-align: right;
  margin-top: 4px;
}}
.whatsapp-container {{
  background: {"#1A2A1A" if dark_mode else "#E5DDD5"};
  border-radius: 10px;
  padding: 20px;
}}

/* Form label emphasis */
.form-label-custom {{
  font-size:12px;
  font-weight:600;
  color: var(--subtext);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 4px;
}}

/* Responsive table */
.table-container {{
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--border);
}}
</style>

<!-- Bootstrap JS (for tooltips, etc.) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
"""
