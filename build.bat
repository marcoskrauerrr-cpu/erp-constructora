@echo off
REM ============================================
REM BUILD SCRIPT - ERP Constructora
REM Genera .exe instalable para Windows
REM ============================================
echo ========================================
echo  ERP Constructora - Build
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instale Python 3.11+ desde python.org
    pause
    exit /b 1
)

REM Crear entorno virtual
echo [1/4] Creando entorno virtual...
if not exist venv (
    python -m venv venv
)

REM Activar entorno
call venv\Scripts\activate.bat

REM Instalar dependencias
echo [2/4] Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

REM Ejecutar PyInstaller
echo [3/4] Compilando ejecutable...
pyinstaller --name "ERP Constructora" ^
    --onefile ^
    --windowed ^
    --icon build\icon.ico ^
    --add-data "data;data" ^
    --noconfirm ^
    main.py

REM Copiar base de datos de ejemplo
echo [4/4] Preparando distribucion...
if not exist dist\data mkdir dist\data
copy data\erp_constructora.db dist\data\ 2>nul

echo.
echo ========================================
echo  LISTO!
echo  Ejecutable: dist\ERP Constructora.exe
echo ========================================
pause
