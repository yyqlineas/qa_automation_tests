#!/usr/bin/env python3
"""
Verificador de correspondencia entre batt_dept_id y client_code
Autor: Automatización FDSU
Fecha: 2025-09-05

Este script permite:
1. Verificar si un batt_dept_id corresponde al client_code correcto
2. Mostrar discrepancias encontradas
3. Corregir automáticamente los IDs incorrectos
4. Reasignar IDs libres cuando sea necesario
"""

import psycopg2
import sys
from datetime import datetime
import re

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
DB_CONFIG = {
    'host': 'calliope.localitymedia.com',
    'port': 5432,
    'database': 'stage_fdsu',
    'user': 'yatary',
    'password': 'QuagvipFatuctEsFielkunIpbijik<'
}

class BattDeptVerificador:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def conectar_bd(self):
        """Establece conexión con la base de datos"""
        try:
            if self.connection:
                self.connection.close()
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            print("✓ Conexión establecida con la base de datos")
            return True
        except Exception as e:
            print(f"✗ Error al conectar con la base de datos: {e}")
            return False
    
    def desconectar_bd(self):
        """Cierra la conexión con la base de datos"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("✓ Conexión cerrada")
        except:
            pass
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecuta una consulta de manera segura"""
        try:
            if not self.connection or self.connection.closed:
                if not self.conectar_bd():
                    return None
            
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"✗ Error en consulta: {e}")
            # Reconectar y reintentar una vez
            try:
                if self.conectar_bd():
                    self.cursor.execute(query, params or ())
                    return self.cursor.fetchall()
            except Exception as e2:
                print(f"✗ Error en reintento: {e2}")
            return None
    
    def ejecutar_update(self, query, params=None):
        """Ejecuta un UPDATE de manera segura"""
        try:
            if not self.connection or self.connection.closed:
                if not self.conectar_bd():
                    return False
            
            self.cursor.execute(query, params or ())
            filas_afectadas = self.cursor.rowcount
            self.connection.commit()
            return filas_afectadas > 0
        except Exception as e:
            print(f"✗ Error en actualización: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def verificar_correspondencia(self, batt_dept_id, client_code):
        """Verifica si el batt_dept_id corresponde al client_code"""
        query = """
        SELECT id, client_code, name 
        FROM batt_dept 
        WHERE id = %s AND client_code = %s
        """
        result = self.ejecutar_consulta(query, (batt_dept_id, client_code))
        
        if result and len(result) > 0:
            row = result[0]
            return True, f"ID: {row[0]}, Client Code: {row[1]}, Name: {row[2]}"
        else:
            return False, None
    
    def buscar_por_id(self, batt_dept_id):
        """Busca qué client_code tiene asignado un ID específico"""
        query = """
        SELECT id, client_code, name 
        FROM batt_dept 
        WHERE id = %s
        """
        result = self.ejecutar_consulta(query, (batt_dept_id,))
        
        if result and len(result) > 0:
            return True, result[0]
        else:
            return False, None
    
    def buscar_por_client_code(self, client_code):
        """Busca qué ID tiene asignado un client_code específico"""
        query = """
        SELECT id, client_code, name 
        FROM batt_dept 
        WHERE client_code = %s
        """
        result = self.ejecutar_consulta(query, (client_code,))
        
        if result and len(result) > 0:
            return True, result[0]
        else:
            return False, None
    
    def buscar_id_libre(self):
        """Busca el próximo ID libre en la tabla batt_dept"""
        query = """
        SELECT COALESCE(MAX(id), 0) + 1 as free_id 
        FROM batt_dept
        """
        result = self.ejecutar_consulta(query)
        
        if result and len(result) > 0:
            return result[0][0]
        else:
            return 100000  # ID por defecto si falla
    
    def actualizar_id(self, old_id, new_id, client_code):
        """Actualiza el ID de un registro específico"""
        # Verificar que el nuevo ID esté libre
        existe_query = "SELECT id FROM batt_dept WHERE id = %s"
        result = self.ejecutar_consulta(existe_query, (new_id,))
        
        if result and len(result) > 0:
            print(f"✗ El ID {new_id} ya está en uso")
            return False
        
        # Actualizar el ID
        update_query = """
        UPDATE batt_dept 
        SET id = %s 
        WHERE id = %s AND client_code = %s
        """
        
        exito = self.ejecutar_update(update_query, (new_id, old_id, client_code))
        
        if exito:
            print(f"✓ Actualización exitosa: {client_code} del ID {old_id} al ID {new_id}")
            return True
        else:
            print(f"✗ No se pudo actualizar el registro {client_code} del ID {old_id} al ID {new_id}")
            return False
    
    def reasignar_id(self, id_deseado, client_code_deseado, client_code_actual):
        """Reasigna un ID ocupado por otro client_code"""
        print(f"\n🔄 Iniciando proceso de reasignación...")
        print(f"   ID deseado: {id_deseado}")
        print(f"   Client code deseado: {client_code_deseado}")
        print(f"   Client code que ocupa el ID: {client_code_actual}")
        
        # Paso 1: Buscar ID libre para mover el registro actual
        id_libre = self.buscar_id_libre()
        print(f"   ID libre encontrado: {id_libre}")
        
        # Paso 2: Mover el registro actual a un ID libre
        print(f"   Moviendo {client_code_actual} del ID {id_deseado} al ID {id_libre}...")
        if not self.actualizar_id(id_deseado, id_libre, client_code_actual):
            return False
        
        # Paso 3: Buscar el registro del client_code deseado
        encontrado, datos = self.buscar_por_client_code(client_code_deseado)
        if not encontrado or not datos:
            print(f"✗ No se encontró el client_code {client_code_deseado}")
            return False
        
        id_actual_deseado = datos[0]
        print(f"   {client_code_deseado} está actualmente en ID {id_actual_deseado}")
        
        # Paso 4: Mover el client_code deseado al ID deseado
        print(f"   Moviendo {client_code_deseado} del ID {id_actual_deseado} al ID {id_deseado}...")
        if not self.actualizar_id(id_actual_deseado, id_deseado, client_code_deseado):
            return False
        
        print(f"✅ Reasignación exitosa: {client_code_deseado} ahora tiene el ID {id_deseado}")
        return True
    
    def mostrar_estado_final(self, verificaciones):
        """Muestra el estado final de todas las verificaciones"""
        print("\n" + "="*60)
        print("ESTADO FINAL DE VERIFICACIONES")
        print("="*60)
        
        for batt_dept_id, client_code in verificaciones:
            encontrado, info = self.verificar_correspondencia(batt_dept_id, client_code)
            if encontrado:
                print(f"✓ ID {batt_dept_id} - {client_code}: CORRECTO")
                print(f"  {info}")
            else:
                print(f"✗ ID {batt_dept_id} - {client_code}: INCORRECTO")
                
                # Mostrar qué hay actualmente
                encontrado_id, datos_id = self.buscar_por_id(batt_dept_id)
                if encontrado_id and datos_id:
                    print(f"  ID {batt_dept_id} actualmente asignado a: {datos_id[1]}")
                
                encontrado_cc, datos_cc = self.buscar_por_client_code(client_code)
                if encontrado_cc and datos_cc:
                    print(f"  {client_code} actualmente tiene ID: {datos_cc[0]}")
            print()

def parsear_entrada(entrada):
    """Parsea la entrada del usuario para extraer pares ID-ClientCode"""
    pares = []
    # Dividir por comas o espacios múltiples
    elementos = re.split(r'[,\s]+', entrada.strip())
    
    # Agrupar de a pares
    for i in range(0, len(elementos), 2):
        if i + 1 < len(elementos):
            # Intentar determinar cuál es ID y cuál es client_code
            elem1, elem2 = elementos[i], elementos[i + 1]
            
            # Si uno es numérico, es el ID
            if elem1.isdigit() and not elem2.isdigit():
                pares.append((int(elem1), elem2))
            elif elem2.isdigit() and not elem1.isdigit():
                pares.append((int(elem2), elem1))
            else:
                print(f"⚠️  Advertencia: No se pudo determinar ID y client_code para '{elem1}' y '{elem2}'")
                # Asumir que el primero es ID si ambos son numéricos
                if elem1.isdigit():
                    pares.append((int(elem1), elem2))
    
    return pares

def main():
    print("="*60)
    print("VERIFICADOR DE BATT_DEPT_ID Y CLIENT_CODE")
    print("="*60)
    print()
    
    # Información de configuración de BD
    print("🔧 CONFIGURACIÓN DE BASE DE DATOS")
    print("-" * 35)
    print(f"📍 Host: {DB_CONFIG['host']}")
    print(f"🔢 Puerto: {DB_CONFIG['port']}")
    print(f"🗄️  Base de datos: {DB_CONFIG['database']}")
    print(f"👤 Usuario: {DB_CONFIG['user']}")
    print(f"🔒 Password: {'*' * len(DB_CONFIG['password'])}")
    print()
    print("⚠️  IMPORTANTE: Verifique que las credenciales de BD sean correctas")
    print("   Si necesita cambiarlas, modifique la sección DB_CONFIG en el script")
    print()
    
    verificador = BattDeptVerificador()
    
    # Conectar a la base de datos
    if not verificador.conectar_bd():
        print("❌ No se pudo conectar a la base de datos")
        input("Presione Enter para salir...")
        return
    
    try:
        while True:  # Bucle principal para múltiples verificaciones
            # Solicitar datos de entrada
            print("📝 FORMATO DE ENTRADA DE DATOS")
            print("-" * 32)
            print("💡 Ingrese los pares ID-ClientCode que desea verificar:")
            print()
            print("📋 FORMATO ACEPTADO:")
            print("   • Separados por espacios: ID ClientCode ID2 ClientCode2")
            print("   • Separados por comas: ID,ClientCode,ID2,ClientCode2") 
            print("   • Orden flexible: ClientCode ID o ID ClientCode")
            print()
            print("📌 EJEMPLOS VÁLIDOS:")
            print("   ✓ 4471 ALPINE_TOWNSHIP_MI")
            print("   ✓ 4471 ALPINE_TOWNSHIP_MI 2083 MARION_IL")
            print("   ✓ ALPINE_TOWNSHIP_MI 4471")
            print("   ✓ 4471,ALPINE_TOWNSHIP_MI,2083,MARION_IL")
            print()
            print("🔍 QUÉ VERIFICA EL SCRIPT:")
            print("   • Si el ID (batt_dept_id) corresponde al CLIENT_CODE correcto")
            print("   • Si hay discrepancias, puede corregirlas automáticamente")
            print("   • Reasigna IDs cuando hay conflictos")
            print()
            
            entrada = input("➡️  Ingrese los datos a verificar: ").strip()
            if not entrada:
                print("✗ No se ingresaron datos")
                continue  # Volver a pedir datos
            
            # Parsear entrada
            verificaciones = parsear_entrada(entrada)
            if not verificaciones:
                print("✗ No se pudieron parsear los datos de entrada")
                continue  # Volver a pedir datos
            
            print(f"\n📋 Se verificarán {len(verificaciones)} pares:")
            for batt_dept_id, client_code in verificaciones:
                print(f"   ID: {batt_dept_id} - Client Code: {client_code}")
            print()
            
            # Realizar verificaciones
            resultados = []
            for batt_dept_id, client_code in verificaciones:
                print(f"🔍 Verificando ID {batt_dept_id} con {client_code}...")
                
                correcto, info = verificador.verificar_correspondencia(batt_dept_id, client_code)
                
                if correcto:
                    print(f"✓ CORRECTO: {info}")
                    resultados.append((batt_dept_id, client_code, True, None))
                else:
                    print(f"✗ INCORRECTO: No coinciden")
                    
                    # Verificar qué está en cada lugar
                    encontrado_id, datos_id = verificador.buscar_por_id(batt_dept_id)
                    encontrado_cc, datos_cc = verificador.buscar_por_client_code(client_code)
                    
                    info_error = {
                        'id_ocupado_por': datos_id[1] if encontrado_id and datos_id else None,
                        'client_code_tiene_id': datos_cc[0] if encontrado_cc and datos_cc else None
                    }
                    
                    if encontrado_id and datos_id:
                        print(f"  El ID {batt_dept_id} está asignado a: {datos_id[1]} ({datos_id[2]})")
                    if encontrado_cc and datos_cc:
                        print(f"  El client_code {client_code} tiene ID: {datos_cc[0]} ({datos_cc[2]})")
                    
                    resultados.append((batt_dept_id, client_code, False, info_error))
                print()
            
            # Procesar correcciones
            hay_errores = any(not resultado[2] for resultado in resultados)
            correcciones_realizadas = False
            
            if hay_errores:
                print("\n🔧 Se encontraron discrepancias. ¿Desea corregirlas?")
                respuesta = input("Ingrese 'si' para continuar con las correcciones: ").strip().lower()
                
                if respuesta in ['si', 'sí', 's', 'yes', 'y']:
                    print("\n🚀 Iniciando correcciones automáticas...")
                    correcciones_realizadas = True
                    
                    for batt_dept_id, client_code, es_correcto, info_error in resultados:
                        if not es_correcto:
                            print(f"\n🔧 Corrigiendo ID {batt_dept_id} - {client_code}...")
                            
                            # Verificar si el client_code existe en la BD
                            encontrado_cc, datos_cc = verificador.buscar_por_client_code(client_code)
                            if not encontrado_cc or not datos_cc:
                                print(f"❌ Error: El client_code {client_code} no existe en la base de datos")
                                continue
                            
                            # Verificar si el ID está ocupado (consulta fresca)
                            encontrado_id, datos_id = verificador.buscar_por_id(batt_dept_id)
                            
                            if encontrado_id and datos_id and datos_id[1] != client_code:
                                # El ID está ocupado por otro client_code, hacer reasignación
                                exito = verificador.reasignar_id(
                                    batt_dept_id, 
                                    client_code, 
                                    datos_id[1]  # client_code que ocupa actualmente el ID
                                )
                            elif not encontrado_id or not datos_id:
                                # El ID está libre, solo mover el client_code al ID deseado
                                id_actual_client = datos_cc[0]
                                exito = verificador.actualizar_id(id_actual_client, batt_dept_id, client_code)
                            else:
                                # Ya está correcto
                                exito = True
                                print(f"✓ {client_code} ya está en el ID {batt_dept_id}")
                            
                            if exito:
                                print(f"✅ Corrección exitosa para ID {batt_dept_id} - {client_code}")
                            else:
                                print(f"❌ Error al corregir ID {batt_dept_id} - {client_code}")
                    
                    # Mostrar estado final
                    print("\n⏳ Verificando estado final...")
                    verificador.mostrar_estado_final(verificaciones)
                else:
                    print("ℹ️  Correcciones canceladas por el usuario")
            else:
                print("✅ Todas las verificaciones son correctas")
            
            # Mostrar resumen
            print(f"\n{'='*60}")
            print("📋 RESUMEN DEL PROCESO:")
            print(f"   📊 Pares verificados: {len(verificaciones)}")
            print(f"   ⚠️ Discrepancias encontradas: {len([r for r in resultados if not r[2]])}")
            if hay_errores:
                print(f"   🔧 Correcciones realizadas: {'Sí' if correcciones_realizadas else 'No'}")
            print(f"{'='*60}")
            
            # SIEMPRE preguntar si continuar
            print(f"\n{'-'*60}")
            print("🔄 ¿Desea verificar otro batt_dept_id?")
            print("   📝 Ingrese 'si' para continuar")
            print("   📝 Ingrese cualquier otra cosa para salir")
            respuesta_continuar = input("➡️ Su respuesta: ").lower().strip()
            
            if respuesta_continuar != 'si':
                print(f"\n✅ Saliendo del verificador de batt_dept_id...")
                print("   Gracias por usar la herramienta!")
                break
            
            # Limpiar pantalla visualmente para nueva verificación
            print(f"\n{'='*60}")
            print("🔄 NUEVA VERIFICACIÓN")
            print(f"{'='*60}")
            print()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
    finally:
        verificador.desconectar_bd()
        print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    main()
