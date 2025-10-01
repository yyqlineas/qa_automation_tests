@echo off
echo 🧹 Iniciando limpieza de archivos innecesarios...
echo.

REM Eliminar archivos de copia (- Copy)
echo Eliminando archivos duplicados "- Copy"...
del /q "check_narratives - Copy.py" 2>nul
del /q "check_report - Copy.py" 2>nul
del /q "check_status_code - Copy.py" 2>nul
del /q "debug_hamilton_real - Copy.py" 2>nul
del /q "debug_missing_fields - Copy.py" 2>nul
del /q "debug_nfirs - Copy.py" 2>nul
del /q "debug_nfirs_notification - Copy.py" 2>nul
del /q "ejecutar_comparador - Copy.bat" 2>nul
del /q "limpiar_proyecto - Copy.bat" 2>nul
del /q "README - Copy.md" 2>nul
del /q "requirements - Copy.txt" 2>nul
del /q "test_coordinate_normalization - Copy.py" 2>nul
del /q "test_universal_case_insensitive - Copy.py" 2>nul

REM Eliminar carpetas duplicadas
echo Eliminando carpetas duplicadas...
rmdir /s /q "config - Copy" 2>nul
rmdir /s /q "logs - Copy" 2>nul
rmdir /s /q "mappings - Copy" 2>nul
rmdir /s /q "reportes - Copy" 2>nul
rmdir /s /q "src - Copy" 2>nul
rmdir /s /q "xml - Copy" 2>nul

REM Eliminar backups y archivos ZIP
echo Eliminando backups y archivos ZIP...
rmdir /s /q "XML_BD_Comparator_last_backup" 2>nul
del /q "XML_BD_Comparator_v*.zip" 2>nul

REM Eliminar archivos de debug y prueba (mantener solo los de prueba de coordenadas)
echo Eliminando archivos de debug y prueba innecesarios...
del /q "check_narratives.py" 2>nul
del /q "check_report.py" 2>nul
del /q "check_status_code.py" 2>nul
del /q "debug_hamilton_real.py" 2>nul
del /q "debug_missing_fields.py" 2>nul
del /q "debug_nfirs.py" 2>nul
del /q "debug_nfirs_notification.py" 2>nul
del /q "test_universal_case_insensitive.py" 2>nul

REM Limpiar logs antiguos (mantener solo los últimos 10)
echo Limpiando logs antiguos...
cd logs
for /f "skip=10 delims=" %%i in ('dir /b /o-d comparison_*.log') do del /q "%%i" 2>nul
cd ..

REM Limpiar reportes antiguos (mantener solo los últimos 15)
echo Limpiando reportes antiguos...
cd reportes
for /f "skip=15 delims=" %%i in ('dir /b /o-d reporte_*.xlsx') do del /q "%%i" 2>nul
REM Eliminar archivos temporales de Excel
del /q "~$*.xlsx" 2>nul
cd ..

REM Limpiar cache de Python
echo Limpiando cache de Python...
rmdir /s /q "src\__pycache__" 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul

echo.
echo ✅ Limpieza completada!
echo.
echo 📁 Archivos mantenidos (esenciales):
echo   - src/xml_compare.py (motor principal)
echo   - src/gui_compare.py (interfaz gráfica)
echo   - config/ (configuración)
echo   - mappings/ (mapeos Excel)
echo   - ejecutar_comparador.bat (launcher)
echo   - limpiar_proyecto.bat (limpieza)
echo   - README.md (documentación)
echo   - requirements.txt (dependencias)
echo   - test_coordinate_normalization.py (prueba de coordenadas)
echo   - logs/ (últimos 10 archivos)
echo   - reportes/ (últimos 15 archivos)
echo   - xml/ (archivos XML de prueba)
echo.
echo 🗑️ Archivos eliminados:
echo   - Todos los archivos "- Copy"
echo   - Backups y archivos ZIP
echo   - Scripts de debug antiguos
echo   - Logs antiguos (más de 10)
echo   - Reportes antiguos (más de 15)
echo   - Cache de Python
echo.
pause