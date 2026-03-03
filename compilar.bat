@echo off
chcp 65001 >nul
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║     TIENDA DE PROGRAMAS LIBRES - Compilar .exe      ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

SET PYTHON=C:\Users\camel\AppData\Local\Programs\Python\Python314\python.exe

echo [1/3] Verificando Python...
if not exist "%PYTHON%" (
    echo ERROR: No se encontro Python en:
    echo   %PYTHON%
    echo.
    echo Ajusta la ruta PYTHON al inicio de este archivo.
    pause
    exit /b 1
)
echo  OK: %PYTHON%
echo.

echo [2/3] Verificando Flet y PyInstaller...
"%PYTHON%" -c "import flet; import PyInstaller; print(' Flet', flet.__version__, '- PyInstaller OK')"
if errorlevel 1 (
    echo ERROR: Flet o PyInstaller no estan instalados.
    echo Instalalos con:  pip install flet pyinstaller
    pause
    exit /b 1
)
echo.

echo [3/3] Compilando con PyInstaller...
echo  (Puede tardar 2-4 minutos la primera vez)
echo.

"%PYTHON%" -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "TiendaLibre" ^
    --add-data "programas.json;." ^
    --add-data "fotos;fotos" ^
    --add-data "C:\Users\camel\AppData\Local\Programs\Python\Python314\Lib\site-packages\flet_desktop\app;flet_desktop\app" ^
    --collect-all flet ^
    --collect-all flet_core ^
    --collect-all flet_desktop ^
    --hidden-import flet ^
    --hidden-import flet_desktop ^
    tienda_libre.py

echo.
if exist "dist\TiendaLibre.exe" (
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║              ✓ COMPILACION EXITOSA                  ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    echo  El ejecutable esta en:  dist\TiendaLibre.exe
    echo.
    echo  COMO DESPLEGAR EN UNA PC DE CLIENTE:
    echo  ─────────────────────────────────────────────────────
    echo  1. Copia  dist\TiendaLibre.exe  al Escritorio
    echo  2. Copia  programas.json        junto al .exe
    echo  3. Crea la carpeta  descargas\  junto al .exe
    echo  4. Coloca los instaladores dentro de  descargas\
    echo.
    echo  Estructura final esperada en el Escritorio:
    echo    Escritorio\
    echo      TiendaLibre.exe
    echo      programas.json
    echo      descargas\
    echo        onlyoffice_8.2.2_x86_64.exe
    echo        audacity-win-3.7.3-x64.exe
    echo        vlc-3.0.21-win64.exe
    echo        ... (otros instaladores)
    echo  ─────────────────────────────────────────────────────
    echo.
) else (
    echo  ERROR: No se genero el ejecutable.
    echo  Revisa los mensajes de error arriba.
)
pause
