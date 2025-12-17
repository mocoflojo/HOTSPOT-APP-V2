# 📦 Guía de Instalación y Actualización para Cliente
## Windows 10 - HOTSPOT-APP V2.1

---

## 🎯 INSTALACIÓN INICIAL (Solo Primera Vez)

### Requisitos Previos:
- ✅ Windows 10
- ✅ Git instalado (ya lo tienes)
- ✅ Python 3.8 o superior

---

### Paso 1: Descargar Python (Si no lo tienes)

1. Ve a: https://www.python.org/downloads/
2. Descarga Python 3.13 (o la última versión)
3. **IMPORTANTE:** Durante la instalación, marca:
   - ☑️ "Add Python to PATH"
4. Instala con opciones por defecto

**Verificar instalación:**
```powershell
# Abre PowerShell o CMD y ejecuta:
python --version

# Deberías ver algo como: Python 3.13.5
```

---

### Paso 2: Descargar la Aplicación

**Opción A: Con Git (Recomendada)**

```powershell
# 1. Abre PowerShell o CMD

# 2. Ve a la carpeta donde quieres instalar (ejemplo: Escritorio)
cd C:\Users\TuUsuario\Desktop

# 3. Clona el repositorio
git clone https://github.com/mocoflojo/HOTSPOT-APP-V2.git

# 4. Entra a la carpeta
cd HOTSPOT-APP-V2
```

**Opción B: Sin Git (Manual)**

1. Ve a: https://github.com/mocoflojo/HOTSPOT-APP-V2
2. Click en el botón verde "Code"
3. Click en "Download ZIP"
4. Descomprime el archivo en tu carpeta deseada

---

### Paso 3: Instalar la Aplicación

```powershell
# Estando en la carpeta HOTSPOT-APP-V2:

# Ejecuta el instalador (doble click o desde terminal):
install.bat

# El instalador te guiará para:
# - Instalar dependencias
# - Configurar el router MikroTik
# - Crear usuario administrador
# - Inicializar la base de datos
```

**Sigue las instrucciones en pantalla:**
- Ingresa la IP de tu router MikroTik
- Ingresa usuario y contraseña del router
- Crea tu usuario administrador
- ¡Listo!

---

### Paso 4: Ejecutar la Aplicación

```powershell
# Doble click en:
run.bat

# O desde terminal:
run.bat
```

La aplicación se abrirá automáticamente en tu navegador en:
**http://localhost:5000**

---

## 🔄 ACTUALIZACIÓN (Cuando haya nueva versión)

### ¿Cuándo actualizar?

Te avisaré cuando haya una nueva versión disponible.

### Cómo Actualizar:

**Método 1: Automático (Recomendado) ⭐**

```powershell
# 1. Doble click en:
update.bat

# 2. Espera 1-2 minutos
# 3. ¡Listo! La aplicación se reiniciará automáticamente
```

**Método 2: Manual**

```powershell
# 1. Detén la aplicación (Ctrl+C en la terminal)

# 2. Abre PowerShell o CMD en la carpeta de la aplicación

# 3. Ejecuta:
git pull origin main

# 4. Actualiza dependencias (si es necesario):
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 5. Reinicia la aplicación:
run.bat
```

---

## ✅ Verificar que Todo Funciona

### Después de Instalar o Actualizar:

1. **Abrir navegador:** http://localhost:5000
2. **Login** con tus credenciales
3. **Verificar:**
   - Dashboard carga correctamente
   - Puedes ver usuarios del hotspot
   - Puedes generar vouchers
   - Reportes funcionan

---

## 🔒 TUS DATOS ESTÁN SEGUROS

### Al Actualizar, NO se Pierden:

- ✅ Base de datos (usuarios, routers, ventas)
- ✅ Configuración del router
- ✅ Precios configurados
- ✅ Plantillas personalizadas
- ✅ Todos tus datos

### Solo se Actualiza:

- ✅ Código de la aplicación
- ✅ Nuevas funcionalidades
- ✅ Correcciones de errores

---

## 📁 Estructura de Carpetas

