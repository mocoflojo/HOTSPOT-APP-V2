import routeros_api
import sys
import re
from config import ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD

def get_api_connection(router=None):
    """
    Establece y devuelve una conexión a la API del router MikroTik.
    
    Args:
        router: Objeto Router o None. Si es None, usa el router activo de la sesión.
    
    Devuelve None si la conexión falla.
    """
    try:
        # Si no se proporciona un router, intentar obtener el activo
        if router is None:
            try:
                from flask import session, has_request_context
                from database import Router
                
                # Solo intentar obtener de sesión si estamos en un contexto de request
                if has_request_context():
                    router_id = session.get('active_router_id')
                    if router_id:
                        router = Router.query.get(router_id)
                    
                    # Si no hay en sesión, usar el router por defecto
                    if not router:
                        router = Router.query.filter_by(is_default=True, is_active=True).first()
                    
                    # Si no hay default, usar el primero activo
                    if not router:
                        router = Router.query.filter_by(is_active=True).first()
            except Exception as e:
                # Si falla la importación o query, usar config.ini como fallback
                print(f"⚠️  Usando configuración de config.ini como fallback: {e}", file=sys.stderr)
                router = None
        
        # Si tenemos un objeto router, usar sus credenciales
        if router and hasattr(router, 'ip'):
            ip = router.ip
            username = router.username
            password = router.password
        else:
            # Fallback a config.ini
            ip = ROUTER_IP
            username = ROUTER_USER
            password = ROUTER_PASSWORD
        
        connection = routeros_api.RouterOsApiPool(
            ip,
            username=username,
            password=password,
            plaintext_login=True
        )
        api = connection.get_api()
        return api
    except Exception as e:
        print(f"❌ Error de conexión al router MikroTik: {e}", file=sys.stderr)
        return None

def parse_limit_uptime(time_str):
    """
    Parsea una cadena de tiempo de límite de actividad (ej. '30m', '1h') al formato de MikroTik.
    """
    time_str = str(time_str).strip().lower()
    if not time_str:
        return None
    if time_str.isnumeric():
        return f"{time_str}m"
    if time_str[-1] in ['d', 'h', 'm', 's', 'w']:
        return time_str
    return f"{time_str}m"

# --- Funciones de servicio de alto nivel para Hotspot User y Profile ---

def get_hotspot_users(filters=None):
    api = get_api_connection()
    if api:
        users = api.get_resource('/ip/hotspot/user').get(**(filters or {}))
        return users
    return None

def get_hotspot_user_by_id(user_id):
    api = get_api_connection()
    if api:
        users = api.get_resource('/ip/hotspot/user').get(id=user_id)
        if users:
            return users[0]
    return None

def add_hotspot_user(**kwargs):
    api = get_api_connection()
    if api:
        users_path = api.get_resource('/ip/hotspot/user')
        return users_path.add(**kwargs)
    return False

def set_hotspot_user(user_id, params):
    api = get_api_connection()
    if api:
        users_path = api.get_resource('/ip/hotspot/user')
        return users_path.set(id=user_id, **params)
    return False

def remove_hotspot_user(user_id):
    api = get_api_connection()
    if api:
        users_path = api.get_resource('/ip/hotspot/user')
        return users_path.remove(id=user_id)
    return False

def get_active_hotspot_users():
    api = get_api_connection()
    if api:
        active_users = api.get_resource('/ip/hotspot/active').get()
        return active_users
    return None

def disconnect_hotspot_user(user_id):
    api = get_api_connection()
    if api:
        active_users_path = api.get_resource('/ip/hotspot/active')
        return active_users_path.remove(id=user_id)
    return False

def get_hotspot_profiles():
    api = get_api_connection()
    if api:
        profiles = api.get_resource('/ip/hotspot/user/profile').get()
        return profiles
    return None

def get_hotspot_profile_by_id(profile_id):
    api = get_api_connection()
    if api:
        profiles = api.get_resource('/ip/hotspot/user/profile').get(id=profile_id)
        if profiles:
            return profiles[0]
    return None

