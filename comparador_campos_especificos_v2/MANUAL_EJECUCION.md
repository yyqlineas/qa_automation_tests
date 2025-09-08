# 📋 MANUAL DE EJECUCIÓN - COMPARADOR DE CAMPOS XML vs BD

## 🎯 **DESCRIPCIÓN DEL PROYECTO**

Sistema automatizado para comparar campos específicos entre archivos XML y una base de datos PostgreSQL, con interfaz gráfica moderna desarrollada en Python con CustomTkinter.

### **Funcionalidades Principales:**
- ✅ Carga de archivos JSON con configuración de campos objetivo
- ✅ Búsqueda automática de `batt_dept_id` en JSON
- ✅ Extracción de XPath para `xref_id` desde JSON
- ✅ Configuración manual de campos objetivo para comparación
- ✅ Selección de carpeta con archivos XML
- ✅ Configuración de filtros manuales para consultas de BD
- ✅ Comparación automática XML vs Base de Datos
- ✅ Generación de reportes en Excel

---

## 🔧 **NUEVAS FUNCIONALIDADES IMPLEMENTADAS**

### **Paso 6 - Gestión Avanzada de Filtros:**
- ✅ **Visualización completa** de todos los filtros configurados
- ✅ **Eliminación individual** con botón 🗑️ por cada filtro
- ✅ **Numeración secuencial** de filtros para mejor organización
- ✅ **Autocompletado inteligente** para campos `xref_id`/`dispatch_number`
- ✅ **Validación anti-duplicados** para evitar filtros repetidos
- ✅ **Vista previa XRef IDs** disponibles del Paso 5

### **Paso 7 - Comparación Completa XML vs BD:**
- ✅ **Procesamiento masivo** de archivos XML en carpeta seleccionada
- ✅ **Filtrado inteligente** usando XPath específico del JSON
- ✅ **Consulta BD dinámica** con filtros configurados
- ✅ **Comparación campo por campo** automática
- ✅ **Reporte Excel colorizado** con código visual de estados
- ✅ **Información completa** de filtros aplicados por registro
- ✅ **Manejo de errores** robusto con logging detallado
- ✅ **Interfaz de progreso** en tiempo real durante procesamiento
- ✅ **Apertura automática** del reporte al completar

---

## 🚀 **MÉTODOS DE EJECUCIÓN**

### **Método 1: Archivo Batch (RECOMENDADO)**
```batch
# Navegar a la carpeta del proyecto
cd "c:\FDSU\Automatizacion\Yatary_Pruebas\comparador_campos_especificos_v2"

# Hacer doble clic en:
ejecutar_interfaz_web.bat
```

### **Método 2: Línea de Comandos**
```powershell
# Abrir PowerShell o CMD
cd "c:\FDSU\Automatizacion\Yatary_Pruebas\comparador_campos_especificos_v2"
python main_web.py
```

### **Método 3: Ejecución Directa**
```powershell
cd "c:\FDSU\Automatizacion\Yatary_Pruebas\comparador_campos_especificos_v2"
python src/web_style_gui.py
```

---

## ⚙️ **REQUISITOS DEL SISTEMA**

### **Software Requerido:**
- ✅ **Python 3.8+** (Recomendado Python 3.11 o superior)
- ✅ **PostgreSQL** (para conexión a base de datos)
- ✅ **Windows 10/11** (Sistema operativo soportado)

### **Librerías Python Requeridas:**
```bash
pip install customtkinter
pip install pillow
pip install psycopg2-binary
pip install openpyxl
pip install pandas
pip install lxml
```

**Nota:** El archivo `ejecutar_interfaz_web.bat` instala automáticamente las dependencias necesarias.

---

## 🗂️ **ESTRUCTURA DEL PROYECTO**

