"""
Script 6: Verificador de registros en base de datos
Verifica que los registros existan en la base de datos PostgreSQL
"""

import psycopg2
import os
import logging
import json
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

class DatabaseVerifier:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.logger: Optional[logging.Logger] = None
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el verificador"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"db_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
    
    def connect_database(self) -> bool:
        """
        Conecta a la base de datos PostgreSQL
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            if not self.config:
                raise Exception("Configuración no cargada")
            
            db_config = self.config.get('postgresql', {})
            
            # Obtener parámetros de conexión
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 5432)
            database = db_config.get('database')
            username = db_config.get('username')
            password = db_config.get('password')
            
            if not all([database, username]):
                raise Exception("Faltan parámetros de conexión a base de datos")
            
            if self.logger:
                self.logger.info(f"Conectando a base de datos: {username}@{host}:{port}/{database}")
            
            # Crear conexión
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            
            if self.logger:
                self.logger.info("Conexión a base de datos establecida exitosamente")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al conectar a base de datos: {str(e)}")
            return False
    
    def disconnect_database(self):
        """Cierra la conexión a la base de datos"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                if self.logger:
                    self.logger.info("Conexión a base de datos cerrada")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al cerrar conexión: {str(e)}")
    
    def verify_record_exists(self, xref_id: str, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Verifica si existe un registro con el xref_id específico
        
        Args:
            xref_id: ID a buscar
            table_name: Tabla específica (opcional, usa configuración por defecto)
            
        Returns:
            Diccionario con información del registro
        """
        try:
            if not self.connection:
                if not self.connect_database():
                    return {'exists': False, 'error': 'No se pudo conectar a la base de datos'}
            
            # Usar tabla de configuración si no se especifica
            if not table_name and self.config:
                table_name = self.config.get('postgresql', {}).get('tabla_principal', 'reportes')
            
            if not table_name:
                return {'exists': False, 'error': 'No se especificó tabla'}
            
            cursor = self.connection.cursor()
            
            if self.logger:
                self.logger.info(f"Verificando xref_id: {xref_id} en tabla: {table_name}")
            
            # Buscar por diferentes campos posibles
            search_fields = ['xref_id', 'CAD', 'dispatch_number', 'report_number', 'id']
            
            record_data = None
            found_field = None
            
            for field in search_fields:
                try:
                    query = f"SELECT * FROM {table_name} WHERE {field} = %s LIMIT 1"
                    cursor.execute(query, (xref_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        # Obtener nombres de columnas
                        column_names = [desc[0] for desc in cursor.description]
                        record_data = dict(zip(column_names, result))
                        found_field = field
                        break
                        
                except psycopg2.Error as e:
                    # Campo no existe en la tabla, continuar con el siguiente
                    if self.logger:
                        self.logger.debug(f"Campo {field} no existe en tabla {table_name}")
                    continue
            
            cursor.close()
            
            if record_data:
                if self.logger:
                    self.logger.info(f"✅ Registro encontrado por campo: {found_field}")
                
                return {
                    'exists': True,
                    'found_by_field': found_field,
                    'table': table_name,
                    'record_data': record_data,
                    'record_count': 1
                }
            else:
                if self.logger:
                    self.logger.warning(f"❌ Registro no encontrado: {xref_id}")
                
                return {
                    'exists': False,
                    'table': table_name,
                    'searched_fields': search_fields,
                    'xref_id': xref_id
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al verificar registro: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def verify_multiple_records(self, xref_ids: List[str], 
                              table_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Verifica múltiples registros
        
        Args:
            xref_ids: Lista de IDs a buscar
            table_name: Tabla específica (opcional)
            
        Returns:
            Diccionario con resultados para cada xref_id
        """
        results = {}
        
        if self.logger:
            self.logger.info(f"Verificando {len(xref_ids)} registros")
        
        for xref_id in xref_ids:
            results[xref_id] = self.verify_record_exists(xref_id, table_name)
        
        # Estadísticas
        found_count = sum(1 for result in results.values() if result.get('exists', False))
        total_count = len(results)
        
        if self.logger:
            self.logger.info(f"Verificación completada: {found_count}/{total_count} registros encontrados")
        
        return results
    
    def get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """
        Obtiene la estructura de una tabla
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Información de la estructura de la tabla
        """
        try:
            if not self.connection:
                if not self.connect_database():
                    return {'error': 'No se pudo conectar a la base de datos'}
            
            cursor = self.connection.cursor()
            
            # Obtener información de columnas
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
            
            cursor.execute(query, (table_name,))
            columns = cursor.fetchall()
            
            if not columns:
                return {'error': f'Tabla {table_name} no encontrada'}
            
            # Formatear información de columnas
            column_info = []
            for col in columns:
                column_info.append({
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'YES',
                    'default': col[3]
                })
            
            # Obtener información de índices
            index_query = """
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = %s
            """
            
            cursor.execute(index_query, (table_name,))
            indexes = cursor.fetchall()
            
            cursor.close()
            
            return {
                'table_name': table_name,
                'columns': column_info,
                'column_count': len(column_info),
                'indexes': [{'name': idx[0], 'definition': idx[1]} for idx in indexes]
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al obtener estructura de tabla: {str(e)}")
            return {'error': str(e)}
    
    def search_records_by_criteria(self, criteria: Dict[str, Any], 
                                 table_name: Optional[str] = None,
                                 limit: int = 100) -> Dict[str, Any]:
        """
        Busca registros por criterios específicos
        
        Args:
            criteria: Diccionario con criterios de búsqueda
            table_name: Tabla específica (opcional)
            limit: Límite de registros a retornar
            
        Returns:
            Resultados de la búsqueda
        """
        try:
            if not self.connection:
                if not self.connect_database():
                    return {'error': 'No se pudo conectar a la base de datos'}
            
            # Usar tabla de configuración si no se especifica
            if not table_name and self.config:
                table_name = self.config.get('postgresql', {}).get('tabla_principal', 'reportes')
            
            if not table_name:
                return {'error': 'No se especificó tabla'}
            
            cursor = self.connection.cursor()
            
            # Construir query WHERE
            where_conditions = []
            query_params = []
            
            for field, value in criteria.items():
                if value is not None:
                    if isinstance(value, str) and '%' in value:
                        # Búsqueda con LIKE para wildcards
                        where_conditions.append(f"{field} LIKE %s")
                    else:
                        where_conditions.append(f"{field} = %s")
                    query_params.append(value)
            
            if not where_conditions:
                return {'error': 'No se especificaron criterios de búsqueda'}
            
            # Construir query completa
            where_clause = " AND ".join(where_conditions)
            query = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT %s"
            query_params.append(limit)
            
            if self.logger:
                self.logger.info(f"Ejecutando búsqueda con criterios: {criteria}")
            
            cursor.execute(query, query_params)
            results = cursor.fetchall()
            
            # Obtener nombres de columnas
            column_names = [desc[0] for desc in cursor.description]
            
            # Formatear resultados
            records = []
            for row in results:
                records.append(dict(zip(column_names, row)))
            
            cursor.close()
            
            if self.logger:
                self.logger.info(f"Encontrados {len(records)} registros")
            
            return {
                'success': True,
                'table': table_name,
                'criteria': criteria,
                'record_count': len(records),
                'records': records,
                'column_names': column_names
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en búsqueda por criterios: {str(e)}")
            return {'error': str(e)}
    
    def get_record_statistics(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la tabla
        
        Args:
            table_name: Tabla específica (opcional)
            
        Returns:
            Estadísticas de la tabla
        """
        try:
            if not self.connection:
                if not self.connect_database():
                    return {'error': 'No se pudo conectar a la base de datos'}
            
            # Usar tabla de configuración si no se especifica
            if not table_name and self.config:
                table_name = self.config.get('postgresql', {}).get('tabla_principal', 'reportes')
            
            if not table_name:
                return {'error': 'No se especificó tabla'}
            
            cursor = self.connection.cursor()
            
            # Contar total de registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records = cursor.fetchone()[0]
            
            # Obtener fecha más reciente y más antigua (si existe campo de fecha)
            date_fields = ['created_at', 'updated_at', 'fecha', 'timestamp']
            date_info = {}
            
            for date_field in date_fields:
                try:
                    cursor.execute(f"SELECT MIN({date_field}), MAX({date_field}) FROM {table_name}")
                    min_date, max_date = cursor.fetchone()
                    if min_date and max_date:
                        date_info[date_field] = {
                            'min_date': str(min_date),
                            'max_date': str(max_date)
                        }
                        break
                except psycopg2.Error:
                    continue
            
            cursor.close()
            
            if self.logger:
                self.logger.info(f"Estadísticas de tabla {table_name}: {total_records} registros")
            
            return {
                'table_name': table_name,
                'total_records': total_records,
                'date_info': date_info
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al obtener estadísticas: {str(e)}")
            return {'error': str(e)}

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verificador de registros en base de datos')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--xref_id', help='ID específico a verificar')
    parser.add_argument('--xref_ids', nargs='+', help='Múltiples IDs a verificar')
    parser.add_argument('--table', help='Tabla específica a consultar')
    parser.add_argument('--structure', action='store_true', help='Mostrar estructura de tabla')
    parser.add_argument('--statistics', action='store_true', help='Mostrar estadísticas de tabla')
    parser.add_argument('--search', nargs='+', help='Buscar por criterios (formato: campo=valor)')
    
    args = parser.parse_args()
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        verifier = DatabaseVerifier(config_path)
        
        if args.structure:
            # Mostrar estructura de tabla
            table_name = args.table or verifier.config.get('postgresql', {}).get('tabla_principal', 'reportes')
            structure = verifier.get_table_structure(table_name)
            
            if 'error' in structure:
                print(f"❌ Error: {structure['error']}")
            else:
                print(f"✅ Estructura de tabla {table_name}:")
                print(json.dumps(structure, indent=2, ensure_ascii=False))
        
        elif args.statistics:
            # Mostrar estadísticas
            stats = verifier.get_record_statistics(args.table)
            
            if 'error' in stats:
                print(f"❌ Error: {stats['error']}")
            else:
                print(f"✅ Estadísticas:")
                print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif args.search:
            # Buscar por criterios
            criteria = {}
            for criterion in args.search:
                if '=' in criterion:
                    field, value = criterion.split('=', 1)
                    criteria[field] = value
            
            if criteria:
                results = verifier.search_records_by_criteria(criteria, args.table)
                
                if 'error' in results:
                    print(f"❌ Error: {results['error']}")
                else:
                    print(f"✅ Búsqueda completada: {results['record_count']} registros encontrados")
                    for record in results['records']:
                        print(f"  - {record}")
            else:
                print("❌ Error: Formato de criterios incorrecto (usar campo=valor)")
        
        elif args.xref_id:
            # Verificar ID específico
            result = verifier.verify_record_exists(args.xref_id, args.table)
            
            if result.get('exists', False):
                print(f"✅ Registro encontrado: {args.xref_id}")
                print(f"   Campo: {result.get('found_by_field')}")
                print(f"   Tabla: {result.get('table')}")
            else:
                print(f"❌ Registro NO encontrado: {args.xref_id}")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        elif args.xref_ids:
            # Verificar múltiples IDs
            results = verifier.verify_multiple_records(args.xref_ids, args.table)
            
            found_count = sum(1 for r in results.values() if r.get('exists', False))
            total_count = len(results)
            
            print(f"✅ Verificación completada: {found_count}/{total_count} registros encontrados")
            
            for xref_id, result in results.items():
                status = "✅" if result.get('exists', False) else "❌"
                print(f"  {status} {xref_id}")
        
        else:
            print("❌ Error: Debe especificar --xref_id, --xref_ids, --structure, --statistics o --search")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    finally:
        try:
            verifier.disconnect_database()
        except:
            pass

if __name__ == "__main__":
    exit(main())
