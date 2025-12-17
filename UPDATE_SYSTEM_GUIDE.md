# 🔄 Sistema de Actualizaciones - HOTSPOT-APP V2.1

## 🎯 Opciones de Actualización

### Comparación Rápida:

| Método | Facilidad | Automático | Tamaño Descarga | Requiere Reinicio |
|--------|-----------|------------|-----------------|-------------------|
| **Git Pull** | ⭐⭐⭐⭐⭐ | ❌ No | ~1-5 MB | ✅ Sí |
| **Update Script** | ⭐⭐⭐⭐ | ✅ Sí | ~1-5 MB | ✅ Sí |
| **Auto-Update** | ⭐⭐⭐ | ✅ Sí | ~1-5 MB | ✅ Sí |
| **Reinstalar** | ⭐⭐ | ❌ No | ~80 MB | ✅ Sí |

---

## ⭐ Opción 1: Git Pull (Recomendada para Desarrollo)

### Ventajas:
- ✅ Muy fácil
- ✅ Solo descarga cambios
- ✅ Mantiene base de datos
- ✅ Rápido (~1-5 MB)

### Desventajas:
- ❌ Requiere Git instalado
- ❌ Manual

### Cómo Funciona:

**Para el Cliente:**
```powershell
# 1. Detener la aplicación (Ctrl+C)

# 2. Actualizar código
git pull origin main

# 3. Actualizar dependencias (si es necesario)
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Reiniciar aplicación
run.bat
```

### Crear Script de Actualización:

**`update.bat`:**
```batch
@echo off
echo ========================================
echo  HOTSPOT-APP - Actualización
echo ========================================
echo.

echo [1/4] Deteniendo aplicación...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Aplicación detenida
echo.

echo [2/4] Descargando actualizaciones...
git pull origin main
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo actualizar
    pause
    exit /b 1
)
echo [OK] Actualizaciones descargadas
echo.

echo [3/4] Actualizando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo [OK] Dependencias actualizadas
echo.

echo [4/4] Reiniciando aplicación...
echo.
echo ========================================
echo  Actualización Completada!
echo ========================================
echo.
echo La aplicación se reiniciará en 3 segundos...
timeout /t 3 /nobreak >nul

start run.bat
exit
```

---

## 🚀 Opción 2: Update Script con GitHub Releases

### Ventajas:
- ✅ No requiere Git
- ✅ Descarga solo lo necesario
- ✅ Mantiene base de datos
- ✅ Más profesional

### Desventajas:
- ❌ Requiere crear releases en GitHub
- ❌ Más complejo de implementar

### Cómo Funciona:

**1. Crear archivo de versión:**

**`version.json`:**
```json
{
    "version": "2.1.0",
    "release_date": "2025-12-17",
    "changelog": [
        "Gestión multi-router",
        "Separación de ventas por router",
        "Cambio de contraseña"
    ]
}
```

**2. Script de actualización automática:**

**`updater.py`:**
```python
import requests
import json
import os
import zipfile
import shutil
from packaging import version

GITHUB_API = "https://api.github.com/repos/mocoflojo/HOTSPOT-APP-V2/releases/latest"
CURRENT_VERSION_FILE = "version.json"

def get_current_version():
    """Obtiene la versión actual instalada"""
    try:
        with open(CURRENT_VERSION_FILE, 'r') as f:
            data = json.load(f)
            return data['version']
    except:
        return "0.0.0"

def get_latest_version():
    """Obtiene la última versión disponible en GitHub"""
    try:
        response = requests.get(GITHUB_API)
        if response.status_code == 200:
            data = response.json()
            return {
                'version': data['tag_name'].replace('v', ''),
                'download_url': data['zipball_url'],
                'changelog': data['body']
            }
    except Exception as e:
        print(f"Error al verificar actualizaciones: {e}")
    return None

def download_update(url, filename="update.zip"):
    """Descarga la actualización"""
    print("Descargando actualización...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                percent = (downloaded / total_size) * 100
                print(f"\rProgreso: {percent:.1f}%", end='')
    
    print("\n¡Descarga completada!")
    return filename

def apply_update(zip_file):
    """Aplica la actualización"""
    print("Aplicando actualización...")
    
    # Crear backup
    backup_dir = "backup_" + get_current_version()
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    
    # Backup de archivos importantes
    important_files = ['instance/users.db', 'config.ini', 'app_data/']
    os.makedirs(backup_dir, exist_ok=True)
    
    for file in important_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                shutil.copytree(file, os.path.join(backup_dir, file))
            else:
                os.makedirs(os.path.dirname(os.path.join(backup_dir, file)), exist_ok=True)
                shutil.copy2(file, os.path.join(backup_dir, file))
    
    # Extraer actualización
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("temp_update")
    
    # Copiar archivos nuevos (excepto los importantes)
    # ... (lógica de actualización)
    
    # Restaurar archivos importantes
    for file in important_files:
        backup_file = os.path.join(backup_dir, file)
        if os.path.exists(backup_file):
            if os.path.isdir(backup_file):
                if os.path.exists(file):
                    shutil.rmtree(file)
                shutil.copytree(backup_file, file)
            else:
                shutil.copy2(backup_file, file)
    
    print("¡Actualización aplicada!")

def check_for_updates():
    """Verifica si hay actualizaciones disponibles"""
    current = get_current_version()
    latest_info = get_latest_version()
    
    if not latest_info:
        print("No se pudo verificar actualizaciones")
        return
    
    latest = latest_info['version']
    
    print(f"Versión actual: {current}")
    print(f"Última versión: {latest}")
    
    if version.parse(latest) > version.parse(current):
        print("\n¡Hay una nueva versión disponible!")
        print(f"\nCambios:\n{latest_info['changelog']}")
        
        response = input("\n¿Deseas actualizar ahora? (s/n): ")
        if response.lower() == 's':
            zip_file = download_update(latest_info['download_url'])
            apply_update(zip_file)
            print("\n¡Actualización completada! Reinicia la aplicación.")
    else:
        print("\nEstás usando la última versión.")

if __name__ == "__main__":
    check_for_updates()
```

