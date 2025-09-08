#!/usr/bin/env python3
"""
Comparador de Campos Específicos V2 - Punto de entrada principal
Versión de línea de comandos y GUI clásica
"""

import sys
import os
import argparse
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal del comparador"""
    parser = argparse.ArgumentParser(description='Comparador de Campos Específicos V2')
    parser.add_argument('--gui', action='store_true', help='Ejecutar interfaz gráfica')
    parser.add_argument('--web', action='store_true', help='Ejecutar interfaz web moderna')
    parser.add_argument('--config', type=str, help='Ruta al archivo de configuración')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    try:
        if args.web:
            # Lanzar interfaz web moderna
            from web_style_gui import main as launch_web_gui
            launch_web_gui()
        elif args.gui:
            # Lanzar interfaz gráfica clásica
            import tkinter as tk
            from gui_comparator import ComparatorGUI
            root = tk.Tk()
            app = ComparatorGUI(root)
            root.mainloop()
        else:
            # Modo línea de comandos
            from field_comparator import FieldComparator
            
            config_path = args.config or os.path.join(os.path.dirname(__file__), 'config', 'config.json')
            
            if not os.path.exists(config_path):
                print(f"Error: Archivo de configuración no encontrado: {config_path}")
                sys.exit(1)
            
            comparator = FieldComparator(config_path)
            
            print("=== Comparador de Campos Específicos V2 ===")
            print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Configuración: {config_path}")
            print()
            
            # Ejecutar comparación por línea de comandos
            print("Para usar el comparador, ejecute:")
            print("  python main.py --web    (interfaz web moderna)")
            print("  python main.py --gui    (interfaz gráfica clásica)")
            print()
            
    except ImportError as e:
        print(f"Error importando módulos: {e}")
        print("Verifique que todas las dependencias estén instaladas:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()