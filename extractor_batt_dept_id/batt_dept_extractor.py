#!/usr/bin/env python3
"""
Script para extraer batt_dept_id de archivos JSON en formato IN() para consultas SQL
y extraer xpath para xref_id.

Autor: Script generado para extraer información de configuraciones JSON
Fecha: 2025-09-30
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
import argparse
from pathlib import Path


class BattDeptExtractor:
    """Clase para extraer información de batt_dept_id y xref_id de archivos JSON."""
    
    def __init__(self):
        self.batt_dept_ids = []
        self.xref_id_xpaths = []
        self.json_data = None
    
    def load_json_file(self, file_path: str) -> bool:
        """
        Carga un archivo JSON.
        
        Args:
            file_path (str): Ruta al archivo JSON
            
        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)
            print(f"✓ Archivo JSON cargado correctamente: {file_path}")
            return True
        except FileNotFoundError:
            print(f"✗ Error: No se encontró el archivo {file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Error al decodificar JSON: {e}")
            return False
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            return False
    
    def extract_batt_dept_ids(self) -> List[int]:
        """
        Extrae todos los batt_dept_id del JSON.
        
        Returns:
            List[int]: Lista de batt_dept_id encontrados
        """
        self.batt_dept_ids = []
        
        if not self.json_data:
            print("✗ No hay datos JSON cargados")
            return self.batt_dept_ids
        
        # Buscar en la estructura principal
        if 'templates' in self.json_data:
            for template in self.json_data['templates']:
                # Buscar en batt_depts directamente
                if 'batt_depts' in template:
                    batt_depts = template['batt_depts']
                    if isinstance(batt_depts, list):
                        self.batt_dept_ids.extend(batt_depts)
                    elif isinstance(batt_depts, (int, str)):
                        self.batt_dept_ids.append(int(batt_depts))
                
                # Buscar en parser_options -> object_types
                if 'parser_options' in template and 'object_types' in template['parser_options']:
                    for obj_type in template['parser_options']['object_types']:
                        if 'batt_dept' in obj_type:
                            self.batt_dept_ids.append(obj_type['batt_dept'])
                
                # Buscar en update_rules -> batt_depts
                if 'update_rules' in template:
                    for rule in template['update_rules']:
                        if 'batt_depts' in rule:
                            batt_depts = rule['batt_depts']
                            if isinstance(batt_depts, list):
                                self.batt_dept_ids.extend(batt_depts)
                            elif isinstance(batt_depts, (int, str)):
                                self.batt_dept_ids.append(int(batt_depts))
        
        # Buscar en la raíz del documento
        elif 'batt_depts' in self.json_data:
            batt_depts = self.json_data['batt_depts']
            if isinstance(batt_depts, list):
                self.batt_dept_ids.extend(batt_depts)
            elif isinstance(batt_depts, (int, str)):
                self.batt_dept_ids.append(int(batt_depts))
        
        # Eliminar duplicados y ordenar
        self.batt_dept_ids = sorted(list(set(self.batt_dept_ids)))
        
        print(f"✓ Encontrados {len(self.batt_dept_ids)} batt_dept_id únicos")
        return self.batt_dept_ids
    
    def extract_xref_id_xpaths(self) -> List[str]:
        """
        Extrae todos los xpath para xref_id del JSON.
        Soporta tanto xpath directos como regex patterns.
        Solo incluye valores que tengan contenido real.
        
        Returns:
            List[str]: Lista de xpath/regex para xref_id encontrados (solo no vacíos)
        """
        self.xref_id_xpaths = []
        
        if not self.json_data:
            print("✗ No hay datos JSON cargados")
            return self.xref_id_xpaths
        
        # Buscar en templates -> parser_options -> xpaths -> xref_id
        if 'templates' in self.json_data:
            for template in self.json_data['templates']:
                if ('parser_options' in template and 
                    'xpaths' in template['parser_options'] and
                    'xref_id' in template['parser_options']['xpaths']):
                    
                    xref_id_data = template['parser_options']['xpaths']['xref_id']
                    
                    # Caso 1: xpath directo (string simple)
                    if isinstance(xref_id_data, str):
                        cleaned_xpath = xref_id_data.strip()
                        if cleaned_xpath:  # Solo agregar si no está vacío
                            self.xref_id_xpaths.append(cleaned_xpath)
                    
                    # Caso 2: estructura con regex u otros campos
                    elif isinstance(xref_id_data, dict):
                        # Buscar regex
                        if 'regex' in xref_id_data and xref_id_data['regex']:
                            regex_pattern = str(xref_id_data['regex']).strip()
                            # Filtrar valores vacíos, comillas vacías, etc.
                            if regex_pattern and regex_pattern not in ['', '""', "''", '``', '""', "''"]:
                                self.xref_id_xpaths.append(f"REGEX: {regex_pattern}")
                        
                        # Buscar otros posibles campos en la estructura
                        for key in ['xpath', 'pattern', 'expression']:
                            if key in xref_id_data and xref_id_data[key]:
                                value = str(xref_id_data[key]).strip()
                                # Filtrar valores vacíos, comillas vacías, etc.
                                if value and value not in ['', '""', "''", '``', '""', "''"]:
                                    self.xref_id_xpaths.append(f"{key.upper()}: {value}")
                
                # Buscar también en regexes si existe esa sección
                if ('parser_options' in template and 
                    'regexes' in template['parser_options'] and
                    'xref_id' in template['parser_options']['regexes']):
                    
                    regex_data = template['parser_options']['regexes']['xref_id']
                    if isinstance(regex_data, str):
                        cleaned_regex = str(regex_data).strip()
                        # Filtrar valores vacíos, comillas vacías, etc.
                        if cleaned_regex and cleaned_regex not in ['', '""', "''", '``', '""', "''"]:
                            self.xref_id_xpaths.append(f"REGEX: {cleaned_regex}")
                    elif isinstance(regex_data, dict) and 'regex' in regex_data:
                        regex_pattern = str(regex_data['regex']).strip()
                        # Filtrar valores vacíos, comillas vacías, etc.
                        if regex_pattern and regex_pattern not in ['', '""', "''", '``', '""', "''"]:
                            self.xref_id_xpaths.append(f"REGEX: {regex_pattern}")
        
        # Buscar en otras posibles ubicaciones en la raíz
        if 'xpaths' in self.json_data and 'xref_id' in self.json_data['xpaths']:
            xref_id_data = self.json_data['xpaths']['xref_id']
            if isinstance(xref_id_data, str):
                cleaned_xpath = str(xref_id_data).strip()
                # Filtrar valores vacíos, comillas vacías, etc.
                if cleaned_xpath and cleaned_xpath not in ['', '""', "''", '``', '""', "''"]:
                    self.xref_id_xpaths.append(cleaned_xpath)
            elif isinstance(xref_id_data, dict) and 'regex' in xref_id_data:
                regex_pattern = str(xref_id_data['regex']).strip()
                # Filtrar valores vacíos, comillas vacías, etc.
                if regex_pattern and regex_pattern not in ['', '""', "''", '``', '""', "''"]:
                    self.xref_id_xpaths.append(f"REGEX: {regex_pattern}")
        
        # Eliminar duplicados
        self.xref_id_xpaths = list(set(self.xref_id_xpaths))
        
        print(f"✓ Encontrados {len(self.xref_id_xpaths)} xpath/regex para xref_id únicos")
        return self.xref_id_xpaths
    
    def format_sql_in_clause(self) -> str:
        """
        Formatea los batt_dept_id en una cláusula IN() para SQL.
        
        Returns:
            str: Cláusula IN() formateada
        """
        if not self.batt_dept_ids:
            return "IN ()"
        
        # Convertir todos los IDs a string para el formato SQL
        ids_str = ', '.join(str(id) for id in self.batt_dept_ids)
        return f"IN ({ids_str})"
    
    def generate_report(self) -> str:
        """
        Genera un reporte completo de la extracción.
        
        Returns:
            str: Reporte formateado
        """
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE EXTRACCIÓN - BATT_DEPT_ID y XREF_ID")
        report.append("=" * 60)
        report.append("")
        
        # Sección batt_dept_id
        report.append("📊 BATT_DEPT_ID ENCONTRADOS:")
        report.append("-" * 30)
        if self.batt_dept_ids:
            for i, dept_id in enumerate(self.batt_dept_ids, 1):
                report.append(f"  {i}. {dept_id}")
            report.append("")
            report.append("🔗 FORMATO PARA CONSULTA SQL:")
            report.append(f"  WHERE batt_dept_id {self.format_sql_in_clause()}")
        else:
            report.append("  ⚠️  No se encontraron batt_dept_id")
        
        report.append("")
        report.append("🗺️  XPATH/REGEX PARA XREF_ID:")
        report.append("-" * 30)
        if self.xref_id_xpaths:
            for i, xpath in enumerate(self.xref_id_xpaths, 1):
                report.append(f"  {i}. {xpath}")
        else:
            report.append("  ⚠️  No se encontraron xpath/regex para xref_id")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report_to_file(self, output_file: str) -> bool:
        """
        Guarda el reporte en un archivo.
        
        Args:
            output_file (str): Ruta del archivo de salida
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            report = self.generate_report()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✓ Reporte guardado en: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error al guardar reporte: {e}")
            return False
    
    def extract_all(self, file_path: str) -> Dict[str, Any]:
        """
        Ejecuta todo el proceso de extracción.
        
        Args:
            file_path (str): Ruta al archivo JSON
            
        Returns:
            Dict[str, Any]: Diccionario con los resultados
        """
        result = {
            'success': False,
            'batt_dept_ids': [],
            'xref_id_xpaths': [],
            'sql_in_clause': '',
            'file_path': file_path
        }
        
        if self.load_json_file(file_path):
            result['batt_dept_ids'] = self.extract_batt_dept_ids()
            result['xref_id_xpaths'] = self.extract_xref_id_xpaths()
            result['sql_in_clause'] = self.format_sql_in_clause()
            result['success'] = True
        
        return result


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Extrae batt_dept_id y xpath para xref_id de archivos JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python batt_dept_extractor.py archivo.json
  python batt_dept_extractor.py archivo.json --output reporte.txt
  python batt_dept_extractor.py archivo.json --quiet
  
  También puedes arrastrar un archivo JSON directamente sobre este script.
        """
    )
    
    parser.add_argument(
        'json_file',
        nargs='?',  # Hacer el argumento opcional
        help='Archivo JSON a procesar'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Archivo donde guardar el reporte (opcional)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso - solo muestra resultados'
    )
    
    args = parser.parse_args()
    
    # Bucle principal para procesar múltiples archivos
    while True:
        # Si no se proporciona archivo, solicitar al usuario
        json_file = args.json_file
        if not json_file:
            print("🔍 EXTRACTOR DE BATT_DEPT_ID y XPATH")
            print("=" * 40)
            print()
            print("Puedes:")
            print("• Arrastrar un archivo JSON aquí y presionar Enter")
            print("• Escribir la ruta completa del archivo")
            print("• Presionar Enter sin nada para salir")
            print()
            
            try:
                while True:
                    user_input = input("📁 Archivo JSON (arrastra aquí): ")
                    
                    if not user_input.strip():
                        print("👋 Saliendo...")
                        sys.exit(0)
                    
                    # Limpiar la entrada del usuario
                    json_file = user_input.strip()
                    
                    # Remover comillas si las hay (común cuando se arrastra desde Windows)
                    if json_file.startswith('"') and json_file.endswith('"'):
                        json_file = json_file[1:-1]
                    elif json_file.startswith("'") and json_file.endswith("'"):
                        json_file = json_file[1:-1]
                    
                    # Usar raw string para evitar problemas con backslashes
                    json_file = json_file.strip()
                    
                    print(f"🔍 Procesando ruta: {json_file}")
                    
                    # Verificar directamente si el archivo existe
                    if os.path.isfile(json_file):
                        print("✅ Archivo encontrado")
                        break
                    else:
                        print(f"❌ Archivo no encontrado en: {json_file}")
                        
                        # Mostrar información de debug
                        print(f"   • ¿Existe la ruta? {os.path.exists(json_file)}")
                        if os.path.exists(json_file):
                            print(f"   • ¿Es archivo? {os.path.isfile(json_file)}")
                            print(f"   • ¿Es directorio? {os.path.isdir(json_file)}")
                        
                        print("   Intenta de nuevo:")
                    
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                sys.exit(0)
        
        # Verificar que el archivo existe
        if not os.path.isfile(json_file):
            print(f"✗ Error: El archivo no existe o no es válido")
            print(f"   Ruta: {json_file}")
            print(f"   ¿Existe? {os.path.exists(json_file)}")
            if os.path.exists(json_file):
                print(f"   ¿Es archivo? {os.path.isfile(json_file)}")
                print(f"   ¿Es directorio? {os.path.isdir(json_file)}")
            sys.exit(1)
        
        # Crear extractor y procesar
        extractor = BattDeptExtractor()
        
        if not args.quiet:
            print("🚀 Iniciando extracción de datos...")
            print(f"📁 Archivo: {json_file}")
            print("-" * 50)
        
        result = extractor.extract_all(json_file)
        
        if result['success']:
            if not args.quiet:
                print("\n" + extractor.generate_report())
            else:
                # Modo silencioso - solo resultados clave
                if result['batt_dept_ids']:
                    print(f"BATT_DEPT_IDs: {', '.join(map(str, result['batt_dept_ids']))}")
                    print(f"SQL: WHERE batt_dept_id {result['sql_in_clause']}")
                if result['xref_id_xpaths']:
                    print(f"XREF_ID XPATH: {', '.join(result['xref_id_xpaths'])}")
            
            # Guardar reporte si se especificó archivo de salida
            if args.output:
                extractor.save_report_to_file(args.output)
            
            # Preguntar si quiere procesar otro archivo
            print("\n" + "=" * 50)
            try:
                while True:
                    respuesta = input("¿Quieres analizar otro archivo JSON? (s/n): ").strip().lower()
                    if respuesta in ['s', 'si', 'y', 'yes']:
                        print()  # Línea en blanco para separar
                        args.json_file = None  # Resetear para pedir nuevo archivo
                        break
                    elif respuesta in ['n', 'no']:
                        print("👋 ¡Hasta luego!")
                        sys.exit(0)
                    else:
                        print("Por favor responde 's' para sí o 'n' para no")
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                sys.exit(0)
            
        else:
            print("✗ Error en el procesamiento del archivo")
            
            # Preguntar si quiere intentar con otro archivo
            try:
                while True:
                    respuesta = input("\n¿Quieres intentar con otro archivo JSON? (s/n): ").strip().lower()
                    if respuesta in ['s', 'si', 'y', 'yes']:
                        print()  # Línea en blanco para separar
                        args.json_file = None  # Resetear para pedir nuevo archivo
                        break
                    elif respuesta in ['n', 'no']:
                        print("👋 ¡Hasta luego!")
                        sys.exit(1)
                    else:
                        print("Por favor responde 's' para sí o 'n' para no")
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                sys.exit(1)


if __name__ == "__main__":
    main()