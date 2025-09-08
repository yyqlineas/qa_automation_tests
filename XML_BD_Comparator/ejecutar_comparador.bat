@echo off
cd /d "%~dp0"
echo ============================================
echo Comparador de XML vs Base de Datos
echo ============================================

REM Verificar si Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor, instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar si las dependencias de Python están instaladas
echo Verificando dependencias...
echo Instalando/Actualizando dependencias necesarias...
python -m pip install pandas psycopg2-binary lxml openpyxl --no-cache-dir --user

REM Ejecutar el programa
echo.
echo Iniciando el programa...
cd src
python -u gui_compare.py

if errorlevel 1 (
    echo.
    echo Ha ocurrido un error durante la ejecución.
    echo Por favor, revisa los mensajes de error arriba.
    echo Los logs se encuentran en: ..\logs
    pause
) else (
    echo.
    echo Programa finalizado correctamente.
    echo Los reportes se encuentran en: ..\reportes
)

echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause > nul
