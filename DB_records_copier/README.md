# Database Records Copier

Script unificado para copiar registros entre bases de datos SQL Server con filtro obligatorio por `batt_dept_id`.

## 📁 Archivos del Proyecto

- **`database_record_copier.py`** - Script principal unificado (TODO EN UNO)
- **`config_database_copier.json`** - Configuración externa (opcional)
- **`requirements_copier.txt`** - Dependencias Python
- **`instalar_copier.bat`** - Instalar dependencias automáticamente
- **`ejecutar_copier.bat`** - Ejecutar el script desde Windows
- **`verificar_config.bat`** - Verificar configuración
- **`verificar_config_copier.py`** - Script de verificación Python

## 🚀 Uso Rápido

### Opción 1: Script Unificado (Recomendado)
```bash
# 1. Editar credenciales en database_record_copier.py
# 2. Ejecutar directamente
python database_record_copier.py
```

### Opción 2: Con archivos batch
```bash
# 1. Instalar dependencias
instalar_copier.bat

# 2. Configurar credenciales en el script

# 3. Ejecutar
ejecutar_copier.bat
```

## 🔧 Configuración

Edite las credenciales en la sección `DEFAULT_CONFIG` del archivo `database_record_copier.py`:

```python
DEFAULT_CONFIG = {
    "source_database": {
        "database": "NOMBRE_BD_ORIGEN",
        "password": "PASSWORD_YATARY",
        # ...
    },
    "destination_database": {
        "database": "NOMBRE_BD_DESTINO", 
        "username": "USUARIO_STAGE",
        "password": "PASSWORD_STAGE",
        # ...
    }
}
```

## ✅ Características

- ✅ Script todo-en-uno (no necesita archivos externos)
- ✅ Configuración hardcodeada (sin prompts interactivos)
- ✅ Soporte SSH para STAGE10 
- ✅ Filtro obligatorio por `batt_dept_id`
- ✅ Confirmación antes de copiar
- ✅ Manejo de restricciones de claves foráneas
- ✅ Transacciones seguras con rollback

## 📋 Requisitos

- Python 3.7+
- pyodbc (obligatorio)
- sshtunnel, paramiko (opcional, para SSH)

Fecha: 2025-09-08
