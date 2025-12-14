# 🌐 HOTSPOT-APP V2

Sistema de Gestión de Hotspot para MikroTik - Versión Mejorada

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Descripción

Aplicación web completa para la gestión de usuarios Hotspot en routers MikroTik. Incluye generación de vouchers, gestión de perfiles, reportes de ventas y más.

### ✨ Características Principales

- 🎫 **Generación de Vouchers**: Crea códigos de acceso PIN o Usuario/Contraseña
- 👥 **Gestión de Usuarios**: Administra usuarios del hotspot
- 📊 **Perfiles Personalizables**: Configura límites de velocidad y tiempo
- 💰 **Reportes de Ventas**: Visualiza estadísticas y gráficos de ventas
- 🖨️ **Impresión de Vouchers**: Plantillas personalizables para imprimir
- ⏱️ **Modos de Expiración**: Scripts predefinidos y personalizados
- 🔐 **Sistema de Login**: Autenticación segura para administradores

---

## 🖥️ Requisitos del Sistema

### Windows 10/11

- **Python 3.8 o superior** (Recomendado: Python 3.13)
- **Git** (para clonar el repositorio)
- **Router MikroTik** con API habilitada
- **Navegador Web** moderno (Chrome, Firefox, Edge)

---

## 🚀 Instalación en Windows 10/11

### Paso 1: Instalar Python

1. Descarga Python desde: https://www.python.org/downloads/
2. **IMPORTANTE**: Durante la instalación, marca la opción **"Add Python to PATH"**
3. Verifica la instalación abriendo PowerShell o CMD:
   ```powershell
   python --version
   ```
   Deberías ver algo como: `Python 3.13.5`

### Paso 2: Instalar Git (Opcional)

1. Descarga Git desde: https://git-scm.com/download/win
2. Instala con las opciones por defecto
3. Verifica:
   ```powershell
   git --version
   ```

### Paso 3: Clonar el Repositorio

Abre PowerShell o CMD y ejecuta:

```powershell
# Navega a la carpeta donde quieres instalar
cd C:\Users\TuUsuario\Desktop

# Clona el repositorio
git clone https://github.com/mocoflojo/HOTSPOT-APP-V2.git

# Entra a la carpeta del proyecto
cd HOTSPOT-APP-V2
```

**Alternativa sin Git**: Descarga el ZIP desde GitHub y descomprímelo.

### Paso 4: Crear Entorno Virtual (Recomendado)

```powershell
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1
```

**Nota**: Si obtienes un error de permisos, ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 5: Instalar Dependencias

```powershell
# Asegúrate de que el entorno virtual esté activado (verás "(venv)" en el prompt)
pip install -r requirements.txt
```

Esto instalará automáticamente:
- Flask 3.1.1
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- RouterOS-api 0.21.0
- Y todas las demás dependencias necesarias

### Paso 6: Configurar el Router MikroTik

Edita el archivo `config.ini` con los datos de tu router:

```ini
[MIKROTIK]
IP = 192.168.88.1          # IP de tu MikroTik
USER = admin               # Usuario con permisos API
PASSWORD = tu_password     # Contraseña del usuario
HOTSPOT_DNS = hotspot.local # DNS del hotspot
```

**Importante**: Asegúrate de que la API del MikroTik esté habilitada:
- En Winbox/WebFig: `IP → Services → API` (debe estar habilitado en puerto 8728)

### Paso 7: Inicializar la Base de Datos

```powershell
# Ejecutar la aplicación por primera vez
python app.py
```

La aplicación creará automáticamente:
- Base de datos SQLite en `instance/users.db`
- Carpeta `app_data` para archivos de configuración

### Paso 8: Crear Usuario Administrador

Al ejecutar por primera vez, la aplicación te pedirá crear un usuario administrador:

1. Abre tu navegador en: `http://localhost:5000`
2. Completa el formulario de configuración inicial
3. Crea tu usuario y contraseña de administrador

---

## 🎮 Uso de la Aplicación

### Iniciar el Servidor

```powershell
# Activar entorno virtual (si no está activo)
.\venv\Scripts\Activate.ps1

# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

### Detener el Servidor

Presiona `Ctrl + C` en la terminal donde está corriendo.

---

## 📁 Estructura del Proyecto

```
HOTSPOT-APP-V2/
├── app.py                    # Aplicación principal
├── auth.py                   # Autenticación
├── config.py                 # Configuración
├── config.ini                # Configuración del MikroTik
├── database.py               # Modelos de base de datos
├── mikrotik_service.py       # Servicios de MikroTik API
├── routes.py                 # Rutas de la aplicación
├── utils.py                  # Utilidades
├── clear_sales.py            # Script para limpiar ventas
├── requirements.txt          # Dependencias Python
├── templates/                # Plantillas HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── users.html
│   ├── profiles.html
│   ├── generate.html
│   ├── reports.html
│   └── ...
├── app_data/                 # Datos de la aplicación
│   ├── prices.json
│   ├── expiration_scripts.json
│   └── voucher_template.html
└── instance/                 # Base de datos
    └── users.db
```

---

## 🛠️ Mantenimiento

### Limpiar Ventas (Cambio de MikroTik)

Si cambias de router MikroTik y quieres limpiar los reportes antiguos:

```powershell
python clear_sales.py
```

Esto eliminará las ventas pero mantendrá tus usuarios de login.

### Actualizar Dependencias

```powershell
pip install --upgrade -r requirements.txt
```

### Backup de la Base de Datos

Copia el archivo `instance/users.db` a un lugar seguro.

---

## 🔧 Solución de Problemas

### Error: "No se puede conectar al router"

- Verifica que la IP en `config.ini` sea correcta
- Asegúrate de que el servicio API esté habilitado en el MikroTik
- Verifica que el firewall no bloquee el puerto 8728

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

### La aplicación no inicia

```powershell
# Verifica que Python esté instalado
python --version

# Verifica que las dependencias estén instaladas
pip list

# Revisa los logs en la terminal para ver el error específico
```

---

## 📝 Configuración Avanzada

### Cambiar el Puerto de la Aplicación

Edita `app.py` y cambia:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia 5000 por el puerto deseado
```

### Habilitar Acceso desde Otras Computadoras

La aplicación ya está configurada con `host='0.0.0.0'`, lo que permite acceso desde otras computadoras en la red local. Accede usando:
```
http://IP_DE_TU_PC:5000
```

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
2. Abre un **Issue** en GitHub
3. Consulta la documentación de MikroTik: https://wiki.mikrotik.com/

---

## 🎯 Roadmap

- [ ] Soporte para múltiples routers MikroTik
- [ ] API REST para integraciones
- [ ] Dashboard con más estadísticas
- [ ] Notificaciones por email
- [ ] Modo oscuro en la interfaz
- [ ] Exportación de reportes a PDF/Excel

---

## ⭐ Agradecimientos

- MikroTik por su excelente API
- Flask y su comunidad
- Todos los contribuidores del proyecto

---

**¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!**
