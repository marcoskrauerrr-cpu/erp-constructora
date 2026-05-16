@echo off
REM ============================================================
REM Build Script — ERP Constructora para Windows
REM Requiere: Python 3.11+ y PyInstaller
REM ============================================================
echo ========================================
echo  ERP Constructora - Build Windows
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instale Python 3.11+ desde python.org
    pause
    exit /b 1
)

REM Crear virtualenv si no existe
if not exist venv (
    echo [1/4] Creando entorno virtual...
    python -m venv venv
)

echo [2/4] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

echo [4/4] Compilando ejecutable...
pyinstaller ^
    --name "ERP Constructora" ^
    --onefile ^
    --windowed ^
    --add-data "src;src" ^
    --hidden-import "openpyxl" ^
    --hidden-import "dateutil" ^
    --distpath "dist" ^
    --workpath "build" ^
    --icon "NONE" ^
    main.py

echo.
echo ========================================
echo  LISTO! Ejecutable en: dist\ERP Constructora.exe
echo ========================================
pause
