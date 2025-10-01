@echo off
title Verificador de EmailTag para BATT_DEPT_ID y CLIENT_CODE
color 0A
cls

echo.
echo ============================================================
echo           VERIFICADOR DE EMAILTAG - FDSU
echo ============================================================
echo.
echo Iniciando verificador de correspondencia emailtag...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH del sistema
    echo.
    echo Por favor instale Python desde: https://python.org/downloads/
    echo Durante la instalacion, marque "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Intentar instalar psycopg2 si no está disponible
echo Verificando dependencias...
python -c "import psycopg2" >nul 2>&1
if errorlevel 1 (
    echo Instalando psycopg2-binary...
    pip install psycopg2-binary
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar psycopg2-binary
        echo Intente ejecutar manualmente: pip install psycopg2-binary
        pause
        exit /b 1
    )
)

REM Ejecutar el script principal
echo.
echo Ejecutando verificador de emailtag...
echo.
python "%~dp0verificador_emailtag.py"

REM Pausa final
echo.
echo ============================================================
echo           Proceso completado
echo ============================================================
pause