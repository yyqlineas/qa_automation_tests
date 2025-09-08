# JSON Comparator - Comparador de Archivos JSON

Script independiente para comparar dos archivos JSON y detectar diferencias por secciones.

## 🚀 Características

- **Comparación profunda**: Analiza todos los niveles del JSON recursivamente
- **Análisis por secciones**: Identifica qué secciones principales tienen diferencias
- **Múltiples tipos de diferencias**: Detecta valores diferentes, tipos diferentes, elementos faltantes, etc.
- **Estadísticas detalladas**: Muestra resumen de coincidencias y diferencias
- **Reporte opcional**: Guarda un reporte completo en archivo de texto
- **Fácil de usar**: Interfaz de línea de comandos simple

## 📋 Requisitos

- Python 3.6 o superior
- No requiere librerías externas (solo usa módulos estándar de Python)

## 🛠️ Uso

### Uso básico
```bash
python json_comparator.py archivo1.json archivo2.json
```

### Guardar reporte detallado
```bash
python json_comparator.py archivo1.json archivo2.json --save-report
```

### Modo silencioso (solo resultado)
```bash
python json_comparator.py archivo1.json archivo2.json --quiet
```

### Ver ayuda
```bash
python json_comparator.py --help
```

## 📊 Tipos de diferencias que detecta

1. **Valor diferente**: Misma clave, diferente valor
2. **Tipo diferente**: Misma clave, diferente tipo de dato
3. **Falta en archivo 1**: Clave existe solo en archivo 2
4. **Falta en archivo 2**: Clave existe solo en archivo 1
5. **Longitud de lista diferente**: Arrays con diferente cantidad de elementos
6. **Elemento extra**: Elementos adicionales en una de las listas

## 🎯 Ejemplos de salida

### Archivos idénticos
```
✅ Los archivos JSON son IDÉNTICOS

📈 ESTADÍSTICAS:
   • Total de elementos comparados: 15
   • Diferencias encontradas: 0
   • Secciones idénticas: 4
   • Secciones con diferencias: 0
```

### Archivos con diferencias
```
❌ Los archivos JSON tienen DIFERENCIAS

📈 ESTADÍSTICAS:
   • Total de elementos comparados: 20
   • Diferencias encontradas: 8
   • Secciones idénticas: 1
   • Secciones con diferencias: 3

❌ SECCIONES CON DIFERENCIAS:
   • config
   • database
   • features
   • users

🔍 DETALLES DE LAS DIFERENCIAS:

1. Ruta: config.version
   Tipo: Valor diferente
   Archivo 1: '1.0.0'
   Archivo 2: '1.0.1'

2. Ruta: config.debug
   Tipo: Valor diferente
   Archivo 1: True
   Archivo 2: False
```

## 🧪 Probar el script

He incluido dos archivos de ejemplo para que puedas probar:

```bash
# Comparar los archivos de ejemplo
python json_comparator.py ejemplo1.json ejemplo2.json

# Con reporte detallado
python json_comparator.py ejemplo1.json ejemplo2.json --save-report
```

## 📝 Códigos de salida

- `0`: Los archivos son idénticos
- `1`: Los archivos tienen diferencias o hubo un error

Esto es útil para usar el script en automatizaciones o scripts de CI/CD.

## 🔧 Personalización

El script está diseñado para ser modificado fácilmente. Puedes:

- Cambiar el formato de salida
- Agregar nuevos tipos de comparación
- Modificar la lógica de comparación de listas
- Personalizar el formato del reporte

## 📄 Licencia

Script de uso libre para proyectos personales y comerciales.
