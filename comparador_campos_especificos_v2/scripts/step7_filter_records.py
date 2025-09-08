"""
Script 7: Filtrador de registros
Filtra registros basado en múltiples criterios y genera reportes
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
import re

class RecordFilter:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.logger: Optional[logging.Logger] = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el filtrador"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"record_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
    
    def filter_by_date_range(self, records: List[Dict], 
                           date_field: str = 'created_at',
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> List[Dict]:
        """
        Filtra registros por rango de fechas
        
        Args:
            records: Lista de registros
            date_field: Campo de fecha a usar
            start_date: Fecha inicio (formato: YYYY-MM-DD)
            end_date: Fecha fin (formato: YYYY-MM-DD)
            
        Returns:
            Lista de registros filtrados
        """
        try:
            if not records:
                return []
            
            filtered_records = []
            
            # Convertir fechas string a datetime si se proporcionan
            start_dt = None
            end_dt = None
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                # Incluir todo el día final
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            
            if self.logger:
                self.logger.info(f"Filtrando por fecha en campo '{date_field}': {start_date} - {end_date}")
            
            for record in records:
                if date_field not in record or not record[date_field]:
                    continue
                
                try:
                    # Intentar parsear la fecha del registro
                    record_date = record[date_field]
                    
                    # Si es string, convertir a datetime
                    if isinstance(record_date, str):
                        # Intentar diferentes formatos
                        date_formats = [
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d',
                            '%Y/%m/%d %H:%M:%S',
                            '%Y/%m/%d',
                            '%d/%m/%Y %H:%M:%S',
                            '%d/%m/%Y'
                        ]
                        
                        record_dt = None
                        for fmt in date_formats:
                            try:
                                record_dt = datetime.strptime(record_date, fmt)
                                break
                            except ValueError:
                                continue
                        
                        if not record_dt:
                            if self.logger:
                                self.logger.warning(f"No se pudo parsear fecha: {record_date}")
                            continue
                    else:
                        record_dt = record_date
                    
                    # Aplicar filtros de fecha
                    if start_dt and record_dt < start_dt:
                        continue
                    if end_dt and record_dt > end_dt:
                        continue
                    
                    filtered_records.append(record)
                    
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Error al procesar fecha en registro: {str(e)}")
                    continue
            
            if self.logger:
                self.logger.info(f"Filtro de fecha: {len(filtered_records)}/{len(records)} registros")
            
            return filtered_records
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en filtro por fecha: {str(e)}")
            return records
    
    def filter_by_field_values(self, records: List[Dict], 
                             field_filters: Dict[str, Union[str, List[str]]]) -> List[Dict]:
        """
        Filtra registros por valores específicos en campos
        
        Args:
            records: Lista de registros
            field_filters: Diccionario con filtros por campo
            
        Returns:
            Lista de registros filtrados
        """
        try:
            if not records or not field_filters:
                return records
            
            filtered_records = []
            
            if self.logger:
                self.logger.info(f"Aplicando filtros de campo: {field_filters}")
            
            for record in records:
                include_record = True
                
                for field, expected_values in field_filters.items():
                    if field not in record:
                        include_record = False
                        break
                    
                    record_value = str(record[field]).strip().lower()
                    
                    # Convertir valores esperados a lista si es string
                    if isinstance(expected_values, str):
                        expected_values = [expected_values]
                    
                    # Normalizar valores esperados
                    expected_values_lower = [str(v).strip().lower() for v in expected_values]
                    
                    # Verificar si el valor del registro coincide con algún valor esperado
                    if record_value not in expected_values_lower:
                        include_record = False
                        break
                
                if include_record:
                    filtered_records.append(record)
            
            if self.logger:
                self.logger.info(f"Filtro de campos: {len(filtered_records)}/{len(records)} registros")
            
            return filtered_records
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en filtro por campos: {str(e)}")
            return records
    
    def filter_by_text_pattern(self, records: List[Dict], 
                             field: str, 
                             pattern: str, 
                             case_sensitive: bool = False) -> List[Dict]:
        """
        Filtra registros por patrón de texto (regex o substring)
        
        Args:
            records: Lista de registros
            field: Campo donde buscar
            pattern: Patrón a buscar (regex o texto)
            case_sensitive: Si la búsqueda es sensible a mayúsculas
            
        Returns:
            Lista de registros filtrados
        """
        try:
            if not records or not pattern:
                return records
            
            filtered_records = []
            
            # Compilar regex si parece ser un patrón regex
            is_regex = any(char in pattern for char in ['.*', '+', '?', '[', ']', '(', ')', '^', '$'])
            
            if is_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    regex_pattern = re.compile(pattern, flags)
                except re.error:
                    # Si no es regex válido, tratar como texto literal
                    is_regex = False
            
            if self.logger:
                search_type = "regex" if is_regex else "texto"
                self.logger.info(f"Filtrando por {search_type} en campo '{field}': '{pattern}'")
            
            for record in records:
                if field not in record or not record[field]:
                    continue
                
                field_value = str(record[field])
                
                try:
                    if is_regex:
                        # Búsqueda por regex
                        if regex_pattern.search(field_value):
                            filtered_records.append(record)
                    else:
                        # Búsqueda por texto simple
                        if case_sensitive:
                            if pattern in field_value:
                                filtered_records.append(record)
                        else:
                            if pattern.lower() in field_value.lower():
                                filtered_records.append(record)
                
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Error al aplicar patrón en registro: {str(e)}")
                    continue
            
            if self.logger:
                self.logger.info(f"Filtro de patrón: {len(filtered_records)}/{len(records)} registros")
            
            return filtered_records
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en filtro por patrón: {str(e)}")
            return records
    
    def filter_by_xref_id_list(self, records: List[Dict], 
                             xref_ids: List[str], 
                             xref_field: str = 'xref_id',
                             exclude: bool = False) -> List[Dict]:
        """
        Filtra registros por lista de xref_ids
        
        Args:
            records: Lista de registros
            xref_ids: Lista de xref_ids a incluir/excluir
            xref_field: Campo que contiene el xref_id
            exclude: Si True, excluye los IDs especificados; si False, los incluye
            
        Returns:
            Lista de registros filtrados
        """
        try:
            if not records or not xref_ids:
                return records
            
            # Normalizar lista de IDs
            normalized_ids = [str(xid).strip().lower() for xid in xref_ids]
            
            action = "excluyendo" if exclude else "incluyendo"
            if self.logger:
                self.logger.info(f"Filtrando {action} {len(normalized_ids)} xref_ids en campo '{xref_field}'")
            
            filtered_records = []
            
            for record in records:
                if xref_field not in record or not record[xref_field]:
                    if not exclude:  # Si incluimos, saltamos registros sin xref_id
                        continue
                    else:  # Si excluimos, incluimos registros sin xref_id
                        filtered_records.append(record)
                    continue
                
                record_id = str(record[xref_field]).strip().lower()
                
                if exclude:
                    # Excluir si está en la lista
                    if record_id not in normalized_ids:
                        filtered_records.append(record)
                else:
                    # Incluir si está en la lista
                    if record_id in normalized_ids:
                        filtered_records.append(record)
            
            if self.logger:
                self.logger.info(f"Filtro de xref_ids: {len(filtered_records)}/{len(records)} registros")
            
            return filtered_records
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en filtro por xref_ids: {str(e)}")
            return records
    
    def apply_combined_filters(self, records: List[Dict], filters_config: Dict[str, Any]) -> List[Dict]:
        """
        Aplica múltiples filtros de forma secuencial
        
        Args:
            records: Lista de registros inicial
            filters_config: Configuración de filtros a aplicar
            
        Returns:
            Lista de registros filtrados
        """
        try:
            if not records:
                return []
            
            current_records = records.copy()
            initial_count = len(current_records)
            
            if self.logger:
                self.logger.info(f"Aplicando filtros combinados a {initial_count} registros")
            
            # Filtro por rango de fechas
            if 'date_range' in filters_config:
                date_config = filters_config['date_range']
                current_records = self.filter_by_date_range(
                    current_records,
                    date_config.get('field', 'created_at'),
                    date_config.get('start_date'),
                    date_config.get('end_date')
                )
            
            # Filtro por valores de campos
            if 'field_values' in filters_config:
                current_records = self.filter_by_field_values(
                    current_records,
                    filters_config['field_values']
                )
            
            # Filtro por patrón de texto
            if 'text_pattern' in filters_config:
                pattern_config = filters_config['text_pattern']
                current_records = self.filter_by_text_pattern(
                    current_records,
                    pattern_config['field'],
                    pattern_config['pattern'],
                    pattern_config.get('case_sensitive', False)
                )
            
            # Filtro por lista de xref_ids
            if 'xref_id_list' in filters_config:
                xref_config = filters_config['xref_id_list']
                current_records = self.filter_by_xref_id_list(
                    current_records,
                    xref_config['xref_ids'],
                    xref_config.get('field', 'xref_id'),
                    xref_config.get('exclude', False)
                )
            
            final_count = len(current_records)
            
            if self.logger:
                self.logger.info(f"Filtros aplicados: {final_count}/{initial_count} registros finales")
            
            return current_records
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al aplicar filtros combinados: {str(e)}")
            return records
    
    def generate_filter_report(self, original_records: List[Dict], 
                             filtered_records: List[Dict],
                             filters_applied: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera reporte de filtrado
        
        Args:
            original_records: Registros originales
            filtered_records: Registros después del filtrado
            filters_applied: Filtros que se aplicaron
            
        Returns:
            Diccionario con reporte de filtrado
        """
        try:
            original_count = len(original_records)
            filtered_count = len(filtered_records)
            excluded_count = original_count - filtered_count
            retention_rate = (filtered_count / original_count * 100) if original_count > 0 else 0
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'original_count': original_count,
                'filtered_count': filtered_count,
                'excluded_count': excluded_count,
                'retention_rate_percent': round(retention_rate, 2),
                'filters_applied': filters_applied,
                'summary': f"Se filtraron {filtered_count} de {original_count} registros ({retention_rate:.1f}% retenido)"
            }
            
            # Agregar estadísticas de campos si hay registros
            if filtered_records:
                # Campos disponibles
                all_fields = set()
                for record in filtered_records[:100]:  # Muestrea primeros 100
                    all_fields.update(record.keys())
                
                report['available_fields'] = sorted(list(all_fields))
                
                # Estadísticas por campo (para campos comunes)
                field_stats = {}
                common_fields = ['xref_id', 'status', 'type', 'priority']
                
                for field in common_fields:
                    if field in all_fields:
                        values = [str(r.get(field, '')) for r in filtered_records if r.get(field)]
                        if values:
                            unique_values = list(set(values))
                            field_stats[field] = {
                                'unique_count': len(unique_values),
                                'sample_values': unique_values[:10]  # Primeros 10 valores únicos
                            }
                
                report['field_statistics'] = field_stats
            
            if self.logger:
                self.logger.info(f"Reporte generado: {report['summary']}")
            
            return report
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al generar reporte: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def save_filtered_results(self, filtered_records: List[Dict], 
                            output_path: str,
                            format_type: str = 'json') -> bool:
        """
        Guarda resultados filtrados en archivo
        
        Args:
            filtered_records: Registros filtrados
            output_path: Ruta del archivo de salida
            format_type: Formato de salida ('json', 'csv')
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if format_type.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(filtered_records, f, indent=2, ensure_ascii=False, default=str)
            
            elif format_type.lower() == 'csv':
                import csv
                
                if not filtered_records:
                    # Crear archivo CSV vacío
                    with open(output_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['No hay registros filtrados'])
                else:
                    # Obtener todas las columnas
                    all_fields = set()
                    for record in filtered_records:
                        all_fields.update(record.keys())
                    
                    field_names = sorted(list(all_fields))
                    
                    with open(output_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=field_names)
                        writer.writeheader()
                        writer.writerows(filtered_records)
            
            else:
                raise ValueError(f"Formato no soportado: {format_type}")
            
            if self.logger:
                self.logger.info(f"Resultados guardados en: {output_path} ({format_type})")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al guardar resultados: {str(e)}")
            return False

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Filtrador de registros')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--input', required=True, help='Archivo JSON con registros de entrada')
    parser.add_argument('--output', help='Archivo de salida para registros filtrados')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Formato de salida')
    
    # Filtros
    parser.add_argument('--date_field', help='Campo de fecha para filtrar')
    parser.add_argument('--start_date', help='Fecha inicio (YYYY-MM-DD)')
    parser.add_argument('--end_date', help='Fecha fin (YYYY-MM-DD)')
    parser.add_argument('--field_filter', nargs='+', help='Filtros de campo (formato: campo=valor)')
    parser.add_argument('--text_search', help='Buscar texto en campo específico (formato: campo:patrón)')
    parser.add_argument('--xref_ids', nargs='+', help='Lista de xref_ids a incluir')
    parser.add_argument('--exclude_xref_ids', nargs='+', help='Lista de xref_ids a excluir')
    
    args = parser.parse_args()
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        filter_engine = RecordFilter(config_path)
        
        # Cargar registros de entrada
        if not os.path.exists(args.input):
            print(f"❌ Error: Archivo de entrada no existe: {args.input}")
            return 1
        
        print(f"📂 Cargando registros desde: {args.input}")
        
        with open(args.input, 'r', encoding='utf-8') as f:
            original_records = json.load(f)
        
        if not isinstance(original_records, list):
            print(f"❌ Error: El archivo debe contener una lista de registros")
            return 1
        
        print(f"📊 Registros cargados: {len(original_records)}")
        
        # Construir configuración de filtros
        filters_config = {}
        
        # Filtro de fechas
        if args.date_field and (args.start_date or args.end_date):
            filters_config['date_range'] = {
                'field': args.date_field,
                'start_date': args.start_date,
                'end_date': args.end_date
            }
        
        # Filtros de campos
        if args.field_filter:
            field_filters = {}
            for filter_item in args.field_filter:
                if '=' in filter_item:
                    field, value = filter_item.split('=', 1)
                    field_filters[field] = value
            
            if field_filters:
                filters_config['field_values'] = field_filters
        
        # Búsqueda de texto
        if args.text_search and ':' in args.text_search:
            field, pattern = args.text_search.split(':', 1)
            filters_config['text_pattern'] = {
                'field': field,
                'pattern': pattern,
                'case_sensitive': False
            }
        
        # Filtro de xref_ids
        if args.xref_ids:
            filters_config['xref_id_list'] = {
                'xref_ids': args.xref_ids,
                'exclude': False
            }
        elif args.exclude_xref_ids:
            filters_config['xref_id_list'] = {
                'xref_ids': args.exclude_xref_ids,
                'exclude': True
            }
        
        # Aplicar filtros
        if filters_config:
            print(f"🔍 Aplicando filtros...")
            filtered_records = filter_engine.apply_combined_filters(original_records, filters_config)
        else:
            print("⚠️  No se especificaron filtros, usando todos los registros")
            filtered_records = original_records
        
        # Generar reporte
        report = filter_engine.generate_filter_report(original_records, filtered_records, filters_config)
        print(f"📈 {report['summary']}")
        
        # Guardar resultados si se especifica archivo de salida
        if args.output:
            success = filter_engine.save_filtered_results(filtered_records, args.output, args.format)
            if success:
                print(f"💾 Resultados guardados en: {args.output}")
            else:
                print(f"❌ Error al guardar resultados")
                return 1
        else:
            # Mostrar muestra de resultados
            if filtered_records:
                print(f"📄 Muestra de resultados filtrados:")
                for i, record in enumerate(filtered_records[:3]):
                    print(f"  Registro {i+1}: {record}")
                
                if len(filtered_records) > 3:
                    print(f"  ... y {len(filtered_records) - 3} registros más")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
