@echo off
REM ========================================
REM Script de Instalacion Automatica
REM HOTSPOT-APP V2 para Windows 10/11
REM ========================================

echo.
echo ========================================
echo  HOTSPOT-APP V2 - Instalacion Automatica
echo ========================================
echo.

REM Verificar si Python esta instalado
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor instala Python desde: https://www.python.org/downloads/
    echo IMPORTANTE: Marca la opcion "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)
echo [OK] Python encontrado
python --version
echo.

REM Crear entorno virtual
echo [2/6] Creando entorno virtual...
if exist venv (
    echo [INFO] El entorno virtual ya existe, omitiendo...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
)
echo.

REM Activar entorno virtual
echo [3/6] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

REM Actualizar pip
echo [4/6] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip actualizado
echo.

REM Instalar dependencias
echo [5/6] Instalando dependencias...
echo Este proceso puede tomar unos minutos...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas correctamente
echo.

REM Verificar archivo de configuracion
echo [6/6] Verificando configuracion...
if not exist config.ini (
    echo [ADVERTENCIA] No se encontro config.ini
    echo Se creara un archivo de configuracion de ejemplo...
    (
        echo [MIKROTIK]
        echo IP = 192.168.88.1
        echo USER = admin
        echo PASSWORD = 
        echo HOTSPOT_DNS = hotspot.local
    ) > config.ini
    echo [INFO] Archivo config.ini creado. Por favor editalo con los datos de tu MikroTik
)
echo [OK] Configuracion verificada
echo.

echo ========================================
echo  INSTALACION COMPLETADA
echo ========================================
echo.
echo Proximos pasos:
echo.
echo 1. Edita el archivo config.ini con los datos de tu MikroTik
echo 2. Ejecuta: run.bat
echo 3. Abre tu navegador en: http://localhost:5000
echo.
echo ========================================
echo.
pause
