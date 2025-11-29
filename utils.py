import json
import os
import re

# --- RUTAS DE ARCHIVOS CONFIGURABLES (Centralizadas aquí) ---
PRICES_FILE = 'prices.json'
EXPIRATION_SCRIPTS_FILE = 'expiration_scripts.json'
APP_DATA_FOLDER = 'app_data' 
VOUCHER_TEMPLATE_FILE = os.path.join(APP_DATA_FOLDER, 'voucher_template.html') 
LOGO_FILE = os.path.join(APP_DATA_FOLDER, 'logo.png') 

# --- "LIBRERÍA" DE SCRIPTS DE EXPIRACIÓN PREDEFINIDOS (Constante global) ---
SCRIPTS_DE_EXPIRACION = {
    "none": {
        "nombre_visible": "No Expira (Estándar)",
        "script_on_login": ""
    }
}

# --- EXTENSIONES DE ARCHIVO PERMITIDAS PARA SUBIDAS (Constante global) ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def load_prices():
    if not os.path.exists(PRICES_FILE) or os.path.getsize(PRICES_FILE) == 0:
        return {}
    try:
        with open(PRICES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_prices(prices_data):
    with open(PRICES_FILE, 'w') as f:
        json.dump(prices_data, f, indent=4)

# --- FUNCIONES PARA MANEJAR expiration_scripts.json ---
def load_custom_expiration_scripts():
    if not os.path.exists(EXPIRATION_SCRIPTS_FILE) or os.path.getsize(EXPIRATION_SCRIPTS_FILE) == 0:
        return {}
    try:
        with open(EXPIRATION_SCRIPTS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_custom_expiration_scripts(scripts_data):
    with open(EXPIRATION_SCRIPTS_FILE, 'w') as f:
        json.dump(scripts_data, f, indent=4)

def get_all_expiration_scripts():
    custom_scripts = load_custom_expiration_scripts()
    all_scripts = {**SCRIPTS_DE_EXPIRACION, **custom_scripts}
    return all_scripts

# --- FUNCIONES DE UTILIDAD PARA FORMATO ---
def format_uptime_display(uptime_str):
    if uptime_str == '0s' or not uptime_str:
        return "Ilimitado"
    
    match = re.match(r'(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', uptime_str)
    
    if not match:
        return uptime_str 
    
    weeks, days, hours, minutes, seconds = match.groups()
    parts = []
    
    if weeks and int(weeks) > 0:
        parts.append(f"{weeks} {'semanas' if int(weeks) > 1 else 'semana'}")
    if days and int(days) > 0:
        parts.append(f"{days} {'días' if int(days) > 1 else 'día'}")
    if hours and int(hours) > 0:
        parts.append(f"{hours} {'horas' if int(hours) > 1 else 'hora'}")
    if minutes and int(minutes) > 0:
        parts.append(f"{minutes} {'minutos' if int(minutes) > 1 else 'minuto'}")
    if seconds and int(seconds) > 0:
        if not parts or int(seconds) < 60: 
            parts.append(f"{seconds} {'segundos' if int(seconds) > 1 else 'segundo'}")

    if not parts:
        return "0 segundos" 
        
    return " ".join(parts[:2]) 

# --- FUNCIONES PARA MANEJAR ARCHIVOS SUBIDOS ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS