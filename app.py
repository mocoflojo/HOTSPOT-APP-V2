from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, current_app
import sys
import os

# Importar desde módulos personalizados
from config import ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD, HOTSPOT_DNS, ConfigError 
from database import db, login_manager, User, init_db 
from auth import auth_bp 
from routes import main_bp 
from mikrotik_service import get_api_connection # Solo se importa get_api_connection si no se usa directamente en rutas
from utils import ( # Importar todas las funciones y constantes de utils.py
    load_prices, save_prices, load_custom_expiration_scripts, 
    save_custom_expiration_scripts, get_all_expiration_scripts, 
    format_uptime_display, allowed_file, SCRIPTS_DE_EXPIRACION,
    APP_DATA_FOLDER, PRICES_FILE, EXPIRATION_SCRIPTS_FILE, VOUCHER_TEMPLATE_FILE, LOGO_FILE
)

# Importaciones de Flask-Login
from flask_login import current_user


app = Flask(__name__)

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_larga_y_aleatoria_para_sesiones_flask' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos y Flask-Login con la aplicación
init_db(app) 

# REGISTRAR BLUEPRINTS
app.register_blueprint(auth_bp, url_prefix='/auth') 
app.register_blueprint(main_bp) 


# Asegurarse de que la carpeta app_data exista
if not os.path.exists(APP_DATA_FOLDER):
    os.makedirs(APP_DATA_FOLDER)

# Inicializar voucher_template.html si no existe
if not os.path.exists(VOUCHER_TEMPLATE_FILE):
    default_voucher_content = """
<div class="voucher-card p-1 border border-gray-300 rounded-lg text-center text-xs break-all leading-tight" style="width: 2in; height: 1in; display: flex; align-items: center; justify-content: space-between; margin: 0.05in; vertical-align: top; overflow: hidden; page-break-inside: avoid;">
    
    <div class="logo-area" style="flex-shrink: 0; width: 0.5in; height: 0.8in; display: flex; align-items: center; justify-content: center; overflow: hidden;">
        <img src="/app_data/logo.png" alt="Logo" style="max-width: 100%; max-height: 100%; object-fit: contain;">
    </div>

    <div class="content-area flex-grow pl-1 text-left" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
        <p class="font-bold text-lg text-blue-700 leading-none" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${{ voucher.price }}</p>
        
        {% if voucher.mode == 'pin' %}
            <p class="text-gray-800 leading-none mt-1">PIN: <span class="text-2xl font-extrabold text-green-600">{{ voucher.username }}</span></p>
        {% else %}
            <p class="text-gray-800 leading-none mt-1">Usuario: <span class="text-sm font-bold text-green-600">{{ voucher.username }}</span></p>
            <p class="text-gray-800 leading-none">Pass: <span class="text-sm font-bold text-red-600">{{ voucher.password }}</span></p>
        {% endif %}

        {% if voucher.limit_uptime_formatted %}
            <p class="text-gray-700 leading-none mt-1">Tiempo: <span class="font-semibold">{{ voucher.limit_uptime_formatted }}</span></p>
        {% endif %}
        <p class="text-gray-700 leading-none">Expiración: <span class="font-semibold">{{ voucher.expiration_mode_display }}</span></p>
        <p class="text-gray-700 leading-none mt-1" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Login: <span class="font-semibold">{{ hotspot_dns }}</span></p>
    </div>
</div>
"""
    with open(VOUCHER_TEMPLATE_FILE, 'w', encoding='utf-8') as f:
        f.write(default_voucher_content)

# Sirve archivos desde la carpeta app_data bajo la URL /app_data/<filename>
@app.route('/app_data/<path:filename>')
def serve_app_data_file(filename):
    return send_from_directory(APP_DATA_FOLDER, filename)

# --- MANEJADOR DE ERRORES GLOBAL ---
@app.errorhandler(ConfigError)
def handle_config_error(e):
    return render_template('error_conexion.html', message=str(e)), 500

# --- RUTAS PRINCIPALES DE LA APLICACIÓN (Ahora en main_bp en routes.py) ---

# Ruta de inicio que redirige al login o setup si es necesario
@app.route('/')
def index():
    with app.app_context():
        if not User.query.first():
            flash("Por favor, configura el primer usuario administrador.", "info")
            return redirect(url_for('auth.setup_initial_user'))
    
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('main.dashboard')) 

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('users.db'):
            db.create_all() 
    app.run(debug=True, host='0.0.0.0', port=5000)