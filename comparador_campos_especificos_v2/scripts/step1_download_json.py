"""
Script 1: Descargador de JSON
Descarga archivos JSON desde una API basado en parámetros específicos
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional

class JSONDownloader:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el descargador"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"json_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
            
    def download_json(self, batt_dept_id: str, output_dir: str = None) -> Optional[str]:
        """
        Descarga un archivo JSON basado en el batt_dept_id
        
        Args:
            batt_dept_id: ID del departamento de batería
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Ruta del archivo descargado o None si falla
        """
        try:
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads')
            os.makedirs(output_dir, exist_ok=True)
            
            # Construir URL
            api_config = self.config['json_api']
            url = api_config['base_url'] + api_config['endpoints']['download'].format(batt_dept_id=batt_dept_id)
            
            self.logger.info(f"Descargando JSON para batt_dept_id: {batt_dept_id}")
            self.logger.info(f"URL: {url}")
            
            # Realizar petición
            headers = api_config.get('headers', {})
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Guardar archivo
                filename = f"data_{batt_dept_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(response.json(), f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"JSON descargado exitosamente: {filepath}")
                return filepath
            else:
                self.logger.error(f"Error en descarga: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al descargar JSON: {str(e)}")
            return None
    
    def download_multiple_json(self, batt_dept_ids: list, output_dir: str = None) -> Dict[str, str]:
        """
        Descarga múltiples archivos JSON
        
        Args:
            batt_dept_ids: Lista de IDs de departamento
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Diccionario con batt_dept_id como clave y filepath como valor
        """
        results = {}
        
        for batt_dept_id in batt_dept_ids:
            filepath = self.download_json(batt_dept_id, output_dir)
            if filepath:
                results[batt_dept_id] = filepath
            else:
                self.logger.warning(f"Fallo en descarga para batt_dept_id: {batt_dept_id}")
                
        self.logger.info(f"Descarga completada. {len(results)}/{len(batt_dept_ids)} archivos descargados")
        return results

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Descargador de archivos JSON')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--batt_dept_id', required=True, help='ID del departamento de batería')
    parser.add_argument('--output', help='Directorio de salida')
    
    args = parser.parse_args()
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        downloader = JSONDownloader(config_path)
        filepath = downloader.download_json(args.batt_dept_id, args.output)
        
        if filepath:
            print(f"✅ Descarga exitosa: {filepath}")
            return 0
        else:
            print("❌ Error en la descarga")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
