@echo off
echo ===============================================
echo  Comparador de Campos Específicos BD vs XML
echo ===============================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.7 o superior
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
echo Verificando dependencias...
python -c "import pyodbc, pandas, openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error al instalar dependencias
        pause
        exit /b 1
    )
)

REM Ejecutar la aplicación
echo Iniciando aplicación...
python src\gui_comparator.py

REM Pausa si hay error
if %errorlevel% neq 0 (
    echo.
    echo Error al ejecutar la aplicación
    pause
)
