@echo off
echo ========================================
echo   Instalacion de Dependencias V2
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instale Python desde python.org
    pause
    exit /b 1
)

echo.
echo Actualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias desde requirements.txt...
pip install -r requirements.txt

echo.
echo ========================================
echo   Instalacion Completada
echo ========================================
echo.
echo Dependencias instaladas:
echo - customtkinter (GUI moderna)
echo - psycopg2-binary (PostgreSQL)
echo - pandas (procesamiento de datos)
echo - paramiko (SFTP)
echo - requests (API HTTP)
echo - pillow (imagenes)
echo - openpyxl (Excel)
echo - lxml (XML)
echo.
echo Ya puede ejecutar el Comparador V2

pause
