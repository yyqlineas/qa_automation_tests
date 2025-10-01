# Verificador de BATT_DEPT_ID y CLIENT_CODE

## 📋 Descripción
Aplicación independiente para verificar y corregir correspondencias entre `batt_dept_id` (campo `id`) y `client_code` en la tabla `batt_dept` de la base de datos.

## 🚀 Ejecución Rápida
**Simplemente haga doble clic en:** `verificador_batt_dept.bat`

## 📁 Archivos Incluidos
- `verificador_batt_dept.py` - Script principal de Python
- `verificador_batt_dept.bat` - Ejecutable para Windows
- `README.md` - Este archivo de documentación

## ⚙️ Requisitos del Sistema
- **Windows** (cualquier versión moderna)
- **Python 3.6+** instalado y en el PATH del sistema
- **Conexión a Internet** (solo para instalación inicial de dependencias)
- **Acceso a la red** donde está la base de datos

## 🔧 Configuración
La configuración de la base de datos está integrada en el script:
- **Host:** calliope.localitymedia.com
- **Puerto:** 5432
- **Base de datos:** stage_fdsu
- **Usuario:** yatary

⚠️ **Para cambiar estas credenciales:** Edite la sección `DB_CONFIG` en `verificador_batt_dept.py`

## 📝 Formato de Entrada
El script acepta múltiples formatos para los datos de entrada:

### Ejemplos Válidos:
```
4471 ALPINE_TOWNSHIP_MI
4471 ALPINE_TOWNSHIP_MI 2083 MARION_IL
ALPINE_TOWNSHIP_MI 4471
4471,ALPINE_TOWNSHIP_MI,2083,MARION_IL
```

### Reglas:
- **Separadores:** Espacios o comas
- **Orden flexible:** ID ClientCode o ClientCode ID
- **Múltiples pares:** Soportado
- **IDs:** Deben ser numéricos
- **Client Codes:** Texto (generalmente en MAYÚSCULAS)

## 🎯 Funcionalidades

### ✅ Verificación
- Verifica si un `batt_dept_id` corresponde al `client_code` correcto
- Muestra discrepancias encontradas
- Informa qué `client_code` ocupa cada ID y viceversa

### 🔧 Corrección Automática
- **Reasignación de IDs:** Cuando un ID está ocupado por otro client_code
- **Movimiento a IDs libres:** Busca automáticamente IDs disponibles
- **Actualización segura:** Con confirmación del usuario antes de hacer cambios

### 📊 Reportes
- Estado inicial de cada verificación
- Proceso detallado de correcciones
- Estado final después de las correcciones

## 🔄 Proceso de Uso

1. **Ejecutar:** Doble clic en `verificador_batt_dept.bat`
2. **Verificar conexión:** El script se conecta automáticamente a la BD
3. **Ingresar datos:** Seguir el formato indicado en pantalla
4. **Revisar resultados:** Ver qué está correcto e incorrecto
5. **Confirmar correcciones:** Responder 'si' para aplicar cambios
6. **Verificar estado final:** Revisar que todo quedó como se esperaba

## ⚠️ Importante

### Antes de Usar:
- ✅ Verifique que tiene acceso a la base de datos
- ✅ Confirme que las credenciales son correctas
- ✅ Haga backup de datos importantes si es necesario

### Durante el Uso:
- ⚡ El script hace cambios REALES en la base de datos
- 🛡️ Siempre confirma antes de hacer modificaciones
- 🔄 Puede manejar múltiples correcciones en una sola ejecución

## 🐛 Resolución de Problemas

### Error: "Python no está instalado"
**Solución:** Instalar Python desde https://python.org/downloads/
- ✅ Marcar "Add Python to PATH" durante la instalación

### Error: "psycopg2 no está instalado"
**Solución:** El script lo instala automáticamente, o manualmente:
```cmd
pip install psycopg2-binary
```

### Error: "No se puede conectar a la BD"
**Solución:** Verificar:
- ✅ Conexión a red
- ✅ Credenciales en la sección DB_CONFIG del script
- ✅ Firewall/proxy no bloquea la conexión

### Error: "Cursor already closed"
**Solución:** Esta versión maneja automáticamente este problema con reconexión

## 📞 Soporte
- **Desarrollado por:** Automatización FDSU
- **Fecha:** Septiembre 2025
- **Versión:** 2.0 (Estable)

---
*Este script es parte del sistema de automatización FDSU para mantenimiento de base de datos.*