```
comparador_campos_especificos_v2/
├── 📁 config/                    # Configuraciones
│   ├── config.json              # Configuración de BD
│   └── db_config.json           # Configuración específica de BD
├── 📁 downloads/                 # Archivos JSON de ejemplo
│   └── ejemplo_batt_dept.json   # Ejemplo de configuración
├── 📁 logs/                      # Archivos de log
├── 📁 reportes/                  # Reportes generados (Excel)
├── 📁 scripts/                   # Scripts individuales
├── 📁 sql/                       # Consultas SQL
├── 📁 src/                       # Código fuente
│   ├── web_style_gui.py         # Interfaz principal
│   ├── field_comparator.py      # Lógica de comparación
│   └── modern_gui.py            # GUI moderna alternativa
├── 📄 main_web.py               # Ejecutor principal
├── 📄 main_modern.py            # Ejecutor interfaz moderna
├── 📄 ejecutar_interfaz_web.bat # Ejecutor automático
└── 📄 README.md                 # Documentación
```

---

## 🔧 **CONFIGURACIÓN INICIAL**

### **1. Configuración de Base de Datos**
Editar `config/db_config.json`:
```json
{
    "host": "localhost",
    "port": 5432,
    "database": "nombre_base_datos",
    "user": "usuario",
    "password": "contraseña"
}
```

### **2. Verificar Conexión**
Al ejecutar la aplicación, usar el botón "Config" → "BD Config" para probar la conexión.

---

## 📋 **PROCESO DE TRABAJO (7 PASOS)**

### **Paso 1: Seleccionar Archivo JSON** 📂
- **Acción:** Cargar archivo JSON con configuración de campos
- **Archivo ejemplo:** `downloads/ejemplo_batt_dept.json`
- **Resultado:** JSON cargado y validado

### **Paso 2: Buscar batt_dept_id** 🗂️
- **Acción:** Extrae automáticamente IDs del departamento
- **Resultado:** Lista de `batt_dept_id` para filtros SQL
- **Uso:** Se genera condición `WHERE batt_dept_id IN (...)`

### **Paso 3: Encontrar XPath xref_id** 🔍
- **Acción:** Extrae XPath del campo `xref_id` desde JSON
- **Resultado:** XPath específico para procesar XMLs
- **Ejemplo:** `//FMPDSORESULT/ROW[1]/CAD`

### **Paso 4: Definir Campos Objetivo** 🎯
- **Acción:** Configurar campos para comparación XML vs BD
- **Formato:** `tabla.campo = xpath_value`
- **Resultado:** Lista de campos a comparar

### **Paso 5: Seleccionar Carpeta XML** 📁
- **Acción:** Elegir carpeta con archivos XML a procesar
- **Validación:** Cuenta archivos .xml disponibles
- **Extracción:** Extrae XRef IDs usando XPath del Paso 3

### **Paso 6: Configurar Filtros BD** 🔍
- **Acción:** Definir filtros manuales para consultas de BD
- **Funcionalidades nuevas:**
  - ✅ **Lista visual de filtros configurados** con número secuencial
  - ✅ **Botón eliminar (🗑️)** para cada filtro individual
  - ✅ **Autocompletado XRef ID** cuando el campo es `xref_id` o `dispatch_number`
  - ✅ **Validación de duplicados** - no permite agregar el mismo filtro dos veces
- **Formato:** `tabla.campo = valor`
- **Ejemplo:** `dispatch.xref_id = ABC123` o `dispatch.created_at = 2024-01-01`
- **Validación:** Requiere al menos 1 filtro manual para continuar
- **Navegación:** Muestra botón "Paso 7: Comparar" solo cuando hay filtros configurados

### **Paso 7: Ejecutar Comparación** ⚖️
- **Acción:** Comparar campos XML vs Base de Datos con reporte completo
- **Proceso automatizado:**
  1. **Validación completa** de configuración (campos, XMLs, filtros, XPath)
  2. **Conexión a BD** usando configuración `db_config.json`
  3. **Procesamiento XML** de todos los archivos en carpeta seleccionada
  4. **Filtrado XRef ID** usando XPath extraído del JSON (Paso 3)
  5. **Aplicación de filtros BD** configurados en Paso 6
  6. **Comparación campo por campo** XML vs BD
  7. **Generación reporte Excel** con código de colores
