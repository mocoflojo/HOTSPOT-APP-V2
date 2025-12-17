import configparser
import os
import sys

# --- RUTAS DE ARCHIVOS CONFIGURABLES ---
CONFIG_FILE = 'config.ini'

# --- Variables de configuración del router (se cargarán desde config.ini) ---
ROUTER_IP = None
ROUTER_USER = None
ROUTER_PASSWORD = None
HOTSPOT_DNS = None

class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    pass

def load_config():
    """
    Carga la configuración del router desde el archivo config.ini.
    Soporta tanto el formato antiguo (ROUTER_IP) como el nuevo (IP).
    Si hay un error de configuración, lanza una ConfigError.
    """
    global ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD, HOTSPOT_DNS

    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"El archivo de configuración '{CONFIG_FILE}' no se encontró.")
        
        config.read(CONFIG_FILE)
        
        if 'MIKROTIK' not in config and 'HOTSPOT' not in config:
            raise ValueError("No se encontraron las secciones de configuración en el archivo.")
        
        # Intentar formato nuevo primero (IP, USER, PASSWORD)
        # Si no existe, intentar formato antiguo (ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD)
        mikrotik_section = config['MIKROTIK'] if 'MIKROTIK' in config else {}
        hotspot_section = config['HOTSPOT'] if 'HOTSPOT' in config else {}
        
        # IP del router - soporta ambos formatos
        ROUTER_IP = (mikrotik_section.get('IP') or 
                    mikrotik_section.get('ROUTER_IP') or
                    None)
        
        # Usuario del router - soporta ambos formatos
        ROUTER_USER = (mikrotik_section.get('USER') or 
                      mikrotik_section.get('ROUTER_USER') or
                      None)
        
        # Contraseña del router - soporta ambos formatos
        # Nota: Puede ser vacía si el router no tiene contraseña
        ROUTER_PASSWORD = (mikrotik_section.get('PASSWORD', '') or 
                          mikrotik_section.get('ROUTER_PASSWORD', '') or
                          '')
        
        # DNS del hotspot - soporta ambos formatos y secciones
        HOTSPOT_DNS = (mikrotik_section.get('HOTSPOT_DNS') or 
                      hotspot_section.get('HOTSPOT_DNS') or
                      'hotspot.local')  # Default si no existe
        
        # Validar que se hayan cargado los valores esenciales
        if not ROUTER_IP:
            raise ValueError("No se encontró la IP del router (IP o ROUTER_IP)")
        if not ROUTER_USER:
            raise ValueError("No se encontró el usuario del router (USER o ROUTER_USER)")
        # ROUTER_PASSWORD puede ser vacío, no validamos

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"❌ Error crítico de configuración: {e}", file=sys.stderr)
        raise ConfigError(f"Error de configuración: {e}. Por favor, verifica '{CONFIG_FILE}'.")

# Cargar la configuración al importar el módulo
load_config()

# Puedes añadir otras configuraciones aquí si las tuvieras en config.ini, por ejemplo:
# if 'APP_SETTINGS' in config:
#     DEBUG_MODE = config['APP_SETTINGS'].getboolean('DEBUG_MODE', False)