**3. Script batch para actualización:**

**`check_updates.bat`:**
```batch
@echo off
echo ========================================
echo  Verificando Actualizaciones...
echo ========================================
echo.

call venv\Scripts\activate.bat
python updater.py

pause
```

---

## 🔥 Opción 3: Auto-Update Integrado en la App

### Ventajas:
- ✅ Completamente automático
- ✅ Verifica al iniciar
- ✅ Notifica al usuario
- ✅ Muy profesional

### Desventajas:
- ❌ Más complejo de implementar
- ❌ Requiere servidor de actualizaciones

### Implementación:

**1. Agregar verificación al iniciar la app:**

**En `app.py`:**
```python
import threading
import requests
from packaging import version

CURRENT_VERSION = "2.1.0"
UPDATE_CHECK_URL = "https://api.github.com/repos/mocoflojo/HOTSPOT-APP-V2/releases/latest"

def check_for_updates_async():
    """Verifica actualizaciones en segundo plano"""
    try:
        response = requests.get(UPDATE_CHECK_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['tag_name'].replace('v', '')
            
            if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                print(f"\n⚠️  Nueva versión disponible: {latest_version}")
                print(f"   Versión actual: {CURRENT_VERSION}")
                print(f"   Descarga: {data['html_url']}\n")
    except:
        pass  # Silenciosamente falla si no hay internet

# Al iniciar la app
if __name__ == '__main__':
    # Verificar actualizaciones en segundo plano
    update_thread = threading.Thread(target=check_for_updates_async, daemon=True)
    update_thread.start()
    
    # Iniciar la aplicación normalmente
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**2. Notificación en el dashboard:**

**En `routes.py`:**
```python
def get_update_info():
    """Obtiene información de actualizaciones"""
    try:
        response = requests.get(UPDATE_CHECK_URL, timeout=3)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['tag_name'].replace('v', '')
            
            if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                return {
                    'available': True,
                    'version': latest_version,
                    'url': data['html_url'],
                    'changelog': data['body']
                }
    except:
        pass
    
    return {'available': False}

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # ... código existente ...
    
    update_info = get_update_info()
    
    return render_template('dashboard.html',
                          # ... otros parámetros ...
                          update_info=update_info)
```

**3. Banner de actualización en el template:**

**En `templates/dashboard.html`:**
```html
{% if update_info.available %}
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
    <div class="flex items-center justify-between">
        <div class="flex items-center">
            <i class="fas fa-download text-blue-500 text-2xl mr-3"></i>
            <div>
                <h3 class="text-lg font-semibold text-blue-800">
                    ¡Nueva versión disponible!
                </h3>
                <p class="text-sm text-blue-700">
                    Versión {{ update_info.version }} - 
                    <a href="{{ update_info.url }}" target="_blank" 
                       class="underline font-semibold">
                        Descargar ahora
                    </a>
                </p>
            </div>
        </div>
        <button onclick="this.parentElement.parentElement.remove()" 
                class="text-blue-500 hover:text-blue-700">
            <i class="fas fa-times"></i>
        </button>
    </div>
