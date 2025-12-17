# 🌐 HOTSPOT-APP V2.1

Sistema de Gestión Multi-Router de Hotspot para MikroTik - Versión Mejorada

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-2.1.0-orange.svg)

## 📋 Descripción

Aplicación web completa para la gestión de usuarios Hotspot en **múltiples routers MikroTik** desde una sola interfaz. Incluye generación de vouchers, gestión de perfiles, reportes de ventas separados por router, cambio de contraseña y más.

### ✨ Características Principales

#### 🆕 **Nuevas Funcionalidades V2.1**

- 🌐 **Gestión Multi-Router**: Administra múltiples routers MikroTik desde una sola aplicación
- 🔄 **Cambio Dinámico**: Cambia entre routers con un solo click
- 📊 **Separación de Ventas**: Cada router tiene sus propias estadísticas independientes
- 🔐 **Cambio de Contraseña**: Los usuarios pueden cambiar su contraseña desde la interfaz
- 🚀 **Instalación Interactiva**: Script de instalación guiado paso a paso

#### ⭐ **Funcionalidades Core**

- 🎫 **Generación de Vouchers**: Crea códigos de acceso PIN o Usuario/Contraseña
- 👥 **Gestión de Usuarios**: Administra usuarios del hotspot
- 📊 **Perfiles Personalizables**: Configura límites de velocidad y tiempo
- 💰 **Reportes de Ventas**: Visualiza estadísticas y gráficos por router
- 🖨️ **Impresión de Vouchers**: Plantillas personalizables para imprimir
- ⏱️ **Modos de Expiración**: Scripts predefinidos y personalizados
- 🔐 **Sistema de Login**: Autenticación segura para administradores
- 📱 **Diseño Responsivo**: Interfaz adaptable a móviles y tablets

---

## 🖥️ Requisitos del Sistema

### Windows 10/11

- **Python 3.8 o superior** (Recomendado: Python 3.13)
- **Git** (para clonar el repositorio)
- **Uno o más Routers MikroTik** con API habilitada
- **Navegador Web** moderno (Chrome, Firefox, Edge)

---

## 🚀 Instalación Rápida (Recomendada)

### Opción 1: Instalación Automática ⚡

```powershell
# 1. Clonar el repositorio
git clone https://github.com/mocoflojo/HOTSPOT-APP-V2.git
cd HOTSPOT-APP-V2

# 2. Ejecutar instalación automática
install.bat

# El script te guiará para:
# - Instalar dependencias
# - Configurar el router
# - Crear usuario administrador
# - Inicializar la base de datos

# 3. Ejecutar la aplicación
run.bat
```

¡Listo! La aplicación se abrirá automáticamente en tu navegador.

---

## 📖 Instalación Manual Detallada

### Paso 1: Instalar Python

1. Descarga Python desde: https://www.python.org/downloads/
2. **IMPORTANTE**: Durante la instalación, marca la opción **"Add Python to PATH"**
3. Verifica la instalación:
   ```powershell
   python --version
   ```

### Paso 2: Clonar el Repositorio

```powershell
# Navega a la carpeta donde quieres instalar
cd C:\Users\TuUsuario\Desktop

# Clona el repositorio
git clone https://github.com/mocoflojo/HOTSPOT-APP-V2.git

# Entra a la carpeta del proyecto
cd HOTSPOT-APP-V2
```

**Alternativa sin Git**: Descarga el ZIP desde GitHub y descomprímelo.

### Paso 3: Ejecutar Script de Instalación

```powershell
# Ejecuta el instalador interactivo
install.bat
```

El script automáticamente:
- ✅ Crea entorno virtual
- ✅ Instala dependencias
- ✅ Configura el router
- ✅ Crea base de datos
- ✅ Crea usuario administrador

### Paso 4: Ejecutar la Aplicación

```powershell
run.bat
```

La aplicación estará disponible en: **http://localhost:5000**

---

## 🎮 Uso de la Aplicación

### Iniciar la Aplicación

**Forma más fácil:**
```powershell
run.bat
```
El navegador se abrirá automáticamente.

**Alternativa manual:**
```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar aplicación
python app.py
```

### Primer Login

- **Usuario**: El que configuraste durante la instalación (default: `admin`)
- **Contraseña**: La que configuraste durante la instalación (default: `admin`)

⚠️ **IMPORTANTE**: Cambia la contraseña por defecto desde tu perfil.

---

## 🌐 Gestión Multi-Router

### Agregar un Nuevo Router

