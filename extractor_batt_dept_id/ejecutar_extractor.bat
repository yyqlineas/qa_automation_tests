@echo off
REM Script batch para ejecutar el extractor de batt_dept_id
REM Uso: ejecutar_extractor.bat [archivo.json] [opciones]
REM También puedes arrastrar un archivo JSON sobre este script

echo ========================================
echo Extractor de batt_dept_id y XPATH
echo ========================================
echo.

REM Si se proporciona un archivo como argumento, usarlo
if not "%1"=="" (
    REM Verificar si el archivo existe
    if not exist "%1" (
        echo Error: El archivo %1 no existe
        echo.
        pause
        exit /b 1
    )
    
    echo Procesando archivo: %1
    echo.
    python batt_dept_extractor.py %*
    goto :fin
)

REM Si no se proporciona archivo, ejecutar el script en modo interactivo
echo No se proporciono archivo como parametro.
echo El script te pedira la ruta del archivo JSON.
echo Puedes arrastrar el archivo JSON a la ventana cuando se solicite.
echo.
python batt_dept_extractor.py

:fin
REM Verificar el codigo de salida
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Procesamiento completado exitosamente
) else (
    echo.
    echo ✗ Error en el procesamiento
)

echo.
echo Presiona cualquier tecla para cerrar...
pause >nul