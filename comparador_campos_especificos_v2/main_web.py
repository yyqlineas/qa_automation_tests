#!/usr/bin/env python3
"""
Comparador de Campos Específicos V2 - Interfaz Moderna
Estilo Web con CustomTkinter
"""

import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal que lanza la GUI moderna estilo web"""
    try:
        from web_style_gui import main as launch_web_gui
        launch_web_gui()
    except ImportError as e:
        print(f"Error importando la GUI web: {e}")
        print("Verifique que CustomTkinter esté instalado: pip install customtkinter")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