1. Inicia sesión en la aplicación
2. Ve a **"Gestión de Routers"** en el menú lateral
3. Click en **"Agregar Router"**
4. Completa el formulario:
   - Nombre del router
   - IP del router
   - Usuario y contraseña
   - DNS del hotspot
5. Click en **"Guardar Router"**

### Cambiar Entre Routers

**Opción 1 - Desde el Navbar:**
- Click en el selector de router (esquina superior derecha)
- Selecciona el router deseado

**Opción 2 - Desde Gestión de Routers:**
- Ve a "Gestión de Routers"
- Click en **"Conectar"** en el router deseado

### Características Multi-Router

- ✅ **Ventas Separadas**: Cada router tiene sus propias ventas
- ✅ **Estadísticas Independientes**: Dashboard y reportes por router
- ✅ **Cambio Instantáneo**: Cambia entre routers sin reiniciar
- ✅ **Router por Defecto**: Configura cuál router se carga al iniciar
- ✅ **Persistencia**: El sistema recuerda tu último router usado

---

## 🔐 Gestión de Perfil de Usuario

### Cambiar Contraseña

1. Click en **"Perfil"** en el sidebar
2. Completa el formulario:
   - Contraseña actual
   - Nueva contraseña
   - Confirmar nueva contraseña
3. Click en **"Cambiar Contraseña"**

### Requisitos de Contraseña

- Mínimo 4 caracteres
- Debe coincidir con la confirmación
- Requiere contraseña actual para cambiar

---

## 📁 Estructura del Proyecto

```
HOTSPOT-APP-V2/
├── app.py                          # Aplicación principal
├── auth.py                         # Autenticación
├── config.py                       # Configuración
├── config.ini                      # Configuración del MikroTik (backup)
├── database.py                     # Modelos de base de datos
├── mikrotik_service.py             # Servicios de MikroTik API
├── routes.py                       # Rutas principales
├── router_routes.py                # 🆕 Rutas de gestión de routers
├── utils.py                        # Utilidades
├── install.py                      # 🆕 Script de instalación interactiva
├── init_db.py                      # 🆕 Inicialización de base de datos
├── install.bat                     # 🆕 Instalación automatizada (Windows)
├── run.bat                         # Ejecutar aplicación (Windows)
├── requirements.txt                # Dependencias Python
├── templates/                      # Plantillas HTML
│   ├── base.html                   # 🔄 Template base (actualizado)
│   ├── dashboard.html
│   ├── users.html
│   ├── profiles.html
│   ├── generate.html
│   ├── reports.html
│   ├── routers.html                # 🆕 Gestión de routers
│   ├── edit_router.html            # 🆕 Editar router
│   ├── user_profile.html           # 🆕 Perfil de usuario
│   └── ...
├── app_data/                       # Datos de la aplicación
│   ├── prices.json
│   ├── expiration_scripts.json
│   └── voucher_template.html
├── instance/                       # Base de datos
│   └── users.db                    # 🔄 BD con soporte multi-router
└── docs/                           # 🆕 Documentación
    ├── MULTI_ROUTER_DOCS.md
    ├── ROUTER_SEPARATION_DOCS.md
    ├── PASSWORD_CHANGE_DOCS.md
    ├── INSTALLATION_GUIDE.md
    └── INSTALLATION_FLOW.md
```

---

## 🛠️ Mantenimiento

### Backup de la Base de Datos

```powershell
# Copia el archivo de base de datos
copy instance\users.db instance\users.db.backup
```

### Actualizar Dependencias

```powershell
pip install --upgrade -r requirements.txt
```

### Reinstalar desde Cero

```powershell
# Elimina la base de datos
del instance\users.db

# Ejecuta la instalación
install.bat
```

---

## 🔧 Solución de Problemas

### Error: "No se puede conectar al router"

- Verifica que la IP del router sea correcta
- Asegúrate de que el servicio API esté habilitado en el MikroTik
- Verifica que el firewall no bloquee el puerto 8728
- Usa el botón "Test" en Gestión de Routers para probar la conexión

### Error: "No hay router activo"

- Ve a "Gestión de Routers"
- Asegúrate de tener al menos un router activo
- Selecciona un router para conectarte

### Error: "ModuleNotFoundError"

