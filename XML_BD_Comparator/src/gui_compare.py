import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys
from xml_compare import XPathMapper
from datetime import datetime

class ComparadorXMLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador XML vs Base de Datos")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Centrar la ventana
        self.center_window()
        
        # Variables para almacenar rutas
        self.mapping_path = None
        self.xml_folder = None
        
        # Verificar archivos necesarios
        try:
            self.check_required_files()
        except Exception as e:
            messagebox.showerror("Error de inicialización", str(e))
            return
        
        # Crear interfaz
        self.create_gui()
        
        # Asegurar que la ventana se muestre
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
    def center_window(self):
        """Centrar la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def check_required_files(self):
        """Verifica que existan los archivos necesarios y los crea si no existen"""
        # Obtener la ruta base del programa
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Verificar y crear directorios necesarios
        config_path = os.path.join(base_path, 'config')
        mappings_path = os.path.join(base_path, 'mappings')
        reportes_path = os.path.join(base_path, 'reportes')
        logs_path = os.path.join(base_path, 'logs')
        
        # Crear directorios si no existen
        for dir_path in [config_path, mappings_path, reportes_path, logs_path]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Verificar config.json
        config_json = os.path.join(config_path, 'config.json')
        config_template = os.path.join(config_path, 'config.json.template')
        
        if not os.path.exists(config_json):
            if os.path.exists(config_template):
                messagebox.showwarning(
                    "Configuración necesaria",
                    "Por favor, configura tus credenciales de base de datos y filtros en el archivo config.json"
                )
                # Copiar el template
                import shutil
                shutil.copy2(config_template, config_json)
                # Abrir el archivo para edición
                if sys.platform == 'win32':
                    os.system(f'notepad "{config_json}"')
                else:
                    os.system(f'xdg-open "{config_json}"')
            else:
                messagebox.showerror(
                    "Error",
                    f"No se encuentra el archivo de configuración template en:\n{config_template}"
                )
                sys.exit(1)
                
        # Guardar las rutas para uso posterior
        self.config_path = config_json

    def create_gui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo para configuración
        left_frame = tk.LabelFrame(main_frame, text="Configuración", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame derecho para el botón de ejecutar
        right_frame = tk.Frame(main_frame, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Etiqueta de estado
        self.status_label = tk.Label(
            left_frame, 
            text="Estado: Listo para ejecutar", 
            wraplength=550,
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, pady=(0, 20))
        
        # 1. Botón para editar configuración
        config_frame = tk.Frame(left_frame)
        config_frame.pack(fill=tk.X, pady=5)
        
        self.config_button = tk.Button(
            config_frame,
            text="1. Editar configuración de conexión",
            command=self.edit_config,
            bg='#e6e6e6'
        )
        self.config_button.pack(fill=tk.X)
        
        # 2. Frame para selección de mapping
        mapping_frame = tk.Frame(left_frame)
        mapping_frame.pack(fill=tk.X, pady=5)
        
        self.mapping_button = tk.Button(
            mapping_frame,
            text="2. Seleccionar archivo de mapping (XLS)",
            command=self.select_mapping_file,
            bg='#e6e6e6'
        )
        self.mapping_button.pack(fill=tk.X)
        
        self.mapping_label = tk.Label(
            mapping_frame,
            text="No se ha seleccionado archivo de mapping",
            wraplength=400,
            justify=tk.LEFT
        )
        self.mapping_label.pack(fill=tk.X, pady=(5,0))
        
        # 3. Frame para selección de XML
        xml_frame = tk.Frame(left_frame)
        xml_frame.pack(fill=tk.X, pady=5)
        
        self.xml_button = tk.Button(
            xml_frame,
            text="3. Seleccionar carpeta con XMLs",
            command=self.select_xml_folder,
            bg='#e6e6e6'
        )
        self.xml_button.pack(fill=tk.X)
        
        self.xml_label = tk.Label(
            xml_frame,
            text="No se ha seleccionado carpeta XML",
            wraplength=400,
            justify=tk.LEFT
        )
        self.xml_label.pack(fill=tk.X, pady=(5,0))
        
        # Botón para ejecutar (en el frame derecho)
        self.run_button = tk.Button(
            right_frame,
            text="Ejecutar\ncomparación",
            command=self.run_comparison,
            height=4,
            bg='#4CAF50',  # Verde
            fg='white',
            font=('Arial', 10, 'bold')
        )
        self.run_button.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para log
        self.log_text = tk.Text(left_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
    def select_xml_folder(self):
        folder = filedialog.askdirectory(
            title="Selecciona la carpeta que contiene los archivos XML"
        )
        if folder:
            self.xml_folder = folder
            self.xml_label.config(text=f"Carpeta seleccionada: {folder}")
            self.log_message(f"Carpeta de XMLs seleccionada: {folder}")
    
    def select_mapping_file(self):
        file_types = [
            ('Archivos Excel', '*.xls;*.xlsx'),
            ('Todos los archivos', '*.*')
        ]
        file = filedialog.askopenfilename(
            title="Selecciona el archivo de mapping",
            filetypes=file_types,
            initialdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mappings')
        )
        if file:
            # Copiar el archivo a la carpeta mappings
            mappings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mappings')
            if not os.path.exists(mappings_dir):
                os.makedirs(mappings_dir)
            
            filename = os.path.basename(file)
            dest_path = os.path.join(mappings_dir, filename)
            
            import shutil
            shutil.copy2(file, dest_path)
            
            self.mapping_path = dest_path
            self.mapping_label.config(text=f"Archivo seleccionado: {filename}")
            self.log_message(f"Archivo de mapping seleccionado: {filename}")
    
    def edit_config(self):
        if sys.platform == 'win32':
            os.system(f'notepad "{self.config_path}"')
        else:
            os.system(f'xdg-open "{self.config_path}"')
        
        self.log_message("Recuerda guardar los cambios en el archivo de configuración")
    
    def update_config(self, new_values):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        for key, value in new_values.items():
            if isinstance(value, dict):
                if key not in config:
                    config[key] = {}
                config[key].update(value)
            else:
                config[key] = value
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def run_comparison(self):
        try:
            # Verificar que se haya seleccionado el archivo de mapping
            if not hasattr(self, 'mapping_path') or not self.mapping_path or not os.path.exists(self.mapping_path):
                messagebox.showerror(
                    "Error",
                    "Por favor, selecciona primero el archivo de mapping (XLS)"
                )
                return
                
            # Verificar carpeta de XMLs
            if not hasattr(self, 'xml_folder') or not self.xml_folder or not os.path.exists(self.xml_folder):
                messagebox.showerror(
                    "Error",
                    "Por favor, selecciona primero la carpeta que contiene los archivos XML"
                )
                return
            
            # Deshabilitar el botón durante la ejecución
            self.run_button.config(state='disabled', text='Ejecutando...')
            self.log_message("Iniciando comparación...")
            
            # Crear comparador
            comparator = XPathMapper(self.config_path, self.mapping_path)
            
            # Conectar a BD
            self.log_message("Conectando a la base de datos...")
            if not comparator.connect_to_db():
                self.log_message("Error conectando a la base de datos")
                messagebox.showerror(
                    "Error",
                    "Error al conectar con la base de datos. Verifica las credenciales en el archivo de configuración."
                )
                return
            
            # Procesar los XMLs
            self.log_message(f"Procesando archivos XML en: {self.xml_folder}")
            report_path = comparator.compare_xml_with_db(self.xml_folder)
            
            # Cerrar conexión
            comparator.close_db_connection()
            
            if report_path and os.path.exists(report_path):
                self.log_message(f"¡Comparación completada! Reporte generado en: {report_path}")
                
                # Preguntar si desea abrir el reporte
                response = messagebox.askyesno(
                    "Éxito",
                    f"La comparación ha finalizado exitosamente.\n\n"
                    f"El reporte se encuentra en:\n{report_path}\n\n"
                    f"¿Deseas abrir el reporte ahora?"
                )
                
                if response:
                    try:
                        if sys.platform == 'win32':
                            os.startfile(report_path)
                        else:
                            os.system(f'xdg-open "{report_path}"')
                    except Exception as e:
                        self.log_message(f"Error al abrir el reporte: {str(e)}")
                        
            else:
                self.log_message("Error durante la comparación")
                messagebox.showerror(
                    "Error",
                    "Ha ocurrido un error durante la comparación.\nPor favor, revisa los logs para más detalles."
                )
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error durante la ejecución: {str(e)}")
        finally:
            # Rehabilitar el botón
            self.run_button.config(state='normal', text='Ejecutar\ncomparación')

def main():
    try:
        # Crear la ventana principal
        root = tk.Tk()
        
        # Configuraciones adicionales para asegurar que se muestre
        root.withdraw()  # Ocultar temporalmente
        
        # Crear la aplicación
        app = ComparadorXMLGUI(root)
        
        # Mostrar la ventana
        root.deiconify()
        root.lift()
        root.attributes('-topmost', True)  # Traer al frente
        root.after_idle(lambda: root.attributes('-topmost', False))  # Quitar topmost después
        
        # Iniciar el loop principal
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
