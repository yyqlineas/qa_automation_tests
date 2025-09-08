"""
Script 2: Buscador de batt_dept_id en JSON
Busca y extrae batt_dept_id de archivos JSON descargados
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

class BattDeptIdFinder:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el buscador"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"batt_dept_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(log_dir, log_filename)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.info("Configuración cargada exitosamente")
        except Exception as e:
            self.logger.error(f"Error al cargar configuración: {str(e)}")
            raise
            
    def find_batt_dept_ids_in_json(self, json_file_path: str) -> List[str]:
        """
        Busca batt_dept_id en un archivo JSON
        
        Args:
            json_file_path: Ruta al archivo JSON
            
        Returns:
            Lista de batt_dept_ids encontrados
        """
        try:
            self.logger.info(f"Buscando batt_dept_id en: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            batt_dept_ids = []
            
            # Buscar recursivamente en el JSON
            def search_recursive(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Buscar claves que contengan 'batt_dept_id'
                        if 'batt_dept_id' in key.lower() or key == 'batt_dept_id':
                            if isinstance(value, (str, int)):
                                batt_dept_ids.append(str(value))
                                self.logger.info(f"Encontrado batt_dept_id en {current_path}: {value}")
                        
                        # Continuar búsqueda recursiva
                        search_recursive(value, current_path)
                        
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_recursive(item, f"{path}[{i}]")
            
            search_recursive(data)
            
            # Eliminar duplicados manteniendo orden
            unique_ids = list(dict.fromkeys(batt_dept_ids))
            
            self.logger.info(f"Total batt_dept_ids únicos encontrados: {len(unique_ids)}")
            return unique_ids
            
        except Exception as e:
            self.logger.error(f"Error al buscar batt_dept_id en JSON: {str(e)}")
            return []
    
    def find_batt_dept_ids_in_directory(self, directory_path: str) -> Dict[str, List[str]]:
        """
        Busca batt_dept_ids en todos los archivos JSON de un directorio
        
        Args:
            directory_path: Ruta al directorio con archivos JSON
            
        Returns:
            Diccionario con filename como clave y lista de batt_dept_ids como valor
        """
        try:
            results = {}
            
            if not os.path.exists(directory_path):
                self.logger.error(f"Directorio no existe: {directory_path}")
                return results
            
            json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
            
            if not json_files:
                self.logger.warning(f"No se encontraron archivos JSON en: {directory_path}")
                return results
            
            self.logger.info(f"Procesando {len(json_files)} archivos JSON")
            
            for filename in json_files:
                filepath = os.path.join(directory_path, filename)
                batt_dept_ids = self.find_batt_dept_ids_in_json(filepath)
                
                if batt_dept_ids:
                    results[filename] = batt_dept_ids
                    self.logger.info(f"{filename}: {len(batt_dept_ids)} batt_dept_ids encontrados")
                else:
                    self.logger.warning(f"{filename}: No se encontraron batt_dept_ids")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error al procesar directorio: {str(e)}")
            return {}
    
    def extract_specific_fields(self, json_file_path: str, fields: List[str]) -> Dict[str, List]:
        """
        Extrae campos específicos del JSON
        
        Args:
            json_file_path: Ruta al archivo JSON
            fields: Lista de campos a extraer
            
        Returns:
            Diccionario con los campos extraídos
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = {field: [] for field in fields}
            
            def search_recursive(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Buscar cada campo solicitado
                        for field in fields:
                            if field.lower() in key.lower() or key == field:
                                results[field].append({
                                    'path': current_path,
                                    'value': value
                                })
                        
                        search_recursive(value, current_path)
                        
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_recursive(item, f"{path}[{i}]")
            
            search_recursive(data)
            
            self.logger.info(f"Campos extraídos de {os.path.basename(json_file_path)}:")
            for field, values in results.items():
                self.logger.info(f"  {field}: {len(values)} ocurrencias")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error al extraer campos: {str(e)}")
            return {}

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Buscador de batt_dept_id en archivos JSON')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--json_file', help='Archivo JSON específico a procesar')
    parser.add_argument('--directory', help='Directorio con archivos JSON')
    parser.add_argument('--fields', nargs='+', default=['batt_dept_id'], help='Campos a buscar')
    
    args = parser.parse_args()
    
    if not args.json_file and not args.directory:
        print("❌ Error: Debe especificar --json_file o --directory")
        return 1
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        finder = BattDeptIdFinder(config_path)
        
        if args.json_file:
            # Procesar archivo único
            if args.fields == ['batt_dept_id']:
                ids = finder.find_batt_dept_ids_in_json(args.json_file)
                print(f"✅ batt_dept_ids encontrados: {ids}")
            else:
                results = finder.extract_specific_fields(args.json_file, args.fields)
                print(f"✅ Campos extraídos: {json.dumps(results, indent=2, ensure_ascii=False)}")
        
        elif args.directory:
            # Procesar directorio
            results = finder.find_batt_dept_ids_in_directory(args.directory)
            print(f"✅ Resultados del directorio:")
            for filename, ids in results.items():
                print(f"  {filename}: {ids}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
