#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar dos archivos JSON y detectar diferencias por secciones.
Autor: Assistant
Fecha: 2025-09-04
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime
import argparse

class JSONComparator:
    def __init__(self, ignore_sections=None):
        self.differences = []
        self.ignored_sections = ignore_sections or ['example_data', 'example data', 'examples', 'sample_data', 'sample data']
        self.stats = {
            'total_keys_compared': 0,
            'differences_found': 0,
            'sections_with_differences': set(),
            'identical_sections': set(),
            'ignored_sections': set()
        }
    
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Carga un archivo JSON y retorna su contenido"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: El archivo {file_path} no es un JSON válido")
            print(f"   Detalle del error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error inesperado al cargar {file_path}: {str(e)}")
            sys.exit(1)
    
    def compare_values(self, val1: Any, val2: Any, path: str) -> bool:
        """Compara dos valores y registra diferencias si las hay"""
        self.stats['total_keys_compared'] += 1
        
        if type(val1) != type(val2):
            self.differences.append({
                'path': path,
                'type': 'type_difference',
                'file1_value': val1,
                'file1_type': type(val1).__name__,
                'file2_value': val2,
                'file2_type': type(val2).__name__
            })
            self.stats['differences_found'] += 1
            return False
        
        if isinstance(val1, dict) and isinstance(val2, dict):
            return self.compare_dicts(val1, val2, path)
        elif isinstance(val1, list) and isinstance(val2, list):
            return self.compare_lists(val1, val2, path)
        else:
            if val1 != val2:
                self.differences.append({
                    'path': path,
                    'type': 'value_difference',
                    'file1_value': val1,
                    'file2_value': val2
                })
                self.stats['differences_found'] += 1
                return False
        
        return True
    
    def should_ignore_section(self, key: str, path: str = "") -> bool:
        """Verifica si una sección debe ser ignorada en la comparación"""
        key_lower = key.lower()
        
        # Verificar si la clave coincide con alguna sección a ignorar
        for ignored in self.ignored_sections:
            if ignored.lower() in key_lower or key_lower == ignored.lower():
                return True
        
        # Verificar si el path contiene alguna sección a ignorar
        path_lower = path.lower()
        for ignored in self.ignored_sections:
            if ignored.lower() in path_lower:
                return True
                
        return False

    def compare_dicts(self, dict1: Dict, dict2: Dict, path: str = "") -> bool:
        """Compara dos diccionarios recursivamente"""
        is_identical = True
        
        # Obtener todas las claves únicas
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            # Verificar si esta sección debe ser ignorada
            if self.should_ignore_section(key, current_path):
                self.stats['ignored_sections'].add(current_path)
                print(f"⏭️  Ignorando sección: {current_path}")
                continue
            
            if key not in dict1:
                self.differences.append({
                    'path': current_path,
                    'type': 'missing_in_file1',
                    'file2_value': dict2[key]
                })
                self.stats['differences_found'] += 1
                is_identical = False
            elif key not in dict2:
                self.differences.append({
                    'path': current_path,
                    'type': 'missing_in_file2',
                    'file1_value': dict1[key]
                })
                self.stats['differences_found'] += 1
                is_identical = False
            else:
                if not self.compare_values(dict1[key], dict2[key], current_path):
                    is_identical = False
        
        return is_identical
    
    def compare_lists(self, list1: List, list2: List, path: str) -> bool:
        """Compara dos listas"""
        is_identical = True
        
        if len(list1) != len(list2):
            self.differences.append({
                'path': path,
                'type': 'list_length_difference',
                'file1_length': len(list1),
                'file2_length': len(list2)
            })
            self.stats['differences_found'] += 1
            is_identical = False
        
        # Comparar elementos hasta la longitud mínima
        min_length = min(len(list1), len(list2))
        for i in range(min_length):
            if not self.compare_values(list1[i], list2[i], f"{path}[{i}]"):
                is_identical = False
        
        # Si una lista es más larga, marcar elementos extra como diferencias
        if len(list1) > min_length:
            for i in range(min_length, len(list1)):
                self.differences.append({
                    'path': f"{path}[{i}]",
                    'type': 'extra_in_file1',
                    'file1_value': list1[i]
                })
                self.stats['differences_found'] += 1
                is_identical = False
        
        if len(list2) > min_length:
            for i in range(min_length, len(list2)):
                self.differences.append({
                    'path': f"{path}[{i}]",
                    'type': 'extra_in_file2',
                    'file2_value': list2[i]
                })
                self.stats['differences_found'] += 1
                is_identical = False
        
        return is_identical
    
    def analyze_sections(self, json1: Dict, json2: Dict) -> None:
        """Analiza las secciones principales del JSON para estadísticas"""
        all_sections = set(json1.keys()) | set(json2.keys())
        
        for section in all_sections:
            # Verificar si la sección debe ser ignorada
            if self.should_ignore_section(section):
                self.stats['ignored_sections'].add(section)
                continue
                
            if section in json1 and section in json2:
                # Crear un comparador temporal para esta sección
                temp_comparator = JSONComparator(ignore_sections=self.ignored_sections)
                section_identical = temp_comparator.compare_values(json1[section], json2[section], section)
                
                if section_identical:
                    self.stats['identical_sections'].add(section)
                else:
                    self.stats['sections_with_differences'].add(section)
            else:
                self.stats['sections_with_differences'].add(section)
    
    def compare_json_files(self, file1_path: str, file2_path: str) -> bool:
        """Función principal para comparar dos archivos JSON"""
        print(f"🔍 Comparando archivos JSON...")
        print(f"   Archivo 1: {os.path.basename(file1_path)}")
        print(f"   Archivo 2: {os.path.basename(file2_path)}")
        print("=" * 60)
        
        # Cargar archivos JSON
        json1 = self.load_json_file(file1_path)
        json2 = self.load_json_file(file2_path)
        
        # Analizar secciones principales
        self.analyze_sections(json1, json2)
        
        # Realizar comparación completa
        is_identical = self.compare_dicts(json1, json2)
        
        return is_identical
    
    def print_results(self, file1_path: str, file2_path: str, is_identical: bool) -> None:
        """Imprime los resultados de la comparación"""
        print(f"\n📊 RESULTADO DE LA COMPARACIÓN")
        print("=" * 60)
        
        if is_identical:
            print("✅ Los archivos JSON son IDÉNTICOS")
        else:
            print("❌ Los archivos JSON tienen DIFERENCIAS")
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   • Total de elementos comparados: {self.stats['total_keys_compared']}")
        print(f"   • Diferencias encontradas: {self.stats['differences_found']}")
        print(f"   • Secciones idénticas: {len(self.stats['identical_sections'])}")
        print(f"   • Secciones con diferencias: {len(self.stats['sections_with_differences'])}")
        print(f"   • Secciones ignoradas: {len(self.stats['ignored_sections'])}")
        
        if self.stats['ignored_sections']:
            print(f"\n⏭️  SECCIONES IGNORADAS:")
            for section in sorted(self.stats['ignored_sections']):
                print(f"   • {section}")
        
        if self.stats['identical_sections']:
            print(f"\n✅ SECCIONES IDÉNTICAS:")
            for section in sorted(self.stats['identical_sections']):
                print(f"   • {section}")
        
        if self.stats['sections_with_differences']:
            print(f"\n❌ SECCIONES CON DIFERENCIAS:")
            for section in sorted(self.stats['sections_with_differences']):
                print(f"   • {section}")
        
        if not is_identical and self.differences:
            print(f"\n🔍 DETALLES DE LAS DIFERENCIAS:")
            print("-" * 60)
            
            for i, diff in enumerate(self.differences[:20], 1):  # Mostrar máximo 20 diferencias
                print(f"\n{i}. Ruta: {diff['path']}")
                
                if diff['type'] == 'value_difference':
                    print(f"   Tipo: Valor diferente")
                    print(f"   Archivo 1: {repr(diff['file1_value'])}")
                    print(f"   Archivo 2: {repr(diff['file2_value'])}")
                
                elif diff['type'] == 'type_difference':
                    print(f"   Tipo: Tipo de dato diferente")
                    print(f"   Archivo 1: {repr(diff['file1_value'])} (tipo: {diff['file1_type']})")
                    print(f"   Archivo 2: {repr(diff['file2_value'])} (tipo: {diff['file2_type']})")
                
                elif diff['type'] == 'missing_in_file1':
                    print(f"   Tipo: Falta en archivo 1")
                    print(f"   Valor en archivo 2: {repr(diff['file2_value'])}")
                
                elif diff['type'] == 'missing_in_file2':
                    print(f"   Tipo: Falta en archivo 2")
                    print(f"   Valor en archivo 1: {repr(diff['file1_value'])}")
                
                elif diff['type'] == 'list_length_difference':
                    print(f"   Tipo: Longitud de lista diferente")
                    print(f"   Archivo 1: {diff['file1_length']} elementos")
                    print(f"   Archivo 2: {diff['file2_length']} elementos")
                
                elif diff['type'] == 'extra_in_file1':
                    print(f"   Tipo: Elemento extra en archivo 1")
                    print(f"   Valor: {repr(diff['file1_value'])}")
                
                elif diff['type'] == 'extra_in_file2':
                    print(f"   Tipo: Elemento extra en archivo 2")
                    print(f"   Valor: {repr(diff['file2_value'])}")
            
            if len(self.differences) > 20:
                print(f"\n... y {len(self.differences) - 20} diferencias más.")
    
    def save_report(self, file1_path: str, file2_path: str, is_identical: bool) -> str:
        """Guarda un reporte detallado en un archivo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"json_comparison_report_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE COMPARACIÓN DE ARCHIVOS JSON\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivo 1: {file1_path}\n")
            f.write(f"Archivo 2: {file2_path}\n\n")
            
            if is_identical:
                f.write("RESULTADO: Los archivos JSON son IDÉNTICOS\n\n")
            else:
                f.write("RESULTADO: Los archivos JSON tienen DIFERENCIAS\n\n")
            
            f.write("ESTADÍSTICAS:\n")
            f.write(f"• Total de elementos comparados: {self.stats['total_keys_compared']}\n")
            f.write(f"• Diferencias encontradas: {self.stats['differences_found']}\n")
            f.write(f"• Secciones idénticas: {len(self.stats['identical_sections'])}\n")
            f.write(f"• Secciones con diferencias: {len(self.stats['sections_with_differences'])}\n")
            f.write(f"• Secciones ignoradas: {len(self.stats['ignored_sections'])}\n\n")
            
            if self.stats['ignored_sections']:
                f.write("SECCIONES IGNORADAS:\n")
                for section in sorted(self.stats['ignored_sections']):
                    f.write(f"• {section}\n")
                f.write("\n")
            
            if self.stats['identical_sections']:
                f.write("SECCIONES IDÉNTICAS:\n")
                for section in sorted(self.stats['identical_sections']):
                    f.write(f"• {section}\n")
                f.write("\n")
            
            if self.stats['sections_with_differences']:
                f.write("SECCIONES CON DIFERENCIAS:\n")
                for section in sorted(self.stats['sections_with_differences']):
                    f.write(f"• {section}\n")
                f.write("\n")
            
            if not is_identical and self.differences:
                f.write("DETALLES DE TODAS LAS DIFERENCIAS:\n")
                f.write("-" * 60 + "\n\n")
                
                for i, diff in enumerate(self.differences, 1):
                    f.write(f"{i}. Ruta: {diff['path']}\n")
                    
                    if diff['type'] == 'value_difference':
                        f.write(f"   Tipo: Valor diferente\n")
                        f.write(f"   Archivo 1: {repr(diff['file1_value'])}\n")
                        f.write(f"   Archivo 2: {repr(diff['file2_value'])}\n")
                    
                    elif diff['type'] == 'type_difference':
                        f.write(f"   Tipo: Tipo de dato diferente\n")
                        f.write(f"   Archivo 1: {repr(diff['file1_value'])} (tipo: {diff['file1_type']})\n")
                        f.write(f"   Archivo 2: {repr(diff['file2_value'])} (tipo: {diff['file2_type']})\n")
                    
                    elif diff['type'] == 'missing_in_file1':
                        f.write(f"   Tipo: Falta en archivo 1\n")
                        f.write(f"   Valor en archivo 2: {repr(diff['file2_value'])}\n")
                    
                    elif diff['type'] == 'missing_in_file2':
                        f.write(f"   Tipo: Falta en archivo 2\n")
                        f.write(f"   Valor en archivo 1: {repr(diff['file1_value'])}\n")
                    
                    elif diff['type'] == 'list_length_difference':
                        f.write(f"   Tipo: Longitud de lista diferente\n")
                        f.write(f"   Archivo 1: {diff['file1_length']} elementos\n")
                        f.write(f"   Archivo 2: {diff['file2_length']} elementos\n")
                    
                    elif diff['type'] == 'extra_in_file1':
                        f.write(f"   Tipo: Elemento extra en archivo 1\n")
                        f.write(f"   Valor: {repr(diff['file1_value'])}\n")
                    
                    elif diff['type'] == 'extra_in_file2':
                        f.write(f"   Tipo: Elemento extra en archivo 2\n")
                        f.write(f"   Valor: {repr(diff['file2_value'])}\n")
                    
                    f.write("\n")
        
        return report_filename


def get_file_input(prompt: str) -> str:
    """Solicita al usuario la ruta de un archivo y valida que exista"""
    while True:
        print(prompt)
        print("💡 Tip: Puedes arrastrar el archivo aquí o escribir la ruta completa")
        file_path = input("👉 Ruta del archivo: ").strip().strip('"').strip("'")
        
        if not file_path:
            print("❌ Por favor, ingresa una ruta válida.\n")
            continue
        
        # Normalizar la ruta
        file_path = os.path.normpath(file_path)
        
        # Mostrar la ruta que se está intentando verificar
        print(f"🔍 Verificando: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ Error: No se encontró el archivo")
            print(f"   Ruta buscada: {file_path}")
            
            # Mostrar archivos en el directorio actual para ayudar
            try:
                current_dir = os.getcwd()
                print(f"   Directorio actual: {current_dir}")
                json_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.json')]
                if json_files:
                    print(f"   Archivos JSON disponibles aquí:")
                    for f in json_files[:5]:  # Mostrar máximo 5
                        print(f"     - {f}")
                    if len(json_files) > 5:
                        print(f"     ... y {len(json_files) - 5} más")
            except:
                pass
            
            print("💡 Verifica que la ruta sea correcta y el archivo exista.\n")
            continue
        
        if not file_path.lower().endswith('.json'):
            print(f"❌ Error: El archivo debe ser un JSON (.json)")
            print(f"   Archivo proporcionado: {file_path}\n")
            continue
        
        return file_path

def interactive_mode():
    """Modo interactivo para solicitar archivos al usuario"""
    print("=" * 60)
    print("🔍 COMPARADOR INTERACTIVO DE ARCHIVOS JSON")
    print("=" * 60)
    print("Este script comparará dos archivos JSON y te mostrará las diferencias.")
    print("Puedes usar rutas absolutas o relativas.\n")
    
    # Mostrar directorio actual y archivos JSON disponibles
    current_dir = os.getcwd()
    print(f"📁 Directorio actual: {current_dir}")
    
    try:
        json_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.json')]
        if json_files:
            print(f"📋 Archivos JSON disponibles aquí:")
            for i, f in enumerate(json_files, 1):
                print(f"   {i}. {f}")
            print()
        else:
            print("⚠️  No hay archivos JSON en el directorio actual.\n")
    except Exception as e:
        print(f"⚠️  Error al listar archivos: {e}\n")
    
    # Solicitar primer archivo
    file1 = get_file_input("📄 PRIMER ARCHIVO JSON:")
    print(f"✅ Primer archivo: {os.path.basename(file1)}\n")
    
    # Solicitar segundo archivo
    file2 = get_file_input("📄 SEGUNDO ARCHIVO JSON:")
    print(f"✅ Segundo archivo: {os.path.basename(file2)}\n")
    
    return file1, file2

def main():
    """Función principal del script"""
    # Si no hay argumentos, usar modo interactivo
    if len(sys.argv) == 1:
        try:
            file1, file2 = interactive_mode()
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            sys.exit(1)
    else:
        # Usar argumentos de línea de comandos (modo original)
        parser = argparse.ArgumentParser(
            description="Compara dos archivos JSON y detecta diferencias por secciones",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos de uso:
  python json_comparator.py archivo1.json archivo2.json
  python json_comparator.py  (modo interactivo)
            """
        )
        
        parser.add_argument('file1', help='Primer archivo JSON a comparar')
        parser.add_argument('file2', help='Segundo archivo JSON a comparar')
        
        args = parser.parse_args()
        
        # Verificar que los archivos existan
        if not os.path.exists(args.file1):
            print(f"❌ Error: No se encontró el archivo {args.file1}")
            sys.exit(1)
        
        if not os.path.exists(args.file2):
            print(f"❌ Error: No se encontró el archivo {args.file2}")
            sys.exit(1)
        
        file1, file2 = args.file1, args.file2
    
    # Crear comparador y ejecutar comparación
    comparator = JSONComparator()
    is_identical = comparator.compare_json_files(file1, file2)
    
    # Mostrar resultados siempre en consola
    comparator.print_results(file1, file2, is_identical)
    
    # Código de salida
    sys.exit(0 if is_identical else 1)


if __name__ == "__main__":
    main()
