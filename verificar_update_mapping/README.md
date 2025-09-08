# Comparador de Campos Específicos BD vs XML

Este proyecto permite comparar campos específicos de una base de datos **PostgreSQL** con valores extraídos de archivos XML mediante XPath, proporcionando una interfaz gráfica intuitiva y moderna para la configuración y ejecución.

## 🌟 Características Principales

- **🎨 Interfaz gráfica moderna**: Diseño intuitivo con scroll automático y layout responsive
- **🐘 Soporte para PostgreSQL**: Conectividad nativa a bases de datos PostgreSQL
- **⚙️ Configuración flexible**: Define campos específicos, conexión a BD y XPaths mediante archivos JSON
- **📝 Consultas SQL personalizables**: Define tu propia consulta SQL para obtener los registros a comparar
- **📊 Reportes detallados**: Genera reportes profesionales en Excel con múltiples hojas
- **📄 Logging avanzado**: Sistema completo de logs con guardado automático
- **🔄 Ejecución en tiempo real**: Barra de progreso y logs en vivo durante la ejecución

## Estructura del Proyecto

```
verificar_update_mapping/
├── config/
│   ├── config.json.template    # Plantilla de configuración
│   └── config.json            # Configuración actual (se crea automáticamente)
├── sql/
│   └── consulta_registros.sql # Consulta SQL para obtener registros
├── src/
│   ├── field_comparator.py   # Lógica principal de comparación
│   └── gui_comparator.py     # Interfaz gráfica
├── reportes/                 # Reportes generados
├── logs/                     # Archivos de log
└── requirements.txt          # Dependencias de Python
```

## 🚀 Instalación Rápida

1. **Ejecutar script automático**:
   ```bash
   comparador_campos_especificos.bat
   ```

2. **O instalar manualmente**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuración para PostgreSQL

### 1. Archivo de Configuración (config.json)

```json
{
  "database": {
    "driver": "PostgreSQL Unicode",
    "server": "localhost",
    "database": "mi_base_datos",
    "username": "mi_usuario",
    "password": "mi_contraseña",
    "port": 5432,
    "connection_string": "postgresql://usuario:contraseña@localhost:5432/base_datos"
  },
  "comparison": {
    "campos_comparar": ["dispatch_number", "dispatch_type", "psap_call_at", "zone"],
    "tabla_principal": "nfirs_notification",
    "campo_identificador": "dispatch_number",
    "sql_query_file": "consulta_registros.sql"
  },
  "xml": {
    "xpath_mappings": {
      "dispatch_number": "//dispatch/number/text()",
      "dispatch_type": "//dispatch/type/text()",
      "psap_call_at": "//dispatch/psap_call_at/text()",
      "zone": "//dispatch/zone/text()"
    },
    "identificador_xpath": "//dispatch/number/text()"
  },
  "reportes": {
    "incluir_timestamp": true,
    "formato": "xlsx",
    "incluir_detalles": true
  }
}
```

#### Parámetros de Configuración:

**database**:
- `server`: Servidor PostgreSQL (localhost, IP, etc.)
- `database`: Nombre de la base de datos
- `username/password`: Credenciales de acceso a PostgreSQL
- `port`: Puerto de PostgreSQL (por defecto 5432)
- `connection_string`: String de conexión completo (opcional)

**comparison**:
- `campos_comparar`: Lista de campos que se van a comparar entre BD y XML
- `tabla_principal`: Tabla principal de la que se obtienen los datos
- `campo_identificador`: Campo que identifica únicamente cada registro
- `sql_query_file`: Nombre del archivo SQL con la consulta

**xml**:
- `xpath_mappings`: Mapeo de cada campo con su XPath correspondiente en el XML
- `identificador_xpath`: XPath para extraer el identificador del XML

### 2. Consulta SQL para PostgreSQL (consulta_registros.sql)

Define la consulta SQL para obtener los registros a comparar. Debe incluir:
- El campo identificador
- Todos los campos listados en `campos_comparar`

Ejemplo:
```sql
-- Consulta SQL para PostgreSQL
SELECT 
    dispatch_number,
    dispatch_type,
    psap_call_at,
    zone
FROM nfirs_notification
WHERE dispatch_number IS NOT NULL
  AND created_at >= '2025-08-01'::date
ORDER BY dispatch_number;
```

## 🖥️ Uso de la Aplicación

1. **Ejecutar la aplicación**:
   ```bash
   comparador_campos_especificos.bat
   # O directamente:
   python src/gui_comparator.py
   ```

2. **Interfaz moderna**:
   - **Ventana maximizada** automáticamente
   - **Scroll automático** para contenido extenso
   - **Layout en dos columnas** para mejor organización
   - **Logs en tiempo real** con colores

3. **Configurar paso a paso**:
   - 🐘 **PostgreSQL**: Configurar conexión y campos
   - 📝 **SQL**: Definir consulta de registros
   - 📁 **XML**: Seleccionar carpeta con archivos

4. **Ejecutar y monitorear**:
   - 🚀 Botón de ejecución grande y visible
   - � Barra de progreso durante ejecución
   - 📄 Logs detallados en tiempo real
   - 💾 Opción de guardar logs

## Reporte Generado

El reporte Excel incluye las siguientes hojas:

1. **Estadísticas**: Resumen general de la comparación
   - Total de registros procesados
   - XMLs encontrados vs no encontrados
   - Total de coincidencias y diferencias
   - Porcentajes y fecha de procesamiento

2. **Resumen**: Vista general por registro
   - ID del registro
   - Archivo XML correspondiente
   - Número de coincidencias, diferencias y errores

3. **Detalles**: Información detallada de cada comparación
   - Registro ID y campo
   - Tipo (Coincidencia/Diferencia)
   - Valores en BD vs XML

4. **Errores**: Lista de errores encontrados durante el proceso

## Logs

Los logs se almacenan en la carpeta `logs/` con timestamp. Incluyen:
- Operaciones de conexión a BD
- Procesamiento de archivos XML
- Errores y advertencias
- Estadísticas de ejecución

## 📋 Requisitos del Sistema

- **Python 3.7+**
- **PostgreSQL** con acceso de red
- **Archivos XML** válidos y bien formados
- **Sistema operativo**: Windows (optimizado para Windows)

## Solución de Problemas

### Error de conexión a BD
- Verificar credenciales en `config.json`
- Comprobar que el servidor esté accesible
- Verificar que el driver ODBC esté instalado

### XMLs no encontrados
- Verificar que el XPath del identificador sea correcto
- Comprobar que los archivos XML estén bien formados
- Verificar que los identificadores coincidan entre BD y XML

### Campos no encontrados
- Verificar que los XPaths sean correctos
- Comprobar la estructura de los archivos XML
- Verificar que los nombres de campos en la configuración coincidan con la BD

## Desarrollo

Para contribuir al proyecto:
1. Fork del repositorio
2. Crear rama para la feature
3. Realizar cambios y pruebas
4. Crear pull request

## Licencia

Este proyecto es de uso interno para automatización de procesos de comparación de datos.
