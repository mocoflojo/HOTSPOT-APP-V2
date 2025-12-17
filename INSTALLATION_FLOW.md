# 🚀 Flujo de Instalación Actualizado - HOTSPOT-APP V2

## 📋 Resumen de Cambios

Se ha actualizado el proceso de instalación para incluir la inicialización automática de la base de datos.

---

## 🎯 Nuevo Flujo de Instalación

### Para un Cliente Nuevo:

```
1. Ejecutar: install.bat
   ├─ Instala Python dependencies
   ├─ Crea entorno virtual
   ├─ Verifica config.ini
   └─ Ejecuta configuración interactiva (install.py)
       ├─ Solicita datos del router
       ├─ Solicita credenciales del admin
       ├─ Crea base de datos
       └─ Configura todo automáticamente

2. Ejecutar: run.bat
   ├─ Verifica que la BD exista
   ├─ Inicia la aplicación
   └─ Abre el navegador automáticamente
```

---

## 📁 Archivos de Instalación

### 1. `install.bat` (Actualizado) ⭐
**Qué hace:**
- ✅ Verifica Python
- ✅ Crea entorno virtual
- ✅ Instala dependencias
- ✅ Verifica/crea config.ini
- ✅ **NUEVO:** Ejecuta `install.py` para configurar la BD
- ✅ **NUEVO:** Crea router y usuario admin automáticamente

**Cuándo usarlo:**
- Primera instalación en un cliente nuevo
- Reinstalación completa

### 2. `install.py` (Nuevo)
**Qué hace:**
- ✅ Solicita datos del router interactivamente
- ✅ Prueba conexión con el router (opcional)
- ✅ Solicita credenciales del admin
- ✅ Crea base de datos
- ✅ Crea router en la BD
- ✅ Crea usuario admin
- ✅ Actualiza config.ini como backup

**Cuándo usarlo:**
- Lo ejecuta `install.bat` automáticamente
- Puedes ejecutarlo manualmente si quieres: `python install.py`

### 3. `init_db.py` (Existente)
**Qué hace:**
- ✅ Crea base de datos
- ✅ Crea router desde config.ini
- ✅ Crea usuario admin con credenciales por defecto

**Cuándo usarlo:**
- **Ya NO es necesario ejecutarlo manualmente**
- Se mantiene como alternativa si `install.py` falla
- Útil para scripts automatizados

### 4. `run.bat` (Actualizado)
**Qué hace:**
- ✅ Activa entorno virtual
- ✅ **NUEVO:** Verifica si existe la BD
- ✅ **NUEVO:** Ofrece ejecutar configuración si no existe BD
- ✅ Inicia la aplicación
- ✅ Abre el navegador automáticamente

**Cuándo usarlo:**
- Para iniciar la aplicación después de instalar
- Cada vez que quieras ejecutar la app

---

## 🔄 Comparación: Antes vs Ahora

### ❌ **Antes (Proceso Antiguo):**
```
1. Ejecutar: install.bat
   └─ Solo instalaba dependencias

2. Editar manualmente: config.ini
   └─ Con datos del router

3. Ejecutar manualmente: python init_db.py
   └─ Para crear la BD

4. Ejecutar: run.bat
   └─ Para iniciar la app

5. Login con credenciales por defecto
   └─ admin / admin
```

### ✅ **Ahora (Proceso Nuevo):**
```
1. Ejecutar: install.bat
   ├─ Instala dependencias
   ├─ Abre config.ini para editar (si no existe)
   └─ Ejecuta configuración interactiva
       ├─ Solicita datos del router
       ├─ Solicita credenciales del admin
       └─ Crea todo automáticamente

2. Ejecutar: run.bat
   └─ Inicia la app (verifica BD automáticamente)

3. Login con las credenciales que configuraste
```

---

## 🎯 Escenarios de Uso

