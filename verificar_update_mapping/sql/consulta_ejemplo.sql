-- Ejemplo de consulta SQL para obtener registros a comparar
-- Tabla de ejemplo: personas
SELECT 
    id_persona,
    nombre,
    apellido,
    cedula,
    telefono,
    fecha_registro
FROM personas 
WHERE estado = 'ACTIVO'
  AND fecha_registro >= DATEADD(month, -1, GETDATE())  -- Registros del último mes
  AND id_persona IS NOT NULL
ORDER BY id_persona;
