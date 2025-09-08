# Comparador de Valores XML vs Base de Datos

Esta herramienta permite comparar valores entre archivos XML y una base de datos PostgreSQL, utilizando mapeos de xpath definidos en un archivo Excel.

## Estructura del Proyecto

```
XML_BD_Comparator/
│
├── config/                    # Carpeta para archivos de configuración
│   ├── config.json           # Configuración de BD y filtros
│   ├── config.json.template  # Plantilla de configuración
│   └── xpath_mappings.xlsx   # Mapeos de xpath para campos
│
├── logs/                     # Carpeta para archivos de log
│   └── (logs generados automáticamente)
│
├── reportes/                 # Carpeta para los reportes generados
│   └── (reportes generados automáticamente)
│
├── ejecutar_comparador.bat   # Script principal de ejecución
├── gui_compare.py           # Interfaz gráfica
├── xml_compare.py          # Lógica de comparación
└── requirements.txt        # Dependencias del proyecto
```

## Requisitos Previos

1. Python 3.7 o superior (Instalación necesaria)
2. Las siguientes librerías de Python (se instalarán automáticamente):
   - pandas
   - psycopg2-binary
   - lxml

## Configuración Inicial

1. Copiar `config.json.template` a `config.json` (se hace automáticamente en primera ejecución)
2. Editar `config.json` con:
   - Credenciales de base de datos
   - IDs de batt_dept_id para filtrar
   - Fecha de inicio para el filtrado
   - Rutas de archivos

### Ejemplo de config.json:
```json
{
  "database": {
    "host": "tu_servidor",
    "port": 5432,
    "dbname": "tu_base_de_datos",
    "user": "tu_usuario",
    "password": "tu_contraseña"
  },
  "filters": {
    "batt_dept_id": {
      "column_name": "batt_dept_id",
      "values": [2095],
      "comments": "Este campo se usará para filtrar en todas las tablas"
    },
    "datetime": {
      "column_name": "created_at",
      "start_datetime": "2025-08-18 00:00:00",
      "format": "%Y-%m-%d %H:%M:%S",
      "comments": "Formato: YYYY-MM-DD HH:MI:SS"
    }
  }
}
```

## Uso

1. Doble clic en `ejecutar_comparador.bat`
2. El programa verificará:
   - La existencia de Python
   - La configuración necesaria
   - Las dependencias requeridas
3. Se abrirá la interfaz gráfica donde podrás:
   - Seleccionar la carpeta con los XMLs a comparar
   - Editar la configuración si es necesario
   - Ejecutar la comparación

## Resultados

Los resultados se guardan en:
- Reportes detallados en la carpeta `reportes/`
- Logs de ejecución en la carpeta `logs/`

Los reportes mostrarán:
1. Diferencias encontradas (primero)
2. Valores que coinciden
3. Resumen general de la comparación

## Soporte

Si encuentras algún problema:
1. Revisa los logs en la carpeta `logs/`
2. Verifica la configuración en `config/config.json`
3. Asegúrate de que los archivos XML y el archivo de mapeos existen y son accesibles
