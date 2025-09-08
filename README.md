# Yatary Pruebas - Automatización FDSU

## 📋 Descripción
Colección de herramientas de automatización para mantenimiento y verificación de bases de datos del sistema FDSU.

## 🛠️ Herramientas Disponibles

### 1. **Verificador BATT_DEPT_ID** 🎯
**Ubicación:** `verificador batt_dept_id/`

Verifica y corrige correspondencias entre `batt_dept_id` (campo `id`) y `client_code` en la tabla `batt_dept`.

#### Ejecución:
```bash
# Navegar a la carpeta
cd "verificador batt_dept_id"

# Ejecutar con el archivo .bat
ejecutar.bat

# O ejecutar directamente con Python
python verificador_batt_dept.py
```

#### Características:
- ✅ Verificación de correspondencias ID-ClientCode
- ✅ Corrección automática de discrepancias
- ✅ Reasignación inteligente de IDs
- ✅ Interfaz visual con instrucciones claras
- ✅ Manejo robusto de conexiones a BD

---

### 2. **Comparador de Campos Específicos v2** 📊
**Ubicación:** `comparador_campos_especificos_v2/`

Herramienta avanzada para comparar campos específicos entre diferentes entornos de base de datos.

#### Ejecución:
```bash
cd comparador_campos_especificos_v2
python main_web.py
```

#### Características:
- 🌐 Interfaz web moderna
- 📈 Reportes detallados en Excel
- 🔍 Comparación selectiva de campos
- 📝 Logs detallados de operaciones

---

### 3. **Database Record Copier** 🔄
**Ubicación:** Archivos en carpeta principal

Copia registros específicos entre bases de datos con configuración flexible.

#### Archivos principales:
- `database_record_copier.py` - Script principal
- `config_database_copier.json` - Configuración
- `verificar_config_copier.py` - Verificador de configuración

#### Ejecución:
```bash
python database_record_copier.py
```

---

### 4. **Comparador de JSON** 📄
**Ubicación:** `comparador de json/`

Compara archivos JSON y genera reportes de diferencias.

#### Archivos:
- `json_comparator.py` - Comparador principal
- `test_comparator.py` - Tests unitarios

---

### 5. **XML-BD Comparator** 🔍
**Ubicación:** `XML_BD_Comparator/`

Herramienta para comparar estructuras XML con datos de base de datos.

---

### 6. **Verificador Update Mapping** 🗺️
**Ubicación:** `verificar_update_mapping/`

Verifica y valida mapeos de actualización entre sistemas.

---

## 🚀 Inicio Rápido

### Prerrequisitos:
- **Python 3.6+** instalado
- **pip** para gestión de paquetes
- **Acceso a red** para conexiones a BD

### Dependencias Comunes:
```bash
pip install psycopg2-binary
pip install pandas
pip install openpyxl
pip install flask
```

## 📁 Estructura del Proyecto

```
Yatary_Pruebas/
├── verificador batt_dept_id/           # Verificador de correspondencias BD
│   ├── verificador_batt_dept.py        # Script principal
│   └── ejecutar.bat                    # Ejecutable Windows
├── comparador_campos_especificos_v2/   # Comparador avanzado de campos
├── XML_BD_Comparator/                  # Comparador XML-BD
├── verificar_update_mapping/           # Verificador de mapeos
├── comparador de json/                 # Herramientas JSON
├── database_record_copier.py           # Copiador de registros
├── config_database_copier.json         # Config del copiador
└── README.md                          # Este archivo
```

## 🔧 Configuración

### Base de Datos:
Cada herramienta incluye su configuración de BD específica. Los parámetros comunes son:
- **Host:** calliope.localitymedia.com
- **Puerto:** 5432
- **BD:** stage_fdsu
- **Usuario:** yatary

### Modificar Credenciales:
Busque la sección `DB_CONFIG` en cada script para personalizar las credenciales.

## 📞 Soporte

**Desarrollado por:** Automatización FDSU  
**Fecha:** Septiembre 2025  
**Propósito:** Automatización de tareas de mantenimiento de BD

---

## 📝 Notas de Uso

⚠️ **IMPORTANTE:** Estas herramientas realizan cambios REALES en bases de datos. Siempre:
- Verifique las credenciales antes de ejecutar
- Haga backup de datos críticos
- Confirme las operaciones antes de aplicar cambios
- Revise los logs y reportes generados

💡 **Recomendación:** Comience probando en entornos de desarrollo antes de usar en producción.
