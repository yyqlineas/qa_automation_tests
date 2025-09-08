#!/usr/bin/env python3
"""
Script para verificar la configuración de Database Record Copier
Autor: Sistema Automatizado
Fecha: 2025-09-05
"""

import json
import os
import sys

def verificar_configuracion():
    """Verifica que la configuración esté correcta"""
    config_file = "config_database_copier.json"
    
    print("🔍 VERIFICADOR DE CONFIGURACIÓN")
    print("="*50)
    
    # Verificar que el archivo existe
    if not os.path.exists(config_file):
        print(f"❌ Archivo {config_file} no encontrado")
        print("💡 Ejecute el script principal primero para crear el archivo de configuración")
        return False
    
    try:
        # Cargar configuración
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ Archivo {config_file} encontrado y válido")
        
        # Verificar estructura
        errores = []
        advertencias = []
        
        # Verificar sección source_database
        if 'source_database' not in config:
            errores.append("Falta sección 'source_database'")
        else:
            source_db = config['source_database']
            
            # Verificar campos obligatorios
            if source_db.get('database', '').startswith('COLOCA_AQUI'):
                errores.append("❌ source_database.database no configurado")
            else:
                print(f"✅ Base de datos origen: {source_db.get('database')}")
                
            if source_db.get('password', '').startswith('COLOCA_AQUI'):
                errores.append("❌ source_database.password no configurado")
            else:
                print("✅ Password de origen configurado")
            
            # Verificar configuración SSH
            ssh_config = source_db.get('ssh_tunnel', {})
            if ssh_config.get('enabled', False):
                print("🔐 Túnel SSH habilitado para origen")
                
                ssh_key = ssh_config.get('ssh_key_file', '')
                if not os.path.exists(ssh_key):
                    errores.append(f"❌ Llave SSH no encontrada: {ssh_key}")
                else:
                    print(f"✅ Llave SSH encontrada: {ssh_key}")
                    
                print(f"   📡 SSH Host: {ssh_config.get('ssh_host')}")
                print(f"   🔌 SSH Port: {ssh_config.get('ssh_port')}")
                print(f"   👤 SSH User: {ssh_config.get('ssh_username')}")
        
        # Verificar sección destination_database
        if 'destination_database' not in config:
            errores.append("Falta sección 'destination_database'")
        else:
            dest_db = config['destination_database']
            
            if dest_db.get('database', '').startswith('COLOCA_AQUI'):
                errores.append("❌ destination_database.database no configurado")
            else:
                print(f"✅ Base de datos destino: {dest_db.get('database')}")
                
            if dest_db.get('username', '').startswith('COLOCA_AQUI'):
                errores.append("❌ destination_database.username no configurado")
            else:
                print(f"✅ Usuario destino: {dest_db.get('username')}")
                
            if dest_db.get('password', '').startswith('COLOCA_AQUI'):
                errores.append("❌ destination_database.password no configurado")
            else:
                print("✅ Password de destino configurado")
        
        # Mostrar resultados
        print("\n" + "="*50)
        
        if errores:
            print("❌ ERRORES ENCONTRADOS:")
            for error in errores:
                print(f"   {error}")
            print("\n🔧 Por favor corrija estos errores en config_database_copier.json")
            return False
        else:
            print("✅ CONFIGURACIÓN VÁLIDA")
            print("🚀 El script está listo para ejecutarse")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Error en formato JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
        return False

def verificar_dependencias():
    """Verifica que las dependencias estén instaladas"""
    print("\n🔍 VERIFICANDO DEPENDENCIAS")
    print("="*30)
    
    dependencias = [
        ('pyodbc', 'pyodbc'),
        ('sshtunnel', 'sshtunnel'),
        ('paramiko', 'paramiko')
    ]
    
    todas_ok = True
    
    for nombre, modulo in dependencias:
        try:
            __import__(modulo)
            print(f"✅ {nombre} instalado")
        except ImportError:
            print(f"❌ {nombre} NO instalado")
            todas_ok = False
    
    if not todas_ok:
        print("\n💡 Para instalar dependencias ejecute:")
        print("   pip install pyodbc sshtunnel paramiko")
        print("   O use: instalar_copier.bat")
    
    return todas_ok

def main():
    print("🛠️  VERIFICADOR DE CONFIGURACIÓN - DATABASE RECORD COPIER")
    print("=" * 60)
    
    # Verificar dependencias
    deps_ok = verificar_dependencias()
    
    # Verificar configuración
    config_ok = verificar_configuracion()
    
    print("\n" + "="*60)
    
    if deps_ok and config_ok:
        print("🎉 TODO LISTO PARA EJECUTAR")
        print("▶️  Ejecute: python database_record_copier.py")
    else:
        print("⚠️  HAY PROBLEMAS QUE CORREGIR")
        if not deps_ok:
            print("   - Instale las dependencias faltantes")
        if not config_ok:
            print("   - Configure las credenciales en config_database_copier.json")
    
    print("="*60)

if __name__ == "__main__":
    main()
    input("\nPresione Enter para continuar...")
