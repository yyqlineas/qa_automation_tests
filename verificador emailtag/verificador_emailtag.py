#!/usr/bin/env python3
"""
Verificador de correspondencia entre batt_dept_id, client_code y emailtag
Autor: Automatización FDSU
Fecha: 2025-10-01

Este script permite:
1. Verificar si un emailtag corresponde al batt_dept_id y client_code correctos
2. Mostrar discrepancias encontradas
3. Actualizar automáticamente los emailtags incorrectos
4. Validar que el batt_dept_id corresponda al client_code antes de actualizar emailtag
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

class EmailTagVerificador:
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
            
            if self.cursor is not None:
                self.cursor.execute(query, params or ())
                return self.cursor.fetchall()
        except Exception as e:
            print(f"✗ Error en consulta: {e}")
            # Reconectar y reintentar una vez
            try:
                if self.conectar_bd():
                    if self.cursor is not None:
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
            
            if self.cursor is not None and self.connection is not None:
                self.cursor.execute(query, params or ())
                filas_afectadas = self.cursor.rowcount
                self.connection.commit()
                return filas_afectadas > 0
        except Exception as e:
            print(f"✗ Error en actualización: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def verificar_batt_dept_client_code(self, batt_dept_id, client_code):
        """Verifica si el batt_dept_id corresponde al client_code"""
        query = """
        SELECT id, client_code, name, email_tag
        FROM batt_dept 
        WHERE id = %s AND client_code = %s
        """
        result = self.ejecutar_consulta(query, (batt_dept_id, client_code))
        
        if result and len(result) > 0:
            row = result[0]
            return True, {
                'id': row[0],
                'client_code': row[1], 
                'name': row[2],
                'email_tag': row[3]
            }
        else:
            return False, None
    
    def verificar_emailtag_correspondencia(self, batt_dept_id, client_code, emailtag_esperado):
        """Verifica si el emailtag corresponde al batt_dept_id y client_code dados"""
        # Primero verificar que batt_dept_id y client_code coincidan
        coincide_bd_cc, datos = self.verificar_batt_dept_client_code(batt_dept_id, client_code)
        
        if not coincide_bd_cc or datos is None:
            return False, "NO_COINCIDE_BATT_DEPT_CLIENT_CODE", None
        
        # Si coinciden, verificar el emailtag
        emailtag_actual = datos['email_tag']
        
        if emailtag_actual == emailtag_esperado:
            return True, "EMAILTAG_CORRECTO", datos
        else:
            datos_con_esperado = datos.copy()
            datos_con_esperado['emailtag_esperado'] = emailtag_esperado
            datos_con_esperado['emailtag_actual'] = emailtag_actual
            return False, "EMAILTAG_INCORRECTO", datos_con_esperado
    
    def buscar_por_batt_dept_id(self, batt_dept_id):
        """Busca qué client_code tiene asignado un batt_dept_id específico"""
        query = """
        SELECT id, client_code, name, email_tag
        FROM batt_dept 
        WHERE id = %s
        """
        result = self.ejecutar_consulta(query, (batt_dept_id,))
        
        if result and len(result) > 0:
            row = result[0]
            return True, {
                'id': row[0],
                'client_code': row[1],
                'name': row[2], 
                'email_tag': row[3]
            }
        else:
            return False, None
    
    def actualizar_emailtag(self, batt_dept_id, client_code, nuevo_emailtag):
        """Actualiza el emailtag de un registro específico"""
        update_query = """
        UPDATE batt_dept 
        SET email_tag = %s 
        WHERE id = %s AND client_code = %s
        """
        
        exito = self.ejecutar_update(update_query, (nuevo_emailtag, batt_dept_id, client_code))
        
        if exito:
            print(f"✓ Actualización exitosa: emailtag actualizado a '{nuevo_emailtag}' para ID {batt_dept_id} - {client_code}")
            return True
        else:
            print(f"✗ No se pudo actualizar el emailtag para ID {batt_dept_id} - {client_code}")
            return False
    
    def mostrar_estado_final(self, verificaciones):
        """Muestra el estado final de todas las verificaciones"""
        print("\n" + "="*70)
        print("ESTADO FINAL DE VERIFICACIONES DE EMAILTAG")
        print("="*70)
        
        for batt_dept_id, client_code, emailtag_esperado in verificaciones:
            es_correcto, tipo_resultado, datos = self.verificar_emailtag_correspondencia(
                batt_dept_id, client_code, emailtag_esperado
            )
            
            if es_correcto and datos is not None:
                print(f"✓ ID {batt_dept_id} - {client_code} - emailtag '{emailtag_esperado}': CORRECTO")
                print(f"  {datos['name']}")
            else:
                if tipo_resultado == "NO_COINCIDE_BATT_DEPT_CLIENT_CODE":
                    print(f"✗ ID {batt_dept_id} - {client_code}: BATT_DEPT_ID Y CLIENT_CODE NO COINCIDEN")
                    # Mostrar qué hay en ese ID
                    encontrado, datos_id = self.buscar_por_batt_dept_id(batt_dept_id)
                    if encontrado and datos_id is not None:
                        print(f"  ID {batt_dept_id} actualmente asignado a: {datos_id['client_code']}")
                elif tipo_resultado == "EMAILTAG_INCORRECTO" and datos is not None:
                    print(f"✗ ID {batt_dept_id} - {client_code}: EMAILTAG INCORRECTO")
                    print(f"  Emailtag actual: '{datos['emailtag_actual']}'")
                    print(f"  Emailtag esperado: '{datos['emailtag_esperado']}'")
            print()

def parsear_entrada_emailtag(entrada):
    """Parsea la entrada del usuario para extraer trios ID-ClientCode-EmailTag"""
    elementos = re.split(r'[,\s]+', entrada.strip())
    trios = []
    
    # Agrupar de a tres elementos
    for i in range(0, len(elementos), 3):
        if i + 2 < len(elementos):
            elem1, elem2, elem3 = elementos[i], elementos[i + 1], elementos[i + 2]
            
            # Identificar cuál es el ID (numérico)
            if elem1.isdigit():
                batt_dept_id = int(elem1)
                client_code = elem2
                emailtag = elem3
            elif elem2.isdigit():
                client_code = elem1
                batt_dept_id = int(elem2)
                emailtag = elem3
            elif elem3.isdigit():
                client_code = elem1
                emailtag = elem2
                batt_dept_id = int(elem3)
            else:
                print(f"⚠️  Advertencia: No se encontró ID numérico en '{elem1}', '{elem2}', '{elem3}'")
                continue
            
            trios.append((batt_dept_id, client_code, emailtag))
        else:
            print(f"⚠️  Advertencia: Faltan elementos para formar un trio completo")
    
    return trios

def main():
    print("="*70)
    print("VERIFICADOR DE EMAILTAG PARA BATT_DEPT_ID Y CLIENT_CODE")
    print("="*70)
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
    
    verificador = EmailTagVerificador()
    
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
            print("💡 Ingrese los trios ID-ClientCode-EmailTag que desea verificar:")
            print()
            print("📋 FORMATO ACEPTADO:")
            print("   • Separados por espacios: ID ClientCode EmailTag")
            print("   • Separados por comas: ID,ClientCode,EmailTag")
            print("   • Orden flexible: ClientCode ID EmailTag, etc.")
            print()
            print("📌 EJEMPLOS VÁLIDOS:")
            print("   ✓ 4471 ALPINE_TOWNSHIP_MI alpine@example.com")
            print("   ✓ ALPINE_TOWNSHIP_MI 4471 alpine@example.com")
            print("   ✓ 4471,ALPINE_TOWNSHIP_MI,alpine@example.com")
            print()
            print("🔍 QUÉ VERIFICA EL SCRIPT:")
            print("   • Si el emailtag corresponde al batt_dept_id y client_code correctos")
            print("   • Si batt_dept_id y client_code coinciden entre sí")
            print("   • Permite actualizar emailtag cuando hay discrepancias")
            print()
            
            entrada = input("➡️  Ingrese los datos a verificar: ").strip()
            if not entrada:
                print("✗ No se ingresaron datos")
                continue  # Volver a pedir datos
            
            # Parsear entrada
            verificaciones = parsear_entrada_emailtag(entrada)
            if not verificaciones:
                print("✗ No se pudieron parsear los datos de entrada")
                continue  # Volver a pedir datos
            
            print(f"\n📋 Se verificarán {len(verificaciones)} trios:")
            for batt_dept_id, client_code, emailtag in verificaciones:
                print(f"   ID: {batt_dept_id} - Client Code: {client_code} - EmailTag: {emailtag}")
            print()
            
            # Realizar verificaciones
            resultados = []
            for batt_dept_id, client_code, emailtag_esperado in verificaciones:
                print(f"🔍 Verificando ID {batt_dept_id} con {client_code} y emailtag '{emailtag_esperado}'...")
                
                es_correcto, tipo_resultado, datos = verificador.verificar_emailtag_correspondencia(
                    batt_dept_id, client_code, emailtag_esperado
                )
                
                if es_correcto:
                    print(f"✓ CORRECTO: El emailtag '{emailtag_esperado}' coincide")
                    if datos is not None:
                        print(f"  Departamento: {datos['name']}")
                    resultados.append((batt_dept_id, client_code, emailtag_esperado, True, tipo_resultado, datos))
                else:
                    if tipo_resultado == "NO_COINCIDE_BATT_DEPT_CLIENT_CODE":
                        print(f"✗ ERROR: El batt_dept_id {batt_dept_id} no corresponde al client_code {client_code}")
                        
                        # Verificar qué client_code tiene ese ID
                        encontrado, datos_id = verificador.buscar_por_batt_dept_id(batt_dept_id)
                        if encontrado and datos_id is not None:
                            print(f"  El ID {batt_dept_id} actualmente está asignado a: {datos_id['client_code']}")
                            print(f"  📌 ACCIÓN REQUERIDA: Actualice primero el batt_dept_id antes de actualizar el emailtag")
                        else:
                            print(f"  El ID {batt_dept_id} no existe en la base de datos")
                        
                    elif tipo_resultado == "EMAILTAG_INCORRECTO" and datos is not None:
                        print(f"✗ EMAILTAG INCORRECTO:")
                        print(f"  Emailtag actual: '{datos['emailtag_actual']}'")
                        print(f"  Emailtag esperado: '{datos['emailtag_esperado']}'")
                        print(f"  Departamento: {datos['name']}")
                    
                    resultados.append((batt_dept_id, client_code, emailtag_esperado, False, tipo_resultado, datos))
                print()
            
            # Procesar correcciones
            hay_errores_emailtag = any(
                not resultado[3] and resultado[4] == "EMAILTAG_INCORRECTO" 
                for resultado in resultados
            )
            hay_errores_batt_dept = any(
                not resultado[3] and resultado[4] == "NO_COINCIDE_BATT_DEPT_CLIENT_CODE"
                for resultado in resultados
            )
            
            correcciones_realizadas = False
            
            if hay_errores_batt_dept:
                print("\n❌ ADVERTENCIA: Se encontraron discrepancias en batt_dept_id y client_code")
                print("   📌 Debe usar el verificador de batt_dept_id para corregir estas discrepancias primero")
                print("   📌 Los emailtags NO se actualizarán hasta que los batt_dept_id estén correctos")
                
            if hay_errores_emailtag:
                print("\n🔧 Se encontraron discrepancias en emailtag. ¿Desea corregirlas?")
                respuesta = input("Ingrese 'si' para continuar con las correcciones: ").strip().lower()
                
                if respuesta in ['si', 'sí', 's', 'yes', 'y']:
                    print("\n🚀 Iniciando correcciones automáticas de emailtag...")
                    correcciones_realizadas = True
                    
                    for batt_dept_id, client_code, emailtag_esperado, es_correcto, tipo_resultado, datos in resultados:
                        if not es_correcto and tipo_resultado == "EMAILTAG_INCORRECTO" and datos is not None:
                            print(f"\n🔧 Corrigiendo emailtag para ID {batt_dept_id} - {client_code}...")
                            print(f"   Cambiando de '{datos['emailtag_actual']}' a '{emailtag_esperado}'")
                            
                            exito = verificador.actualizar_emailtag(batt_dept_id, client_code, emailtag_esperado)
                            
                            if exito:
                                print(f"✅ Actualización exitosa para ID {batt_dept_id} - {client_code}")
                            else:
                                print(f"❌ Error al actualizar emailtag para ID {batt_dept_id} - {client_code}")
                        elif not es_correcto and tipo_resultado == "NO_COINCIDE_BATT_DEPT_CLIENT_CODE":
                            print(f"\n⚠️  Saltando ID {batt_dept_id} - {client_code}: batt_dept_id y client_code no coinciden")
                    
                    # Mostrar estado final
                    if correcciones_realizadas:
                        print("\n⏳ Verificando estado final...")
                        verificador.mostrar_estado_final(verificaciones)
                else:
                    print("ℹ️  Correcciones canceladas por el usuario")
            elif not hay_errores_batt_dept:
                print("✅ Todas las verificaciones de emailtag son correctas")
            
            # Mostrar resumen
            print(f"\n{'='*70}")
            print("📋 RESUMEN DEL PROCESO:")
            print(f"   📊 Trios verificados: {len(verificaciones)}")
            print(f"   ⚠️ Errores de batt_dept_id/client_code: {len([r for r in resultados if not r[3] and r[4] == 'NO_COINCIDE_BATT_DEPT_CLIENT_CODE'])}")
            print(f"   ⚠️ Errores de emailtag: {len([r for r in resultados if not r[3] and r[4] == 'EMAILTAG_INCORRECTO'])}")
            if hay_errores_emailtag:
                print(f"   🔧 Correcciones de emailtag realizadas: {'Sí' if correcciones_realizadas else 'No'}")
            print(f"{'='*70}")
            
            # SIEMPRE preguntar si continuar
            print(f"\n{'-'*70}")
            print("🔄 ¿Desea verificar otro emailtag?")
            print("   📝 Ingrese 'si' para continuar")
            print("   📝 Ingrese cualquier otra cosa para salir")
            respuesta_continuar = input("➡️ Su respuesta: ").lower().strip()
            
            if respuesta_continuar != 'si':
                print(f"\n✅ Saliendo del verificador de emailtag...")
                print("   Gracias por usar la herramienta!")
                break
            
            # Limpiar pantalla visualmente para nueva verificación
            print(f"\n{'='*70}")
            print("🔄 NUEVA VERIFICACIÓN")
            print(f"{'='*70}")
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