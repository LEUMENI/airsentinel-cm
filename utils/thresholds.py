# Seuils officiels PM2.5 (µg/m³)
AQI_SAFE_MAX      = 12.7
AQI_VIGILANCE_MAX = 22.2
AQI_SCORE_SAFE_MAX      = 36.3
AQI_SCORE_VIGILANCE_MAX = 63.4

def get_aqi_level_from_score(score):
    if score <= AQI_SCORE_SAFE_MAX:        return "SAFE"
    elif score <= AQI_SCORE_VIGILANCE_MAX: return "VIGILANCE"
    return "DANGER"

def get_aqi_color(level):
    return {"SAFE":"#007A5E","VIGILANCE":"#FCD116","DANGER":"#CE1126"}.get(level,"#007A5E")

def get_aqi_label(level, lang="fr"):
    return {"SAFE":"Safe","VIGILANCE":"Vigilance","DANGER":"Urgent"}.get(level, level)

def is_danger_level(score):
    return score > AQI_SCORE_VIGILANCE_MAX

# Température
TEMP_FRAIS_MAX, TEMP_TEMPERE_MAX, TEMP_CHAUD_MAX = 22.0, 24.0, 26.0

def get_temp_class(temp):
    if temp < 22:   return "Frais"
    elif temp <= 24: return "Tempéré"
    elif temp <= 26: return "Chaud"
    return "Très chaud"

def get_temp_color(temp):
    return {"Frais":"#1A6FA6","Tempéré":"#007A5E","Chaud":"#FCD116","Très chaud":"#CE1126"}[get_temp_class(temp)]

def get_temp_label(temp, lang="fr"):
    return get_temp_class(temp)

# Précipitations
PRECIP_TRES_SEC_MAX, PRECIP_SEC_MAX = 2.5, 4.5
PRECIP_MODERE_MAX,   PRECIP_HUMIDE_MAX = 6.5, 8.0

def get_precip_class(precip):
    if precip < 2.5:   return "Très sec"
    elif precip <= 4.5: return "Sec"
    elif precip <= 6.5: return "Modéré"
    elif precip <= 8.0: return "Humide"
    return "Risque inondation"

def get_precip_color(precip):
    return {"Très sec":"#CE1126","Sec":"#FCD116","Modéré":"#E07800",
            "Humide":"#007A5E","Risque inondation":"#1A4D8F"}[get_precip_class(precip)]

# Vague de chaleur
HW_COLORS = {"Vague de chaleur":"#CE1126","Absence de vague de chaleur":"#007A5E"}