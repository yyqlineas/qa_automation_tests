@echo off
title Database Record Copier
color 0A

echo.
echo ===================================================
echo    DATABASE RECORD COPIER - SCRIPT UNIFICADO
echo    Todo en un solo archivo Python
echo ===================================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instale Python 3.7 o superior
    pause
    exit /b 1
)

:: Ejecutar el script principal (todo integrado)
python database_record_copier.py
