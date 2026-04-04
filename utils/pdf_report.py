"""
AirSentinel CM - PDF Report Generation
"""
from fpdf import FPDF
from datetime import datetime
import io


class AirSentinelPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 122, 94)
        self.rect(0, 0, 70, 4, 'F')
        self.set_fill_color(252, 209, 22)
        self.rect(70, 0, 70, 4, 'F')
        self.set_fill_color(206, 17, 38)
        self.rect(140, 0, 70, 4, 'F')
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 122, 94)
        self.ln(8)
        self.cell(0, 10, "AirSentinel CM", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Surveiller l'air. Proteger les populations. | Monitor the air. Protect the people.",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"AirSentinel CM - InsightX D_Vas - IndabaX Cameroon 2026 | Page {self.page_no()}", align="C")


def generate_aqi_report(city, region, date_str, score, risk_level, pm25_raw, input_data, username):
    pdf = AirSentinelPDF()
    pdf.add_page()
    risk_colors = {"SAFE": (0, 122, 94), "VIGILANCE": (200, 160, 0), "DANGER": (206, 17, 38)}
    rc = risk_colors.get(risk_level, (0, 122, 94))

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(26, 77, 143)
    pdf.cell(0, 10, "RAPPORT DE PREDICTION AQI / AIR QUALITY PREDICTION REPORT",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  User: {username}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, f"  Ville: {city}   |   Region: {region}   |   Date analyse: {date_str}",
             border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_fill_color(*rc)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(95, 22, f"Score AQI: {score:.1f}/100", border=0, fill=True, align="C")
    pdf.cell(95, 22, f"Niveau: {risk_level}", border=0, fill=True, align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, f"PM2.5 estime: {pm25_raw:.2f} microg/m3", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    interpretations = {
        "SAFE": "Qualite de l'air acceptable. Aucune restriction recommandee. / Air quality acceptable.",
        "VIGILANCE": "Qualite moderement degradee. Personnes sensibles: limiter les activites. / Moderately degraded.",
        "DANGER": "Qualite dangereuse. Eviter les activites exterieures. Alertes sanitaires. / Dangerous air quality."
    }
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, "Interpretation:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, interpretations.get(risk_level, ""))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 77, 143)
    pdf.cell(0, 8, "Donnees meteorologiques:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    labels = {
        "temperature_2m_max": "Temp max (C)",
        "temperature_2m_min": "Temp min (C)",
        "temperature_2m_mean": "Temp moyenne (C)",
        "precipitation_sum": "Precipitations (mm)",
        "rain_sum": "Pluie (mm)",
        "wind_speed_10m_max": "Vent max (km/h)",
        "shortwave_radiation_sum": "Rayonnement (MJ/m2)",
        "et0_fao_evapotranspiration": "ET0 (mm)",
    }
    for key, label in labels.items():
        val = input_data.get(key, "N/A")
        if isinstance(val, float):
            val = f"{val:.2f}"
        pdf.cell(95, 6, f"  {label}:", border="LTB", fill=False)
        pdf.cell(95, 6, f"  {val}", border="RTB", new_x="LMARGIN", new_y="NEXT")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()


def generate_heatwave_report(city, region, date_str, probability, prediction, risk_level, input_data, username):
    pdf = AirSentinelPDF()
    pdf.add_page()
    risk_colors = {"SAFE": (0, 122, 94), "VIGILANCE": (200, 160, 0), "DANGER": (206, 17, 38)}
    rc = risk_colors.get(risk_level, (0, 122, 94))

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(206, 17, 38)
    pdf.cell(0, 10, "RAPPORT VAGUE DE CHALEUR / HEATWAVE PREDICTION REPORT",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  User: {username}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, f"  Ville: {city}   |   Region: {region}   |   Date: {date_str}",
             border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_fill_color(*rc)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    txt = "VAGUE DE CHALEUR PROBABLE" if prediction == 1 else "AUCUNE VAGUE DETECTEE"
    pdf.cell(0, 18, txt, border=0, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, f"Probabilite: {probability*100:.1f}%  |  Niveau: {risk_level}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 77, 143)
    pdf.cell(0, 8, "Donnees d'entree:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    for key in ["temperature_2m_max", "temperature_2m_min", "temp_threshold", "temp_lag1", "temp_lag2", "temp_lag3"]:
        val = input_data.get(key, "N/A")
        if isinstance(val, float):
            val = f"{val:.1f}"
        pdf.cell(95, 6, f"  {key}:", border="LTB")
        pdf.cell(95, 6, f"  {val}", border="RTB", new_x="LMARGIN", new_y="NEXT")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()
