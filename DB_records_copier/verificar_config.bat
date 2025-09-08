@echo off
title Verificar Configuración - Database Record Copier
color 0E

echo.
echo =====================================================
echo    VERIFICADOR DE CONFIGURACION
echo    Database Record Copier
echo =====================================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instale Python 3.7 o superior
    pause
    exit /b 1
)

:: Ejecutar verificador
python verificar_config_copier.py

pause