def add_hotspot_profile(params):
    api = get_api_connection()
    if api:
        profiles_path = api.get_resource('/ip/hotspot/user/profile')
        return profiles_path.add(**params)
    return False

def set_hotspot_profile(profile_id, params):
    api = get_api_connection()
    if api:
        profiles_path = api.get_resource('/ip/hotspot/user/profile')
        return profiles_path.set(id=profile_id, **params)
    return False

def remove_hotspot_profile(profile_id):
    api = get_api_connection()
    if api:
        profiles_path = api.get_resource('/ip/hotspot/user/profile')
        return profiles_path.remove(id=profile_id)
    return False

# --- FUNCIÓN PARA OBTENER INFORMACIÓN DEL SISTEMA DEL ROUTER ---
def get_router_system_info():
    """
    Obtiene información del sistema del router MikroTik (recursos, identidad, hora).
    """
    api = get_api_connection()
    if api:
        try:
            # Inicializar todas las variables con valores por defecto 'N/A' o 0
            identity_name = 'N/A'
            cpu_load = 'N/A'
            memory_used_mb = 0
            memory_total_mb = 0
            hdd_used_mb = 0
            hdd_total_mb = 0
            board_name = 'N/A'
            version = 'N/A'
            build_time = 'N/A'
            current_date = 'N/A'
            current_time = 'N/A'
            uptime = 'N/A'

            resource_info = api.get_resource('/system/resource').get()
            routerboard_info = api.get_resource('/system/routerboard').get()
            clock_info = api.get_resource('/system/clock').get()
            identity_info = api.get_resource('/system/identity').get()

            if resource_info:
                resource = resource_info[0]
                
                cpu_load = resource.get('cpu-load', 'N/A')
                version = resource.get('version', 'N/A')
                build_time = resource.get('build-time', 'N/A')
                uptime = resource.get('uptime', 'N/A')

                # Manejo de memoria
                total_memory_raw = int(resource.get('total-memory', 0))
                free_memory_raw = int(resource.get('free-memory', 0))
                
                # Asegurar que la conversión a MB se haga de forma segura
                memory_total_mb = round(total_memory_raw / (1024 * 1024)) if total_memory_raw > 0 else 0
                memory_used_mb = round((total_memory_raw - free_memory_raw) / (1024 * 1024)) if total_memory_raw >= free_memory_raw else 0


                # Manejo de disco
                total_hdd_raw = int(resource.get('total-hdd-space', 0))
                free_hdd_raw = int(resource.get('free-hdd-space', 0))

                # Asegurar que la conversión a MB se haga de forma segura
                hdd_total_mb = round(total_hdd_raw / (1024 * 1024)) if total_hdd_raw > 0 else 0
                hdd_used_mb = round((total_hdd_raw - free_hdd_raw) / (1024 * 1024)) if total_hdd_raw >= free_hdd_raw else 0

            if routerboard_info:
                routerboard = routerboard_info[0]
                board_name = routerboard.get('board-name', 'N/A')

            if clock_info:
                clock = clock_info[0]
                current_date = clock.get('date', 'N/A')
                current_time = clock.get('time', 'N/A')
            
            if identity_info:
                identity = identity_info[0]
                identity_name = identity.get('name', 'N/A')

            return {
                'identity_name': identity_name,
                'cpu_load': cpu_load,
                'memory_used_mb': memory_used_mb,
                'memory_total_mb': memory_total_mb,
                'hdd_used_mb': hdd_used_mb,
                'hdd_total_mb': hdd_total_mb,
                'board_name': board_name,
                'version': version,
                'build_time': build_time,
                'current_date': current_date,
                'current_time': current_time,
                'uptime': uptime
            }
        except Exception as e:
            print(f"❌ Error al obtener información del sistema del router: {e}", file=sys.stderr)
            return None
    return None