# 🚀 Guía de Inicio Rápido - HOTSPOT-APP V2

## Para Usuarios de Windows 10/11

### ⚡ Instalación Rápida (3 minutos)

1. **Descarga el proyecto**
   ```powershell
   git clone https://github.com/mocoflojo/HOTSPOT-APP-V2.git
   cd HOTSPOT-APP-V2
   ```

2. **Ejecuta el instalador automático**
   - Doble clic en `install.bat`
   - Espera a que termine (instalará Python packages automáticamente)

3. **Configura tu MikroTik**
   - Edita `config.ini` con los datos de tu router

4. **Inicia la aplicación**
   - Doble clic en `run.bat`
   - **El navegador se abrirá automáticamente** en http://localhost:5000
   - (Alternativa: usa `run-no-browser.bat` si prefieres abrir el navegador manualmente)


### 📋 Requisitos Previos

- ✅ Python 3.8+ instalado ([Descargar aquí](https://www.python.org/downloads/))
- ✅ Router MikroTik con API habilitada (puerto 8728)

---

## 🎯 Primeros Pasos

### 1. Configuración Inicial

Al abrir la aplicación por primera vez:

1. Crea tu usuario administrador
2. Ingresa con tus credenciales
3. Ve al Dashboard para verificar la conexión con el MikroTik

### 2. Crear tu Primer Perfil

1. Ve a **Perfiles** en el menú
2. Click en **"Crear Nuevo Perfil"**
3. Configura:
   - Nombre: `1-Hora-5Mbps`
   - Usuarios simultáneos: `1`
   - Límite de velocidad: `5M/5M`
   - Modo de expiración: `Eliminar al Agotar`
   - Precio: `2.50`
4. Click **"Crear Perfil"**

### 3. Generar Vouchers

1. Ve a **Generar** en el menú
2. Configura:
   - Cantidad: `10`
   - Modo: `PIN`
   - Longitud: `6`
   - Perfil: `1-Hora-5Mbps`
   - Límite de tiempo: `1h`
3. Click **"Generar Vouchers"**

### 4. Imprimir Vouchers

1. Ve a **Usuarios**
2. Filtra por el perfil creado
3. Click **"Imprimir Vouchers Filtrados"**
4. Se abrirá una vista de impresión

### 5. Ver Reportes

1. Ve a **Reportes**
2. Verás gráficos de ventas automáticas
3. Filtra por fecha o perfil según necesites

---

## 🛠️ Comandos Útiles

### Iniciar la aplicación
```powershell
# Opción 1: Usando el script
run.bat

# Opción 2: Manual
venv\Scripts\activate
python app.py
```

### Limpiar ventas (cambio de MikroTik)
```powershell
venv\Scripts\activate
python clear_sales.py
```

### Actualizar el proyecto
```powershell
git pull origin feature/responsive-sidebar
pip install -r requirements.txt
```

---

## 📱 Acceso desde Otros Dispositivos

La aplicación está configurada para aceptar conexiones desde cualquier dispositivo en tu red local:

1. Encuentra la IP de tu PC:
   ```powershell
   ipconfig
   ```
   Busca "Dirección IPv4" (ej: `192.168.1.100`)

2. Desde otro dispositivo, abre:
   ```
   http://192.168.1.100:5000
   ```

---

## ⚙️ Configuración del MikroTik

### Habilitar la API

1. Conecta a tu MikroTik (Winbox o WebFig)
2. Ve a: `IP → Services`
3. Busca **"api"**
4. Asegúrate de que esté **habilitado** en el puerto `8728`

### Crear Usuario API (Opcional pero Recomendado)

```routeros
# En la terminal del MikroTik:
/user add name=hotspot-api password=tu_password group=full
```

Luego usa estas credenciales en `config.ini`

---

## 🔐 Seguridad

### Cambiar Puerto de la Aplicación

Edita `app.py`, línea final:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambia 5000 por 8080
```

### Deshabilitar Debug Mode (Producción)

Edita `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

### Backup de Datos

Copia estos archivos regularmente:
- `instance/users.db` (Base de datos)
- `config.ini` (Configuración)
- `app_data/` (Precios, plantillas, scripts)

---

## 🆘 Problemas Comunes

### "No se puede conectar al router"
- ✅ Verifica la IP en `config.ini`
- ✅ Verifica que la API esté habilitada
- ✅ Prueba hacer ping al router: `ping 192.168.88.1`

### "ModuleNotFoundError"
```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

### "No se puede activar el entorno virtual"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Los reportes están vacíos
- Es normal si es la primera vez
- Los reportes se generan cuando los usuarios se conectan
- Puedes generar datos de prueba conectándote con un voucher

---

## 📚 Más Información

- **README completo**: Ver `README.md`
- **Documentación MikroTik**: https://wiki.mikrotik.com/
- **Reportar problemas**: https://github.com/mocoflojo/HOTSPOT-APP-V2/issues

---

## ✅ Checklist de Instalación

- [ ] Python instalado
- [ ] Proyecto clonado/descargado
- [ ] Ejecutado `install.bat`
- [ ] `config.ini` configurado
- [ ] Aplicación iniciada con `run.bat`
- [ ] Usuario administrador creado
- [ ] Conexión al MikroTik verificada
- [ ] Primer perfil creado
- [ ] Primeros vouchers generados

---

**¡Listo! Ya puedes empezar a gestionar tu Hotspot MikroTik** 🎉
