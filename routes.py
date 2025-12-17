from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session
from flask_login import login_required, current_user

# Importar desde módulos personalizados
from config import HOTSPOT_DNS, ConfigError
from database import db, User, Sale, Router
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

import sys
import random
import string
from datetime import datetime, timedelta
import re
import os
from sqlalchemy import func, extract


main_bp = Blueprint('main', __name__, template_folder='templates')

# ========== FUNCIONES HELPER PARA MULTI-ROUTER ==========

def get_active_router():
    """
    Obtiene el router activo para el usuario actual.
    Prioridad: 1) Sesión, 2) Último usado por usuario, 3) Router por defecto
    """
    router_id = session.get('active_router_id')
    
    if router_id:
        router = Router.query.get(router_id)
        if router and router.is_active:
            return router
    
    # Si no hay en sesión, usar el último del usuario
    if current_user.is_authenticated and current_user.last_router_id:
        router = Router.query.get(current_user.last_router_id)
        if router and router.is_active:
            session['active_router_id'] = router.id
            return router
    
    # Si no, usar el router por defecto
    router = Router.query.filter_by(is_default=True, is_active=True).first()
    if not router:
        # Si no hay default, usar el primero activo
        router = Router.query.filter_by(is_active=True).first()
    
    if router:
        session['active_router_id'] = router.id
    
    return router

def set_active_router(router_id):
    """Establece el router activo en la sesión y lo guarda como último usado del usuario"""
    router = Router.query.get(router_id)
    if router and router.is_active:
        session['active_router_id'] = router_id
        if current_user.is_authenticated:
            current_user.last_router_id = router_id
            db.session.commit()
        return True
    return False

def get_all_active_routers():
    """Obtiene todos los routers activos"""
    return Router.query.filter_by(is_active=True).order_by(Router.is_default.desc(), Router.name).all()

# ========== FIN FUNCIONES HELPER MULTI-ROUTER ==========


