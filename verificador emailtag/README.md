# Verificador de EmailTag para BATT_DEPT_ID y CLIENT_CODE

## 📋 Descripción
Aplicación independiente para verificar y corregir correspondencias entre `emailtag`, `batt_dept_id` (campo `id`) y `client_code` en la tabla `batt_dept` de la base de datos.

## 🚀 Ejecución Rápida
**Simplemente haga doble clic en:** `verificador_emailtag.bat`

## 📁 Archivos Incluidos
- `verificador_emailtag.py` - Script principal de Python
- `verificador_emailtag.bat` - Ejecutable para Windows
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

⚠️ **Para cambiar estas credenciales:** Edite la sección `DB_CONFIG` en `verificador_emailtag.py`

## 📝 Formato de Entrada
El script acepta trios de datos para verificar emailtag:

### Ejemplos Válidos:
```
4471 ALPINE_TOWNSHIP_MI alpine@example.com
ALPINE_TOWNSHIP_MI 4471 alpine@example.com
4471,ALPINE_TOWNSHIP_MI,alpine@example.com
```

### Reglas:
- **Formato:** ID ClientCode EmailTag (en cualquier orden)
- **Separadores:** Espacios o comas
- **IDs:** Deben ser numéricos
- **Client Codes:** Texto (generalmente en MAYÚSCULAS)
- **EmailTags:** Direcciones de correo electrónico

## 🎯 Funcionalidades

### ✅ Verificación de EmailTag
- Verifica si un `emailtag` corresponde al `batt_dept_id` y `client_code` correctos
- Valida primero que `batt_dept_id` y `client_code` coincidan entre sí
- Muestra discrepancias encontradas

### 🔧 Casos Manejados

#### Caso 1: EmailTag Incorrecto
- Si `batt_dept_id` y `client_code` coinciden, pero el `emailtag` no
- **Acción:** Solicita actualizar el emailtag con el valor nuevo introducido

#### Caso 2: Batt_Dept_ID y Client_Code No Coinciden
- Si el `client_code` no corresponde al `batt_dept_id` introducido
- **Acción:** Muestra mensaje indicando que debe actualizarse primero el batt_dept_id
- **No actualiza:** El emailtag hasta que la correspondencia ID-ClientCode sea correcta

#### Caso 3: Todo Correcto
- Si `batt_dept_id`, `client_code` y `emailtag` coinciden correctamente
- **Resultado:** No hay discrepancias

### 🔄 Corrección Automática
- **Actualización segura:** Con confirmación del usuario antes de hacer cambios
- **Validación previa:** Solo actualiza emailtag si batt_dept_id y client_code coinciden
- **Protección:** Evita actualizaciones en registros con inconsistencias

### 📊 Reportes
- Estado inicial de cada verificación
- Proceso detallado de correcciones
- Estado final después de las correcciones

## 🔄 Proceso de Uso

1. **Ejecutar:** Doble clic en `verificador_emailtag.bat`
2. **Verificar conexión:** El script se conecta automáticamente a la BD
3. **Ingresar datos:** Formato: `ID ClientCode EmailTag`
4. **Revisar resultados:** Ver qué está correcto e incorrecto
5. **Confirmar correcciones:** Responder 'si' para aplicar cambios de emailtag
6. **Verificar estado final:** Revisar que todo quedó como se esperaba

## ⚠️ Importante

### Antes de Usar:
- ✅ Verifique que tiene acceso a la base de datos
- ✅ Confirme que las credenciales son correctas
- ✅ Si hay inconsistencias de batt_dept_id/client_code, use primero el verificador de batt_dept_id

### Durante el Uso:
- ⚡ El script hace cambios REALES en la base de datos
- 🛡️ Siempre confirma antes de hacer modificaciones
- 🔒 Solo actualiza emailtag si batt_dept_id y client_code son consistentes
- 📌 Requiere corrección previa de inconsistencias en batt_dept_id antes de actualizar emailtag

## 🔗 Dependencias con Otros Verificadores

### Verificador de BATT_DEPT_ID
- **Usar antes:** Si hay errores de correspondencia batt_dept_id/client_code
- **Ubicación:** `../verificador batt_dept_id/`
- **Propósito:** Corregir inconsistencias ID-ClientCode antes de actualizar emailtags

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

### Error: "Batt_dept_id y client_code no coinciden"
**Solución:** 
- ✅ Usar primero el verificador de batt_dept_id
- ✅ Corregir las inconsistencias ID-ClientCode
- ✅ Luego volver a usar este verificador de emailtag

## 💡 Ejemplos de Uso

### Verificación Simple:
```
Entrada: 4471 ALPINE_TOWNSHIP_MI alpine@fire.com
Resultado: Verifica si ese emailtag es correcto para esa combinación
```

### Múltiples Verificaciones:
```
Entrada: 4471 ALPINE_TOWNSHIP_MI alpine@fire.com 2083 MARION_IL marion@police.com
Resultado: Verifica ambos emailtags
```

### Caso de Error Común:
```
Entrada: 4471 WRONG_CLIENT_CODE test@email.com
Resultado: Error - Debe corregir primero el batt_dept_id/client_code
```

## 📞 Soporte
- **Desarrollado por:** Automatización FDSU
- **Fecha:** Octubre 2025
- **Versión:** 1.0 (Inicial)
- **Basado en:** Verificador de BATT_DEPT_ID v2.0

---
*Este script es parte del sistema de automatización FDSU para mantenimiento de base de datos.*