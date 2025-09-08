@echo off
echo =========================================
echo  Limpiar Proyecto - Comparador BD vs XML
echo =========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

echo Limpiando archivos temporales y reportes...

REM Limpiar logs antiguos (mantener los últimos 5)
if exist "logs\*.log" (
    echo Limpiando logs antiguos...
    for /f "skip=5 delims=" %%i in ('dir /b /o-d logs\*.log 2^>nul') do del "logs\%%i" 2>nul
)

REM Limpiar reportes antiguos (mantener los últimos 10)
if exist "reportes\*.xlsx" (
    echo Limpiando reportes antiguos...
    for /f "skip=10 delims=" %%i in ('dir /b /o-d reportes\*.xlsx 2^>nul') do del "reportes\%%i" 2>nul
)

REM Limpiar archivos temporales de Python
if exist "src\__pycache__" (
    echo Limpiando cache de Python...
    rmdir /s /q "src\__pycache__" 2>nul
)

if exist "*.pyc" (
    echo Limpiando archivos .pyc...
    del /s "*.pyc" 2>nul
)

echo.
echo Limpieza completada.
echo.
pause
