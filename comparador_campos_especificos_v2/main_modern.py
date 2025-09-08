#!/usr/bin/env python3
"""
Comparador de Campos Específicos V2 - Interfaz Moderna
Punto de entrada principal para la GUI moderna con tkinter
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal que lanza la GUI moderna"""
    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Importar y lanzar la GUI moderna
        from modern_gui import ModernGUI
        app = ModernGUI(root)
        
        # Ejecutar la aplicación
        root.mainloop()
        
    except ImportError as e:
        print(f"Error importando la GUI moderna: {e}")
        print("Verifique que todos los módulos estén disponibles")
        if '--no-gui' not in sys.argv:
            try:
                messagebox.showerror("Error de Importación", 
                                   f"Error importando la GUI moderna:\n{e}\n\nVerifique las dependencias.")
            except:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando la aplicación: {e}")
        if '--no-gui' not in sys.argv:
            try:
                messagebox.showerror("Error", f"Error ejecutando la aplicación:\n{e}")
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()