"""
Script 4: Extractor de xref_id desde XML
Extrae valores de xref_id de archivos XML usando XPath
"""

import xml.etree.ElementTree as ET
import os
import logging
import json
from datetime import datetime
from typing import Optional, Dict, List, Union

class XrefIdExtractor:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.logger: Optional[logging.Logger] = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el extractor"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"xref_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
            if self.logger:
                self.logger.info("Configuración cargada exitosamente")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al cargar configuración: {str(e)}")
            raise
    
    def extract_xref_id_from_xml(self, xml_file_path: str, xpath: Optional[str] = None) -> Optional[str]:
        """
        Extrae xref_id de un archivo XML usando XPath
        
        Args:
            xml_file_path: Ruta al archivo XML
            xpath: XPath personalizado (opcional, usa configuración por defecto)
            
        Returns:
            Valor del xref_id o None si no se encuentra
        """
        try:
            if self.logger:
                self.logger.info(f"Extrayendo xref_id de: {xml_file_path}")
            
            # Usar XPath de configuración si no se especifica uno
            if xpath is None and self.config:
                xpath = self.config['xml'].get('identificador_xpath', '//CAD')
            
            if self.logger:
                self.logger.info(f"Usando XPath: {xpath}")
            
            # Parsear XML
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Extraer valor usando XPath
            xref_value = self._extract_value_with_xpath(root, xpath)
            
            if xref_value:
                if self.logger:
                    self.logger.info(f"xref_id encontrado: {xref_value}")
                return xref_value
            else:
                # Intentar búsquedas alternativas
                alternative_xpaths = [
                    '//CAD',
                    '//xref_id',
                    '//dispatch_number',
                    '//ReportNumber',
                    '//RECORDID',
                    '//ID'
                ]
                
                for alt_xpath in alternative_xpaths:
                    if alt_xpath != xpath:  # No repetir el xpath original
                        if self.logger:
                            self.logger.debug(f"Intentando XPath alternativo: {alt_xpath}")
                        xref_value = self._extract_value_with_xpath(root, alt_xpath)
                        if xref_value:
                            if self.logger:
                                self.logger.info(f"xref_id encontrado con XPath alternativo {alt_xpath}: {xref_value}")
                            return xref_value
                
                if self.logger:
                    self.logger.warning(f"No se encontró xref_id en {xml_file_path}")
                return None
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al extraer xref_id: {str(e)}")
            return None
    
    def _extract_value_with_xpath(self, root, xpath: Optional[str]) -> Optional[str]:
        """
        Extrae valor usando XPath con múltiples estrategias
        
        Args:
            root: Elemento raíz del XML
            xpath: XPath a evaluar
            
        Returns:
            Valor extraído o None
        """
        if not xpath:
            return None
            
        try:
            # Estrategia 1: Búsqueda directa por tag name
            if xpath.startswith('//'):
                tag_name = xpath[2:].split('[')[0]  # Extraer solo el nombre del tag
                if self.logger:
                    self.logger.debug(f"Buscando directamente el tag: {tag_name}")
                
                elements = root.findall(f".//{tag_name}")
                if self.logger:
                    self.logger.debug(f"Encontrados {len(elements)} elementos para tag '{tag_name}'")
                
                for element in elements:
                    if element.text and element.text.strip():
                        value = element.text.strip()
                        if self.logger:
                            self.logger.debug(f"Valor encontrado: '{value}'")
                        return value
            
            # Estrategia 2: Búsqueda recursiva manual
            def find_element_recursive(elem, target_tag):
                """Busca un elemento recursivamente en todo el árbol"""
                if elem.tag == target_tag or elem.tag.endswith(f"}}{target_tag}"):
                    return elem
                
                for child in elem:
                    result = find_element_recursive(child, target_tag)
                    if result is not None:
                        return result
                return None
            
            if xpath.startswith('//'):
                target_tag = xpath[2:].split('[')[0].split('/')[-1]
                if self.logger:
                    self.logger.debug(f"Búsqueda recursiva manual para tag: {target_tag}")
                
                found_element = find_element_recursive(root, target_tag)
                if found_element is not None and found_element.text and found_element.text.strip():
                    value = found_element.text.strip()
                    if self.logger:
                        self.logger.debug(f"Valor encontrado con búsqueda recursiva: '{value}'")
                    return value
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en extracción con XPath {xpath}: {str(e)}")
            return None
    
    def extract_xref_ids_from_directory(self, directory_path: str, xpath: Optional[str] = None) -> Dict[str, str]:
        """
        Extrae xref_ids de todos los archivos XML en un directorio
        
        Args:
            directory_path: Ruta al directorio con archivos XML
            xpath: XPath personalizado (opcional)
            
        Returns:
            Diccionario con filename como clave y xref_id como valor
        """
        try:
            results = {}
            
            if not os.path.exists(directory_path):
                if self.logger:
                    self.logger.error(f"Directorio no existe: {directory_path}")
                return results
            
            xml_files = [f for f in os.listdir(directory_path) if f.endswith('.xml')]
            
            if not xml_files:
                if self.logger:
                    self.logger.warning(f"No se encontraron archivos XML en: {directory_path}")
                return results
            
            if self.logger:
                self.logger.info(f"Procesando {len(xml_files)} archivos XML")
            
            for filename in xml_files:
                filepath = os.path.join(directory_path, filename)
                xref_id = self.extract_xref_id_from_xml(filepath, xpath)
                
                if xref_id:
                    results[filename] = xref_id
                    if self.logger:
                        self.logger.info(f"{filename}: xref_id = {xref_id}")
                else:
                    if self.logger:
                        self.logger.warning(f"{filename}: No se encontró xref_id")
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al procesar directorio: {str(e)}")
            return {}
    
    def analyze_xml_structure_for_xref(self, xml_file_path: str) -> Dict[str, List]:
        """
        Analiza la estructura del XML para encontrar posibles campos xref_id
        
        Args:
            xml_file_path: Ruta al archivo XML
            
        Returns:
            Diccionario con información de la estructura
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            potential_xref_fields = []
            all_elements = []
            
            def analyze_recursive(element, path=""):
                current_path = f"{path}/{element.tag}" if path else element.tag
                
                # Agregar a lista de todos los elementos
                all_elements.append({
                    'tag': element.tag,
                    'path': current_path,
                    'text': element.text.strip() if element.text else None,
                    'attributes': element.attrib
                })
                
                # Buscar campos que podrían ser xref_id
                tag_lower = element.tag.lower()
                if any(keyword in tag_lower for keyword in ['xref', 'id', 'cad', 'dispatch', 'report', 'record']):
                    if element.text and element.text.strip():
                        potential_xref_fields.append({
                            'tag': element.tag,
                            'xpath': f"//{element.tag}",
                            'value': element.text.strip(),
                            'full_path': current_path
                        })
                
                # Continuar recursivamente
                for child in element:
                    analyze_recursive(child, current_path)
            
            analyze_recursive(root)
            
            results = {
                'potential_xref_fields': potential_xref_fields,
                'total_elements': len(all_elements),
                'xml_file': os.path.basename(xml_file_path),
                'root_tag': root.tag
            }
            
            if self.logger:
                self.logger.info(f"Análisis completado para {xml_file_path}:")
                self.logger.info(f"  - Total elementos: {len(all_elements)}")
                self.logger.info(f"  - Posibles campos xref: {len(potential_xref_fields)}")
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al analizar estructura XML: {str(e)}")
            return {}

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extractor de xref_id desde archivos XML')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--xml_file', help='Archivo XML específico a procesar')
    parser.add_argument('--directory', help='Directorio con archivos XML')
    parser.add_argument('--xpath', help='XPath personalizado para xref_id')
    parser.add_argument('--analyze', action='store_true', help='Analizar estructura XML para encontrar campos xref')
    
    args = parser.parse_args()
    
    if not args.xml_file and not args.directory:
        print("❌ Error: Debe especificar --xml_file o --directory")
        return 1
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        extractor = XrefIdExtractor(config_path)
        
        if args.xml_file:
            # Procesar archivo único
            if args.analyze:
                analysis = extractor.analyze_xml_structure_for_xref(args.xml_file)
                print(f"✅ Análisis de estructura:")
                print(json.dumps(analysis, indent=2, ensure_ascii=False))
            else:
                xref_id = extractor.extract_xref_id_from_xml(args.xml_file, args.xpath)
                if xref_id:
                    print(f"✅ xref_id encontrado: {xref_id}")
                else:
                    print(f"❌ No se encontró xref_id")
        
        elif args.directory:
            # Procesar directorio
            results = extractor.extract_xref_ids_from_directory(args.directory, args.xpath)
            print(f"✅ Resultados del directorio:")
            for filename, xref_id in results.items():
                print(f"  {filename}: {xref_id}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
