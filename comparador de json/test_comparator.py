#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar el comparador JSON
"""

import json_comparator
import os

def test_comparator():
    """Función de prueba para el comparador"""
    print("🧪 PRUEBA DEL COMPARADOR JSON")
    print("=" * 50)
    
    # Verificar que los archivos existen
    file1 = "ejemplo1.json"
    file2 = "ejemplo2.json"
    
    if not os.path.exists(file1):
        print(f"❌ No se encuentra {file1}")
        return
    
    if not os.path.exists(file2):
        print(f"❌ No se encuentra {file2}")
        return
    
    print(f"✅ Archivos encontrados: {file1} y {file2}")
    
    # Crear comparador y ejecutar
    comparator = json_comparator.JSONComparator()
    
    try:
        print("\n🔍 Realizando comparación...")
        is_identical = comparator.compare_json_files(file1, file2)
        
        print("\n📊 RESULTADOS:")
        comparator.print_results(file1, file2, is_identical)
        
        print(f"\n✅ Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_comparator()
