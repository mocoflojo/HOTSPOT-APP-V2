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
echo [4/7] Compilando aplicación principal...
echo Este proceso puede tomar 10-15 minutos...
echo.
echo NOTA: Usando modo --onedir para permitir archivos de configuración externos
echo.

pyinstaller --name=HOTSPOT-APP ^
    --onedir ^
    --console ^
    --add-data "templates;templates" ^
    --add-data "expiration_scripts.json;." ^
    --hidden-import=flask ^
    --hidden-import=flask_login ^
    --hidden-import=flask_sqlalchemy ^
    --hidden-import=routeros_api ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=sqlalchemy ^
    --hidden-import=waitress ^
    app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La compilación de la app principal falló
    pause
    exit /b 1
)

echo.
echo [OK] Aplicación principal compilada
echo.

REM Compilar scripts de utilidad
echo [5/7] Compilando scripts de utilidad...
echo.

echo Compilando clear_sales.exe...
pyinstaller --name=clear_sales ^
    --onefile ^
    --console ^
    --hidden-import=flask_sqlalchemy ^
    --hidden-import=sqlalchemy ^
    clear_sales.py

if %errorlevel% neq 0 (
    echo [ADVERTENCIA] No se pudo compilar clear_sales.exe
)

echo.
echo Compilando check_sales.exe...
pyinstaller --name=check_sales ^
    --onefile ^
    --console ^
    --hidden-import=flask_sqlalchemy ^
    --hidden-import=sqlalchemy ^
    check_sales.py

if %errorlevel% neq 0 (
    echo [ADVERTENCIA] No se pudo compilar check_sales.exe
)

echo.
echo [OK] Scripts de utilidad compilados
echo.

REM Crear carpeta de distribución
echo [6/7] Creando paquete de distribución...
mkdir dist-package
xcopy /E /I dist\HOTSPOT-APP dist-package\HOTSPOT-APP

REM Copiar archivos de configuración EXTERNOS (editables por el cliente)
echo Copiando archivos de configuración externos...
copy config.ini dist-package\HOTSPOT-APP\
copy prices.json dist-package\HOTSPOT-APP\
xcopy /E /I app_data dist-package\HOTSPOT-APP\app_data\
copy README.md dist-package\HOTSPOT-APP\

REM Copiar scripts de utilidad para el cliente (como ejecutables)
echo Copiando scripts de utilidad...
copy dist\clear_sales.exe dist-package\HOTSPOT-APP\ 2>nul
copy dist\check_sales.exe dist-package\HOTSPOT-APP\ 2>nul

REM Crear README para el cliente
(
    echo ========================================
    echo  HOTSPOT-APP V2.1 - Guía Rápida
    echo ========================================
    echo.
    echo COMO EJECUTAR:
    echo 1. Ejecutar: HOTSPOT-APP.exe
    echo 2. La aplicación se abrirá en tu navegador
    echo 3. Login con las credenciales que configuraste
    echo.
    echo ========================================
    echo  Archivos de Configuración
    echo ========================================
    echo.
    echo Puedes editar estos archivos según tus necesidades:
    echo - config.ini: Configuración de RouterOS y base de datos
    echo - prices.json: Precios de los planes de internet
    echo - app_data\voucher_template.html: Plantilla de vouchers
    echo - app_data\logo.png: Logo de tu empresa
    echo.
    echo IMPORTANTE: Después de editar config.ini o prices.json,
    echo reinicia la aplicación para que los cambios tomen efecto.
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
    echo  Scripts de Utilidad
    echo ========================================
    echo.
    echo LIMPIAR VENTAS DE PRUEBA:
    echo - Ejecutar: clear_sales.exe
    echo - Permite eliminar ventas de prueba o resetear el sistema
    echo - PRECAUCIÓN: Esta acción no se puede deshacer
    echo - NO requiere Python instalado
    echo.
    echo VERIFICAR VENTAS:
    echo - Ejecutar: check_sales.exe
    echo - Muestra un resumen de las ventas registradas
    echo - NO requiere Python instalado
    echo.
    echo ========================================
    echo  Soporte
    echo ========================================
    echo.
    echo Para más información, consulta README.md
    echo.
) > dist-package\HOTSPOT-APP\INSTRUCCIONES.txt

echo [OK] Paquete creado
echo.

REM Mostrar información
echo [7/7] Generando información del paquete...
echo.
echo ========================================
echo  EMPAQUETADO COMPLETADO!
echo ========================================
echo.
echo Ubicación: dist-package\HOTSPOT-APP\
echo Archivo principal: HOTSPOT-APP.exe
echo Tamaño aproximado: ~150 MB
echo.
echo ========================================
echo  Archivos Editables por el Cliente
echo ========================================
echo.
echo - config.ini (Configuración de RouterOS y DB)
echo - prices.json (Precios de planes)
echo - app_data\voucher_template.html (Plantilla de vouchers)
echo - app_data\logo.png (Logo de la empresa)
echo.
echo ========================================
echo  Para Distribuir al Cliente
echo ========================================
echo.
echo 1. Comprimir la carpeta dist-package\HOTSPOT-APP\ a ZIP
echo 2. Enviar al cliente
echo 3. Cliente descomprime
echo 4. Cliente ejecuta HOTSPOT-APP.exe
echo.
echo ========================================
echo  Archivos en el Paquete
echo ========================================
echo.
dir /B dist-package\HOTSPOT-APP
echo.
echo ========================================
echo.
pause