- **Reporte generado:** `reportes/reporte_comparacion_campos_YYYYMMDD_HHMMSS.xlsx`
- **Código de colores:**
  - 🟢 **Verde:** Valores coinciden perfectamente
  - 🔴 **Rojo:** Valores no coinciden
  - 🔵 **Azul:** Error en procesamiento/comparación
  - 🟡 **Amarillo:** Información de filtros aplicados
- **Columnas del reporte:**
  - `xml_file`: Nombre del archivo XML procesado
  - `xref_id`: ID de referencia usado para filtrar
  - `campo`: Campo comparado (BD)
  - `valor_xml`: Valor extraído del XML
  - `valor_bd`: Valor obtenido de la BD
  - `estado`: COINCIDE/NO_COINCIDE/ERROR/INFO
  - `xpath_usado`: XPath utilizado para extraer valor XML
  - `filtros_usados`: Filtros aplicados en la consulta BD

---

## 🎮 **INTERFAZ DE USUARIO**

### **Panel Lateral Izquierdo:**
- 📂 **Paso 1:** Cargar JSON
- 🗂️ **Paso 2:** Buscar batt_dept_id  
- 🔍 **Paso 3:** XPath xref_id
- 🎯 **Paso 4:** Campos objetivo
- 📁 **Paso 5:** Seleccionar XMLs
- 🔍 **Paso 6:** Filtros BD
- ⚖️ **Paso 7:** Ejecutar comparación

### **Panel Superior:**
- 🔧 **Config:** Configuración de BD
- 👤 **Client Code:** Código cliente
- 🕐 **UTC:** Configuración horaria
- 🔗 **Nueva Integración:** Integraciones
- 🛠️ **Modificador XML:** Herramientas XML
- 📊 **Reportes:** Ver reportes
- 📝 **Logs:** Archivos de log

### **Panel Derecho:**
- 📊 **Seguimiento de Progreso:** Estado actual (X/7 pasos)
- 📋 **Detalle de cada paso:** Información específica
- ✅ **Indicadores de completado:** Visual por paso

---

## 🐛 **SOLUCIÓN DE PROBLEMAS**

### **Error: No se puede conectar a la base de datos**
```
Solución:
1. Verificar config/db_config.json
2. Comprobar que PostgreSQL esté ejecutándose
3. Validar credenciales de usuario
4. Verificar permisos de acceso
```

### **Error: ModuleNotFoundError**
```
Solución:
1. Ejecutar: pip install -r requirements.txt
2. O usar: ejecutar_interfaz_web.bat (instala automáticamente)
```

### **Error: Archivo JSON no válido**
```
Solución:
1. Verificar formato JSON válido
2. Usar ejemplo: downloads/ejemplo_batt_dept.json
3. Validar estructura requerida
```

### **Error: No se encuentran archivos XML**
```
Solución:
1. Verificar que la carpeta contenga archivos .xml
2. Comprobar permisos de lectura
3. Validar estructura XML
```

### **Error: Configuración de comparación incompleta**
```
Solución:
1. Verificar que el Paso 4 tenga campos objetivo configurados
2. Confirmar que el Paso 5 haya extraído XRef IDs
3. Validar que el Paso 6 tenga al menos 1 filtro configurado
4. Verificar que el Paso 3 haya extraído el XPath correctamente
```

### **Error: No se pudo conectar a la base de datos durante comparación**
```
Solución:
1. Verificar config/db_config.json existe y tiene datos válidos
2. Probar conexión BD desde el botón "Config" → "BD Config"
3. Comprobar que PostgreSQL esté ejecutándose
4. Validar credenciales y permisos de usuario
```

### **Error: Reporte Excel no se puede abrir**
```
Solución:
1. Verificar que Microsoft Excel esté instalado
2. Comprobar permisos de escritura en carpeta reportes/
3. Verificar que el archivo no esté siendo usado por otro proceso
4. Navegar manualmente a carpeta reportes/ para abrir archivo
```

