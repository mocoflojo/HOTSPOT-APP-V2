# 🔐 Guía de Sistemas de Licencias para HOTSPOT-APP

## 🎯 Opciones de Licenciamiento (De Más Sencilla a Más Compleja)

---

## 📋 Comparación Rápida

| Opción | Complejidad | Seguridad | Costo | Requiere Internet | Recomendado Para |
|--------|-------------|-----------|-------|-------------------|------------------|
| **1. Código de Activación Simple** | ⭐ | ⭐⭐ | Gratis | ❌ No | Pruebas, clientes confiables |
| **2. Archivo de Licencia** | ⭐⭐ | ⭐⭐⭐ | Gratis | ❌ No | Pequeños negocios |
| **3. Licencia con Fecha de Expiración** | ⭐⭐ | ⭐⭐⭐ | Gratis | ❌ No | Suscripciones anuales |
| **4. Licencia por Hardware (HWID)** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Gratis | ❌ No | Evitar piratería |
| **5. Servidor de Validación Online** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $5-20/mes | ✅ Sí | Máxima seguridad |
| **6. Plataforma de Licencias (Gumroad/Paddle)** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 5-10% comisión | ✅ Sí | Venta automatizada |

---

## 1️⃣ Código de Activación Simple (MÁS SENCILLA)

### ✅ Ventajas:
- Muy fácil de implementar (30 minutos)
- No requiere internet
- Sin costos adicionales
- Fácil de entender para el cliente

### ❌ Desventajas:
- Fácil de piratear (el código está en el ejecutable)
- No hay control de cuántas veces se usa
- No hay expiración automática

### 🔧 Cómo Funciona:

1. **Generas un código único para cada cliente**
2. **El cliente ingresa el código al instalar**
3. **La app verifica el código y se activa**

### 💻 Implementación:

```python
# license.py
import hashlib

# Tu clave secreta (cámbiala por algo único)
SECRET_KEY = "tu_clave_secreta_super_larga_12345"

def generate_license_key(client_name):
    """Genera una clave de licencia para un cliente"""
    data = f"{client_name}{SECRET_KEY}"
    hash_object = hashlib.sha256(data.encode())
    license_key = hash_object.hexdigest()[:16].upper()
    return license_key

def validate_license_key(client_name, license_key):
    """Valida una clave de licencia"""
    expected_key = generate_license_key(client_name)
    return license_key == expected_key

# Ejemplo de uso:
# Para generar una licencia para "Juan Perez":
# license = generate_license_key("Juan Perez")
# print(f"Licencia: {license}")  # Ej: A3F2E1D4C5B6A7F8
```

**Uso:**
```python
# Al iniciar la app
stored_license = load_license_from_file()  # Cargar de config.ini
client_name = "Juan Perez"

if validate_license_key(client_name, stored_license):
    print("Licencia válida")
else:
    print("Licencia inválida - Contacta al vendedor")
    exit()
```

---

## 2️⃣ Archivo de Licencia (RECOMENDADA PARA EMPEZAR)

### ✅ Ventajas:
- Más seguro que código simple
- Puede incluir información adicional (fecha, cliente, features)
- Fácil de distribuir
- No requiere internet

### ❌ Desventajas:
- El archivo puede ser copiado
- Requiere un poco más de código

### 🔧 Cómo Funciona:

1. **Generas un archivo `license.key` para cada cliente**
2. **El archivo contiene datos encriptados**
3. **La app lee y valida el archivo al iniciar**

### 💻 Implementación:

