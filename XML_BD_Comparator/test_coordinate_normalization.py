#!/usr/bin/env python3
"""
Prueba de la función de normalización de coordenadas
"""

def normalize_coordinate(coord_str):
    """
    Normalizar coordenadas (latitude/longitude) a 7 decimales.
    - Si tiene menos de 7 decimales, completar con ceros
    - Si tiene más de 7 decimales, redondear a 7 decimales
    """
    if not coord_str or coord_str.strip() == "" or coord_str in ["ERROR_XPATH", "ERROR_CONEXION", "ERROR_QUERY", "CAMPO_NO_EXISTE"]:
        return coord_str
    
    try:
        # Convertir a float para manejar la precisión
        coord_float = float(coord_str.strip())
        # Formatear a exactamente 7 decimales
        normalized = f"{coord_float:.7f}"
        return normalized
    except (ValueError, TypeError):
        # Si no se puede convertir a float, devolver el valor original
        return coord_str

# Casos de prueba según la imagen del usuario
test_cases = [
    ("36.4084", "36.4084000"),      # XML -> BD esperada
    ("-89.0113", "-89.0113000"),   # XML -> BD esperada  
    ("36.4084000", "36.4084000"),  # BD -> BD (sin cambios)
    ("-89.0113000", "-89.0113000"), # BD -> BD (sin cambios)
    ("36.40840001", "36.4084000"),  # Más de 7 decimales -> redondear
    ("-89.01134567", "-89.0113457") # Más de 7 decimales -> redondear
]

print("🗺️ Prueba de normalización de coordenadas:")
print("=" * 60)

for i, (input_val, expected) in enumerate(test_cases, 1):
    result = normalize_coordinate(input_val)
    match = result == expected
    status = "✅ PASS" if match else "❌ FAIL"
    
    print(f"Prueba {i}: {status}")
    print(f"  Input:    '{input_val}'")
    print(f"  Result:   '{result}'") 
    print(f"  Expected: '{expected}'")
    print(f"  Match:    {match}")
    print()

print("Prueba de casos especiales:")
print("-" * 30)

special_cases = [
    ("", ""),
    ("ERROR_XPATH", "ERROR_XPATH"),
    ("invalid", "invalid"),
    (None, None)
]

for input_val, expected in special_cases:
    try:
        result = normalize_coordinate(input_val) if input_val is not None else input_val
        print(f"Input: {input_val} -> Result: {result}")
    except Exception as e:
        print(f"Input: {input_val} -> Error: {e}")