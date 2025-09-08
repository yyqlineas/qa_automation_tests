#!/usr/bin/env python3
"""
Database Record Copier - Script Unificado
==========================================

Script completo para copiar registros entre bases de datos SQL Server con filtro batt_dept_id
Incluye configuración SSH para STAGE10 y manejo de credenciales integrado

CARACTERÍSTICAS:
- ✅ Todo en un solo archivo Python
- ✅ Configuración hardcodeada (editar directamente en el script)
- ✅ Conexión SSH con llave pública para STAGE10
- ✅ Filtro obligatorio por batt_dept_id
- ✅ Filtros adicionales opcionales
- ✅ Confirmación antes de copiar registros
- ✅ Manejo de campos problemáticos (created_by, etc.)
- ✅ Verificación de restricciones de claves foráneas
- ✅ Transacciones seguras con rollback
- ✅ Resumen detallado de operaciones

CONFIGURACIÓN PREESTABLECIDA:
- Servidor origen: stage10_fdsu (con túnel SSH)
- SSH Host: 3.232.18.126:5422
- SSH Usuario: yatary  
- SSH Key: C:\\Users\\Yatary\\.ssh\\id_rsa.ppk
- Servidor destino: stage (conexión directa)

REQUISITOS:
- Python 3.7+
- pyodbc (obligatorio)
- sshtunnel, paramiko (opcional, para SSH)

USO:
1. Editar credenciales en la sección CONFIGURACIÓN DE BASES DE DATOS
2. Ejecutar: python database_record_copier.py
3. Seguir las instrucciones en pantalla

Autor: Sistema Automatizado
Fecha: 2025-09-05
"""

import pyodbc
import json
import sys
import os
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Intentar importar dependencias SSH (opcionales)
try:
    from sshtunnel import SSHTunnelForwarder
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False

# ==========================================
# CONFIGURACIÓN DE BASES DE DATOS
# ==========================================
# ⚠️ IMPORTANTE: Configure las credenciales antes de ejecutar

DEFAULT_CONFIG = {
    "source_database": {
        "server": "stage10_fdsu",
        "database": "PONER_AQUI_NOMBRE_BD_ORIGEN",          # 📝 Cambiar por el nombre real de la BD
        "username": "yatary",
        "password": "PONER_AQUI_PASSWORD_YATARY",            # 🔑 Cambiar por la contraseña real
        "driver": "{ODBC Driver 17 for SQL Server}",
        "ssh_tunnel": {
            "enabled": True,
            "ssh_host": "3.232.18.126",                     # 🌐 Host SSH configurado
            "ssh_port": 5422,                               # 🔌 Puerto SSH configurado
            "ssh_username": "yatary",                       # 👤 Usuario SSH configurado
            "ssh_key_file": "C:\\Users\\Yatary\\.ssh\\id_rsa.ppk",  # 🔑 Ruta de llave SSH
            "local_bind_port": 5432,
            "remote_bind_host": "172.42.10.172",
            "remote_bind_port": 5432
        }
    },
    "destination_database": {
        "server": "stage",
        "database": "PONER_AQUI_NOMBRE_BD_DESTINO",          # 📝 Cambiar por el nombre real de la BD
        "username": "PONER_AQUI_USUARIO_STAGE",              # 👤 Cambiar por el usuario real
        "password": "PONER_AQUI_PASSWORD_STAGE",             # 🔑 Cambiar por la contraseña real
        "driver": "{ODBC Driver 17 for SQL Server}",
        "ssh_tunnel": {
            "enabled": False
        }
    },
    "settings": {
        "verify_foreign_keys": True,
        "backup_before_insert": False,
        "max_batch_size": 1000
    }
}

# ==========================================
# CLASE PRINCIPAL
# ==========================================

