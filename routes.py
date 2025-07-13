from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user

# Importar desde módulos personalizados
from config import HOTSPOT_DNS, ConfigError 
from database import db, User 
from mikrotik_service import ( # Importar servicios de MikroTik
    get_api_connection, parse_limit_uptime, 
    get_hotspot_users, get_hotspot_user_by_id, add_hotspot_user, set_hotspot_user, remove_hotspot_user,
    get_active_hotspot_users, disconnect_hotspot_user,
    get_hotspot_profiles, get_hotspot_profile_by_id, add_hotspot_profile, set_hotspot_profile, remove_hotspot_profile,
    get_router_system_info # Importar la nueva función
)
from utils import ( # Importar de utils.py
    load_prices, save_prices, load_custom_expiration_scripts, 
    save_custom_expiration_scripts, get_all_expiration_scripts, 
    format_uptime_display, allowed_file, SCRIPTS_DE_EXPIRACION,
    APP_DATA_FOLDER, PRICES_FILE, EXPIRATION_SCRIPTS_FILE, VOUCHER_TEMPLATE_FILE, LOGO_FILE
)

# Constantes adicionales que podrían ser movidas a config.py o utils.py si no lo están
# Estas variables ya deberían importarse desde utils, no definirse aquí.
# sys, random, string, datetime, re, secure_filename se deberían importar solo si se usan en este archivo y no en un servicio.
import sys # Usado en este archivo, sí
import random # Usado en generar_vouchers
import string # Usado en generar_vouchers
from datetime import datetime # Usado en generar_vouchers
import re # Usado en parse_limit_uptime (aunque ahora está en mikrotik_service)
# from werkzeug.utils import secure_filename # Ya no se usa aquí directamente, se usa en mikrotik_service


# Crear un Blueprint para las rutas principales
main_bp = Blueprint('main', __name__, template_folder='templates') 

# --- RUTAS DE LA INTERFAZ DE ADMINISTRACIÓN ---

@main_bp.route('/dashboard')
@login_required 
def dashboard():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    active_users = get_active_hotspot_users() 
    all_users = get_hotspot_users() 
    
    router_info = get_router_system_info() # Obtener la información del router
    
    # Formatear datos para la plantilla
    formatted_router_info = {
        'current_datetime': 'N/A',
        'uptime_display': 'N/A',
        'model': 'N/A',
        'version': 'N/A',
        'cpu_load': 'N/A',
        'memory_used_mb': 'N/A',
        'memory_total_mb': 'N/A',
        'hdd_used_mb': 'N/A',
        'hdd_total_mb': 'N/A'
    }

    if router_info:
        formatted_router_info['current_datetime'] = f"{router_info['current_date']} {router_info['current_time']}"
        formatted_router_info['uptime_display'] = format_uptime_display(router_info['uptime'])
        formatted_router_info['model'] = router_info['board_name']
        formatted_router_info['version'] = router_info['version']
        formatted_router_info['cpu_load'] = f"{router_info['cpu_load']}%"
        formatted_router_info['memory_used_mb'] = f"{router_info['memory_used_mb']} MB"
        formatted_router_info['memory_total_mb'] = f"{router_info['memory_total_mb']} MB"
        formatted_router_info['hdd_used_mb'] = f"{router_info['hdd_used_mb']} MB"
        formatted_router_info['hdd_total_mb'] = f"{router_info['hdd_total_mb']} MB"


    return render_template('dashboard.html', 
                           active_users=active_users, 
                           all_users=all_users, 
                           active_page='dashboard',
                           router_info=formatted_router_info) # Pasar los datos formateados

@main_bp.route('/profiles')
@login_required 
def profiles_page():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profiles_list = get_hotspot_profiles() 
    prices = load_prices()
    all_expiration_scripts = get_all_expiration_scripts()

    for profile in profiles_list:
        profile_price_data = prices.get(profile['name'], {})
        profile['price'] = profile_price_data.get('price', 'N/A')
        
        current_on_login_script = profile.get('on-login', '')
        found_mode_name = "Personalizado/Desconocido" 
        for key, value in all_expiration_scripts.items():
            if value.get('script_on_login') == current_on_login_script:
                found_mode_name = value.get('nombre_visible')
                break
        profile['expiration_mode_name'] = found_mode_name

    return render_template('profiles.html', profiles_list=profiles_list, 
                           expiration_scripts=all_expiration_scripts, active_page='profiles')

