# Script para mover archivos del comparador XML-BD
$sourceDir = "C:\FDSU\Automatizacion\Yatary_Pruebas"
$targetDir = "C:\FDSU\Automatizacion\Yatary_Pruebas\XML_BD_Comparator"

# Mover archivos de configuración
Move-Item "$sourceDir\config.json" "$targetDir\config\config.json" -Force
Move-Item "$sourceDir\config.json.template" "$targetDir\config\config.json.template" -Force

# Mover archivos Python
Move-Item "$sourceDir\gui_compare.py" "$targetDir\gui_compare.py" -Force
Move-Item "$sourceDir\xml_compare.py" "$targetDir\xml_compare.py" -Force

# Mover archivos de requisitos y batch
Move-Item "$sourceDir\requirements.txt" "$targetDir\requirements.txt" -Force
Move-Item "$sourceDir\ejecutar_comparador.bat" "$targetDir\ejecutar_comparador.bat" -Force

# Mover archivo de mapeos si existe
if (Test-Path "$sourceDir\xpath_mappings.xlsx") {
    Move-Item "$sourceDir\xpath_mappings.xlsx" "$targetDir\config\xpath_mappings.xlsx" -Force
}

# Eliminar README.md antiguo si existe
if (Test-Path "$sourceDir\README.md") {
    Remove-Item "$sourceDir\README.md" -Force
    Write-Host "README.md antiguo eliminado"
}

Write-Host "Archivos movidos exitosamente a $targetDir"
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
