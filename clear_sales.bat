@echo off
REM ========================================
REM HOTSPOT-APP - Limpiar Ventas
REM Script para ejecutar clear_sales.py
REM ========================================

echo.
echo ========================================
echo  HOTSPOT-APP - Limpiar Ventas
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
echo [1/2] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

REM Ejecutar script de limpieza
echo [2/2] Ejecutando script de limpieza...
echo.
python clear_sales.py

REM Desactivar entorno virtual
call deactivate

echo.
echo ========================================
echo.
pause
