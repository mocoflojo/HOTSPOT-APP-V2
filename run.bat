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

echo.
echo Servidor iniciando en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Ejecutar la aplicacion
python app.py

pause