---

## 📊 **ARCHIVOS DE SALIDA**

### **Reportes Excel Mejorados:**
- **Ubicación:** `reportes/reporte_comparacion_campos_YYYYMMDD_HHMMSS.xlsx`
- **Contenido:** Comparación completa campo por campo XML vs BD
- **Formato:** Tabla con columnas:
  - `xml_file`: Archivo XML procesado
  - `xref_id`: ID de referencia usado para búsqueda
  - `campo`: Campo de BD comparado
  - `valor_xml`: Valor extraído del XML usando XPath
  - `valor_bd`: Valor obtenido de la BD
  - `estado`: COINCIDE/NO_COINCIDE/ERROR/INFO
  - `xpath_usado`: XPath utilizado para extracción
  - `filtros_usados`: Filtros aplicados en consulta BD
- **Colores automáticos:**
  - 🟢 Verde: Coincidencias perfectas
  - 🔴 Rojo: Valores diferentes
  - 🔵 Azul: Errores de procesamiento
  - 🟡 Amarillo: Información de filtros

### **Logs Detallados:**
- **Ubicación:** `logs/web_gui_YYYYMMDD_HHMMSS.log`
- **Contenido:** Información detallada de ejecución y errores
- **Formato:** Timestamp + Level + Mensaje
- **Uso:** Para diagnóstico y solución de problemas

---

## 🔒 **SEGURIDAD Y BUENAS PRÁCTICAS**

### **Configuración Segura:**
- ✅ No hardcodear credenciales en código
- ✅ Usar archivos de configuración externos
- ✅ Validar entradas de usuario
- ✅ Manejo seguro de excepciones

### **Backup y Recuperación:**
- ✅ Respaldar carpeta `config/` regularmente
- ✅ Mantener archivos JSON de ejemplo
- ✅ Archivar reportes importantes

---

## 👥 **INFORMACIÓN PARA EL EQUIPO**

### **Roles y Responsabilidades:**
- **Administrador:** Configuración inicial y mantenimiento
- **Usuario Final:** Ejecución de comparaciones diarias
- **Analista:** Revisión de reportes y resultados

### **Capacitación Requerida:**
- ✅ Conocimiento básico de JSON
- ✅ Comprensión de estructura XML
- ✅ Fundamentos de bases de datos SQL
- ✅ Uso de Excel para análisis de reportes

### **Contacto Técnico:**
- **Desarrollador:** [Incluir información de contacto]
- **Documentación:** Este archivo y README.md
- **Soporte:** [Definir proceso de soporte]

---

## 🚀 **INICIO RÁPIDO**

```powershell
# 1. Navegar al proyecto
cd "c:\FDSU\Automatizacion\Yatary_Pruebas\comparador_campos_especificos_v2"

# 2. Ejecutar aplicación
.\ejecutar_interfaz_web.bat

# 3. Seguir los 7 pasos en orden:
#    Paso 1: Cargar JSON
#    Paso 2: Buscar batt_dept_id
#    Paso 3: XPath xref_id  
#    Paso 4: Campos objetivo
#    Paso 5: Seleccionar XMLs
#    Paso 6: Filtros BD
#    Paso 7: Ejecutar comparación

# 4. Revisar reporte en carpeta reportes/
```

---

**Versión del Manual:** 2.1  
**Fecha de Actualización:** Agosto 23, 2025  
**Autor:** Sistema de Comparación de Campos  
**Estado:** FUNCIONAL CON NUEVAS CARACTERÍSTICAS ✅  
**Últimas mejoras:** Paso 6 gestión avanzada filtros + Paso 7 comparación completa XML vs BD

---

## 📞 **SOPORTE TÉCNICO**

Para soporte técnico o preguntas adicionales:
1. Consultar este manual
2. Revisar archivos de log en `logs/`
3. Contactar al equipo de desarrollo
4. Documentar errores con capturas de pantalla

**¡El sistema está listo para uso en producción!** 🎉
