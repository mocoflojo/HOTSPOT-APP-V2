@echo off
REM ========================================
REM HOTSPOT-APP - Script de Actualización
REM Actualiza la aplicación sin perder datos
REM ========================================

echo.
echo ========================================
echo  HOTSPOT-APP - Actualización Automática
echo ========================================
echo.

REM Verificar si Git está instalado
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no está instalado
    echo.
    echo Para actualizar necesitas Git instalado.
    echo Descarga Git desde: https://git-scm.com/download/win
    echo.
    echo Alternativa: Descarga la nueva versión manualmente desde GitHub
    pause
    exit /b 1
)

REM Verificar si estamos en un repositorio Git
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Esta carpeta no es un repositorio Git
    echo.
    echo Para usar actualizaciones automáticas, clona el repositorio con:
    echo git clone https://github.com/mocoflojo/HOTSPOT-APP-V2.git
    echo.
    echo Alternativa: Descarga la nueva versión manualmente desde GitHub
    pause
    exit /b 1
)

echo [1/6] Deteniendo aplicación...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Aplicación detenida
echo.

echo [2/6] Guardando cambios locales...
git stash >nul 2>&1
echo [OK] Cambios guardados
echo.

echo [3/6] Descargando actualizaciones...
REM Detectar rama actual
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
echo [INFO] Rama actual: %CURRENT_BRANCH%
git pull origin %CURRENT_BRANCH%
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo descargar la actualización
    echo.
    echo Posibles causas:
    echo - No hay conexión a internet
    echo - Conflictos con archivos locales
    echo - Rama incorrecta: %CURRENT_BRANCH%
    echo.
    echo Intenta manualmente:
    echo   git pull origin %CURRENT_BRANCH%
    echo.
    pause
    exit /b 1
)
echo [OK] Actualizaciones descargadas
echo.

echo [4/6] Restaurando cambios locales...
git stash pop >nul 2>&1
echo [OK] Cambios restaurados
echo.

echo [5/6] Actualizando dependencias...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet --upgrade
    echo [OK] Dependencias actualizadas
) else (
    echo [ADVERTENCIA] No se encontró el entorno virtual
    echo Ejecuta install.bat para crear el entorno virtual
)
echo.

echo [6/6] Verificando base de datos...
if exist instance\users.db (
    echo [OK] Base de datos preservada
) else (
    echo [ADVERTENCIA] No se encontró la base de datos
    echo Ejecuta install.py para configurar la aplicación
)
echo.

echo ========================================
echo  Actualización Completada!
echo ========================================
echo.
echo Cambios aplicados:
git log -1 --pretty=format:"  - %s" HEAD
echo.
echo.
echo ========================================
echo.
echo La aplicación se reiniciará en 5 segundos...
echo Presiona Ctrl+C para cancelar
timeout /t 5

start run.bat
exit
