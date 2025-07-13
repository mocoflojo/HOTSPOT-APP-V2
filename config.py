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
    Si hay un error de configuración, lanza una ConfigError.
    """
    global ROUTER_IP, ROUTER_USER, ROUTER_PASSWORD, HOTSPOT_DNS

    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"El archivo de configuración '{CONFIG_FILE}' no se encontró.")
        
        config.read(CONFIG_FILE)
        
        if 'MIKROTIK' not in config:
            raise ValueError("La sección '[MIKROTIK]' no se encontró en el archivo de configuración.")
            
        ROUTER_IP = config['MIKROTIK']['IP']
        ROUTER_USER = config['MIKROTIK']['USER']
        ROUTER_PASSWORD = config['MIKROTIK']['PASSWORD']
        HOTSPOT_DNS = config['MIKROTIK']['HOTSPOT_DNS']

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"❌ Error crítico de configuración: {e}", file=sys.stderr)
        raise ConfigError(f"Error de configuración: {e}. Por favor, verifica '{CONFIG_FILE}'.")

# Cargar la configuración al importar el módulo
load_config()

# Puedes añadir otras configuraciones aquí si las tuvieras en config.ini, por ejemplo:
# if 'APP_SETTINGS' in config:
#     DEBUG_MODE = config['APP_SETTINGS'].getboolean('DEBUG_MODE', False)