def check_and_record_active_sales():
    """
    Verifica los usuarios activos y registra una venta si es la primera vez que se detectan.
    Asocia la venta con el router activo.
    """
    # Obtener router activo
    active_router = get_active_router()
    if not active_router:
        print("⚠️  No hay router activo, no se pueden registrar ventas")
        return
    
    active_users = get_active_hotspot_users()
    if not active_users:
        return

    prices = load_prices()
    all_users = get_hotspot_users() # Necesitamos esto para saber el perfil del usuario activo si no viene en active_users
    
    # Crear un mapa de usuario -> perfil para acceso rápido
    user_profile_map = {u['name']: u.get('profile') for u in all_users} if all_users else {}

    for active_user in active_users:
        username = active_user.get('user')
        if not username:
            continue

        # Verificar si ya existe una venta para este usuario EN ESTE ROUTER
        existing_sale = Sale.query.filter_by(
            ticket_code=username,
            router_id=active_router.id
        ).first()
        
        if not existing_sale:
            # Es una nueva venta!
            profile_name = user_profile_map.get(username, 'Unknown')
            price_data = prices.get(profile_name, {})
            price = float(price_data.get('price', 0.0))

            if price > 0:
                new_sale = Sale(
                    ticket_code=username,
                    profile_name=profile_name,
                    price=price,
                    date_created=datetime.now(),
                    router_id=active_router.id  # ← Asociar con router activo
                )
                db.session.add(new_sale)
                print(f"💰 Venta registrada en {active_router.name}: {username} - ${price}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar ventas: {e}")

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Obtener router activo
    active_router = get_active_router()
    if not active_router:
        flash("No hay router activo. Por favor, configura un router primero.", "danger")
        return redirect(url_for('routers.list_routers'))
    
    # Registrar ventas de usuarios activos
    check_and_record_active_sales()

    # Calcular ventas SOLO DEL ROUTER ACTIVO
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Ventas de hoy (Suma de precios) - FILTRADO POR ROUTER
    sales_today = db.session.query(func.sum(Sale.price)).filter(
        Sale.date_created >= today_start,
        Sale.router_id == active_router.id
    ).scalar() or 0
    
    # Ventas del mes (Suma de precios) - FILTRADO POR ROUTER
    sales_month = db.session.query(func.sum(Sale.price)).filter(
        Sale.date_created >= month_start,
        Sale.router_id == active_router.id
    ).scalar() or 0



    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router MikroTik. Por favor, verifica la configuración o la conexión.", "danger")
        return render_template('dashboard.html',
                               active_users=[],
                               all_users=[],
                               active_page='dashboard',
                               router_info={
                                   'current_datetime': 'N/A',
                                   'uptime_display': 'N/A',
                                   'model': 'N/A',
                                   'version': 'N/A',
                                   'cpu_load': 'N/A',
                                   'memory_used_mb': 'N/A',
                                   'memory_total_mb': 'N/A',
                                   'hdd_used_mb': 'N/A',
                                   'hdd_total_mb': 'N/A'
                               })

    active_users = get_active_hotspot_users()
    all_users = get_hotspot_users()

    router_info = get_router_system_info()

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
        formatted_router_info['current_datetime'] = f"{router_info.get('current_date', 'N/A')} {router_info.get('current_time', 'N/A')}"
        formatted_router_info['uptime_display'] = format_uptime_display(router_info.get('uptime', '0s'))
        formatted_router_info['model'] = router_info.get('board_name', 'N/A')
        formatted_router_info['version'] = router_info.get('version', 'N/A')
        formatted_router_info['cpu_load'] = f"{router_info.get('cpu_load', '0')}%"
        
        formatted_router_info['memory_used_mb'] = f"{router_info.get('memory_used_mb', 0)} MB"
        formatted_router_info['memory_total_mb'] = f"{router_info.get('memory_total_mb', 0)} MB"

        formatted_router_info['hdd_used_mb'] = f"{router_info.get('hdd_used_mb', 0)} MB"
        formatted_router_info['hdd_total_mb'] = f"{router_info.get('hdd_total_mb', 0)} MB"

    # --- Datos para el Gráfico (Últimos 7 días) - FILTRADO POR ROUTER ---
    chart_labels = []
    chart_values = []
    
    # Iterar por los últimos 7 días (incluyendo hoy)
    for i in range(6, -1, -1):
        date_point = now - timedelta(days=i)
        start_of_day = date_point.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date_point.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_total = db.session.query(func.sum(Sale.price)).filter(
            Sale.date_created >= start_of_day,
            Sale.date_created <= end_of_day,
            Sale.router_id == active_router.id  # ← FILTRADO POR ROUTER
        ).scalar() or 0
        
        # Etiqueta: Solo día/mes (ej. 17/12)
        chart_labels.append(date_point.strftime("%d/%m"))
        chart_values.append(float(daily_total))

    # --- Actividad Reciente (Últimas 5 ventas) - FILTRADO POR ROUTER ---
    recent_sales = Sale.query.filter_by(router_id=active_router.id).order_by(Sale.date_created.desc()).limit(5).all()

    # --- Perfiles (Para el modal de creación rápida) ---
    all_profiles = get_hotspot_profiles()
    if all_profiles is None:
        all_profiles = []

    return render_template('dashboard.html',
                           active_users=active_users if active_users is not None else [],
                           all_users=all_users if all_users is not None else [],
                           active_page='dashboard',
                           router_info=formatted_router_info,
                           sales_today=sales_today,
                           sales_month=sales_month,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           recent_sales=recent_sales,
                           all_profiles=all_profiles)

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
    
    # Verificar si venimos de generar un lote
    last_batch_comment = request.args.get('last_batch_comment')
    
    return render_template('generate.html', 
                           profiles=profiles, 
                           active_page='generate',
                           last_batch_comment=last_batch_comment)

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

    # Definir caracteres excluyendo los confusos (0, 1, l, o)
    # Digitos seguros: 23456789
    safe_digits = "23456789"
    # Letras seguras: abcdefghijkmnpqrstuvwxyz (sin l, o)
    safe_letters = "abcdefghijkmnpqrstuvwxyz"

    char_set = ""
    if caracteres == 'numeros':
        char_set = safe_digits
    elif caracteres == 'letras':
        char_set = safe_letters
    else:
        # Combinado (letras + números)
        char_set = safe_letters + safe_digits

    # Revertimos a formato ISO (YYYY-MM-DD) para asegurar que el ordenamiento
    # en la lista desplegable sea siempre cronológico correcto (los más nuevos arriba).
    # AÑADIDO: Incluimos Hora y Minuto para diferenciar lotes generados el mismo día
    # NOTA: Esto se calcula UNA sola vez antes del bucle, por lo que todo el lote tendrá la misma hora exacta.
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Construcción inteligente del comentario del lote
    if comment_lote:
        # Si hay comentario manual: "MiComentario - 2025-12-16 15:30 [40]"
        final_comment = f"{comment_lote} - {date_str} [{cantidad}]"
    else:
        # Automático: "2025-12-16 15:30 [1-HORA] [40]"
        final_comment = f"{date_str} [{perfil}] [{cantidad}]"

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
        
    flash(f"Se generaron {cantidad} vouchers exitosamente.", "success")

    # Redirigimos pasando el comentario del lote recién creado como parámetro
    # Esto nos permitirá mostrar un botón de "Imprimir Lote" en la página de destino
    return redirect(url_for('main.generate_page', last_batch_comment=final_comment))

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
        flash("No se pudo conectar con el router. Los usuarios no pudieron ser cargados.", "danger")
        return render_template('users.html',
                               all_users=[],
                               profiles=[],
                               comments=[],
                               selected_profile='',
                               selected_comment='',
                               search_query='',
                               active_page='users',
                               filters_applied=False)

    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    all_users_from_mikrotik = get_hotspot_users()
    
    if all_users_from_mikrotik is None:
        all_users_from_mikrotik = []
        flash("No se pudieron cargar los usuarios del hotspot. Verifica la conexión con el router.", "danger")

    all_profiles_list = get_hotspot_profiles()
    profiles_for_dropdown = sorted([p['name'] for p in all_profiles_list]) if all_profiles_list else []

    comments = sorted(list(set(user.get('comment', '') for user in all_users_from_mikrotik if user.get('comment'))))

    # Determinar si algún filtro está activo
    filters_applied = bool(profile_filter or comment_filter or search_query)

    # Aplicar los filtros a la lista completa
    filtered_users_list = all_users_from_mikrotik
    if profile_filter:
        filtered_users_list = [user for user in filtered_users_list if user.get('profile') == profile_filter]
    if comment_filter:
        filtered_users_list = [user for user in filtered_users_list if user.get('comment') == comment_filter]
    if search_query:
        filtered_users_list = [user for user in filtered_users_list if search_query.lower() in user.get('name', '').lower()]

    # ORDENAMIENTO: Mostrar los usuarios más nuevos primero
    # MikroTik devuelve los IDs en formato *1, *2, etc. Al ordenar inversamente conseguimos que los últimos creados queden arriba.
    # Usamos una función lambda segura que maneja IDs no estándar por si acaso.
    try:
        filtered_users_list.sort(key=lambda x: int(x.get('.id', '*0').replace('*', ''), 16) if x.get('.id', '').startswith('*') else 0, reverse=True)
    except Exception:
        # Si falla el ordenamiento por ID hexadecimal, simplemente invertimos la lista (fallback)
        filtered_users_list.reverse()

    # Ordenar los comentarios en orden descendente (los lotes más nuevos suelen tener comentarios lexicográficamente mayores o simplemente queremos ver los últimos creados)
    # Si los comentarios son fechas o números de lote, 'reverse=True' ayuda.
    comments.sort(reverse=True)

    return render_template(
        'users.html',
        all_users=filtered_users_list,
        profiles=profiles_for_dropdown,
        comments=comments,
        selected_profile=profile_filter,
        selected_comment=comment_filter,
        search_query=search_query,
        active_page='users',
        filters_applied=filters_applied
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
    if profiles is None:
        profiles = []

    return render_template('edit_user.html', user_data=user_data, profiles=profiles, active_page='users')

@main_bp.route('/update_user/<user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue actualizado.", "danger")
        return redirect(url_for('main.list_users'))

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

    if set_hotspot_user(user_id, update_params):
        flash("Usuario actualizado exitosamente.", "success")
    else:
        flash("Error al actualizar el usuario.", "danger")

    return redirect(url_for('main.list_users'))

@main_bp.route('/delete_by_filter')
@login_required
def delete_by_filter():
    # Obtener los filtros para comprobar si alguno está activo
    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    # Si no hay ningún filtro aplicado, redirigir y mostrar un mensaje
    if not (profile_filter or comment_filter or search_query):
        flash("La eliminación por filtro requiere que se aplique al menos un criterio de búsqueda. Si desea eliminar todos los usuarios, primero filtre por un criterio que los incluya a todos (Ej. un comentario común a todos) y luego use este botón.", "info")
        return redirect(url_for('main.list_users'))

    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. Los usuarios no fueron eliminados.", "danger")
        return redirect(url_for('main.list_users'))

    all_users_list = get_hotspot_users()
    if all_users_list is None:
        all_users_list = []
        flash("No se pudieron cargar los usuarios para eliminar. Verifica la conexión con el router.", "danger")


    users_to_delete = all_users_list
    if profile_filter:
        users_to_delete = [user for user in users_to_delete if user.get('profile') == profile_filter]
    if comment_filter:
        users_to_delete = [user for user in users_to_delete if user.get('comment') == comment_filter]
    if search_query:
        users_to_delete = [user for user in users_to_delete if search_query.lower() in user.get('name', '').lower()]

    ids_to_delete = [user['id'] for user in users_to_delete if 'id' in user]
    
    # Si después de aplicar los filtros la lista está vacía, mostrar mensaje
    if not ids_to_delete:
        flash("No se encontraron usuarios que coincidan con los filtros para eliminar. Ningún usuario fue eliminado.", "warning")
        return redirect(url_for('main.list_users'))

    deleted_count = 0
    for user_id in ids_to_delete:
        if remove_hotspot_user(user_id):
            deleted_count += 1
    
    flash(f"Se eliminaron {deleted_count} de {len(ids_to_delete)} usuarios filtrados.", "success")


    return redirect(url_for('main.list_users'))

@main_bp.route('/delete_user/<user_id>')
@login_required
def delete_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue eliminado.", "danger")
        return redirect(url_for('main.list_users'))

    if remove_hotspot_user(user_id):
        flash("Usuario eliminado exitosamente.", "success")
    else:
        flash("Error al eliminar el usuario.", "danger")

    return redirect(url_for('main.list_users'))

@main_bp.route('/active_users')
@login_required
def list_active_users():
    # Registrar ventas de usuarios activos
    check_and_record_active_sales()

    api = get_api_connection()
    if not api:
        return render_template('error_conexion.html', message="No se pudo conectar con el router. Verifica la configuración o la conexión.")

    active_users_list = get_active_hotspot_users()
    if active_users_list is None:
        active_users_list = []
        flash("No se pudieron cargar los usuarios activos del hotspot. Verifica la conexión con el router.", "danger")

    return render_template('active_users.html', active_users_list=active_users_list, active_page='dashboard')

@main_bp.route('/disconnect_user/<user_id>')
@login_required
def disconnect_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue desconectado.", "danger")
        return redirect(url_for('main.list_active_users'))

    if disconnect_hotspot_user(user_id):
        flash("Usuario desconectado exitosamente.", "success")
    else:
        flash("Error al desconectar el usuario.", "danger")

    return redirect(url_for('main.list_active_users'))

@main_bp.route('/disable_user/<user_id>')
@login_required
def disable_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue deshabilitado.", "danger")
        return redirect(url_for('main.list_users'))

    if set_hotspot_user(user_id, {'disabled': 'true'}):
        flash("Usuario deshabilitado exitosamente.", "success")
    else:
        flash("Error al deshabilitar el usuario.", "danger")

    return redirect(url_for('main.list_users'))

@main_bp.route('/enable_user/<user_id>')
@login_required
def enable_user(user_id):
    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. El usuario no fue habilitado.", "danger")
        return redirect(url_for('main.list_users'))

    if set_hotspot_user(user_id, {'disabled': 'false'}):
        flash("Usuario habilitado exitosamente.", "success")
    else:
        flash("Error al habilitar el usuario.", "danger")

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
        flash("Nombre visible y script son obligatorios.", "danger")
        return redirect(url_for('main.expiration_modes_page'))

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
    flash(f"Modo de expiración '{nombre_visible}' creado exitosamente.", "success")
    return redirect(url_for('main.expiration_modes_page'))

@main_bp.route('/edit_expiration_mode/<mode_key>')
@login_required
def edit_expiration_mode_page(mode_key):
    all_scripts = get_all_expiration_scripts()
    mode_data = all_scripts.get(mode_key)

    if not mode_data:
        flash("Modo de expiración no encontrado.", "danger")
        return redirect(url_for('main.expiration_modes_page'))

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
        flash("Nombre visible y script son obligatorios.", "danger")
        return redirect(url_for('main.edit_expiration_mode_page', mode_key=mode_key))

    if mode_key in SCRIPTS_DE_EXPIRACION:
        flash("No se pueden editar los modos de expiración predefinidos.", "danger")
        return redirect(url_for('main.expiration_modes_page'))

    custom_scripts = load_custom_expiration_scripts()
    if mode_key in custom_scripts:
        custom_scripts[mode_key]['nombre_visible'] = nombre_visible
        custom_scripts[mode_key]['script_on_login'] = script_on_login
        save_custom_expiration_scripts(custom_scripts)
        flash(f"Modo de expiración '{nombre_visible}' actualizado exitosamente.", "success")
    else:
        flash("Modo de expiración personalizado no encontrado para actualizar.", "danger")

    return redirect(url_for('main.expiration_modes_page'))

@main_bp.route('/delete_expiration_mode/<mode_key>')
@login_required
def delete_expiration_mode(mode_key):
    if mode_key in SCRIPTS_DE_EXPIRACION:
        flash("No se pueden eliminar los modos de expiración predefinidos.", "danger")
        return redirect(url_for('main.expiration_modes_page'))

    custom_scripts = load_custom_expiration_scripts()
    if mode_key in custom_scripts:
        del custom_scripts[mode_key]
        save_custom_expiration_scripts(custom_scripts)
        flash("Modo de expiración personalizado eliminado exitosamente.", "success")
    else:
        flash("Modo de expiración personalizado no encontrado para eliminar.", "danger")

    return redirect(url_for('main.expiration_modes_page'))

@main_bp.route('/print_vouchers')
@login_required
def print_vouchers():
    # Obtener los filtros para comprobar si alguno está activo
    profile_filter = request.args.get('profile', '')
    comment_filter = request.args.get('comment', '')
    search_query = request.args.get('search', '').strip()

    # Si no hay ningún filtro aplicado, redirigir y mostrar un mensaje
    if not (profile_filter or comment_filter or search_query):
        flash("Para imprimir vouchers, es necesario aplicar al menos un filtro.", "info")
        return redirect(url_for('main.list_users'))

    api = get_api_connection()
    if not api:
        flash("No se pudo conectar con el router. No se pudieron generar los vouchers para imprimir.", "danger")
        return redirect(url_for('main.list_users'))

    all_users_list = get_hotspot_users()
    if all_users_list is None:
        all_users_list = []
        flash("No se pudieron cargar los usuarios del hotspot. Verifica la conexión con el router.", "danger")

    all_profiles_mikrotik = get_hotspot_profiles()
    if all_profiles_mikrotik is None:
        all_profiles_mikrotik = []

    all_prices = load_prices()
    all_expiration_scripts = get_all_expiration_scripts()

    filtered_users = all_users_list
    if profile_filter:
        filtered_users = [user for user in filtered_users if user.get('profile') == profile_filter]
    if comment_filter:
        filtered_users = [user for user in filtered_users if user.get('comment') == comment_filter]
    if search_query:
        filtered_users = [user for user in filtered_users if search_query.lower() in user.get('name', '').lower()]

    # Si después de aplicar los filtros la lista está vacía, mostrar mensaje
    if not filtered_users:
        flash("No se encontraron usuarios que coincidan con los filtros para imprimir. Ningún voucher fue generado.", "warning")
        return redirect(url_for('main.list_users'))

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
        flash("No se encontró la plantilla de vouchers. Usa el editor de plantillas para crearla.", "warning")
    except Exception as e:
        voucher_template_content = ""
        flash(f"Error al leer la plantilla de vouchers: {e}", "danger")

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
            flash(f"Error al renderizar voucher para {voucher.get('username', 'N/A')}: {e}", "danger")

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
            flash("Plantilla guardada exitosamente.", "success")
            return redirect(url_for('main.voucher_template_editor'))
        except Exception as e:
            flash(f"Error al guardar la plantilla: {e}", "danger")
            return redirect(url_for('main.voucher_template_editor'))

    try:
        with open(VOUCHER_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            current_template_content = f.read()
    except FileNotFoundError:
        current_template_content = ""
        flash("La plantilla de vouchers no existe. Se ha cargado una plantilla vacía.", "warning")
    except Exception as e:
        current_template_content = f""
        flash(f"Error al leer la plantilla de vouchers: {e}", "danger")


    return render_template('template_editor.html',
                           current_template_content=current_template_content,
                           active_page='template_editor',
                           upload_logo_message=upload_logo_message)

@main_bp.route('/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    if 'logo_file' not in request.files:
        flash('No se seleccionó ningún archivo.', "warning")
        return redirect(url_for('main.voucher_template_editor'))

    file = request.files['logo_file']

    if file.filename == '':
        flash('No se seleccionó ningún archivo.', "warning")
        return redirect(url_for('main.voucher_template_editor'))

    if file and allowed_file(file.filename):
        try:
            filename = 'logo.png'
            if not os.path.exists(APP_DATA_FOLDER):
                os.makedirs(APP_DATA_FOLDER)
            file.save(os.path.join(APP_DATA_FOLDER, filename))
            flash('Logo subido exitosamente.', "success")
            return redirect(url_for('main.voucher_template_editor'))
        except Exception as e:
            flash(f'Error al subir el logo: {e}', "danger")
            return redirect(url_for('main.voucher_template_editor'))
    else:
        flash('Tipo de archivo no permitido. Solo PNG, JPG, JPEG, GIF.', "warning")
        return redirect(url_for('main.voucher_template_editor'))



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

@main_bp.route('/reports')
@login_required
def reports_page():
    # Obtener router activo
    active_router = get_active_router()
    if not active_router:
        flash("No hay router activo. Por favor, configura un router primero.", "danger")
        return redirect(url_for('routers.list_routers'))
    
    # Asegurar que las ventas estén actualizadas
    check_and_record_active_sales()

    # Obtener filtros de la URL
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    profile_filter = request.args.get('profile')

    # Construir la consulta base - FILTRADO POR ROUTER
    query = Sale.query.filter_by(router_id=active_router.id)

    # Aplicar filtros
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(Sale.date_created >= start_date)
        except ValueError:
            pass # Ignorar fecha inválida

    if end_date_str:
        try:
            # Ajustar para incluir todo el día final (hasta las 23:59:59)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(Sale.date_created <= end_date)
        except ValueError:
            pass

    if profile_filter:
        query = query.filter(Sale.profile_name == profile_filter)

    # Ejecutar consulta para la tabla (ordenada por fecha descendente)
    # Si hay filtros, mostramos todos los resultados que coincidan. Si no, limitamos a 50.
    if start_date_str or end_date_str or profile_filter:
        sales_list = query.order_by(Sale.date_created.desc()).all()
    else:
        sales_list = query.order_by(Sale.date_created.desc()).limit(50).all()

    # Calcular totales
    total_filtered = sum(sale.price for sale in sales_list)

    # Totales generales (para las tarjetas fijas) - FILTRADO POR ROUTER
    today = datetime.now().date()
    sales_today = Sale.query.filter(
        func.date(Sale.date_created) == today,
        Sale.router_id == active_router.id
    ).all()
    total_today = sum(sale.price for sale in sales_today)

    current_month = datetime.now().strftime('%Y-%m')
    sales_month = Sale.query.filter(
        func.strftime('%Y-%m', Sale.date_created) == current_month,
        Sale.router_id == active_router.id
    ).all()
    total_month = sum(sale.price for sale in sales_month)

    # Obtener lista de perfiles únicos para el filtro - FILTRADO POR ROUTER
    unique_profiles = db.session.query(Sale.profile_name).filter(
        Sale.router_id == active_router.id
    ).distinct().all()
    profiles_list = sorted([p[0] for p in unique_profiles])

    # ===== WEEKLY SALES CALCULATIONS - FILTRADO POR ROUTER =====
    today_date = datetime.now()
    current_weekday = today_date.weekday()  # 0 = Monday, 6 = Sunday
    week_start = (today_date - timedelta(days=current_weekday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7) - timedelta(seconds=1)
    
    sales_this_week = Sale.query.filter(
        Sale.date_created >= week_start,
        Sale.date_created <= week_end,
        Sale.router_id == active_router.id
    ).all()
    total_this_week = sum(sale.price for sale in sales_this_week)
    
    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(seconds=1)
    sales_prev_week = Sale.query.filter(
        Sale.date_created >= prev_week_start,
        Sale.date_created <= prev_week_end,
        Sale.router_id == active_router.id
    ).all()
    total_prev_week = sum(sale.price for sale in sales_prev_week)
    
    if total_prev_week > 0:
        week_change_percent = ((total_this_week - total_prev_week) / total_prev_week) * 100
    else:
        week_change_percent = 100 if total_this_week > 0 else 0

    # ===== DAILY TREND DATA (Last 7 Days) - FILTERED BY ROUTER =====
    daily_labels = []
    daily_totals = []
    for i in range(6, -1, -1):  # 6 días atrás hasta hoy
        day = today_date - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_query = Sale.query.filter(
            Sale.date_created >= day_start,
            Sale.date_created <= day_end,
            Sale.router_id == active_router.id  # ← FILTRADO POR ROUTER
        )
        
        if profile_filter:
            daily_query = daily_query.filter(Sale.profile_name == profile_filter)
            
        daily_sales = daily_query.all()
        daily_total = sum(sale.price for sale in daily_sales)
        
        daily_labels.append(day.strftime('%d/%m'))
        daily_totals.append(daily_total)

    # ===== PROFILE DISTRIBUTION DATA - FILTERED BY ROUTER =====
    if not sales_list and not (start_date_str or end_date_str or profile_filter):
         dist_query = Sale.query.filter(
             func.strftime('%Y-%m', Sale.date_created) == current_month,
             Sale.router_id == active_router.id  # ← FILTRADO POR ROUTER
         )
         dist_sales = dist_query.all()
    else:
        dist_sales = sales_list

    profile_sales_map = {}
    for sale in dist_sales:
        p_name = sale.profile_name
        profile_sales_map[p_name] = profile_sales_map.get(p_name, 0) + sale.price

    profile_labels = list(profile_sales_map.keys())
    profile_totals = list(profile_sales_map.values())

    return render_template('reports.html',
                           sales_list=sales_list,
                           total_filtered=total_filtered,
                           total_today=total_today,
                           total_month=total_month,
                           total_this_week=total_this_week,
                           total_prev_week=total_prev_week,
                           week_change_percent=week_change_percent,
                           daily_labels=daily_labels,
                           daily_totals=daily_totals,
                           profile_labels=profile_labels,
                           profile_totals=profile_totals,
                           profiles_list=profiles_list,
                           selected_start_date=start_date_str,
                           selected_end_date=end_date_str,
                           selected_profile=profile_filter,
                           active_page='reports')
# ========== RUTAS DE PERFIL DE USUARIO ==========

@main_bp.route('/profile')
@login_required
def user_profile():
    """Página de perfil del usuario"""
    return render_template('user_profile.html', active_page='profile')

@main_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Cambiar contraseña del usuario actual"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validaciones
    if not all([current_password, new_password, confirm_password]):
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for('main.user_profile'))
    
    # Verificar contraseña actual
    if not current_user.check_password(current_password):
        flash("La contraseña actual es incorrecta", "danger")
        return redirect(url_for('main.user_profile'))
    
    # Verificar que las nuevas contraseñas coincidan
    if new_password != confirm_password:
        flash("Las contraseñas nuevas no coinciden", "danger")
        return redirect(url_for('main.user_profile'))
    
    # Verificar longitud mínima
    if len(new_password) < 4:
        flash("La contraseña debe tener al menos 4 caracteres", "danger")
        return redirect(url_for('main.user_profile'))
    
    # Cambiar contraseña
    current_user.set_password(new_password)
    db.session.commit()
    
    flash("Contraseña cambiada exitosamente", "success")
    return redirect(url_for('main.user_profile'))
