@echo off
echo ============================================
echo Limpiando archivos duplicados y temporales
echo ============================================

REM Eliminar archivos cache de Python
echo Eliminando archivos cache...
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Eliminar archivos temporales
echo Eliminando archivos temporales...
del /q "*.tmp" 2>nul
del /q "*.temp" 2>nul
del /q "*.log" 2>nul

REM Eliminar archivos de prueba
echo Eliminando archivos de prueba...
del /q "test_*.py" 2>nul
del /q "analyze_*.py" 2>nul
del /q "check_*.py" 2>nul

REM Mostrar archivos restantes
echo.
echo Archivos principales del proyecto:
dir /b *.bat
dir /b src\*.py
dir /b config\*.json
dir /b mappings\*.xlsx

echo.
echo Limpieza completada.
pause