@main_bp.route('/create_profile', methods=['POST'])
@login_required 
def create_profile():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_name = request.form['name']
    shared_users = request.form['shared_users']
    rate_limit = request.form['rate_limit']
    expiration_key = request.form['expiration_mode']
    price = request.form.get('price', "0.00")

    on_login_script = get_all_expiration_scripts().get(expiration_key, {}).get('script_on_login', '')

    add_hotspot_profile( 
        {'name': profile_name,
        'shared_users': shared_users,
        'rate_limit': rate_limit,
        'on_login': on_login_script}
    )

    prices = load_prices()
    if price:
        prices[profile_name] = {'price': price}
        save_prices(prices)

    return redirect(url_for('main.profiles_page')) 

@main_bp.route('/edit_profile/<profile_id>')
@login_required 
def edit_profile_page(profile_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_data = get_hotspot_profile_by_id(profile_id) 
    if not profile_data:
        return "Perfil no encontrado", 404

    prices = load_prices()
    profile_price_data = prices.get(profile_data['name'], {})
    profile_data['price'] = profile_price_data.get('price', '')

    all_expiration_scripts = get_all_expiration_scripts()
    
    current_on_login = profile_data.get('on-login', '')
    selected_expiration_key = "none" 
    for key, value in all_expiration_scripts.items():
        if value.get('script_on_login') == current_on_login:
            selected_expiration_key = key
            break

    return render_template('edit_profile.html', profile_data=profile_data, 
                           expiration_scripts=all_expiration_scripts, 
                           selected_expiration_key=selected_expiration_key,
                           active_page='profiles') 

@main_bp.route('/update_profile/<profile_id>', methods=['POST'])
@login_required 
def update_profile(profile_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_name = request.form['name']
    price = request.form.get('price', "0.00")

    expiration_key = request.form['expiration_mode']
    on_login_script = get_all_expiration_scripts().get(expiration_key, {}).get('script_on_login', '')

    update_params = {
        'shared-users': request.form['shared_users'],
        'rate-limit': request.form['rate_limit'],
        'on-login': on_login_script
    }
    set_hotspot_profile(profile_id, update_params) 


    prices = load_prices()
    if price:
        prices[profile_name] = {'price': price}
        save_prices(prices)

    return redirect(url_for('main.profiles_page')) 

@main_bp.route('/delete_profile/<profile_id>')
@login_required 
def delete_profile(profile_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_list = get_hotspot_profile_by_id(profile_id) 
    if profile_list:
        profile_name = profile_list['name'] 
        prices = load_prices()
        if profile_name in prices:
            prices.pop(profile_name)
            save_prices(prices)

    remove_hotspot_profile(profile_id) 

    return redirect(url_for('main.profiles_page')) 


@main_bp.route('/generate')
@login_required 
def generate_page():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profiles = get_hotspot_profiles() 
    return render_template('generate.html', profiles=profiles, active_page='generate')

@main_bp.route('/generar_vouchers', methods=['POST'])
@login_required 
def generar_vouchers():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    cantidad = int(request.form['cantidad'])
    server = request.form['server']
    modo_usuario = request.form['modo_usuario']
    longitud = int(request.form['longitud'])
    caracteres = request.form['caracteres']
    perfil = request.form['profile']
    limit_uptime_raw = request.form.get('limit_uptime', '')
    comment_lote = request.form.get('comment', '').strip()

    limit_uptime_mikrotik_format = parse_limit_uptime(limit_uptime_raw) 

    char_set = string.digits # Defino aquí para evitar NameError
    if caracteres == 'numeros':
        char_set = string.digits
    elif caracteres == 'letras':
        char_set = string.ascii_lowercase
    else:
        char_set = string.ascii_lowercase + string.digits

    date_str = datetime.now().strftime('%Y-%m-%d')
    final_comment = f"{comment_lote} - {date_str}" if comment_lote else date_str

    for _ in range(cantidad):
        params = {
            'profile': perfil,
            'server': server,
            'comment': final_comment
        }
        if modo_usuario == 'pin':
            codigo = ''.join(random.choices(char_set, k=longitud))
            params['name'] = codigo
            params['password'] = codigo
        else:
            usuario = ''.join(random.choices(char_set, k=longitud))
            password = ''.join(random.choices(char_set, k=longitud))
            params['name'] = usuario
            params['password'] = password

        if limit_uptime_mikrotik_format: 
            params['limit-uptime'] = limit_uptime_mikrotik_format

        add_hotspot_user(**params) 

    return redirect(url_for('main.generate_page')) 

@main_bp.route('/create_manual_user', methods=['POST'])
@login_required 
def create_manual_user():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    params = {
        'name': request.form['username'],
        'password': request.form['password'],
        'profile': request.form['profile'],
        'comment': request.form.get('comment', '')
    }
    limit_uptime_raw = request.form.get('limit_uptime', '')
    limit_uptime_mikrotik_format = parse_limit_uptime(limit_uptime_raw) 
    if limit_uptime_mikrotik_format:
        params['limit-uptime'] = limit_uptime_mikrotik_format

    add_hotspot_user(**params) 

    return redirect(url_for('main.list_users')) 


@main_bp.route('/users')
@login_required 
def list_users():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    all_users_list = get_hotspot_users() 

    all_profiles_list = get_hotspot_profiles() 
    profiles_for_dropdown = sorted([p['name'] for p in all_profiles_list])

    comments = sorted(list(set(user.get('comment', '') for user in all_users_list if user.get('comment'))))

    filtered_users = all_users_list
    if profile_filter:
        filtered_users = [user for user in filtered_users if user.get('profile') == profile_filter]
    if comment_filter:
        filtered_users = [user for user in filtered_users if user.get('comment') == comment_filter]
    if search_query:
        filtered_users = [user for user in filtered_users if search_query.lower() in user.get('name', '').lower()]

    return render_template(
        'users.html', 
        all_users=filtered_users,
        profiles=profiles_for_dropdown,
        comments=comments,
        selected_profile=profile_filter,
        selected_comment=comment_filter,
        search_query=search_query,
        active_page='users'
    )

@main_bp.route('/edit_user/<user_id>')
@login_required 
def edit_user_page(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    user_data = get_hotspot_user_by_id(user_id) 
    if not user_data:
        return "Usuario no encontrado", 404

    profiles = get_hotspot_profiles() 

    return render_template('edit_user.html', user_data=user_data, profiles=profiles, active_page='users')

@main_bp.route('/update_user/<user_id>', methods=['POST'])
@login_required 
def update_user(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    update_params = {
        'profile': request.form['profile'],
        'comment': request.form['comment']
    }
    new_password = request.form['password']
    if new_password:
        update_params['password'] = new_password

    limit_uptime_raw = request.form.get('limit_uptime', '')
    limit_uptime_mikrotik_format = parse_limit_uptime(limit_uptime_raw) 
    if limit_uptime_mikrotik_format:
        update_params['limit-uptime'] = limit_uptime_mikrotik_format

    set_hotspot_user(user_id, update_params) 

    return redirect(url_for('main.list_users')) 

@main_bp.route('/delete_by_filter')
@login_required 
def delete_by_filter():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    all_users_list = get_hotspot_users() 
    
    users_to_delete = all_users_list
    if profile_filter:
        users_to_delete = [user for user in users_to_delete if user.get('profile') == profile_filter]
    if comment_filter:
        users_to_delete = [user for user in users_to_delete if user.get('comment') == comment_filter]
    if search_query:
        users_to_delete = [user for user in users_to_delete if search_query.lower() in user.get('name', '').lower()]

    ids_to_delete = [user['id'] for user in users_to_delete if 'id' in user]
    for user_id in ids_to_delete:
        remove_hotspot_user(user_id) 

    return redirect(url_for('main.list_users')) 

@main_bp.route('/delete_user/<user_id>')
@login_required 
def delete_user(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    remove_hotspot_user(user_id) 

    return redirect(url_for('main.list_users')) 

@main_bp.route('/active_users')
@login_required 
def list_active_users():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    active_users_list = get_active_hotspot_users() 

    return render_template('active_users.html', active_users_list=active_users_list, active_page='dashboard') 

@main_bp.route('/disconnect_user/<user_id>')
@login_required 
def disconnect_user(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    disconnect_hotspot_user(user_id) 

    return redirect(url_for('main.list_active_users')) 

@main_bp.route('/disable_user/<user_id>')
@login_required 
def disable_user(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    set_hotspot_user(user_id, {'disabled': 'true'}) 

    return redirect(url_for('main.list_users')) 

@main_bp.route('/enable_user/<user_id>')
@login_required 
def enable_user(user_id):
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    set_hotspot_user(user_id, {'disabled': 'false'}) 

    return redirect(url_for('main.list_users')) 

@main_bp.route('/expiration_modes')
@login_required 
def expiration_modes_page():
    custom_scripts = load_custom_expiration_scripts()
    all_scripts = get_all_expiration_scripts() 
    
    predefined_modes = {k: v for k, v in all_scripts.items() if k in SCRIPTS_DE_EXPIRACION}
    custom_modes = {k: v for k, v in all_scripts.items() if k not in SCRIPTS_DE_EXPIRACION}

    return render_template('expiration_modes.html', 
                           predefined_modes=predefined_modes, 
                           custom_modes=custom_modes,
                           active_page='expiration_modes')

@main_bp.route('/create_expiration_mode', methods=['POST'])
@login_required 
def create_expiration_mode():
    nombre_visible = request.form['nombre_visible'].strip()
    script_on_login = request.form['script_on_login'].strip()

    if not nombre_visible or not script_on_login:
        return "Nombre visible y script son obligatorios", 400

    custom_scripts = load_custom_expiration_scripts()
    new_key = nombre_visible.lower().replace(" ", "_")
    i = 1
    while new_key in custom_scripts or new_key in SCRIPTS_DE_EXPIRACION:
        new_key = f"{nombre_visible.lower().replace(' ', '_')}_{i}"
        i += 1
    
    custom_scripts[new_key] = {
        "nombre_visible": nombre_visible,
        "script_on_login": script_on_login
    }
    save_custom_expiration_scripts(custom_scripts)

    return redirect(url_for('main.expiration_modes_page')) 

@main_bp.route('/edit_expiration_mode/<mode_key>')
@login_required 
def edit_expiration_mode_page(mode_key):
    all_scripts = get_all_expiration_scripts()
    mode_data = all_scripts.get(mode_key)

    if not mode_data:
        return "Modo de expiración no encontrado", 404
    
    is_predefined = mode_key in SCRIPTS_DE_EXPIRACION

    return render_template('edit_expiration_mode.html', 
                           mode_key=mode_key, 
                           mode_data=mode_data, 
                           is_predefined=is_predefined,
                           active_page='expiration_modes') 

@main_bp.route('/update_expiration_mode/<mode_key>', methods=['POST'])
@login_required 
def update_expiration_mode(mode_key):
    nombre_visible = request.form['nombre_visible'].strip()
    script_on_login = request.form['script_on_login'].strip()

    if not nombre_visible or not script_on_login:
        return "Nombre visible y script son obligatorios", 400
    
    if mode_key in SCRIPTS_DE_EXPIRACION:
        return "No se pueden editar los modos de expiración predefinidos.", 403

    custom_scripts = load_custom_expiration_scripts()
    if mode_key in custom_scripts:
        custom_scripts[mode_key]['nombre_visible'] = nombre_visible
        custom_scripts[mode_key]['script_on_login'] = script_on_login
        save_custom_expiration_scripts(custom_scripts)
    else:
        return "Modo de expiración personalizado no encontrado para actualizar", 404

    return redirect(url_for('main.expiration_modes_page')) 

@main_bp.route('/delete_expiration_mode/<mode_key>')
@login_required 
def delete_expiration_mode(mode_key):
    if mode_key in SCRIPTS_DE_EXPIRACION:
        return "No se pueden eliminar los modos de expiración predefinidos.", 403

    custom_scripts = load_custom_expiration_scripts()
    if mode_key in custom_scripts:
        del custom_scripts[mode_key]
        save_custom_scripts(custom_scripts)
    else:
        return "Modo de expiración personalizado no encontrado para eliminar", 404
    
    return redirect(url_for('main.expiration_modes_page')) 

@main_bp.route('/print_vouchers')
@login_required 
def print_vouchers():
    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    all_users_list = get_hotspot_users() 
    all_profiles_mikrotik = get_hotspot_profiles() 
    all_prices = load_prices()
    all_expiration_scripts = get_all_expiration_scripts()

    filtered_users = all_users_list
    if profile_filter:
        filtered_users = [user for user in filtered_users if user.get('profile') == profile_filter]
    if comment_filter:
        filtered_users = [user for user in filtered_users if user.get('comment') == comment_filter]
    if search_query:
        filtered_users = [user for user in filtered_users if search_query.lower() in user.get('name', '').lower()]

    vouchers_data = []
    for user in filtered_users:
        mode = 'pin' if user.get('name') == user.get('password') else 'userpass'
        
        user_profile_name = user.get('profile')
        user_profile_data = next((p for p in all_profiles_mikrotik if p.get('name') == user_profile_name), None)
        
        expiration_display_name = "N/A"
        if user_profile_data:
            user_on_login_script = user_profile_data.get('on-login', '')
            for key, script_info in all_expiration_scripts.items():
                if script_info.get('script_on_login') == user_on_login_script:
                    expiration_display_name = script_info.get('nombre_visible')
                    break
        
        price_for_profile = all_prices.get(user_profile_name, {}).get('price', 'N/A')

        formatted_limit_uptime = format_uptime_display(user.get('limit-uptime', '0s'))

        vouchers_data.append({
            'username': user.get('name'),
            'password': user.get('password') if mode == 'userpass' else '',
            'limit_uptime_formatted': formatted_limit_uptime,
            'expiration_mode_display': expiration_display_name,
            'price': price_for_profile,
            'mode': mode
        })
    
    try:
        with open(VOUCHER_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            voucher_template_content = f.read()
    except FileNotFoundError:
        voucher_template_content = ""

    rendered_vouchers_html = []
    for voucher in vouchers_data:
        try:
            rendered_html_for_one_voucher = current_app.jinja_env.from_string(voucher_template_content).render( 
                voucher=voucher,
                hotspot_dns=HOTSPOT_DNS
            )
            rendered_vouchers_html.append(rendered_html_for_one_voucher)
        except Exception as e:
            error_html = f"<div style='color: red; padding: 5px; border: 1px solid red; margin: 5px;'>Error en plantilla del voucher '{voucher.get('username', 'N/A')}': {e}</div>"
            rendered_vouchers_html.append(error_html)


    return render_template('vouchers/print_vouchers.html', 
                           rendered_vouchers_html=rendered_vouchers_html, 
                           hotspot_dns=HOTSPOT_DNS) 

@main_bp.route('/template_editor/voucher', methods=['GET', 'POST'])
@login_required 
def voucher_template_editor():
    upload_logo_message = request.args.get('upload_logo_message')

    if request.method == 'POST':
        new_template_content = request.form['template_code']
        try:
            with open(VOUCHER_TEMPLATE_FILE, 'w', encoding='utf-8') as f:
                f.write(new_template_content)
            return redirect(url_for('main.voucher_template_editor', saved='true')) 
        except Exception as e:
            return render_template('error_conexion.html', message=f"Error al guardar la plantilla: {e}")

    try:
        with open(VOUCHER_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            current_template_content = f.read()
    except FileNotFoundError:
        current_template_content = ""
    except Exception as e:
        current_template_content = f""
    
    saved_message = request.args.get('saved')
    if saved_message == 'true':
        saved_message = "Plantilla guardada exitosamente."

    return render_template('template_editor.html', 
                           current_template_content=current_template_content,
                           active_page='template_editor', 
                           saved_message=saved_message,
                           upload_logo_message=upload_logo_message) 

@main_bp.route('/upload_logo', methods=['POST'])
@login_required 
def upload_logo():
    if 'logo_file' not in request.files:
        return redirect(url_for('main.voucher_template_editor', upload_logo_message='No se seleccionó ningún archivo.')) 
    
    file = request.files['logo_file']
    
    if file.filename == '':
        return redirect(url_for('main.voucher_template_editor', upload_logo_message='No se seleccionó ningún archivo.')) 
    
    if file and allowed_file(file.filename): 
        try:
            filename = 'logo.png' 
            file.save(os.path.join(APP_DATA_FOLDER, filename))
            return redirect(url_for('main.voucher_template_editor', upload_logo_message='Logo subido exitosamente.')) 
        except Exception as e:
            return redirect(url_for('main.voucher_template_editor', upload_logo_message=f'Error al subir el logo: {e}')) 
    else:
        return redirect(url_for('main.voucher_template_editor', upload_logo_message='Tipo de archivo no permitido. Solo PNG, JPG, JPEG, GIF.')) 


@main_bp.route('/preview_voucher_template', methods=['POST'])
@login_required 
def preview_voucher_template():
    template_code = request.form['template_code']
    
    example_voucher = {
        'username': 'ABCDEF',
        'password': '123456',
        'mode': 'pin', 
        'limit_uptime_formatted': '1 hora',
        'expiration_mode_display': 'Eliminar al Agotar',
        'price': '2.50'
    }
    
    try:
        rendered_html = current_app.jinja_env.from_string(template_code).render(
            voucher=example_voucher,
            hotspot_dns=HOTSPOT_DNS 
        )
        return rendered_html
    except Exception as e:
        return f"<div style='color: red; padding: 20px;'>Error de Jinja2 en la plantilla:<br><pre>{e}</pre></div>"