import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
from lxml import etree
import psycopg2
import logging
from datetime import datetime
import os
import json

class XPathMapper:
    def __init__(self, config_file=None, mapping_file=None):
        self.config_file = config_file
        self.mapping_file = mapping_file
        self.mapping_data = None
        self.conn = None
        self.cursor = None
        self.config = None
        self.logger = self._setup_logger()
        
        # Cargar configuración primero
        if config_file:
            self._load_config()
        
        # Si se proporciona archivo de mapeo, cargarlo después de la configuración
        if mapping_file:
            self.mapping_file = mapping_file
            self.load_mapping_file()

    def _setup_logger(self):
        # Configurar el logger
        logger = logging.getLogger('XPathMapper')
        logger.setLevel(logging.INFO)
        
        # Crear el directorio de logs si no existe
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Crear el archivo de log con la fecha actual
        log_file = os.path.join(logs_dir, f'comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file)
        
        # Configurar el formato del log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)
        
        return logger

    def _process_xpath(self, xpath_raw):
        """Procesar rutas XPath desde diferentes formatos."""
        if pd.isna(xpath_raw) or not xpath_raw:
            return None
            
        xpath_str = str(xpath_raw).strip()
        
        # Si contiene "CAD Field" o similar, no es un XPath válido - skip
        if any(term in xpath_str for term in ['CAD Field', 'Field Notes', 'Unnamed:']):
            return None
        
        # Si ya es una ruta XPath válida (comienza con // o /)
        if xpath_str.startswith('//') or xpath_str.startswith('/'):
            return xpath_str
        
        # Si contiene el operador de concatenación "+", procesarlo por partes
        if '+' in xpath_str:
            # Dividir por "+" y procesar cada parte individualmente
            parts = [part.strip() for part in xpath_str.split('+')]
            processed_parts = []
            
            for part in parts:
                # Procesar cada parte individualmente
                if '<' in part and '>' in part:
                    # Extraer los nombres de los elementos
                    import re
                    elements = re.findall(r'<([^>]+)>', part)
                    if elements:
                        # Construir la ruta XPath para esta parte
                        part_xpath = '//' + '/'.join(elements)
                        processed_parts.append(part_xpath)
                elif part.startswith('//') or part.startswith('/'):
                    processed_parts.append(part)
                elif part and not any(char in part for char in ['/', '<', '>', 'Field']):
                    processed_parts.append(f'//{part}')
            
            # Unir las partes con " + " para mantener el formato de concatenación
            if processed_parts:
                return ' + '.join(processed_parts)
        
        # Si está en formato de elementos XML: <Incident> <IncidentNumber>
        if '<' in xpath_str and '>' in xpath_str:
            # Extraer los nombres de los elementos
            import re
            elements = re.findall(r'<([^>]+)>', xpath_str)
            if elements:
                # Construir la ruta XPath
                xpath = '//' + '/'.join(elements)
                return xpath
        
        # Si es un nombre simple, asumir que es un elemento raíz
        if xpath_str and not any(char in xpath_str for char in ['/', '<', '>', 'Field']):
            return f'//{xpath_str}'
        
        return None

    def _load_config(self):
        """Cargar la configuración desde el archivo JSON."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"Configuración cargada exitosamente: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error al cargar la configuración: {str(e)}")
            return False

    def _normalize_field_name(self, field_name):
        """Normalizar nombres de campos reemplazando espacios con guiones bajos y corrigiendo nombres."""
        if not field_name:
            return field_name
        
        # Mapeo de corrección de nombres de campos
        field_corrections = {
            # Campos que no existen en dispatch pero sí en nfirs_notification
            'street_number': 'house_num',  # dispatch no lo tiene, nfirs sí
            'street_prefix': 'prefix_direction',  # dispatch no lo tiene, nfirs sí  
            'street_suffix': 'suffix_direction',  # dispatch no lo tiene, nfirs sí
        }
        
        normalized = str(field_name).strip().replace(' ', '_')
        
        # Aplicar correcciones específicas si existen
        if normalized in field_corrections:
            return field_corrections[normalized]
            
        return normalized
    
    def load_mapping_file(self):
        """Cargar el archivo de mapeo Excel."""
        try:
            if not self.mapping_file:
                raise Exception("No se ha especificado el archivo de mapeo")
                
            # Leer el archivo Excel
            self.mapping_data = pd.read_excel(self.mapping_file)
            
            self.logger.info(f"Columnas encontradas en el Excel: {list(self.mapping_data.columns)}")
            
            # Definir columnas específicas basándose en la estructura real del Excel
            xpath_col = 'Data Source Mappings'
            
            # Columnas para CAD Dispatch (columnas 5 y 6)
            dispatch_table_col = 'CAD Dispatch '  # Columna 5: nombres de tabla
            dispatch_field_col = 'Unnamed: 6'    # Columna 6: nombres de campo
            
            # Columnas para CAD Incident (columnas 7 y 8)
            incident_table_col = 'CAD Incident'   # Columna 7: nombres de tabla
            incident_field_col = 'Unnamed: 8'    # Columna 8: nombres de campo
            
            self.logger.info(f"Usando columnas definidas - XPath: {xpath_col}")
            self.logger.info(f"Dispatch - Tabla: {dispatch_table_col} (col 5), Campo: {dispatch_field_col} (col 6)")
            self.logger.info(f"Incident - Tabla: {incident_table_col} (col 7), Campo: {incident_field_col} (col 8)")
            
            # Crear mapeos válidos leyendo directamente del Excel
            valid_mappings = []
            
            for idx, row in self.mapping_data.iterrows():
                # Saltar fila de headers (fila 0)
                if idx == 0:
                    continue
                    
                # Obtener ruta XPath
                xpath_raw = row.get(xpath_col, '') if xpath_col in self.mapping_data.columns else ''
                if pd.isna(xpath_raw) or not str(xpath_raw).strip():
                    continue
                
                # Procesar XPath
                xpath = self._process_xpath(xpath_raw)
                if not xpath:
                    continue
                
                # Procesar AMBAS columnas (CAD Dispatch y CAD Incident) por separado
                mappings_found = []
                
                # 1. Verificar CAD Dispatch (columnas 5 y 6)
                if dispatch_table_col in self.mapping_data.columns and dispatch_field_col in self.mapping_data.columns:
                    dispatch_table_val = row.get(dispatch_table_col, '')
                    dispatch_field_val = row.get(dispatch_field_col, '')
                    
                    if (not pd.isna(dispatch_table_val) and str(dispatch_table_val).strip() and 
                        str(dispatch_table_val).strip() not in ['CAD Table'] and
                        not pd.isna(dispatch_field_val) and str(dispatch_field_val).strip() and
                        str(dispatch_field_val).strip() not in ['CAD Column']):
                        
                        table_name = str(dispatch_table_val).strip()
                        field_original = str(dispatch_field_val).strip()
                        field_normalized = self._normalize_field_name(field_original)
                        
                        mappings_found.append({
                            'table_name': table_name,
                            'field_original': field_original,
                            'field_normalized': field_normalized,
                            'source': 'CAD_Dispatch'
                        })
                
                # 2. Verificar CAD Incident (columnas 7 y 8)
                if incident_table_col in self.mapping_data.columns and incident_field_col in self.mapping_data.columns:
                    incident_table_val = row.get(incident_table_col, '')
                    incident_field_val = row.get(incident_field_col, '')
                    
                    if (not pd.isna(incident_table_val) and str(incident_table_val).strip() and 
                        str(incident_table_val).strip() not in ['CAD Table'] and
                        not pd.isna(incident_field_val) and str(incident_field_val).strip() and
                        str(incident_field_val).strip() not in ['CAD Column']):
                        
                        table_name = str(incident_table_val).strip()
                        field_original = str(incident_field_val).strip()
                        field_normalized = self._normalize_field_name(field_original)
                        
                        mappings_found.append({
                            'table_name': table_name,
                            'field_original': field_original,
                            'field_normalized': field_normalized,
                            'source': 'CAD_Incident'
                        })
                
                # 3. Crear mapeos válidos para cada tabla/campo encontrado
                for mapping_info in mappings_found:
                    # Crear query SQL con filtros específicos
                    query = self._build_filtered_query(mapping_info['table_name'], mapping_info['field_normalized'])
                    
                    valid_mappings.append({
                        'xpath': xpath,
                        'query': query,
                        'xpath_raw': xpath_raw,
                        'table_name': mapping_info['table_name'],
                        'column_name': mapping_info['field_normalized'],
                        'column_original': mapping_info['field_original'],
                        'source': mapping_info['source'],
                        'row_index': idx
                    })
            
            if not valid_mappings:
                self.logger.warning("No se encontraron mapeos válidos. Usando mapeo de ejemplo.")
                # Crear un mapeo de ejemplo para probar
                valid_mappings = [{
                    'xpath': '//Incident/IncidentNumber',
                    'query': self._build_filtered_query('nfirs_notification', 'incident_number'),
                    'xpath_raw': '<Incident> <IncidentNumber>',
                    'table_name': 'nfirs_notification',
                    'column_name': 'incident_number',
                    'column_original': 'incident_number',
                    'source': 'Example'
                }]
            
            # Guardar los mapeos válidos tanto como lista como DataFrame
            self.valid_mappings = valid_mappings
            self.mapping_data = pd.DataFrame(valid_mappings)
            
            self.logger.info(f"Archivo de mapeo cargado exitosamente: {self.mapping_file}")
            self.logger.info(f"Número de mapeos válidos cargados: {len(valid_mappings)}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error al cargar el archivo de mapeo: {str(e)}")
            return False

    def _build_filtered_query(self, table_name, column_name):
        """Construir query SQL con filtros específicos para cada tabla."""
        try:
            # Normalizar nombres de columnas reemplazando espacios con guiones bajos
            normalized_column = column_name.replace(' ', '_') if column_name else column_name
            
            # Construir la query base con alias para evitar ambigüedades
            table_alias = table_name[0]  # Usar primera letra como alias (d para dispatch, n para nfirs_notification)
            query = f"SELECT {table_alias}.{normalized_column} FROM {table_name} {table_alias} WHERE 1=1"
            
            # Aplicar filtros específicos según la tabla
            if table_name.lower() == 'dispatch':
                # Para tabla dispatch: filtrar por batt_dept_id y created_at
                query += f" AND {table_alias}.batt_dept_id IN (3453)"
                query += f" AND {table_alias}.created_at >= '2025-08-18 17:00:00'"
                
            elif table_name.lower() == 'nfirs_notification':
                # Para tabla nfirs_notification: filtrar por batt_dept_id y created_at
                query += f" AND {table_alias}.batt_dept_id IN (3453)"
                query += f" AND {table_alias}.created_at >= '2025-08-18 17:00:00'"
                
            elif table_name.lower() == 'nfirs_notification_apparatus':
                # Para nfirs_notification_apparatus: necesita JOIN con nfirs_notification
                query = f"""SELECT nna.{normalized_column} 
                           FROM nfirs_notification_apparatus nna
                           INNER JOIN nfirs_notification nn ON nna.nfirs_notification_id = nn.id
                           WHERE nn.batt_dept_id IN (3453)
                           AND nn.created_at >= '2025-08-18 17:00:00'
                           ORDER BY nn.id DESC LIMIT 1"""
                           
            elif table_name.lower() == 'nfirs_notification_personnel':
                # Para nfirs_notification_personnel: necesita JOIN con nfirs_notification
                query = f"""SELECT nnp.{normalized_column} 
                           FROM nfirs_notification_personnel nnp
                           INNER JOIN nfirs_notification nn ON nnp.nfirs_notification_id = nn.id
                           WHERE nn.batt_dept_id IN (3453)
                           AND nn.created_at >= '2025-08-18 17:00:00'
                           ORDER BY nn.id DESC LIMIT 1"""
                           
            else:
                # Para otras tablas, usar filtros generales
                self.logger.warning(f"Tabla desconocida: {table_name}, usando filtros generales")
                query += f" AND {table_alias}.batt_dept_id IN (3453)"
                query += f" AND {table_alias}.created_at >= '2025-08-18 17:00:00'"
            
            # Limitar resultados para pruebas (solo si no es una query de JOIN que ya tiene ORDER BY)
            if not ('JOIN' in query and 'ORDER BY' in query):
                query += f" ORDER BY {table_alias}.id DESC LIMIT 1"
            
            self.logger.info(f"Query generada para {table_name}.{column_name}: {query}")
            return query
            
        except Exception as e:
            self.logger.error(f"Error construyendo query filtrada: {str(e)}")
            # Query simple sin filtros como fallback
            escaped_column = f'"{column_name}"' if ' ' in column_name else column_name
            return f"SELECT {escaped_column} FROM {table_name} LIMIT 1"

    def connect_to_db(self):
        """Conectar a la base de datos PostgreSQL usando la configuración cargada."""
        try:
            if not hasattr(self, 'config'):
                raise Exception("No se ha cargado la configuración de la base de datos")
                
            db_params = self.config.get('database', {})
            if not db_params:
                raise Exception("No se encontró la configuración de la base de datos")
                
            self.conn = psycopg2.connect(**db_params)
            self.cursor = self.conn.cursor()
            self.logger.info("Conexión a la base de datos establecida exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al conectar a la base de datos: {str(e)}")
            return False

    def close_db_connection(self):
        """Cerrar la conexión a la base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.logger.info("Conexión a la base de datos cerrada")

    def compare_xml_with_db(self, xml_folder_path):
        """Comparar archivos XML con la base de datos."""
        if self.mapping_data is None or self.conn is None:
            self.logger.error("Debe cargar el archivo de mapeo y conectarse a la BD primero")
            return None

        results = []
        
        # Crear directorio de reportes si no existe
        report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reportes')
        os.makedirs(report_dir, exist_ok=True)

        try:
            # Obtener lista de archivos XML
            xml_files = [f for f in os.listdir(xml_folder_path) if f.endswith('.xml')]
            
            if not xml_files:
                self.logger.warning(f"No se encontraron archivos XML en: {xml_folder_path}")
                return None
            
            self.logger.info(f"Se encontraron {len(xml_files)} archivos XML para procesar")

            # Procesar cada archivo XML en la carpeta
            for xml_file in xml_files:
                xml_path = os.path.join(xml_folder_path, xml_file)
                self.logger.info(f"Procesando archivo: {xml_file}")

                try:
                    # Parsear el archivo XML
                    tree = etree.parse(xml_path)
                    root = tree.getroot()

                    # Procesar cada mapeo válido generado
                    for row in self.valid_mappings:
                        xpath = row['xpath']
                        query = row['query']
                        
                        if not xpath or not query:
                            self.logger.warning(f"Mapeo incompleto: xpath='{xpath}', query='{query}'")
                            continue
                        
                        # Obtener valor del XML con soporte para XPath concatenados
                        xml_value = None
                        try:
                            # Verificar si el XPath contiene múltiples rutas separadas por "+"
                            if '+' in xpath:
                                xpath_parts = [part.strip() for part in xpath.split('+')]
                                xml_values = []
                                
                                for xpath_part in xpath_parts:
                                    try:
                                        elements = root.xpath(xpath_part)
                                        if elements:
                                            element = elements[0]
                                            # Manejar diferentes tipos de elementos
                                            if hasattr(element, 'text') and element.text:
                                                part_value = element.text.strip()
                                            elif hasattr(element, 'tag'):
                                                # Si es un elemento, obtener todo el texto interno
                                                part_value = ''.join(element.itertext()).strip()
                                            else:
                                                # Si es un atributo o valor directo
                                                part_value = str(element).strip()
                                            
                                            if part_value:  # Solo agregar si no está vacío
                                                xml_values.append(part_value)
                                    except Exception as e:
                                        self.logger.debug(f"Error en parte del XPath '{xpath_part}': {str(e)}")
                                        continue
                                
                                # Concatenar los valores encontrados
                                if xml_values:
                                    xml_value = " + ".join(xml_values)
                                    self.logger.debug(f"XPath concatenado '{xpath}' resultó en: '{xml_value}'")
                                else:
                                    xml_value = None
                                    
                            else:
                                # XPath simple (sin concatenación)
                                elements = root.xpath(xpath)
                                if elements:
                                    element = elements[0]
                                    # Manejar diferentes tipos de elementos
                                    if hasattr(element, 'text') and element.text:
                                        xml_value = element.text.strip()
                                    elif hasattr(element, 'tag'):
                                        # Si es un elemento, obtener todo el texto interno
                                        xml_value = ''.join(element.itertext()).strip()
                                    else:
                                        # Si es un atributo o valor directo
                                        xml_value = str(element).strip()
                                else:
                                    xml_value = None
                                    self.logger.debug(f"No se encontró elemento para XPath '{xpath}' en {xml_file}")
                        except Exception as e:
                            self.logger.error(f"Error al procesar XPath '{xpath}' en {xml_file}: {str(e)}")
                            xml_value = "ERROR_XPATH"

                        # Obtener valor de la BD con lógica mejorada
                        db_value = None
                        try:
                            # Normalizar nombre de campo
                            normalized_campo = self._normalize_field_name(row['column_name'])
                            
                            # Determinar la tabla y join apropiados
                            tabla_base = row['table_name'].lower()
                            
                            if tabla_base == "dispatch":
                                query = f"""
                                    SELECT {normalized_campo}
                                    FROM dispatch
                                    WHERE batt_dept_id = 3453
                                    AND created_at >= '2025-08-18 17:00:00'
                                    LIMIT 1
                                """
                            elif tabla_base == "nfirs_notification":
                                query = f"""
                                    SELECT {normalized_campo}
                                    FROM nfirs_notification
                                    WHERE batt_dept_id = 3453
                                    AND created_at >= '2025-08-18 17:00:00'
                                    LIMIT 1
                                """
                            elif tabla_base == "nfirs_notification_apparatus":
                                query = f"""
                                    SELECT nna.{normalized_campo}
                                    FROM nfirs_notification_apparatus nna
                                    INNER JOIN nfirs_notification nn ON nna.nfirs_notification_id = nn.id
                                    WHERE nn.batt_dept_id = 3453
                                    AND nn.created_at >= '2025-08-18 17:00:00'
                                    LIMIT 1
                                """
                            elif tabla_base == "nfirs_notification_personnel":
                                query = f"""
                                    SELECT nnp.{normalized_campo}
                                    FROM nfirs_notification_personnel nnp
                                    INNER JOIN nfirs_notification nn ON nnp.nfirs_notification_id = nn.id
                                    WHERE nn.batt_dept_id = 3453
                                    AND nn.created_at >= '2025-08-18 17:00:00'
                                    LIMIT 1
                                """
                            elif tabla_base == "batt_dept":
                                query = f"""
                                    SELECT {normalized_campo}
                                    FROM batt_dept
                                    WHERE id = 3453
                                    LIMIT 1
                                """
                            else:
                                # Para otras tablas usar estructura básica
                                query = f"""
                                    SELECT {normalized_campo}
                                    FROM {tabla_base}
                                    WHERE batt_dept_id = 3453
                                    LIMIT 1
                                """
                            
                            self.logger.debug(f"Ejecutando query mejorada: {query}")
                            # Usar autocommit para evitar problemas de transacción
                            self.conn.autocommit = True
                            
                            # Crear nueva conexión para cada query si hay error anterior
                            try:
                                self.cursor.execute(query)
                                result = self.cursor.fetchone()
                                if result and result[0] is not None:
                                    db_value = str(result[0]).strip()
                                else:
                                    db_value = None
                                    self.logger.debug(f"Query no retornó resultados: {query}")
                            except psycopg2.Error as db_error:
                                # Error específico de BD - reconectar para siguiente query
                                error_msg = str(db_error)
                                self.logger.error(f"Error SQL para {tabla_base}.{normalized_campo}: {error_msg}")
                                
                                if "does not exist" in error_msg or "column" in error_msg.lower():
                                    db_value = "CAMPO_NO_EXISTE"
                                else:
                                    db_value = "ERROR_QUERY"
                                
                                try:
                                    # Cerrar cursor actual
                                    self.cursor.close()
                                    # Crear nuevo cursor
                                    self.cursor = self.conn.cursor()
                                    self.cursor.execute("SELECT 1")  # Test query
                                except:
                                    # Reconectar completamente si es necesario
                                    self._connect_to_database()
                                
                        except Exception as e:
                            self.logger.error(f"Error general al ejecutar query para {row['table_name']}.{row['column_name']}: {str(e)}")
                            db_value = "ERROR_QUERY"

                        # Comparar valores (convertir a string para comparación)
                        xml_str = str(xml_value) if xml_value is not None else ""
                        db_str = str(db_value) if db_value is not None else ""
                        
                        # Comparación exacta (case-sensitive)
                        match = (xml_str == db_str) and xml_str != "" and db_str != ""
                        
                        # Log detallado para debugging
                        self.logger.debug(f"Comparación - XPath: {xpath}, XML: '{xml_str}', DB: '{db_str}', Match: {match}")
                        
                        results.append({
                            'archivo': xml_file,
                            'tabla': row['table_name'],
                            'campo': row.get('column_original', row['column_name']), 
                            'xpath': xpath,
                            'valor_xml': xml_value,
                            'valor_bd': db_value,
                            'coincide': match,
                            'observaciones': self._get_comparison_notes(xml_value, db_value)
                        })

                except Exception as e:
                    self.logger.error(f"Error al procesar el archivo {xml_file}: {str(e)}")
                    # Agregar entrada de error para este archivo
                    results.append({
                        'archivo': xml_file,
                        'tabla': 'ERROR',
                        'campo': 'ERROR',
                        'xpath': 'ERROR',
                        'valor_xml': f"Error al procesar archivo: {str(e)}",
                        'valor_bd': None,
                        'coincide': False,
                        'observaciones': 'Error de procesamiento'
                    })

            # Crear reporte Excel
            if results:
                report_path = os.path.join(report_dir, f'reporte_comparacion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
                df = pd.DataFrame(results)
                
                # Crear resumen
                total_comparaciones = len(results)
                coincidencias = len([r for r in results if r['coincide']])
                errores = len([r for r in results if 'ERROR' in str(r['valor_xml']) or 'ERROR' in str(r['valor_bd'])])
                
                with pd.ExcelWriter(report_path) as writer:
                    # Hoja principal con los resultados
                    df.to_excel(writer, sheet_name='Resultados', index=False)
                    
                    # Hoja de resumen
                    resumen = pd.DataFrame({
                        'Métrica': ['Total de comparaciones', 'Coincidencias', 'Diferencias', 'Errores', 'Porcentaje de coincidencias'],
                        'Valor': [total_comparaciones, coincidencias, total_comparaciones - coincidencias - errores, errores, f"{(coincidencias/total_comparaciones*100):.2f}%" if total_comparaciones > 0 else "0%"]
                    })
                    resumen.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Aplicar formato de colores
                self._apply_color_formatting(report_path, df)
                
                self.logger.info(f"Reporte generado: {report_path}")
                self.logger.info(f"Resumen: {coincidencias}/{total_comparaciones} coincidencias ({(coincidencias/total_comparaciones*100):.2f}%)")
                return report_path
            else:
                self.logger.warning("No se generó ningún resultado para el reporte")
                return None

        except Exception as e:
            self.logger.error(f"Error durante la comparación: {str(e)}")
            return None

    def _get_comparison_notes(self, xml_value, db_value):
        """Generar notas sobre la comparación."""
        # Verificar si hay errores
        if "ERROR" in str(xml_value):
            return "Error al obtener valor XML"
        elif "ERROR" in str(db_value) or "CAMPO_NO_EXISTE" in str(db_value):
            return "Error al obtener valor BD"
        
        # Verificar valores nulos
        xml_is_null = xml_value is None or str(xml_value).strip() == ""
        db_is_null = db_value is None or str(db_value).strip() == ""
        
        if xml_is_null and db_is_null:
            return "Ambos valores son nulos"
        elif xml_is_null:
            return "Valor XML es nulo"
        elif db_is_null:
            return "Valor BD es nulo"
        
        # Comparar valores no nulos
        xml_str = str(xml_value).strip()
        db_str = str(db_value).strip()
        
        if xml_str == db_str:
            return "Valores coinciden"
        else:
            return f"Valores diferentes: XML='{xml_str}' vs BD='{db_str}'"

    def _apply_color_formatting(self, report_path, df):
        """Aplicar formato de colores al reporte Excel."""
        try:
            # Cargar el archivo Excel generado
            workbook = openpyxl.load_workbook(report_path)
            worksheet = workbook['Resultados']
            
            # Definir colores
            green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Verde claro
            red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")    # Rojo claro
            yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # Amarillo claro
            blue_fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")   # Azul claro
            
            # Buscar la columna de "observaciones"
            observaciones_col = None
            for col_idx, cell in enumerate(worksheet[1], 1):  # Primera fila (encabezados)
                if cell.value and 'observacion' in str(cell.value).lower():
                    observaciones_col = col_idx
                    break
            
            if not observaciones_col:
                self.logger.warning("No se encontró la columna 'observaciones' para aplicar colores")
                return
            
            # Aplicar colores según el contenido de observaciones
            for row_idx in range(2, len(df) + 2):  # Empezar desde la fila 2 (datos, no encabezados)
                cell = worksheet.cell(row=row_idx, column=observaciones_col)
                if cell.value:
                    observacion = str(cell.value).lower()
                    
                    if "coinciden" in observacion:
                        # Verde para coincidencias - solo la celda de observaciones
                        cell.fill = green_fill
                    elif "error" in observacion:
                        # Amarillo para errores - solo la celda de observaciones
                        cell.fill = yellow_fill
                    elif "diferentes" in observacion:
                        # Rojo para diferencias - solo la celda de observaciones
                        cell.fill = red_fill
                    elif "nulo" in observacion or "nulos" in observacion:
                        # Azul para valores nulos - solo la celda de observaciones
                        cell.fill = blue_fill
            
            # Guardar cambios
            workbook.save(report_path)
            self.logger.info("Formato de colores aplicado al reporte Excel")
            
        except Exception as e:
            self.logger.error(f"Error aplicando formato de colores: {str(e)}")
            # El reporte se genera sin colores si hay error
