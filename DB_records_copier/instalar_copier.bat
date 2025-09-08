@echo off
echo Instalando dependencias para Database Record Copier...
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instale Python 3.7 o superior
    pause
    exit /b 1
)

:: Instalar dependencias
echo Instalando dependencias...
pip install pyodbc>=4.0.34 sshtunnel>=0.4.0 paramiko>=2.11.0

if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    echo Puede necesitar instalar Visual C++ Redistributable
    pause
    exit /b 1
)

echo.
echo ✓ Dependencias instaladas correctamente
echo.
echo IMPORTANTE: Configure el archivo config_database_copier.json antes de ejecutar
echo.
echo Para ejecutar el script use:
echo python database_record_copier.py
echo.
pause
