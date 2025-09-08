# Database Record Copier

Script para copiar registros entre bases de datos SQL Server con filtro obligatorio de `batt_dept_id`. 
Incluye soporte para conexiones SSH con llave pública para acceso seguro a STAGE10.

## Características

- ✅ Copia registros entre servidores stage10 (origen) y stage (destino)
- ✅ **Conexión SSH con llave pública** para STAGE10
- ✅ **Archivo de configuración JSON** para credenciales
- ✅ Filtro obligatorio por `batt_dept_id`
- ✅ Filtros adicionales opcionales (WHERE clauses)
- ✅ Verificación de restricciones de claves foráneas
- ✅ Manejo de campos problemáticos (como `created_by`)
- ✅ Resumen detallado de la operación
- ✅ Validación de existencia de tablas
- ✅ Transacciones seguras con rollback

## Requisitos Previos

1. **Python 3.7 o superior**
2. **SQL Server ODBC Driver 17** (o superior)
3. **Llave SSH privada** para acceso a STAGE10
4. **Permisos de lectura** en la base de datos origen
5. **Permisos de escritura** en la base de datos destino

## Instalación

1. Ejecutar el archivo de instalación:
   ```cmd
   instalar_copier.bat
   ```

2. O instalar manualmente:
   ```cmd
   pip install pyodbc>=4.0.34 sshtunnel>=0.4.0 paramiko>=2.11.0
   ```

## Configuración

### 📁 Archivo de Configuración: `config_database_copier.json`

Al ejecutar por primera vez, se crea automáticamente un archivo de configuración con valores de ejemplo. **DEBE editarlo** con las credenciales correctas:

```json
{
  "source_database": {
    "server": "stage10_fdsu",
    "database": "COLOCA_AQUI_EL_NOMBRE_DE_LA_BD_ORIGEN",
    "username": "yatary",
    "password": "COLOCA_AQUI_LA_PASSWORD_ORIGEN", 
    "driver": "{ODBC Driver 17 for SQL Server}",
    "ssh_tunnel": {
      "enabled": true,
      "ssh_host": "3.232.18.126",
      "ssh_port": 5422,
      "ssh_username": "yatary",
      "ssh_key_file": "C:\\Users\\Yatary\\.ssh\\id_rsa.ppk",
      "local_bind_port": 5432,
      "remote_bind_host": "172.42.10.172",
      "remote_bind_port": 5432
    }
  },
  "destination_database": {
    "server": "stage",
    "database": "COLOCA_AQUI_EL_NOMBRE_DE_LA_BD_DESTINO",
    "username": "COLOCA_AQUI_EL_USERNAME_DESTINO",
    "password": "COLOCA_AQUI_LA_PASSWORD_DESTINO",
    "driver": "{ODBC Driver 17 for SQL Server}",
    "ssh_tunnel": {
      "enabled": false
    }
  }
}
```

### 🔑 Configuración SSH para STAGE10

La configuración SSH ya está preconfigurada con:
- **Host**: 3.232.18.126
- **Puerto**: 5422
- **Usuario**: yatary
- **Llave privada**: C:\Users\Yatary\.ssh\id_rsa.ppk

**⚠️ IMPORTANTE**: Asegúrese de que:
1. La llave privada existe en la ruta especificada
2. La llave tiene los permisos correctos
3. La llave corresponde a la llave pública configurada en el servidor

### 📝 Campos Obligatorios a Configurar

Antes de ejecutar, debe cambiar estos valores en `config_database_copier.json`:

**Para STAGE10 (origen):**
- `source_database.database` - Nombre de la base de datos
- `source_database.password` - Contraseña del usuario yatary

**Para STAGE (destino):**
- `destination_database.database` - Nombre de la base de datos
- `destination_database.username` - Usuario para el servidor stage
- `destination_database.password` - Contraseña para el servidor stage

## Uso

### Ejecución del Script

```cmd
ejecutar_copier.bat
```

O directamente:
```cmd
python database_record_copier.py
```

### Proceso de Ejecución