class DatabaseCopier:
    def __init__(self):
        self.config: Dict = DEFAULT_CONFIG.copy()
        self.source_conn = None
        self.dest_conn = None
        self.ssh_tunnel = None
        
    def check_configuration(self) -> bool:
        """Verifica si las credenciales están configuradas"""
        print("🔍 VERIFICANDO CONFIGURACIÓN...")
        print("=" * 50)
        
        source_config = self.config['source_database']
        dest_config = self.config['destination_database']
        
        missing_configs = []
        
        # Verificar configuración de origen
        if source_config['database'].startswith('PONER_AQUI'):
            missing_configs.append("❌ Nombre de BD origen no configurado")
        else:
            print(f"✅ BD Origen: {source_config['database']}")
            
        if source_config['password'].startswith('PONER_AQUI'):
            missing_configs.append("❌ Password de yatary no configurado")
        else:
            print("✅ Password de origen configurado")
        
        # Verificar configuración de destino
        if dest_config['database'].startswith('PONER_AQUI'):
            missing_configs.append("❌ Nombre de BD destino no configurado")
        else:
            print(f"✅ BD Destino: {dest_config['database']}")
            
        if dest_config['username'].startswith('PONER_AQUI'):
            missing_configs.append("❌ Usuario de STAGE no configurado")
        else:
            print(f"✅ Usuario STAGE: {dest_config['username']}")
            
        if dest_config['password'].startswith('PONER_AQUI'):
            missing_configs.append("❌ Password de STAGE no configurado")
        else:
            print("✅ Password de destino configurado")
        
        # Verificar SSH key si está habilitado
        if source_config['ssh_tunnel']['enabled']:
            ssh_key_file = source_config['ssh_tunnel']['ssh_key_file']
            if os.path.exists(ssh_key_file):
                print(f"✅ SSH Key encontrada: {ssh_key_file}")
            else:
                missing_configs.append(f"❌ SSH Key no encontrada: {ssh_key_file}")
        
        if missing_configs:
            print("\n⚠️  CONFIGURACIÓN INCOMPLETA:")
            for config in missing_configs:
                print(f"   {config}")
            print("\n🔧 EDITE LAS CREDENCIALES EN EL SCRIPT ANTES DE CONTINUAR")
            print("   Busque la sección 'CONFIGURACIÓN DE BASES DE DATOS' en el archivo .py")
            return False
        else:
            print("\n✅ CONFIGURACIÓN COMPLETA - LISTO PARA CONECTAR")
            return True
    
    def count_records_preview(self, table_name: str, batt_dept_id: str, additional_filters: str = "") -> int:
        """Cuenta los registros que serían copiados antes de proceder"""
        if not self.source_conn:
            return 0
            
        try:
            cursor = self.source_conn.cursor()
            
            # Construir consulta de conteo
            count_query = f"SELECT COUNT(*) FROM {table_name} WHERE batt_dept_id = ?"
            params = [batt_dept_id]
            
            if additional_filters.strip():
                count_query += f" AND {additional_filters}"
            
            cursor.execute(count_query, params)
            count = cursor.fetchone()[0]
            
            return count
            
        except Exception as e:
            print(f"❌ Error contando registros: {e}")
            return 0
    
    def confirm_copy_operation(self, table_name: str, batt_dept_id: str, record_count: int) -> bool:
        """Solicita confirmación antes de copiar los registros"""
        print("\n" + "="*60)
        print("📋 RESUMEN DE OPERACIÓN")
        print("="*60)
        print(f"🗂️  Tabla: {table_name}")
        print(f"🏷️  Filtro batt_dept_id: {batt_dept_id}")
        print(f"📊 Registros encontrados: {record_count}")
        
        if record_count == 0:
            print("ℹ️  No hay registros para copiar con estos criterios")
            return False
        
        print(f"🎯 Origen: {self.config['source_database']['server']} -> {self.config['source_database']['database']}")
        print(f"🎯 Destino: {self.config['destination_database']['server']} -> {self.config['destination_database']['database']}")
        print("="*60)
        
        while True:
            confirm = input(f"\n¿Desea copiar estos {record_count} registros? (s/n): ").lower().strip()
            if confirm in ['s', 'si', 'sí', 'yes', 'y']:
                return True
            elif confirm in ['n', 'no']:
                print("❌ Operación cancelada por el usuario")
                return False
            else:
                print("Por favor responda 's' para sí o 'n' para no")
    
    def setup_ssh_tunnel(self) -> bool:
        """Configura el túnel SSH para la conexión a origen"""
        source_config = self.config['source_database']
        ssh_config = source_config.get('ssh_tunnel', {})
        
        if not ssh_config.get('enabled', False):
            return True
            
        if not SSH_AVAILABLE:
            print("❌ Dependencias SSH no disponibles. Instale con: pip install sshtunnel paramiko")
            return False
            
        try:
            print("🔐 Configurando túnel SSH para STAGE10...")
            
            # Verificar que el archivo de llave existe
            ssh_key_file = ssh_config.get('ssh_key_file')
            if not os.path.exists(ssh_key_file):
                print(f"❌ Archivo de llave SSH no encontrado: {ssh_key_file}")
                return False
            
            # Configurar el túnel SSH
            self.ssh_tunnel = SSHTunnelForwarder(
                (ssh_config['ssh_host'], ssh_config['ssh_port']),
                ssh_username=ssh_config['ssh_username'],
                ssh_pkey=ssh_key_file,
                remote_bind_address=(ssh_config['remote_bind_host'], ssh_config['remote_bind_port']),
                local_bind_address=('127.0.0.1', ssh_config['local_bind_port'])
            )
            
            self.ssh_tunnel.start()
            print(f"✅ Túnel SSH establecido: localhost:{ssh_config['local_bind_port']} -> {ssh_config['remote_bind_host']}:{ssh_config['remote_bind_port']}")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando túnel SSH: {e}")
            return False
    
    def connect_databases(self) -> bool:
        """Establece conexiones con ambas bases de datos"""
        try:
            source_config = self.config['source_database']
            dest_config = self.config['destination_database']
            
            # Configurar túnel SSH si es necesario
            if not self.setup_ssh_tunnel():
                return False
            
            # Conexión a origen (posiblemente a través de túnel SSH)
            if source_config.get('ssh_tunnel', {}).get('enabled', False):
                # Usar localhost con el puerto del túnel
                server = '127.0.0.1,' + str(source_config['ssh_tunnel']['local_bind_port'])
            else:
                server = source_config['server']
                
            source_conn_str = (
                f"DRIVER={source_config['driver']};"
                f"SERVER={server};"
                f"DATABASE={source_config['database']};"
                f"UID={source_config['username']};"
                f"PWD={source_config['password']}"
            )
            self.source_conn = pyodbc.connect(source_conn_str)
            print(f"✓ Conectado a origen: {source_config['server']}")
            
            # Conexión a destino
            dest_conn_str = (
                f"DRIVER={dest_config['driver']};"
                f"SERVER={dest_config['server']};"
                f"DATABASE={dest_config['database']};"
                f"UID={dest_config['username']};"
                f"PWD={dest_config['password']}"
            )
            self.dest_conn = pyodbc.connect(dest_conn_str)
            print(f"✓ Conectado a destino: {dest_config['server']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error conectando a las bases de datos: {e}")
            return False
    
    def get_table_structure(self, table_name: str, connection) -> List[Tuple]:
        """Obtiene la estructura de una tabla"""
        cursor = connection.cursor()
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, table_name)
        return cursor.fetchall()
    
    def verify_table_exists(self, table_name: str, connection) -> bool:
        """Verifica si una tabla existe en la base de datos"""
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = ?
        """, table_name)
        return cursor.fetchone()[0] > 0
    
    def build_query_with_filters(self, table_name: str, batt_dept_id: str) -> Tuple[str, List[str]]:
        """Construye la consulta con filtros adicionales"""
        base_query = f"SELECT * FROM {table_name} WHERE batt_dept_id = ?"
        params = [batt_dept_id]
        
        print(f"\nConsulta base: {base_query.replace('?', str(batt_dept_id))}")
        
        while True:
            add_filter = input("\n¿Desea agregar otra cláusula WHERE? (s/n): ").lower().strip()
            if add_filter in ['n', 'no']:
                break
            elif add_filter in ['s', 'si', 'sí', 'yes', 'y']:
                additional_clause = input("Ingrese la cláusula adicional (ej: 'created_date > 2024-01-01'): ")
                base_query += f" AND {additional_clause}"
                print(f"Consulta actualizada: {base_query.replace('?', str(batt_dept_id))}")
            else:
                print("Por favor responda 's' para sí o 'n' para no")
        
        return base_query, params
    
    def get_source_records(self, query: str, params: List[str]) -> Tuple[List[Dict], List[str]]:
        """Obtiene los registros de la base de datos origen"""
        if not self.source_conn:
            raise Exception("Conexión a origen no establecida")
            
        cursor = self.source_conn.cursor()
        cursor.execute(query, params)
        
        # Obtener nombres de columnas
        columns = [column[0] for column in cursor.description]
        
        # Obtener datos y convertir a diccionarios
        records = []
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            records.append(record)
        
        return records, columns
    
    def check_foreign_key_constraints(self, records: List[Dict], table_name: str) -> Dict[str, List]:
        """Verifica restricciones de claves foráneas y valores que no existen"""
        problematic_fields = {}
        
        # Lista de campos comunes que suelen tener restricciones
        check_fields = ['created_by', 'updated_by', 'user_id', 'modified_by']
        
        for field in check_fields:
            if field in records[0] if records else {}:
                # Obtener valores únicos del campo
                unique_values = list(set(record.get(field) for record in records if record.get(field) is not None))
                
                if unique_values:
                    # Verificar cuáles valores no existen en destino
                    problematic_values = []
                    if not self.dest_conn:
                        continue
                        
                    cursor = self.dest_conn.cursor()
                    
                    # Asumir que estos campos referencian una tabla 'users' o similar
                    try:
                        # Intentar verificar en tabla users
                        placeholders = ','.join(['?' for _ in unique_values])
                        cursor.execute(f"SELECT id FROM users WHERE id IN ({placeholders})", unique_values)
                        existing_values = [row[0] for row in cursor.fetchall()]
                        
                        problematic_values = [val for val in unique_values if val not in existing_values]
                        
                        if problematic_values:
                            problematic_fields[field] = problematic_values
                            
                    except Exception as e:
                        # Si no se puede verificar, asumir que hay problemas
                        print(f"⚠️  No se pudo verificar el campo {field}: {e}")
                        continue
        
        return problematic_fields
    
    def handle_problematic_fields(self, records: List[Dict], problematic_fields: Dict[str, List]) -> List[Dict]:
        """Maneja los campos problemáticos preguntando al usuario"""
        if not problematic_fields:
            return records
        
        print("\n=== CAMPOS CON VALORES PROBLEMÁTICOS ===")
        field_replacements = {}
        
        for field, problematic_values in problematic_fields.items():
            print(f"\nCampo '{field}' tiene valores que no existen en la BD de destino:")
            print(f"Valores problemáticos: {problematic_values}")
            
            replace = input(f"¿Desea cambiar todos los valores del campo '{field}'? (s/n): ").lower().strip()
            
            if replace in ['s', 'si', 'sí', 'yes', 'y']:
                new_value = input(f"Ingrese el nuevo valor para el campo '{field}': ")
                field_replacements[field] = new_value
        
        # Aplicar reemplazos
        updated_records = []
        for record in records:
            updated_record = record.copy()
            for field, new_value in field_replacements.items():
                if field in updated_record:
                    updated_record[field] = new_value
            updated_records.append(updated_record)
        
        return updated_records
    
    def insert_records(self, records: List[Dict], table_name: str, columns: List[str]) -> int:
        """Inserta los registros en la base de datos destino"""
        if not records:
            return 0
        
        if not self.dest_conn:
            print("❌ Conexión a destino no establecida")
            return 0
            
        cursor = self.dest_conn.cursor()
        inserted_count = 0
        
        # Preparar la consulta de inserción
        placeholders = ','.join(['?' for _ in columns])
        insert_query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        try:
            for record in records:
                values = [record.get(col) for col in columns]
                cursor.execute(insert_query, values)
                inserted_count += 1
            
            self.dest_conn.commit()
            print(f"✓ {inserted_count} registros insertados exitosamente")
            
        except Exception as e:
            self.dest_conn.rollback()
            print(f"❌ Error insertando registros: {e}")
            return 0
        
        return inserted_count
    
    def copy_table_records(self):
        """Proceso principal para copiar registros"""
        print("\n=== COPIA DE REGISTROS ENTRE BASES DE DATOS ===")
        
        # Solicitar información básica
        table_name = input("\nIngrese el nombre de la tabla: ").strip()
        
        if not table_name:
            print("❌ El nombre de la tabla es obligatorio")
            return
        
        # Verificar que la tabla existe en ambas bases
        if not self.verify_table_exists(table_name, self.source_conn):
            print(f"❌ La tabla '{table_name}' no existe en la base de datos origen")
            return
        
        if not self.verify_table_exists(table_name, self.dest_conn):
            print(f"❌ La tabla '{table_name}' no existe en la base de datos destino")
            return
        
        print(f"✓ Tabla '{table_name}' encontrada en ambas bases de datos")
        
        # Solicitar batt_dept_id (obligatorio)
        batt_dept_id = input("\nIngrese el batt_dept_id (OBLIGATORIO): ").strip()
        
        if not batt_dept_id:
            print("❌ El batt_dept_id es obligatorio para la copia")
            return
        
        # Construir consulta con filtros adicionales
        query, params = self.build_query_with_filters(table_name, batt_dept_id)
        
        # Contar registros antes de proceder
        additional_filters = query.split(" AND ", 1)[1] if " AND " in query else ""
        record_count = self.count_records_preview(table_name, batt_dept_id, additional_filters)
        
        # Solicitar confirmación
        if not self.confirm_copy_operation(table_name, batt_dept_id, record_count):
            return
        
        # Obtener registros origen
        print(f"\n🔍 Obteniendo registros de {self.config['source_database']['server']}...")
        try:
            records, columns = self.get_source_records(query, params)
            print(f"✓ {len(records)} registros obtenidos de origen")
            
            if not records:
                print("ℹ️  No hay registros para copiar")
                return
            
        except Exception as e:
            print(f"❌ Error obteniendo registros origen: {e}")
            return
        
        # Verificar restricciones de claves foráneas
        print("\n🔍 Verificando restricciones de claves foráneas...")
        problematic_fields = self.check_foreign_key_constraints(records, table_name)
        
        # Manejar campos problemáticos
        updated_records = self.handle_problematic_fields(records, problematic_fields)
        
        # Insertar registros
        print(f"\n📥 Insertando registros en {self.config['destination_database']['server']}...")
        inserted_count = self.insert_records(updated_records, table_name, columns)
        
        # Resumen final
        print("\n" + "="*50)
        print("RESUMEN DE LA OPERACIÓN")
        print("="*50)
        print(f"Tabla procesada: {table_name}")
        print(f"Filtro batt_dept_id: {batt_dept_id}")
        print(f"Registros encontrados en origen: {len(records)}")
        print(f"Registros insertados en destino: {inserted_count}")
        print(f"Servidor origen: {self.config['source_database']['server']}")
        print(f"Servidor destino: {self.config['destination_database']['server']}")
        
        if problematic_fields:
            print(f"Campos modificados: {list(problematic_fields.keys())}")
        
        print("="*50)
    
    def close_connections(self):
        """Cierra las conexiones a las bases de datos y túnel SSH"""
        if self.source_conn:
            self.source_conn.close()
        if self.dest_conn:
            self.dest_conn.close()
        if self.ssh_tunnel:
            self.ssh_tunnel.stop()
            print("🔒 Túnel SSH cerrado")
    
    def run(self):
        """Ejecuta el proceso completo"""
        try:
            # Verificar configuración
            if not self.check_configuration():
                print("\n❌ Configure las credenciales antes de continuar.")
                return
            
            if not self.connect_databases():
                return
            
            self.copy_table_records()
            
        except KeyboardInterrupt:
            print("\n⚠️  Operación cancelada por el usuario")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
        finally:
            self.close_connections()
            print("\n🔒 Conexiones cerradas")

def main():
    """Función principal"""
    print("🚀 DATABASE RECORD COPIER - SCRIPT UNIFICADO")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar dependencias críticas
    try:
        import pyodbc
        print("✅ pyodbc disponible")
    except ImportError:
        print("❌ pyodbc no disponible. Instale con: pip install pyodbc")
        input("Presione Enter para continuar...")
        return
    
    if not SSH_AVAILABLE:
        print("⚠️  Dependencias SSH no disponibles (sshtunnel, paramiko)")
        print("   Para conexiones SSH instale: pip install sshtunnel paramiko")
        print("   El script puede funcionar sin SSH si no usa túneles")
    
    print()
    
    copier = DatabaseCopier()
    copier.run()
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