```
HOTSPOT-APP-V2/
├── run.bat              ← Ejecutar aplicación
├── update.bat           ← Actualizar aplicación
├── install.bat          ← Instalador (solo primera vez)
├── instance/
│   └── users.db         ← TU BASE DE DATOS (no tocar)
├── app_data/
│   ├── prices.json      ← Tus precios
│   └── ...              ← Tus configuraciones
└── venv/                ← Entorno Python (no tocar)
```

**IMPORTANTE:** No borres las carpetas `instance/` ni `app_data/`

---

## 🆘 Solución de Problemas

### Error: "Python no está instalado"

**Solución:**
1. Instala Python desde: https://www.python.org/downloads/
2. Marca "Add Python to PATH" durante instalación
3. Reinicia PowerShell/CMD
4. Ejecuta `install.bat` de nuevo

---

### Error: "Git no está instalado"

**Solución:**
1. Instala Git desde: https://git-scm.com/download/win
2. Usa opciones por defecto
3. Reinicia PowerShell/CMD
4. Ejecuta `update.bat` de nuevo

---

### Error: "No se puede conectar al router"

**Solución:**
1. Verifica que la IP del router sea correcta
2. Verifica usuario y contraseña del router
3. Asegúrate que el servicio API esté habilitado en el MikroTik:
   - En Winbox: `IP → Services → API` (puerto 8728)
4. Verifica que no haya firewall bloqueando

---

### Error: "ModuleNotFoundError"

**Solución:**
```powershell
# Reinstalar dependencias:
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### La aplicación no inicia

**Solución:**
```powershell
# 1. Verifica Python:
python --version

# 2. Verifica que el entorno virtual exista:
dir venv

# 3. Si no existe, ejecuta:
install.bat

# 4. Intenta ejecutar de nuevo:
run.bat
```

---

### Olvidé mi contraseña

**Solución:**
1. Contacta al administrador del sistema
2. O reinstala la aplicación (perderás datos)

---

## 📞 Contacto y Soporte

### Si tienes problemas:

1. **Revisa esta guía** primero
2. **Verifica los errores** en la terminal
3. **Contacta al soporte** con:
   - Descripción del problema
   - Mensaje de error (si hay)
   - Captura de pantalla

---

## 🎯 Comandos Rápidos

### Uso Diario:

```powershell
# Ejecutar aplicación:
run.bat

# Detener aplicación:
Ctrl + C (en la terminal)
```

### Actualización:

```powershell
# Actualizar a nueva versión:
update.bat
```

### Mantenimiento:

```powershell
# Backup de base de datos:
copy instance\users.db instance\users.db.backup

# Ver versión instalada:
git log -1
```

---

## ✨ Consejos

### Buenas Prácticas:

1. **Backup Regular:**
   - Copia `instance\users.db` cada semana
   - Guarda en un lugar seguro

2. **Actualizar Regularmente:**
   - Ejecuta `update.bat` cuando te avise
   - Las actualizaciones traen mejoras y correcciones

3. **No Modificar Archivos:**
   - No edites archivos `.py` a menos que sepas lo que haces
   - Usa la interfaz web para configurar

4. **Cambiar Contraseña:**
   - Cambia la contraseña por defecto
   - Ve a "Perfil" en el menú

---

## 📋 Checklist de Instalación

### Primera Instalación:

- [ ] Python instalado y en PATH
- [ ] Git instalado
- [ ] Repositorio clonado
- [ ] `install.bat` ejecutado
- [ ] Router configurado
- [ ] Usuario administrador creado
- [ ] Aplicación funciona en http://localhost:5000
- [ ] Contraseña cambiada

### Después de Actualizar:

- [ ] `update.bat` ejecutado sin errores
- [ ] Aplicación reiniciada
- [ ] Login funciona
- [ ] Datos preservados
- [ ] Nuevas funcionalidades visibles

---

## 🎉 ¡Listo!

Ya tienes HOTSPOT-APP instalado y funcionando.

### Próximos Pasos:

1. **Cambiar contraseña** (Perfil → Cambiar Contraseña)
2. **Agregar routers** (si tienes más de uno)
3. **Configurar precios** (si es necesario)
4. **Generar tus primeros vouchers**

---

**¿Necesitas ayuda? Contacta al soporte técnico.**

---

**Versión de esta guía:** 2.1.0  
**Fecha:** Diciembre 2025  
**Sistema:** Windows 10/11