El script:
1. ✅ **Carga automáticamente** las credenciales del archivo de configuración
2. ✅ **Establece túnel SSH** para STAGE10 (si está habilitado)
3. ✅ **Te solicita** información de la tabla y filtros
4. ✅ **Verifica** campos problemáticos
5. ✅ **Copia** los registros de forma segura

### Ejemplo de Ejecución

```
=== CONFIGURACIÓN DE CREDENCIALES ===
📝 Las credenciales se cargan desde config_database_copier.json
🔧 Si necesita modificar las credenciales, edite el archivo de configuración

🔐 Configurando túnel SSH para STAGE10...
✅ Túnel SSH establecido: localhost:5432 -> 172.42.10.172:5432
✓ Conectado a origen: stage10_fdsu
✓ Conectado a destino: stage

=== COPIA DE REGISTROS ENTRE BASES DE DATOS ===

Ingrese el nombre de la tabla: incidents
✓ Tabla 'incidents' encontrada en ambas bases de datos

Ingrese el batt_dept_id (OBLIGATORIO): 12345

Consulta base: SELECT * FROM incidents WHERE batt_dept_id = 12345

¿Desea agregar otra cláusula WHERE? (s/n): n

🔍 Obteniendo registros de stage10_fdsu...
✓ 150 registros encontrados en origen

🔍 Verificando restricciones de claves foráneas...

📥 Insertando registros en stage...
✓ 150 registros insertados exitosamente

==================================================
RESUMEN DE LA OPERACIÓN
==================================================
Tabla procesada: incidents
Filtro batt_dept_id: 12345
Registros encontrados en origen: 150
Registros insertados en destino: 150
Servidor origen: stage10_fdsu
Servidor destino: stage
==================================================
🔒 Túnel SSH cerrado
🔒 Conexiones cerradas
```

## Manejo de Campos Problemáticos

Si hay campos con valores que no existen en la base de datos destino (como `created_by`, `updated_by`), el script:

1. **Detecta automáticamente** los valores problemáticos
2. **Te pregunta** si quieres cambiar esos valores
3. **Te solicita** el nuevo valor a usar
4. **Aplica el cambio** a todos los registros afectados

### Ejemplo:
```
=== CAMPOS CON VALORES PROBLEMÁTICOS ===

Campo 'created_by' tiene valores que no existen en la BD de destino:
Valores problemáticos: ['user123', 'user456']

¿Desea cambiar todos los valores del campo 'created_by'? (s/n): s
Ingrese el nuevo valor para el campo 'created_by': admin_user
```

## Resumen Final

Al final de la ejecución obtienes un resumen completo:

```
==================================================
RESUMEN DE LA OPERACIÓN
==================================================
Tabla procesada: incidents
Filtro batt_dept_id: 12345
Registros encontrados en origen: 150
Registros insertados en destino: 150
Servidor origen: stage10
Servidor destino: stage
Campos modificados: ['created_by']
==================================================
```

## Características de Seguridad

- **Transacciones**: Uso de commit/rollback para operaciones seguras
- **Validación**: Verificación de existencia de tablas antes de copiar
- **Conexiones seguras**: Cierre automático de conexiones
- **Manejo de errores**: Gestión robusta de excepciones

## Troubleshooting

### Error: "No se puede conectar a la base de datos"
- Verificar credenciales
- Verificar conectividad de red
- Verificar que el driver ODBC esté instalado

### Error: "La tabla no existe"
- Verificar el nombre exacto de la tabla
- Verificar permisos de lectura/escritura

### Error: "Foreign key constraint"
- El script maneja automáticamente estos casos
- Sigue las instrucciones para campos problemáticos

## Notas Importantes

- ⚠️ **El `batt_dept_id` es OBLIGATORIO** - sin este filtro no se ejecuta la copia
- ⚠️ **Siempre haz backup** antes de ejecutar en producción
- ⚠️ **Verifica los datos** después de la copia
- ⚠️ **Los registros duplicados** pueden causar errores si hay restricciones únicas

## Archivos del Proyecto

- `database_record_copier.py` - Script principal
- `instalar_copier.bat` - Instalador de dependencias
- `requirements_copier.txt` - Lista de dependencias
- `README_Database_Copier.md` - Esta documentación