```python
# license_manager.py
import json
import base64
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

class LicenseManager:
    def __init__(self, secret_key=None):
        # Genera una clave o usa una existente
        if secret_key is None:
            self.key = Fernet.generate_key()
        else:
            self.key = secret_key.encode()
        self.cipher = Fernet(self.key)
    
    def generate_license(self, client_name, expiration_days=365, features=None):
        """Genera un archivo de licencia"""
        license_data = {
            "client": client_name,
            "issued_date": datetime.now().isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
            "features": features or ["basic"],
            "version": "2.1"
        }
        
        # Encriptar datos
        json_data = json.dumps(license_data)
        encrypted = self.cipher.encrypt(json_data.encode())
        
        # Guardar en archivo
        with open("license.key", "wb") as f:
            f.write(encrypted)
        
        return license_data
    
    def validate_license(self, license_file="license.key"):
        """Valida un archivo de licencia"""
        try:
            # Leer archivo
            with open(license_file, "rb") as f:
                encrypted = f.read()
            
            # Desencriptar
            decrypted = self.cipher.decrypt(encrypted)
            license_data = json.loads(decrypted)
            
            # Verificar expiración
            expiration = datetime.fromisoformat(license_data["expiration_date"])
            if datetime.now() > expiration:
                return False, "Licencia expirada"
            
            return True, license_data
        
        except Exception as e:
            return False, f"Licencia inválida: {str(e)}"

# Uso:
# Para generar licencia:
# manager = LicenseManager(secret_key="TU_CLAVE_SECRETA_AQUI")
# manager.generate_license("Juan Perez", expiration_days=365)

# Para validar:
# valid, data = manager.validate_license()
# if valid:
#     print(f"Licencia válida para: {data['client']}")
# else:
#     print(f"Error: {data}")
```

**Integración en app.py:**
```python
from license_manager import LicenseManager

# Al iniciar la app
license_manager = LicenseManager(secret_key="TU_CLAVE_SECRETA")
valid, result = license_manager.validate_license()

if not valid:
    print(f"ERROR: {result}")
    print("Contacta al vendedor para obtener una licencia válida")
    exit()

print(f"Licencia válida para: {result['client']}")
print(f"Expira: {result['expiration_date']}")
```

---

## 3️⃣ Licencia con Fecha de Expiración

### ✅ Ventajas:
- Control de suscripciones anuales
- Genera ingresos recurrentes
- Fácil de renovar

### 💻 Ya está incluido en la Opción 2

---

## 4️⃣ Licencia por Hardware (HWID) - Más Segura

### ✅ Ventajas:
- La licencia solo funciona en UNA computadora
- Evita que copien la licencia a otras PCs
- Muy difícil de piratear

### ❌ Desventajas:
- Si el cliente cambia de PC, necesita nueva licencia
- Más complejo de implementar

### 💻 Implementación:

```python
# hwid_license.py
import uuid
import platform
import hashlib
import json
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

class HWIDLicenseManager:
    def __init__(self, secret_key):
        self.key = secret_key.encode()
        self.cipher = Fernet(self.key)
    
    def get_hardware_id(self):
        """Obtiene un ID único del hardware"""
        # Combinar varios identificadores del sistema
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0,2*6,2)][::-1])
        
        system_info = f"{platform.node()}{mac}{platform.system()}"
        hwid = hashlib.sha256(system_info.encode()).hexdigest()[:16]
        return hwid
    
    def generate_license(self, client_name, hwid, expiration_days=365):
        """Genera licencia atada a un HWID específico"""
        license_data = {
            "client": client_name,
            "hwid": hwid,
            "issued_date": datetime.now().isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
        }
        
        json_data = json.dumps(license_data)
        encrypted = self.cipher.encrypt(json_data.encode())
        
        with open("license.key", "wb") as f:
            f.write(encrypted)
        
        return license_data
    
    def validate_license(self):
        """Valida que la licencia coincida con este hardware"""
        try:
            with open("license.key", "rb") as f:
                encrypted = f.read()
            
            decrypted = self.cipher.decrypt(encrypted)
            license_data = json.loads(decrypted)
            
            # Verificar HWID
            current_hwid = self.get_hardware_id()
            if license_data["hwid"] != current_hwid:
                return False, "Esta licencia no es válida para esta computadora"
            
            # Verificar expiración
            expiration = datetime.fromisoformat(license_data["expiration_date"])
            if datetime.now() > expiration:
                return False, "Licencia expirada"
            
            return True, license_data
        
        except Exception as e:
            return False, f"Licencia inválida: {str(e)}"

# Proceso:
# 1. Cliente te envía su HWID (lo obtienes con get_hardware_id())
# 2. Generas licencia con ese HWID
# 3. Envías license.key al cliente
# 4. Solo funciona en esa PC
```

---

## 5️⃣ Servidor de Validación Online (MÁS SEGURA)

### ✅ Ventajas:
- Máxima seguridad
- Control total de licencias activas
- Puedes desactivar licencias remotamente
- Estadísticas de uso

### ❌ Desventajas:
- Requiere servidor (costo mensual)
- Cliente necesita internet
- Más complejo de implementar

### 🔧 Arquitectura:

