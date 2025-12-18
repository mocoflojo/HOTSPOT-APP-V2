@echo off
REM ========================================
REM HOTSPOT-APP - Verificar Ventas
REM Script para verificar ventas en BD
REM ========================================

echo.
echo ========================================
echo  HOTSPOT-APP - Verificar Ventas
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist venv (
    echo [ERROR] No se encontró el entorno virtual
    echo Por favor ejecuta install.bat primero
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar script de verificación
python check_sales.py

REM Desactivar entorno virtual
call deactivate

echo.
pause
