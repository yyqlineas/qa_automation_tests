# Comparador de Campos Específicos V2

## Descripción
El Comparador de Campos Específicos V2 es una versión mejorada y automatizada del sistema original que permite procesar archivos XML, JSON y verificar registros en base de datos a través de un workflow completo de 8 pasos.

## Características Principales
- **Workflow Automatizado**: 8 pasos secuenciales completamente automatizados
- **Interfaz Gráfica**: GUI intuitiva para controlar todo el proceso
- **Scripts Individuales**: Cada paso puede ejecutarse independientemente
- **Integración API**: Descarga automática de datos desde APIs REST
- **SFTP Upload**: Subida automática de archivos a servidores remotos
- **Verificación BD**: Conexión y verificación en PostgreSQL
- **Filtrado Avanzado**: Múltiples criterios de filtrado de registros
- **Reportes**: Generación automática de reportes detallados

## Estructura del Proyecto
```
comparador_campos_especificos_v2/
├── config/
│   └── config.json                 # Configuración principal
├── scripts/
│   ├── step1_download_json.py      # Descarga JSON desde API
│   ├── step2_find_batt_dept_id.py  # Busca batt_dept_id
│   ├── step3_find_xref_path.py     # Encuentra XPath xref_id
│   ├── step4_extract_xref_id.py    # Extrae xref_id de XML
│   ├── step5_upload_sftp.py        # Sube archivos vía SFTP
│   ├── step6_verify_database.py    # Verifica en base de datos
│   └── step7_filter_records.py     # Filtra registros
├── downloads/                      # Archivos descargados
├── logs/                          # Logs de ejecución
├── reportes/                      # Reportes generados
├── main.py                        # Interfaz gráfica principal
├── ejecutar_comparador_v2.bat     # Ejecutar aplicación
├── instalar_dependencias.bat      # Instalar librerías
├── ejecutar_paso_individual.bat   # Ejecutar paso específico
└── README.md                      # Este archivo
```

## Workflow de 8 Pasos

### Paso 1: Descarga JSON desde API
- Conecta a API REST configurada
- Descarga archivos JSON basados en batt_dept_id
- Maneja autenticación y errores de conexión
- Guarda archivos en directorio downloads/

### Paso 2: Buscar batt_dept_id
- Busca valores de batt_dept_id en archivos JSON
- Búsqueda recursiva en estructuras anidadas
- Extrae valores únicos y elimina duplicados
- Genera lista de IDs encontrados

### Paso 3: Encontrar XPath de xref_id
- Analiza estructura JSON para encontrar xref_id
- Genera mappings de XPath automáticamente
- Convierte rutas JSON a XPath XML
- Guarda configuración de mappings

### Paso 4: Extraer xref_id de XML
- Extrae valores xref_id de archivos XML
- Usa XPath mappings del paso anterior
- Búsquedas alternativas automáticas
- Procesa múltiples archivos XML

### Paso 5: Subir a SFTP
- Sube archivos XML a servidor SFTP
- Crea directorios remotos automáticamente
- Verifica integridad de subida
- Maneja errores de conexión y transferencia

### Paso 6: Verificar en Base de Datos
- Conecta a PostgreSQL
- Verifica existencia de registros por xref_id
- Búsqueda en múltiples campos alternativos
- Genera estadísticas de verificación

### Paso 7: Filtrar Registros
- Aplica filtros por fecha, campos, patrones
- Filtrado por listas de inclusión/exclusión
- Combinación de múltiples criterios
- Genera reportes de filtrado

### Paso 8: Generar Reporte Final
- Consolida resultados de todos los pasos
- Estadísticas completas del workflow
- Exporta en múltiples formatos
- Guarda en directorio reportes/

## Instalación

### 1. Instalar Dependencias
Ejecutar el archivo batch:
```batch
instalar_dependencias.bat
```

O manualmente:
```bash
pip install psycopg2-binary paramiko requests
```

### 2. Configuración
Editar el archivo `config/config.json` con los parámetros de su entorno:

```json
{
  "api": {
    "base_url": "https://api.ejemplo.com",
    "username": "usuario",
    "password": "contraseña"
  },
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "mi_base",
    "username": "usuario",
    "password": "contraseña"
  },
  "sftp": {
    "hostname": "servidor.com",
    "port": 22,
    "username": "usuario",
    "password": "contraseña"
  }
}
```

## Uso

### Interfaz Gráfica
Ejecutar la aplicación principal:
```batch
ejecutar_comparador_v2.bat
```

