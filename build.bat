@echo off
REM ============================================
REM BUILD SCRIPT - ERP Constructora v1.1.0
REM Genera .exe instalable para Windows
REM ============================================
echo ========================================
echo  ERP Constructora - Build v1.1.0
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instale Python 3.11+ desde python.org
    pause
    exit /b 1
)

REM Crear/activar entorno virtual
echo [1/4] Preparando entorno...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

REM Instalar dependencias
echo [2/4] Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

REM Crear .ico simple si no existe (icono por defecto de PyInstaller)
if not exist build\icon.ico (
    echo [INFO] Icono no encontrado, se usara el icono por defecto
)

REM Ejecutar PyInstaller (modo --onedir para que la BD sea accesible)
echo [3/4] Compilando...
pyinstaller --name "ERP Constructora" ^
    --windowed ^
    --noconfirm ^
    --add-data "data;data" ^
    main.py

REM Copiar base de datos de ejemplo
echo [4/4] Preparando distribucion...
xcopy /E /I /Y data dist\"ERP Constructora"\data 2>nul

echo.
echo ========================================
echo  LISTO!
echo  Ejecutable: dist\ERP Constructora\ERP Constructora.exe
echo ========================================
echo.
echo  NOTA: La primera vez crea la BD automaticamente.
echo  Si quieres resetear, borra data\erp_constructora.db
echo.
pause
