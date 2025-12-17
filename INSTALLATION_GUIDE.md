# 📦 Guía de Instalación - HOTSPOT-APP

## 🎯 Para Instalar en un Cliente Nuevo

### Opción 1: Instalación Interactiva (Recomendada) ⭐

Esta es la forma más fácil y segura:

```bash
python install.py
```

El script te guiará paso a paso:
1. ✅ Solicita datos del router
2. ✅ Prueba la conexión (opcional)
3. ✅ Solicita credenciales del admin
4. ✅ Crea la base de datos
5. ✅ Configura todo automáticamente

**Ventajas:**
- No necesitas editar archivos manualmente
- Prueba la conexión antes de instalar
- Actualiza el config.ini automáticamente
- Validación de datos

---

### Opción 2: Instalación Manual

Si prefieres hacerlo manualmente:

#### Paso 1: Editar `config.ini`

```ini
[MIKROTIK]
ROUTER_IP = 192.168.88.1          # ← IP del router del cliente
ROUTER_USER = admin                # ← Usuario del router
ROUTER_PASSWORD = contraseña       # ← Contraseña del router

[HOTSPOT]
HOTSPOT_DNS = hotspot.local        # ← DNS del hotspot
```

#### Paso 2: Ejecutar Script de Inicialización

```bash
python init_db.py
```

Esto creará:
- ✅ Base de datos
- ✅ Router desde config.ini
- ✅ Usuario admin (usuario: admin, contraseña: admin)

#### Paso 3: Iniciar la Aplicación

```bash
python app.py
```

#### Paso 4: Acceder

- URL: `http://localhost:5000`
- Usuario: `admin`
- Contraseña: `admin`

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login

---

## 📋 Requisitos Previos

Antes de instalar, asegúrate de tener:

### 1. Python Instalado
```bash
python --version  # Debe ser Python 3.7 o superior
```

### 2. Dependencias Instaladas
```bash
pip install -r requirements.txt
```

### 3. Datos del Router del Cliente
- ✅ Dirección IP
- ✅ Usuario de acceso
- ✅ Contraseña
- ✅ DNS del hotspot (opcional, default: 10.5.50.1)

---

## 🔧 Proceso de Instalación Completo

### Para un Cliente Nuevo:

```bash
# 1. Clonar o copiar la aplicación
cd HOTSPOT-APP

# 2. Instalar dependencias (solo primera vez)
pip install -r requirements.txt

# 3. Ejecutar instalación interactiva
python install.py

# 4. Seguir las instrucciones en pantalla

# 5. Iniciar la aplicación
python app.py

# 6. Acceder desde el navegador
# http://localhost:5000
```

---

## 🎯 Flujo de Instalación Visual

```
┌─────────────────────────────────────┐
│  1. Copiar aplicación al servidor  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  2. Instalar dependencias Python   │
│     pip install -r requirements.txt│
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  3. Ejecutar: python install.py    │
│     (o editar config.ini manual)   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  4. Ingresar datos del router      │
│     - IP: 192.168.88.1             │
│     - Usuario: admin               │
│     - Contraseña: ********         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  5. Configurar usuario admin       │
│     - Usuario: admin               │
│     - Contraseña: ********         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  6. Sistema crea BD y configura    │
│     ✅ Base de datos               │
│     ✅ Router principal            │
│     ✅ Usuario admin               │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  7. Iniciar: python app.py         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  8. Acceder: http://localhost:5000│
│     Login y cambiar contraseña     │
└─────────────────────────────────────┘
```

---

## 📁 Archivos Importantes

### Después de la Instalación:

```
HOTSPOT-APP/
├── instance/
│   └── users.db          # ← Base de datos (SE CREA AUTOMÁTICAMENTE)
├── app_data/
│   ├── prices.json       # ← Precios (se crea al usar)
│   └── voucher_*.html    # ← Templates de tickets
├── config.ini            # ← Configuración de respaldo
├── app.py                # ← Aplicación principal
├── install.py            # ← Script de instalación
└── init_db.py            # ← Script de inicialización manual
```

---

## 🔄 Agregar Más Routers Después

Una vez instalado, puedes agregar más routers desde la interfaz web:

1. Login en la aplicación
2. Ve a **"Gestión de Routers"** en el menú
3. Click en **"Agregar Router"**
4. Completa el formulario
5. ¡Listo!

---

## ⚠️ Notas Importantes

### Para el Instalador:

1. **config.ini es solo para el primer router**
   - Después puedes agregar más desde la web
   - El config.ini sirve como fallback

2. **Credenciales por defecto:**
   - Usuario: `admin`
   - Contraseña: `admin`
   - ⚠️ **CAMBIAR DESPUÉS DEL PRIMER LOGIN**

3. **Base de datos:**
   - Se crea automáticamente en `instance/users.db`
   - Hacer backup regularmente
   - No borrar este archivo

4. **Conexión al router:**
   - Verificar que el servidor tenga acceso a la IP del router
   - Probar conexión antes de instalar

---

## 🆘 Solución de Problemas

### Error: "No se puede conectar al router"
- Verificar IP del router
- Verificar usuario y contraseña
- Verificar que el servidor tenga acceso a la red del router

### Error: "Base de datos ya existe"
- Si quieres reinstalar, borrar `instance/users.db`
- O usar el script de instalación que pregunta si quieres sobrescribir

### Error: "Módulo no encontrado"
- Ejecutar: `pip install -r requirements.txt`

---

## 📞 Soporte

Para más información o problemas durante la instalación, contacta al equipo de desarrollo.

---

**Versión:** 2.1
**Última actualización:** Diciembre 2025
