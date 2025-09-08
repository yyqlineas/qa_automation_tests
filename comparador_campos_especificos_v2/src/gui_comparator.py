import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import sys
from field_comparator import FieldComparator
from datetime import datetime
import threading

class FieldComparatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Campos Específicos BD vs XML")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.root.state('zoomed')  # Maximizar en Windows
        
        # Centrar la ventana
        self.center_window()
        
        # Variables para almacenar rutas
        self.xml_file = None
        self.config_path = None
        self.sql_path = None
        
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
        sql_path = os.path.join(base_path, 'sql')
        reportes_path = os.path.join(base_path, 'reportes')
        logs_path = os.path.join(base_path, 'logs')
        
        # Crear directorios si no existen
        for dir_path in [config_path, sql_path, reportes_path, logs_path]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Verificar config.json
        config_json = os.path.join(config_path, 'config.json')
        config_template = os.path.join(config_path, 'config.json.template')
        
        if not os.path.exists(config_json):
            if os.path.exists(config_template):
                messagebox.showwarning(
                    "Configuración necesaria",
                    "Por favor, configura la conexión a base de datos y los campos a comparar en el archivo config.json"
                )
                # Copiar el template
                import shutil
                shutil.copy2(config_template, config_json)
            else:
                messagebox.showerror(
                    "Error",
                    f"No se encuentra el archivo de configuración template en:\n{config_template}"
                )
                sys.exit(1)
                
        # Guardar las rutas para uso posterior
        self.config_path = config_json
        self.sql_path = os.path.join(sql_path, 'consulta_registros.sql')

    def create_gui(self):
        # Crear un canvas con scrollbar para manejar contenido que no cabe
        main_canvas = tk.Canvas(self.root, bg='white')
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        main_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal dentro del scrollable frame
        main_frame = tk.Frame(scrollable_frame, padx=15, pady=15, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título principal
        title_label = tk.Label(
            main_frame, 
            text="🔍 Comparador de Campos Específicos BD vs XML", 
            font=('Arial', 18, 'bold'),
            fg='#2E86AB',
            bg='white'
        )
        title_label.pack(pady=(0, 15))
        
        subtitle_label = tk.Label(
            main_frame, 
            text="Compara campos específicos entre PostgreSQL y archivos XML", 
            font=('Arial', 11),
            fg='#6C757D',
            bg='white'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Frame para layout en dos columnas
        columns_frame = tk.Frame(main_frame, bg='white')
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda - Configuración
        left_column = tk.Frame(columns_frame, bg='white')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Columna derecha - Estado y ejecución
        right_column = tk.Frame(columns_frame, bg='white')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # === COLUMNA IZQUIERDA ===
        
        # 1. Configuración de BD
        db_frame = tk.LabelFrame(
            left_column, 
            text="📊 1. Configuración de PostgreSQL", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#0D6EFD'
        )
        db_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.config_button = tk.Button(
            db_frame,
            text="✏️ Editar configuración de BD y campos",
            command=self.edit_config,
            bg='#0D6EFD',
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            height=2
        )
        self.config_button.pack(fill=tk.X, pady=(0, 5))
        
        config_info = tk.Label(
            db_frame,
            text="• Servidor PostgreSQL y credenciales\n• Campos específicos a comparar\n• XPaths correspondientes en XML",
            font=('Arial', 9),
            fg='#6C757D',
            justify=tk.LEFT,
            bg='white'
        )
        config_info.pack(fill=tk.X)
        
        # 2. Consulta SQL
        sql_frame = tk.LabelFrame(
            left_column, 
            text="🗃️ 2. Consulta SQL Personalizada", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#198754'
        )
        sql_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sql_button = tk.Button(
            sql_frame,
            text="📝 Editar consulta SQL",
            command=self.edit_sql,
            bg='#198754',
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            height=2
        )
        self.sql_button.pack(fill=tk.X, pady=(0, 5))
        
        sql_info = tk.Label(
            sql_frame,
            text="• Define qué registros comparar\n• Incluye campo identificador\n• Incluye campos a validar",
            font=('Arial', 9),
            fg='#6C757D',
            justify=tk.LEFT,
            bg='white'
        )
        sql_info.pack(fill=tk.X)
        
        # 3. Archivo XML específico
        xml_frame = tk.LabelFrame(
            left_column, 
            text="📄 3. Archivo XML para Comparar", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#FD7E14'
        )
        xml_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.xml_button = tk.Button(
            xml_frame,
            text="📁 Seleccionar archivo XML",
            command=self.select_xml_file,
            bg='#FD7E14',
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            height=2
        )
        self.xml_button.pack(fill=tk.X, pady=(0, 5))
        
        self.xml_label = tk.Label(
            xml_frame,
            text="📌 No se ha seleccionado archivo XML",
            wraplength=350,
            justify=tk.LEFT,
            font=('Arial', 9),
            fg='#6C757D',
            bg='white'
        )
        self.xml_label.pack(fill=tk.X)
        
        # === COLUMNA DERECHA ===
        
        # Estado actual
        status_frame = tk.LabelFrame(
            right_column, 
            text="📋 Estado del Sistema", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#6F42C1'
        )
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame, 
            text="🟡 Estado: Configuración requerida", 
            wraplength=350,
            justify=tk.LEFT,
            fg='#FFC107',
            font=('Arial', 10, 'bold'),
            bg='white'
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        
        # Configuración actual
        current_config_frame = tk.LabelFrame(
            right_column, 
            text="⚙️ Configuración Actual", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#6C757D'
        )
        current_config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para texto y scrollbar de configuración
        config_text_frame = tk.Frame(current_config_frame, bg='white')
        config_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.config_display = tk.Text(
            config_text_frame, 
            height=8, 
            wrap=tk.WORD,
            font=('Consolas', 8),
            bg='#F8F9FA',
            fg='#212529',
            relief=tk.FLAT,
            borderwidth=1
        )
        
        config_scrollbar = tk.Scrollbar(config_text_frame, orient="vertical", command=self.config_display.yview)
        self.config_display.configure(yscrollcommand=config_scrollbar.set)
        
        self.config_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        config_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones de configuración
        config_buttons_frame = tk.Frame(current_config_frame, bg='white')
        config_buttons_frame.pack(fill=tk.X, pady=(5,0))
        
        refresh_button = tk.Button(
            config_buttons_frame,
            text="🔄 Actualizar vista",
            command=self.update_config_display,
            font=('Arial', 8),
            bg='#E9ECEF',
            relief=tk.FLAT
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        validate_button = tk.Button(
            config_buttons_frame,
            text="✅ Validar configuración",
            command=self.validate_and_show_config,
            font=('Arial', 8),
            bg='#28A745',
            fg='white',
            relief=tk.FLAT
        )
        validate_button.pack(side=tk.LEFT)
        
        # Panel de ejecución
        execution_frame = tk.LabelFrame(
            right_column, 
            text="🚀 Ejecutar Comparación", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#DC3545'
        )
        execution_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.run_button = tk.Button(
            execution_frame,
            text="🚀 EJECUTAR COMPARACIÓN",
            command=self.run_comparison,
            bg='#DC3545',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=3,
            relief=tk.FLAT
        )
        self.run_button.pack(fill=tk.X, pady=(0, 10))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            execution_frame, 
            mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Log de ejecución - EXPANDIDO
        log_frame = tk.LabelFrame(
            main_frame, 
            text="📄 Log de Ejecución", 
            padx=12, pady=12, 
            font=('Arial', 10, 'bold'),
            fg='#495057'
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Frame para el texto y scrollbar del log
        log_text_frame = tk.Frame(log_frame, bg='white')
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_text_frame, 
            height=12, 
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#212529',
            fg='#00FF00',
            relief=tk.FLAT,
            borderwidth=1
        )
        
        log_scrollbar = tk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de control del log
        log_controls_frame = tk.Frame(log_frame, bg='white')
        log_controls_frame.pack(fill=tk.X, pady=(5,0))
        
        clear_log_button = tk.Button(
            log_controls_frame,
            text="🗑️ Limpiar log",
            command=self.clear_log,
            font=('Arial', 8),
            bg='#6C757D',
            fg='white',
            relief=tk.FLAT
        )
        clear_log_button.pack(side=tk.LEFT, padx=(0, 5))
        
        save_log_button = tk.Button(
            log_controls_frame,
            text="💾 Guardar log",
            command=self.save_log,
            font=('Arial', 8),
            bg='#17A2B8',
            fg='white',
            relief=tk.FLAT
        )
        save_log_button.pack(side=tk.LEFT)
        
        # Bind del mouse wheel para scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Inicializar vista de configuración
        self.update_config_display()
        self.log_message("💡 Sistema iniciado. Configura la conexión a PostgreSQL para comenzar.")
        self.log_message("📁 Los logs se guardan automáticamente en la carpeta 'logs' del proyecto.")
    
    def update_config_display(self):
        """Actualiza la vista de la configuración actual"""
        try:
            self.config_display.delete(1.0, tk.END)
            
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Mostrar información resumida de la configuración
                display_text = "=== CONFIGURACIÓN ACTUAL ===\n\n"
                
                # Información de BD
                db_config = config.get('database', {})
                display_text += f"� PostgreSQL:\n"
                display_text += f"   Servidor: {db_config.get('server', 'No configurado')}\n"
                display_text += f"   BD: {db_config.get('database', 'No configurado')}\n"
                display_text += f"   Usuario: {db_config.get('username', 'No configurado')}\n"
                display_text += f"   Puerto: {db_config.get('port', '5432')}\n\n"
                
                # Información de comparación
                comp_config = config.get('comparison', {})
                display_text += f"🔍 Comparación:\n"
                display_text += f"   Tabla: {comp_config.get('tabla_principal', 'No configurado')}\n"
                display_text += f"   Campo ID: {comp_config.get('campo_identificador', 'No configurado')}\n"
                display_text += f"   Campos a comparar (con XML): {', '.join(comp_config.get('campos_comparar', []))}\n"
                
                # Mostrar campos de filtro si existen
                campos_filtro = comp_config.get('campos_filtro_bd', [])
                if campos_filtro:
                    display_text += f"   Campos de filtro BD: {', '.join(campos_filtro)}\n"
                display_text += "\n"
                
                # Información de XML
                xml_config = config.get('xml', {})
                xpath_mappings = xml_config.get('xpath_mappings', {})
                display_text += f"📄 XML:\n"
                
                # El XPath ID ahora es opcional
                xpath_id = xml_config.get('identificador_xpath', '')
                if xpath_id:
                    display_text += f"   XPath ID: {xpath_id}\n"
                else:
                    display_text += f"   XPath ID: No requerido (modo comparación global)\n"
                    
                display_text += f"   Mappings configurados: {len(xpath_mappings)}\n"
                for campo, xpath in xpath_mappings.items():
                    display_text += f"     {campo}: {xpath}\n"
                
                self.config_display.insert(tk.END, display_text)
            else:
                self.config_display.insert(tk.END, "Archivo de configuración no encontrado")
                
        except Exception as e:
            self.config_display.insert(tk.END, f"Error al cargar configuración: {str(e)}")
    
    def validate_and_show_config(self):
        """Valida la configuración y muestra el resultado"""
        try:
            is_valid = self.validate_configuration()
            if is_valid:
                self.log_message("✅ Configuración válida - Lista para ejecutar")
                self.status_label.config(
                    text="🟢 Estado: Configuración válida - Listo para ejecutar",
                    fg='#28A745'
                )
                messagebox.showinfo("Validación", "✅ Configuración válida\n\nTodos los campos están correctamente configurados.")
            else:
                self.log_message("❌ Configuración inválida - Revisa los errores mostrados")
                self.status_label.config(
                    text="🔴 Estado: Configuración inválida - Revisa errores",
                    fg='#DC3545'
                )
        except Exception as e:
            self.log_message(f"❌ Error al validar configuración: {str(e)}")
            self.status_label.config(
                text="🔴 Estado: Error en validación",
                fg='#DC3545'
            )
    
    def select_xml_file(self):
        file = filedialog.askopenfilename(
            title="Selecciona el archivo XML para comparar",
            filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if file:
            self.xml_file = file
            filename = os.path.basename(file)
            self.xml_label.config(text=f"Archivo seleccionado: {filename}")
            self.log_message(f"Archivo XML seleccionado: {filename}")
            # Mostrar ruta completa en el log
            self.log_message(f"Ruta completa: {file}")
    
    def edit_config(self):
        """Abre el archivo de configuración para edición"""
        if sys.platform == 'win32':
            os.system(f'notepad "{self.config_path}"')
        else:
            os.system(f'xdg-open "{self.config_path}"')
        
        self.log_message("📝 Archivo de configuración abierto para edición")
        self.log_message("⚠️  Recuerda: Guarda los cambios y usa 'Actualizar vista' para refrescar")
        
        # Programar actualización de la vista después de un momento
        self.root.after(3000, self.update_config_display)
        
        # Actualizar estado
        self.status_label.config(
            text="🟡 Estado: Configuración en edición - Actualiza la vista después de guardar",
            fg='#FFC107'
        )
    
    def edit_sql(self):
        """Abre el archivo de consulta SQL para edición"""
        if sys.platform == 'win32':
            os.system(f'notepad "{self.sql_path}"')
        else:
            os.system(f'xdg-open "{self.sql_path}"')
        
        self.log_message("Archivo de consulta SQL abierto para edición")
    
    def clear_log(self):
        """Limpia el área de log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("📋 Log limpiado")
    
    def save_log(self):
        """Guarda el contenido del log en un archivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Guardar log como...",
                initialdir=os.path.expanduser("~")
            )
            if filename:
                # Si no tiene extensión, agregar .txt
                if not filename.endswith('.txt'):
                    filename += f"_log_comparador_{timestamp}.txt"
                    
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"💾 Log guardado en: {filename}")
        except Exception as e:
            self.log_message(f"❌ Error al guardar log: {str(e)}")
    
    def log_message(self, message):
        """Añade un mensaje al log con timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def validate_configuration(self) -> bool:
        """Valida que la configuración esté completa"""
        try:
            # Verificar que existe el archivo de configuración
            if not os.path.exists(self.config_path):
                messagebox.showerror("Error", "No se encuentra el archivo de configuración")
                return False
            
            # Cargar y validar configuración
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validar sección de base de datos
            db_config = config.get('database', {})
            required_db_fields = ['server', 'database', 'username', 'password']
            for field in required_db_fields:
                if not db_config.get(field):
                    messagebox.showerror("Error", f"Campo de PostgreSQL requerido no configurado: {field}")
                    return False
            
            # Validar sección de comparación
            comp_config = config.get('comparison', {})
            required_comp_fields = ['campos_comparar', 'tabla_principal', 'campo_identificador']
            for field in required_comp_fields:
                if not comp_config.get(field):
                    messagebox.showerror("Error", f"Campo de comparación requerido no configurado: {field}")
                    return False
            
            # Validar que hay campos para comparar (solo los que tienen XPath en XML)
            if not comp_config.get('campos_comparar') or len(comp_config['campos_comparar']) == 0:
                messagebox.showerror("Error", "No se han configurado campos para comparar")
                return False
            
            # Validar sección XML
            xml_config = config.get('xml', {})
            # El identificador_xpath ya no es requerido - ahora es opcional
            
            xpath_mappings = xml_config.get('xpath_mappings', {})
            # Solo validar XPaths para campos que realmente se van a comparar con XML
            for campo in comp_config['campos_comparar']:
                if campo not in xpath_mappings:
                    messagebox.showerror("Error", f"No se ha configurado XPath para el campo: {campo}")
                    return False
            
            # Verificar archivo XML
            if not self.xml_file or not os.path.exists(self.xml_file):
                messagebox.showerror("Error", "Por favor, selecciona un archivo XML válido")
                return False
            
            # Verificar que es un archivo XML
            if not self.xml_file.lower().endswith('.xml'):
                messagebox.showerror("Error", "El archivo seleccionado no es un archivo XML válido")
                return False
            
            return True
            
        except json.JSONDecodeError:
            messagebox.showerror("Error", "El archivo de configuración no tiene un formato JSON válido")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al validar configuración: {str(e)}")
            return False
    
    def run_comparison_thread(self):
        """Ejecuta la comparación en un hilo separado"""
        try:
            # Crear el comparador
            comparator = FieldComparator(self.config_path)
            
            # Ejecutar la comparación
            report_path = comparator.run_comparison(self.xml_file)
            
            # Actualizar UI en el hilo principal
            self.root.after(0, self.comparison_completed, report_path)
            
        except Exception as e:
            # Manejar errores en el hilo principal
            self.root.after(0, self.comparison_error, str(e))
    
    def comparison_completed(self, report_path):
        """Maneja la finalización exitosa de la comparación"""
        self.progress.stop()
        self.run_button.config(state='normal', text='🚀 Ejecutar Comparación')
        
        self.log_message(f"¡Comparación completada! Reporte generado: {os.path.basename(report_path)}")
        
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
                messagebox.showerror("Error", f"No se pudo abrir el reporte: {str(e)}")
    
    def comparison_error(self, error_message):
        """Maneja errores durante la comparación"""
        self.progress.stop()
        self.run_button.config(state='normal', text='🚀 Ejecutar Comparación')
        
        self.log_message(f"Error durante la comparación: {error_message}")
        messagebox.showerror("Error", f"Error durante la comparación:\n{error_message}")
    
    def run_comparison(self):
        """Ejecuta el proceso de comparación"""
        try:
            # Validar configuración
            if not self.validate_configuration():
                return
            
            # Deshabilitar el botón y mostrar progreso
            self.run_button.config(state='disabled', text='Ejecutando...')
            self.progress.start()
            
            self.log_message("Iniciando comparación de campos...")
            self.log_message("📋 Logs detallados se guardan automáticamente en la carpeta 'logs'")
            self.log_message("Validando configuración...")
            self.log_message("Preparando conexión a base de datos...")
            
            # Ejecutar en hilo separado para no bloquear la UI
            comparison_thread = threading.Thread(target=self.run_comparison_thread)
            comparison_thread.daemon = True
            comparison_thread.start()
            
        except Exception as e:
            self.progress.stop()
            self.run_button.config(state='normal', text='🚀 Ejecutar Comparación')
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error durante la ejecución: {str(e)}")

def main():
    try:
        # Crear la ventana principal
        root = tk.Tk()
        
        # Configuraciones adicionales para asegurar que se muestre
        root.withdraw()  # Ocultar temporalmente
        
        # Crear la aplicación
        app = FieldComparatorGUI(root)
        
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