```powershell
# Asegúrate de tener el entorno virtual activado
.\venv\Scripts\Activate.ps1

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "Access Denied" al activar entorno virtual

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Olvidé mi contraseña

Actualmente no hay recuperación de contraseña. Opciones:

1. **Crear nuevo usuario** desde la base de datos
2. **Reinstalar** la aplicación (perderás datos)
3. **Contactar** al administrador del sistema

---

## 📝 Configuración Avanzada

### Cambiar el Puerto de la Aplicación

Edita `app.py` y cambia:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia 5000 por el puerto deseado
```

### Habilitar Acceso desde Otras Computadoras

La aplicación ya está configurada con `host='0.0.0.0'`. Accede usando:
```
http://IP_DE_TU_PC:5000
```

### Configurar Router por Defecto

1. Ve a "Gestión de Routers"
2. Edita el router deseado
3. Marca "Establecer como router por defecto"
4. Guarda los cambios

---

## 🆕 Novedades de la Versión 2.1

### Gestión Multi-Router

- ✅ Administra múltiples routers desde una sola interfaz
- ✅ Cambio instantáneo entre routers
- ✅ Cada router con sus propias ventas y estadísticas
- ✅ Selector de router en el navbar
- ✅ Router por defecto configurable

### Separación de Ventas

- ✅ Ventas completamente separadas por router
- ✅ Dashboard filtrado por router activo
- ✅ Reportes independientes por router
- ✅ Gráficos y estadísticas por router

### Gestión de Usuario

- ✅ Página de perfil de usuario
- ✅ Cambio de contraseña desde la interfaz
- ✅ Validaciones de seguridad
- ✅ Información del router activo en el perfil

### Instalación Mejorada

- ✅ Script de instalación interactivo (`install.py`)
- ✅ Instalación automatizada con `install.bat`
- ✅ Verificación automática de base de datos
- ✅ Configuración guiada paso a paso

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👨‍💻 Autor

**mocoflojo**

- GitHub: [@mocoflojo](https://github.com/mocoflojo)
- Repositorio: [HOTSPOT-APP-V2](https://github.com/mocoflojo/HOTSPOT-APP-V2)

---

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de **Solución de Problemas**
2. Consulta la **documentación** en la carpeta `docs/`
3. Abre un **Issue** en GitHub
4. Consulta la documentación de MikroTik: https://wiki.mikrotik.com/

---

## 🎯 Roadmap

- [x] Soporte para múltiples routers MikroTik ✅ **V2.1**
- [x] Separación de ventas por router ✅ **V2.1**
- [x] Cambio de contraseña desde interfaz ✅ **V2.1**
- [ ] API REST para integraciones
- [ ] Notificaciones por email
- [ ] Modo oscuro en la interfaz
- [ ] Exportación de reportes a PDF/Excel
- [ ] Autenticación de dos factores (2FA)
- [ ] Recuperación de contraseña por email

---

## 📚 Documentación Adicional

- [Guía de Instalación Completa](INSTALLATION_GUIDE.md)
- [Flujo de Instalación](INSTALLATION_FLOW.md)
- [Documentación Multi-Router](MULTI_ROUTER_DOCS.md)
- [Separación de Ventas por Router](ROUTER_SEPARATION_DOCS.md)
- [Cambio de Contraseña](PASSWORD_CHANGE_DOCS.md)

---

## ⭐ Agradecimientos

- MikroTik por su excelente API
- Flask y su comunidad
- Todos los contribuidores del proyecto

---

## 📊 Estadísticas del Proyecto

- **Versión**: 2.1.0
- **Lenguaje**: Python 3.8+
- **Framework**: Flask 3.1.1
- **Base de Datos**: SQLite
- **Líneas de Código**: ~5,000+
- **Archivos**: 30+
- **Funcionalidades**: 15+

---

**¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!**

---

## 🔄 Changelog

### Versión 2.1.0 (2025-12-17)

**Nuevas Funcionalidades:**
- ✅ Gestión multi-router completa
- ✅ Separación de ventas por router
- ✅ Cambio de contraseña desde interfaz
- ✅ Instalación interactiva mejorada
- ✅ Selector de router en navbar
- ✅ Página de perfil de usuario

**Mejoras:**
- ✅ Scripts de instalación automatizados
- ✅ Documentación completa
- ✅ Validaciones de seguridad
- ✅ Interfaz mejorada

**Correcciones:**
- ✅ Bugs en la gestión de ventas
- ✅ Problemas de conexión con routers
- ✅ Errores en la instalación

### Versión 2.0.0 (2024)
- Versión inicial mejorada

---

**Desarrollado con ❤️ para la comunidad de administradores de redes**
