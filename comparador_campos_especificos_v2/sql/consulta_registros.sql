-- Consulta SQL para obtener los registros a comparar de PostgreSQL
-- Esta consulta debe retornar al menos el campo identificador y los campos a comparar
-- Solo incluimos columnas que existen en la tabla
SELECT 
    batt_dept_id,
    created_at,
    dispatch_number,
    psap_call_answered_at
FROM nfirs_notification
WHERE dispatch_number IN ('CC0026862')
  AND batt_dept_id IN ('2831')
  AND created_at >= '2025-08-22'::date
ORDER BY dispatch_number, created_at DESC
LIMIT 10;