### Escenario 1: Instalación Nueva (Recomendado)
```bash
# Paso 1: Ejecutar instalación completa
install.bat

# El script te guiará:
# - Datos del router
# - Credenciales del admin
# - Todo se configura automáticamente

# Paso 2: Ejecutar la aplicación
run.bat
```

### Escenario 2: Instalación Manual (Avanzado)
```bash
# Paso 1: Instalar dependencias
install.bat

# Paso 2: Editar config.ini manualmente
notepad config.ini

# Paso 3: Inicializar BD manualmente
python init_db.py

# Paso 4: Ejecutar la aplicación
run.bat
```

### Escenario 3: Reinstalación (Mantener Datos)
```bash
# Si ya tienes la BD y solo quieres actualizar código:
run.bat

# La app detectará que la BD existe y no pedirá configuración
```

### Escenario 4: Reinstalación (Borrar Todo)
```bash
# Paso 1: Borrar BD anterior
del instance\users.db

# Paso 2: Ejecutar instalación
install.bat

# Se creará todo desde cero
```

---

## 📝 Respuestas a Preguntas Comunes

### ¿Necesito ejecutar init_db.py manualmente?
**NO**, ya no es necesario. El `install.bat` lo hace automáticamente.

### ¿Qué pasa si ejecuto install.bat en una instalación existente?
Te preguntará si quieres recrear la base de datos. Si dices que NO, mantendrá la existente.

### ¿Puedo seguir usando el proceso manual?
Sí, puedes:
1. Editar `config.ini`
2. Ejecutar `python init_db.py`
3. Ejecutar `run.bat`

### ¿Qué pasa si ejecuto run.bat sin haber instalado?
El script detectará que no existe la BD y te ofrecerá ejecutar la configuración inicial.

### ¿Dónde se guardan las credenciales del admin?
En la base de datos (`instance/users.db`). El `config.ini` solo guarda datos del router.

---

## 🔧 Para Desarrolladores

### Estructura de Archivos de Instalación:

```
HOTSPOT-APP/
├── install.bat          # ← Script principal de instalación (Windows)
├── run.bat              # ← Script para ejecutar la app (Windows)
├── install.py           # ← Configuración interactiva (Python)
├── init_db.py           # ← Inicialización manual (Python, legacy)
├── config.ini           # ← Configuración del router (backup)
└── instance/
    └── users.db         # ← Base de datos (se crea automáticamente)
```

### Orden de Ejecución:

```
install.bat
    │
    ├─> Verifica Python
    ├─> Crea venv
    ├─> Instala requirements.txt
    ├─> Verifica config.ini
    │
    └─> Ejecuta: install.py
            │
            ├─> Solicita datos del router
            ├─> Solicita credenciales admin
            ├─> Crea base de datos
            ├─> Crea router en BD
            ├─> Crea usuario admin
            └─> Actualiza config.ini
```

---

## ⚠️ Notas Importantes

1. **config.ini sigue siendo necesario:**
   - Se usa como backup/fallback
   - `install.py` lo actualiza automáticamente
   - Puedes editarlo manualmente si prefieres

2. **Base de datos es la fuente de verdad:**
   - Después de la instalación, todo se maneja desde la BD
   - El config.ini solo se usa si falla la BD

3. **Compatibilidad hacia atrás:**
   - Los scripts antiguos (`init_db.py`) siguen funcionando
   - Puedes usar el proceso manual si prefieres

4. **Reinstalación:**
   - Si ejecutas `install.bat` de nuevo, te preguntará si quieres sobrescribir
   - Puedes mantener la BD existente o crear una nueva

---

## 🎉 Ventajas del Nuevo Flujo

✅ **Más fácil:** Un solo comando (`install.bat`)
✅ **Más rápido:** Todo automatizado
✅ **Más seguro:** Valida datos antes de crear
✅ **Más flexible:** Puedes elegir credenciales del admin
✅ **Más robusto:** Verifica que todo esté bien antes de continuar

---

**Versión:** 2.1
**Última actualización:** Diciembre 2025