```
Cliente (HOTSPOT-APP)
    ↓
    Envía: license_key + hwid
    ↓
Servidor API (Flask/FastAPI)
    ↓
    Verifica en Base de Datos
    ↓
    Responde: válido/inválido
```

### 💻 Servidor Simple (Flask):

```python
# license_server.py
from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Base de datos de licencias
def init_db():
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (license_key TEXT PRIMARY KEY,
                  client_name TEXT,
                  hwid TEXT,
                  expiration_date TEXT,
                  is_active INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/validate', methods=['POST'])
def validate_license():
    data = request.json
    license_key = data.get('license_key')
    hwid = data.get('hwid')
    
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    
    c.execute('''SELECT * FROM licenses 
                 WHERE license_key=? AND hwid=? AND is_active=1''',
              (license_key, hwid))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        expiration = datetime.fromisoformat(result[3])
        if datetime.now() < expiration:
            return jsonify({"valid": True, "client": result[1]})
    
    return jsonify({"valid": False, "error": "Licencia inválida"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)
```

**Cliente:**
```python
import requests

def validate_online_license(license_key, hwid):
    try:
        response = requests.post(
            "https://tu-servidor.com/validate",
            json={"license_key": license_key, "hwid": hwid},
            timeout=5
        )
        return response.json()
    except:
        return {"valid": False, "error": "No se pudo conectar al servidor"}
```

---

## 6️⃣ Plataformas de Licencias (MÁS FÁCIL PARA VENDER)

### Servicios Recomendados:

1. **Gumroad** (https://gumroad.com)
   - ✅ Muy fácil de usar
   - ✅ Genera códigos de licencia automáticamente
   - ✅ Procesa pagos
   - ❌ Comisión: 10% + $0.30 por venta

2. **Paddle** (https://paddle.com)
   - ✅ Maneja impuestos internacionales
   - ✅ API completa
   - ❌ Comisión: 5% + $0.50

3. **LemonSqueezy** (https://lemonsqueezy.com)
   - ✅ Muy popular para software
   - ✅ Fácil integración
   - ❌ Comisión: 5%

### Integración con Gumroad (Ejemplo):

```python
import requests

def validate_gumroad_license(license_key, product_id):
    response = requests.post(
        "https://api.gumroad.com/v2/licenses/verify",
        data={
            "product_id": product_id,
            "license_key": license_key
        }
    )
    
    data = response.json()
    return data.get("success", False)
```

---

## 🎯 MI RECOMENDACIÓN PARA TI

### Para Empezar (1-10 clientes):
**Opción 2: Archivo de Licencia**
- Fácil de implementar
- Seguro suficiente
- Sin costos adicionales
- No requiere internet

### Para Crecer (10-50 clientes):
**Opción 4: Licencia por Hardware (HWID)**
- Evita piratería
- Profesional
- Control de instalaciones

### Para Escalar (50+ clientes):
**Opción 5 o 6: Servidor Online o Plataforma**
- Máximo control
- Venta automatizada
- Estadísticas

---

## 📝 Flujo de Trabajo Recomendado

### 1. Venta:
```
Cliente interesado
    ↓
Envía pago (PayPal, transferencia, etc.)
    ↓
Tú generas licencia
    ↓
Envías license.key por email
```

### 2. Instalación:
```
Cliente descarga HOTSPOT-APP.exe
    ↓
Copia license.key a la carpeta de la app
    ↓
Ejecuta HOTSPOT-APP.exe
    ↓
App valida licencia
    ↓
¡Funciona!
```

### 3. Renovación:
```
Licencia expira
    ↓
App muestra mensaje
    ↓
Cliente renueva (paga)
    ↓
Generas nueva license.key
    ↓
Cliente reemplaza archivo
```

---

## 💰 Precios Sugeridos

- **Licencia Perpetua:** $200-500 USD
- **Licencia Anual:** $100-200 USD/año
- **Licencia Mensual:** $20-50 USD/mes
- **Soporte Técnico:** +$50-100 USD/año

---

## 🚀 Próximos Pasos

1. **Decide qué opción usar** (recomiendo empezar con Opción 2)
2. **Implementa el sistema de licencias**
3. **Prueba con un cliente de confianza**
4. **Ajusta según necesites**
5. **Escala cuando tengas más clientes**

---

**¿Quieres que implemente alguna de estas opciones en tu app?** 🔐
