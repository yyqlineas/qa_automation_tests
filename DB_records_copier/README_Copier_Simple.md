# Database Record Copier - Script Unificado

## 📁 Archivo Principal
- **`database_record_copier.py`** - Script completo (TODO EN UNO)
- **`ejecutar_copier.bat`** - Launcher ejecutable (opcional)

## 🚀 Ejecución Rápida
```cmd
python database_record_copier.py
```

## ✨ Características
- ✅ **Todo en un solo archivo Python**
- ✅ **Configuración interactiva** (no necesita archivos externos)
- ✅ **Conexión SSH** preconfigurada para STAGE10
- ✅ **Filtro obligatorio** por batt_dept_id
- ✅ **Manejo automático** de campos problemáticos

## 🔧 Configuración Preestablecida

### STAGE10 (Origen) - Con túnel SSH
- **Servidor**: stage10_fdsu
- **Usuario**: yatary  
- **SSH Host**: 3.232.18.126:5422
- **SSH Key**: C:\Users\Yatary\.ssh\id_rsa.ppk

### STAGE (Destino) - Conexión directa
- **Servidor**: stage

## 📝 Al ejecutar te pedirá:
1. Nombre de base de datos origen
2. Password para yatary en STAGE10
3. Nombre de base de datos destino  
4. Usuario y password para STAGE
5. Nombre de tabla a copiar
6. batt_dept_id (obligatorio)
7. Filtros adicionales (opcional)

## 🛠️ Dependencias
- **pyodbc** (obligatorio)
- **sshtunnel, paramiko** (opcional, para SSH)

Instalar con: `pip install pyodbc sshtunnel paramiko`

## ⚠️ Importante
- El filtro `batt_dept_id` es OBLIGATORIO
- Siempre haz backup antes de ejecutar en producción
- El script maneja automáticamente campos problemáticos como `created_by`
