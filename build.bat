@echo off
REM ========================================
REM HOTSPOT-APP - Script de Empaquetado
REM Crea un ejecutable con PyInstaller
REM ========================================

echo.
echo ========================================
echo  HOTSPOT-APP - Empaquetado Automático
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
echo [1/6] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado
echo.

REM Instalar PyInstaller si no está instalado
echo [2/6] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller no está instalado. Instalando...
    pip install pyinstaller
    echo [OK] PyInstaller instalado
) else (
    echo [OK] PyInstaller ya está instalado
)
echo.

REM Limpiar builds anteriores
echo [3/6] Limpiando builds anteriores...
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist
if exist dist-package rmdir /S /Q dist-package
echo [OK] Limpieza completada
echo.

REM Compilar con PyInstaller
echo [4/6] Compilando aplicación...
echo Este proceso puede tomar 10-15 minutos...
echo.

pyinstaller --name=HOTSPOT-APP ^
    --onefile ^
    --console ^
    --add-data "templates;templates" ^
    --add-data "app_data;app_data" ^
    --add-data "config.ini;." ^
    --add-data "prices.json;." ^
    --add-data "expiration_scripts.json;." ^
    --hidden-import=flask ^
    --hidden-import=flask_login ^
    --hidden-import=flask_sqlalchemy ^
    --hidden-import=routeros_api ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=sqlalchemy ^
    app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La compilación falló
    pause
    exit /b 1
)

echo.
echo [OK] Compilación completada
echo.

REM Crear carpeta de distribución
echo [5/6] Creando paquete de distribución...
mkdir dist-package
copy dist\HOTSPOT-APP.exe dist-package\
copy README.md dist-package\

REM Crear README para el cliente
(
    echo ========================================
    echo  HOTSPOT-APP V2.1 - Guía Rápida
    echo ========================================
    echo.
    echo 1. Ejecutar: HOTSPOT-APP.exe
    echo 2. La aplicación se abrirá en tu navegador
    echo 3. Login con las credenciales que configuraste
    echo.
    echo ========================================
    echo  Primer Uso
    echo ========================================
    echo.
    echo Al ejecutar por primera vez:
    echo - Se creará la base de datos automáticamente
    echo - Sigue las instrucciones en pantalla
    echo.
    echo ========================================
    echo  Soporte
    echo ========================================
    echo.
    echo Para más información, consulta README.md
    echo.
) > dist-package\INSTRUCCIONES.txt

echo [OK] Paquete creado
echo.

REM Mostrar información
echo [6/6] Generando información del paquete...
echo.
echo ========================================
echo  EMPAQUETADO COMPLETADO!
echo ========================================
echo.
echo Ubicación: dist-package\
echo Archivo principal: HOTSPOT-APP.exe
echo Tamaño aproximado: ~80 MB
echo.
echo ========================================
echo  Para Distribuir al Cliente
echo ========================================
echo.
echo 1. Comprimir la carpeta dist-package\ a ZIP
echo 2. Enviar al cliente
echo 3. Cliente descomprime y ejecuta HOTSPOT-APP.exe
echo.
echo ========================================
echo  Archivos en el Paquete
echo ========================================
echo.
dir /B dist-package
echo.
echo ========================================
echo.
pause