### Pasos Individuales
Ejecutar un paso específico:
```batch
ejecutar_paso_individual.bat
```

### Línea de Comandos
Ejecutar paso desde terminal:
```bash
cd scripts
python step1_download_json.py --config ../config/config.json
```

## Comandos de Ejemplo

### Descargar JSON por batt_dept_id
```bash
python step1_download_json.py --batt_dept_id 12345 --output ../downloads/
```

### Buscar batt_dept_id en JSON
```bash
python step2_find_batt_dept_id.py --file datos.json --output ids_encontrados.txt
```

### Extraer xref_id de XML
```bash
python step4_extract_xref_id.py --directory ../xml_files/ --xpath "//CAD"
```

### Verificar en base de datos
```bash
python step6_verify_database.py --xref_id "ABC123" --table reportes
```

### Filtrar registros
```bash
python step7_filter_records.py --input registros.json --start_date 2024-01-01 --end_date 2024-12-31
```

## Configuración Avanzada

### Configuración de API
```json
{
  "api": {
    "base_url": "https://api.ejemplo.com",
    "endpoints": {
      "download": "/api/v1/download/{batt_dept_id}",
      "status": "/api/v1/status"
    },
    "authentication": {
      "type": "bearer",
      "token": "your_token_here"
    },
    "timeout": 30,
    "retry_attempts": 3
  }
}
```

### Configuración de SFTP
```json
{
  "sftp": {
    "hostname": "servidor.com",
    "port": 22,
    "username": "usuario",
    "authentication": {
      "type": "key",
      "key_file": "/path/to/private_key.pem"
    },
    "remote_directories": {
      "xml_upload": "/uploads/xml/",
      "backup": "/backup/"
    }
  }
}
```

### Configuración de Filtros
```json
{
  "workflow": {
    "default_filters": {
      "date_range": {
        "field": "created_at",
        "days_back": 30
      },
      "field_values": {
        "status": ["active", "pending"],
        "priority": ["high", "medium"]
      }
    }
  }
}
```

## Logs y Monitoreo

### Ubicación de Logs
- `logs/download_*.log` - Logs de descarga API
- `logs/xref_extraction_*.log` - Logs de extracción XML
- `logs/sftp_upload_*.log` - Logs de subida SFTP
- `logs/db_verification_*.log` - Logs de verificación BD
- `logs/record_filter_*.log` - Logs de filtrado

### Formato de Logs
```
[2024-01-15 10:30:45] INFO: Iniciando descarga para batt_dept_id: 12345
[2024-01-15 10:30:46] INFO: Conectando a API: https://api.ejemplo.com
[2024-01-15 10:30:47] INFO: ✅ Descarga completada: archivo_12345.json (1.2 MB)
```

## Troubleshooting

### Errores Comunes

**Error de conexión API**
```
ERROR: No se pudo conectar a la API
```
- Verificar URL y credenciales en config.json
- Comprobar conectividad de red
- Revisar logs de API para detalles

**Error de base de datos**
```
ERROR: No se pudo conectar a PostgreSQL
```
- Verificar parámetros de conexión
- Comprobar que PostgreSQL esté ejecutándose
- Verificar permisos de usuario

**Error de SFTP**
```
ERROR: Autenticación SFTP fallida
```
- Verificar credenciales SFTP
- Comprobar conectividad al servidor
- Verificar permisos de directorio remoto

### Modo Debug
Agregar logging detallado modificando scripts:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Versión y Changelog

### V2.0.0 (Actual)
- ✅ Workflow automatizado de 8 pasos
- ✅ Interfaz gráfica completa
- ✅ Scripts individuales ejecutables
- ✅ Integración API, SFTP y PostgreSQL
- ✅ Filtrado avanzado de registros
- ✅ Generación automática de reportes
- ✅ Archivos batch para ejecución fácil

### Mejoras respecto a V1
- **Automatización completa**: Workflow de 8 pasos vs manual
- **Interfaz gráfica**: GUI vs solo línea de comandos
- **Integración API**: Descarga automática vs manual
- **SFTP Upload**: Subida automática de archivos
- **Verificación BD**: Conexión y verificación PostgreSQL
- **Filtrado avanzado**: Múltiples criterios vs básico

## Soporte
Para soporte técnico o reportar problemas:
1. Revisar logs en directorio `logs/`
2. Verificar configuración en `config/config.json`
3. Ejecutar validación desde interfaz gráfica
4. Consultar este README para ejemplos de uso

## Licencia
Uso interno - FDSU Automatización Yatary