</div>
{% endif %}
```

---

## 📦 Opción 4: Sistema de Parches

### Ventajas:
- ✅ Descarga mínima (solo archivos cambiados)
- ✅ Muy rápido
- ✅ Mantiene todo

### Desventajas:
- ❌ Complejo de implementar
- ❌ Requiere servidor de parches

### Cómo Funciona:

**1. Crear archivo de parche:**

**`create_patch.py`:**
```python
import hashlib
import json
import os

def get_file_hash(filepath):
    """Calcula el hash de un archivo"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def create_patch_manifest(old_version, new_version):
    """Crea un manifiesto de cambios"""
    changes = {
        'from_version': old_version,
        'to_version': new_version,
        'files': {
            'modified': [],
            'added': [],
            'deleted': []
        }
    }
    
    # Comparar archivos y detectar cambios
    # ... lógica de comparación ...
    
    with open(f'patch_{old_version}_to_{new_version}.json', 'w') as f:
        json.dump(changes, f, indent=2)
    
    return changes
```

**2. Aplicar parche:**

**`apply_patch.py`:**
```python
import json
import requests
import os

def apply_patch(patch_url):
    """Descarga y aplica un parche"""
    # Descargar manifiesto
    response = requests.get(patch_url)
    patch_data = response.json()
    
    # Descargar solo archivos modificados/nuevos
    for file in patch_data['files']['modified'] + patch_data['files']['added']:
        download_file(file['url'], file['path'])
    
    # Eliminar archivos borrados
    for file in patch_data['files']['deleted']:
        os.remove(file['path'])
    
    print("¡Parche aplicado!")
```

---

## 💡 Recomendación por Escenario

### Para Clientes Técnicos:
**Usar: Git Pull + update.bat**
- Muy fácil
- Solo descarga cambios
- Mantiene todo

### Para Clientes No Técnicos:
**Usar: Auto-Update Integrado**
- Automático
- Notifica al usuario
- Profesional

### Para Desarrollo/Testing:
**Usar: Git Pull manual**
- Control total
- Rápido
- Flexible

---

## 🎯 Mi Recomendación: Híbrido

### Implementar 2 sistemas:

**1. Para Desarrollo (Git Pull):**
```powershell
# Cliente ejecuta:
update.bat
```

**2. Para Producción (Auto-Update):**
- Notificación en dashboard
- Link de descarga
- Instrucciones claras

### Ventajas:
- ✅ Fácil para desarrollo
- ✅ Profesional para producción
- ✅ Flexible
- ✅ No requiere infraestructura compleja

---

## 📝 Implementación Recomendada

### Paso 1: Crear `update.bat`

```batch
@echo off
echo Actualizando HOTSPOT-APP...
taskkill /F /IM python.exe >nul 2>&1
git pull origin main
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo ¡Actualización completada!
timeout /t 3
start run.bat
```

### Paso 2: Agregar verificación en `app.py`

```python
# Al iniciar, verificar actualizaciones
threading.Thread(target=check_for_updates_async, daemon=True).start()
```

### Paso 3: Agregar banner en dashboard

```html
<!-- Mostrar si hay actualización disponible -->
{% if update_info.available %}
<div class="alert alert-info">
    Nueva versión disponible: {{ update_info.version }}
    <a href="{{ update_info.url }}">Descargar</a>
</div>
{% endif %}
```

---

## 🔄 Flujo de Actualización Completo

### Para el Cliente:

**Opción A (Automática):**
```
1. Cliente abre la aplicación
2. Ve notificación de actualización
3. Click en "Descargar"
4. Descarga update.zip
5. Ejecuta update.bat
6. ¡Listo!
```

**Opción B (Manual):**
```
1. Cliente ejecuta: update.bat
2. Script actualiza automáticamente
3. Reinicia la aplicación
4. ¡Listo!
```

---

## ✅ Archivos que NO se Sobrescriben

Al actualizar, estos archivos se mantienen:
- ✅ `instance/users.db` (Base de datos)
- ✅ `config.ini` (Configuración)
- ✅ `app_data/` (Datos de la aplicación)
- ✅ `venv/` (Entorno virtual)

---

## 📊 Tamaño de Descargas

| Método | Primera Instalación | Actualización |
|--------|---------------------|---------------|
| Completo | ~80 MB | ~80 MB |
| Git Pull | ~10 MB | ~1-5 MB |
| Parches | ~10 MB | ~100 KB - 2 MB |

---

**Recomendación Final:** Usa `update.bat` con Git Pull. Es simple, efectivo y solo descarga lo necesario.
