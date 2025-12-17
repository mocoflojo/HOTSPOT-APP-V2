@echo off
REM ========================================
REM Script para Ejecutar HOTSPOT-APP V2
REM ========================================

echo.
echo ========================================
echo  Iniciando HOTSPOT-APP V2...
echo ========================================
echo.

REM Activar entorno virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
) else (
    echo [ADVERTENCIA] No se encontro el entorno virtual
    echo Por favor ejecuta install.bat primero
    pause
    exit /b 1
)

REM Verificar si existe la base de datos
if not exist instance\users.db (
    echo.
    echo [ADVERTENCIA] No se encontro la base de datos
    echo.
    echo Parece que es la primera vez que ejecutas la aplicacion.
    echo Necesitas inicializar la base de datos primero.
    echo.
    choice /C SN /M "Deseas ejecutar la configuracion inicial ahora"
    if errorlevel 2 (
        echo.
        echo [INFO] Puedes ejecutar manualmente: python install.py
        pause
        exit /b 1
    )
    echo.
    echo Ejecutando configuracion inicial...
    python install.py
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Hubo un problema durante la configuracion
        pause
        exit /b 1
    )
    echo.
    echo [OK] Configuracion completada!
    echo.
)

echo.
echo Servidor iniciando en: http://localhost:5000
echo El navegador se abrira automaticamente...
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Abrir el navegador despues de un breve delay (en segundo plano)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

REM Ejecutar la aplicacion
python app.py

pause
