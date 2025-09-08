"""
Script 3: Buscador de XPath para xref_id en JSON
Busca y extrae información de XPath para xref_id desde archivos JSON
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List

class XrefIdPathFinder:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el buscador de paths"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"xref_path_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
            
    def find_xref_id_paths(self, json_file_path: str) -> Dict[str, List[Dict]]:
        """
        Busca paths de xref_id en un archivo JSON
        
        Args:
            json_file_path: Ruta al archivo JSON
            
        Returns:
            Diccionario con información de paths encontrados
        """
        try:
            self.logger.info(f"Buscando paths de xref_id en: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            xref_paths = []
            xpath_mappings = []
            
            # Buscar recursivamente en el JSON
            def search_recursive(obj, path="", json_path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        current_json_path = f"{json_path}/{key}" if json_path else key
                        
                        # Buscar claves relacionadas con xref_id
                        if 'xref' in key.lower() and 'id' in key.lower():
                            xref_paths.append({
                                'field_name': key,
                                'json_path': current_path,
                                'xpath_equivalent': self._convert_to_xpath(current_json_path),
                                'value': value,
                                'data_type': type(value).__name__
                            })
                            self.logger.info(f"Encontrado xref_id en {current_path}: {value}")
                        
                        # Buscar xpath mappings
                        elif 'xpath' in key.lower() or 'path' in key.lower():
                            if isinstance(value, str) and ('xref' in value.lower() or '//' in value):
                                xpath_mappings.append({
                                    'mapping_key': key,
                                    'xpath_value': value,
                                    'json_path': current_path
                                })
                                self.logger.info(f"Encontrado xpath mapping en {current_path}: {value}")
                        
                        # Continuar búsqueda recursiva
                        search_recursive(value, current_path, current_json_path)
                        
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_recursive(item, f"{path}[{i}]", f"{json_path}[{i}]")
            
            search_recursive(data)
            
            results = {
                'xref_id_fields': xref_paths,
                'xpath_mappings': xpath_mappings,
                'file_processed': os.path.basename(json_file_path),
                'total_xref_fields': len(xref_paths),
                'total_xpath_mappings': len(xpath_mappings)
            }
            
            self.logger.info(f"Búsqueda completada:")
            self.logger.info(f"  - Campos xref_id encontrados: {len(xref_paths)}")
            self.logger.info(f"  - XPath mappings encontrados: {len(xpath_mappings)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error al buscar paths de xref_id: {str(e)}")
            return {}
    
    def _convert_to_xpath(self, json_path: str) -> str:
        """
        Convierte un path JSON a XPath equivalente
        
        Args:
            json_path: Path en formato JSON
            
        Returns:
            XPath equivalente
        """
        # Convertir path JSON a XPath
        xpath = json_path.replace('.', '/')
        
        # Manejar arrays
        import re
        xpath = re.sub(r'\[(\d+)\]', r'[\1+1]', xpath)  # Ajustar índices (JSON 0-based, XPath 1-based)
        
        # Agregar // al inicio si no está presente
        if not xpath.startswith('//'):
            xpath = '//' + xpath
        
        return xpath
    
    def generate_xpath_mapping(self, json_file_path: str, target_fields: List[str] = None) -> Dict[str, str]:
        """
        Genera mappings de XPath para campos específicos
        
        Args:
            json_file_path: Ruta al archivo JSON
            target_fields: Lista de campos objetivo (default: ['xref_id'])
            
        Returns:
            Diccionario con mappings campo -> xpath
        """
        try:
            if target_fields is None:
                target_fields = ['xref_id', 'dispatch_number', 'CAD']
            
            results = self.find_xref_id_paths(json_file_path)
            xpath_mappings = {}
            
            # Procesar campos encontrados
            for field_info in results.get('xref_id_fields', []):
                field_name = field_info['field_name'].lower()
                
                for target_field in target_fields:
                    if target_field.lower() in field_name:
                        xpath_mappings[target_field] = field_info['xpath_equivalent']
                        self.logger.info(f"Mapping generado: {target_field} -> {field_info['xpath_equivalent']}")
            
            # Agregar mappings existentes del JSON
            for mapping_info in results.get('xpath_mappings', []):
                mapping_key = mapping_info['mapping_key']
                xpath_value = mapping_info['xpath_value']
                
                for target_field in target_fields:
                    if target_field.lower() in mapping_key.lower():
                        xpath_mappings[target_field] = xpath_value
                        self.logger.info(f"Mapping existente encontrado: {target_field} -> {xpath_value}")
            
            return xpath_mappings
            
        except Exception as e:
            self.logger.error(f"Error al generar mappings: {str(e)}")
            return {}
    
    def save_mappings_to_config(self, mappings: Dict[str, str], output_file: str = None) -> bool:
        """
        Guarda los mappings en un archivo de configuración
        
        Args:
            mappings: Diccionario con los mappings
            output_file: Archivo de salida (opcional)
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            if output_file is None:
                config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
                output_file = os.path.join(config_dir, 'xpath_mappings.json')
            
            # Crear estructura de configuración
            config_data = {
                'generated_at': datetime.now().isoformat(),
                'xpath_mappings': mappings,
                'description': 'XPath mappings generados automáticamente para xref_id'
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Mappings guardados en: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar mappings: {str(e)}")
            return False

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Buscador de XPath para xref_id en JSON')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--json_file', required=True, help='Archivo JSON a procesar')
    parser.add_argument('--fields', nargs='+', default=['xref_id', 'dispatch_number', 'CAD'], help='Campos objetivo')
    parser.add_argument('--save_mappings', action='store_true', help='Guardar mappings en archivo de configuración')
    parser.add_argument('--output', help='Archivo de salida para mappings')
    
    args = parser.parse_args()
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        finder = XrefIdPathFinder(config_path)
        
        # Buscar paths
        results = finder.find_xref_id_paths(args.json_file)
        print(f"✅ Resultados de búsqueda:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # Generar mappings
        mappings = finder.generate_xpath_mapping(args.json_file, args.fields)
        print(f"\n✅ XPath Mappings generados:")
        for field, xpath in mappings.items():
            print(f"  {field}: {xpath}")
        
        # Guardar mappings si se solicita
        if args.save_mappings:
            success = finder.save_mappings_to_config(mappings, args.output)
            if success:
                print(f"✅ Mappings guardados exitosamente")
            else:
                print(f"❌ Error al guardar mappings")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
