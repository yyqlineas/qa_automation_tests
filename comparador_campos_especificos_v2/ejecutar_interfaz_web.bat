@echo off
echo ========================================
echo   XML Validation Fields - Interfaz Web
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando dependencias...
python -c "import customtkinter" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo CustomTkinter no esta instalado. Instalando...
    pip install customtkinter pillow
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: No se pudo instalar CustomTkinter
        pause
        exit /b 1
    )
)

echo.
echo Iniciando interfaz web moderna...
python main_web.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: La aplicacion web termino con errores
    pause
) else (
    echo.
    echo Aplicacion web finalizada correctamente
)

pause
