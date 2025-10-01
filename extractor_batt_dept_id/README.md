# Extractor de batt_dept_id y XPATH para xref_id

## Descripción

Este script extrae automáticamente los `batt_dept_id` de archivos JSON y los formatea en una cláusula `IN()` para consultas SQL. También extrae los xpath correspondientes para `xref_id`.

## Características

- ✅ Extrae `batt_dept_id` de diferentes ubicaciones en el JSON
- ✅ Formatea los IDs en cláusula SQL `IN()` lista para usar
- ✅ Extrae xpath para `xref_id`
- ✅ Elimina duplicados automáticamente
- ✅ Genera reportes detallados
- ✅ Soporte para múltiples formatos de JSON
- ✅ Modo silencioso para integración con otros scripts
- ✅ **NUEVO**: Análisis de múltiples archivos en una sesión
- ✅ **NUEVO**: Opción para continuar o salir después de cada análisis

## Requisitos

- Python 3.6 o superior
- Solo utiliza bibliotecas estándar de Python (no requiere instalaciones adicionales)

## Instalación

1. Clona o descarga el script en tu directorio de trabajo
2. No requiere instalación de dependencias adicionales

```bash
# Opcional: Si quieres instalar dependencias para desarrollo
pip install -r requirements.txt
```

## Uso

### Uso básico

```bash
python batt_dept_extractor.py archivo.json
```

### Modo interactivo (Drag & Drop)

```bash
python batt_dept_extractor.py
```
Luego arrastra el archivo JSON a la terminal cuando se solicite.

### Guardar reporte en archivo

```bash
python batt_dept_extractor.py archivo.json --output reporte.txt
```

### Modo silencioso (solo resultados)

```bash
python batt_dept_extractor.py archivo.json --quiet
```

### Ayuda

```bash
python batt_dept_extractor.py --help
```

## Ejemplos de uso

### Ejemplo 1: Usar con archivo específico

```bash
python batt_dept_extractor.py zetron_geoconex_sftp_xml_obion_county_911_tn_v2_enabled.json
```

### Ejemplo 2: Modo interactivo (arrastrando archivos)

```bash
python batt_dept_extractor.py
```
Luego arrastra tu archivo JSON a la terminal.

### Ejemplo 4: Análisis de múltiples archivos en una sesión

```bash
python batt_dept_extractor.py
```
Después de procesar el primer archivo, el script te preguntará si quieres analizar otro JSON.

**Flujo típico:**
1. Ejecutas el script
2. Arrastras/escribes la ruta del primer archivo JSON
3. Ves los resultados
4. El script pregunta: "¿Quieres analizar otro archivo JSON? (s/n)"
5. Si respondes 's', puedes procesar otro archivo
6. Si respondes 'n', el script termina

**Salida:**
```
BATT_DEPT_IDs: 4611, 4612, 4613
SQL: WHERE batt_dept_id IN (4611, 4612, 4613)
XREF_ID XPATH: //FirstDueExport/NFIRSData/DispatchNumber
```

## Estructuras JSON soportadas

El script busca `batt_dept_id` en las siguientes ubicaciones:

1. **En templates principales:**
   ```json
   {
     "templates": [
       {
         "batt_depts": [4611, 4612]
       }
     ]
   }
   ```

2. **En parser_options:**
   ```json
   {
     "templates": [
       {
         "parser_options": {
           "object_types": [
             {"batt_dept": 4611}
           ]
         }
       }
     ]
   }
   ```

3. **En update_rules:**
   ```json
   {
     "templates": [
       {
         "update_rules": [
           {"batt_depts": [4611]}
         ]
       }
     ]
   }
   ```

4. **En la raíz del documento:**
   ```json
   {
     "batt_depts": [4611, 4612]
   }
   ```

## Xpath para xref_id

El script busca xpath en:

```json
{
  "templates": [
    {
      "parser_options": {
        "xpaths": {
          "xref_id": "//FirstDueExport/NFIRSData/DispatchNumber"
        }
      }
    }
  ]
}
```

## Opciones de línea de comandos

| Opción | Descripción |
|--------|-------------|
| `json_file` | Archivo JSON a procesar (requerido) |
| `--output`, `-o` | Archivo donde guardar el reporte |
| `--quiet`, `-q` | Modo silencioso - solo muestra resultados clave |
| `--help`, `-h` | Muestra ayuda |

## Salida del script

### Modo normal
- Reporte completo con formato legible
- Lista de batt_dept_id encontrados
- Cláusula SQL formateada
- Xpath para xref_id
- Estadísticas del proceso

### Modo silencioso
- Solo los IDs encontrados
- Solo la cláusula SQL
- Solo los xpath encontrados

## Casos de uso

1. **Preparación de consultas SQL:**
   ```sql
   SELECT * FROM incidents WHERE batt_dept_id IN (4611, 4612, 4613);
   ```

2. **Validación de configuraciones:**
   - Verificar qué departamentos están configurados
   - Revisar xpath de xref_id

3. **Migración de datos:**
   - Identificar departamentos para migrar
   - Obtener rutas xpath necesarias

## Manejo de errores

El script maneja los siguientes errores:

- ❌ Archivo no encontrado
- ❌ JSON malformado
- ❌ Estructura JSON inesperada
- ❌ Permisos de archivo
- ❌ Errores de codificación

## Características técnicas

- **Codificación:** UTF-8
- **Compatibilidad:** Python 3.6+
- **Rendimiento:** Optimizado para archivos JSON grandes
- **Memoria:** Procesamiento eficiente en memoria
- **Seguridad:** Validación de entrada y manejo seguro de archivos

## Contribución

Para contribuir al proyecto:

1. Reporta bugs o solicita características
2. Propón mejoras en el código
3. Añade nuevos casos de prueba
4. Mejora la documentación

## Licencia

Este script es de uso interno para automatización de procesos de base de datos.

---

**Desarrollado para:** Automatización de extracción de configuraciones JSON  
**Fecha:** Septiembre 2025  
**Versión:** 1.0.0