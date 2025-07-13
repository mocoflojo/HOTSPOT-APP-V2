import routeros_api
import sys
import re
from config import ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD

def get_api_connection():
    """
    Establece y devuelve una conexión a la API del router MikroTik.
    Devuelve None si la conexión falla.
    """
    try:
        connection = routeros_api.RouterOsApiPool(
            ROUTER_IP,
            username=ROUTER_USER,
            password=ROUTER_PASSWORD,
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
        try: # Añadir un bloque try-except para manejar posibles errores en la lectura de recursos
            # Obtener información de recursos (CPU, memoria, disco)
            resource_info = api.get_resource('/system/resource').get()
            # Obtener información de identidad (modelo, versión)
            routerboard_info = api.get_resource('/system/routerboard').get()
            # Obtener la hora actual del sistema
            clock_info = api.get_resource('/system/clock').get()
            # Obtener el nombre de identidad
            identity_info = api.get_resource('/system/identity').get()

            # Inicializar variables con valores por defecto
            total_memory_mb = 0
            free_memory_mb = 0
            used_memory_mb = 0
            total_hdd_mb = 0
            free_hdd_mb = 0
            used_hdd_mb = 0
            cpu_load = 'N/A'
            board_name = 'N/A'
            version = 'N/A'
            build_time = 'N/A'
            current_date = 'N/A'
            current_time = 'N/A'
            uptime = 'N/A'
            identity_name = 'N/A'


            if resource_info:
                resource = resource_info[0]
                # Convertir bytes a MB
                total_memory_mb = round(int(resource.get('total-memory', 0)) / (1024 * 1024))
                free_memory_mb = round(int(resource.get('free-memory', 0)) / (1024 * 1024))
                used_memory_mb = total_memory_mb - free_memory_mb if total_memory_mb >= free_memory_mb else 0 # Asegurar que no sea negativo

                total_hdd_mb = round(int(resource.get('total-hdd-space', 0)) / (1024 * 1024))
                free_hdd_mb = round(int(resource.get('free-hdd-space', 0)) / (1024 * 1024))
                used_hdd_mb = total_hdd_mb - free_hdd_mb if total_hdd_mb >= free_hdd_mb else 0 # Asegurar que no sea negativo
                
                cpu_load = resource.get('cpu-load', 'N/A')
                version = resource.get('version', 'N/A')
                build_time = resource.get('build-time', 'N/A')
                uptime = resource.get('uptime', 'N/A')

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
                'memory_used_mb': used_memory_mb,
                'memory_total_mb': total_memory_mb,
                'hdd_used_mb': hdd_used_mb,
                'hdd_total_mb': total_hdd_mb,
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