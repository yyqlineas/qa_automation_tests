#!/usr/bin/env python3
"""
GUI Moderna para Comparador de Campos Específicos V2
Estructura CSS-like con iconos y paneles dinámicos
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from datetime import datetime
import sys

class ModernGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Campos Específicos V2")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Variables de estado
        self.current_step = None
        self.config_data = {}
        self.selected_json_file = ""
        self.comparison_fields = ["batt_dept_id"]  # Siempre incluido
        
        # Cargar configuración
        self.load_config()
        
        # Crear la interfaz
        self.create_modern_interface()
        
    def load_config(self):
        """Cargar configuración desde archivo"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config_data = self.get_default_config()
    
    def get_default_config(self):
        """Configuración por defecto"""
        return {
            "database": {
                "driver": "PostgreSQL Unicode",
                "server": "calliope.localitymedia.com",
                "database": "stage_fdsu",
                "username": "yatary",
                "password": "",
                "port": 5432
            },
            "comparison": {
                "campos_comparar": ["psap_call_answered_at"],
                "campos_filtro_bd": ["created_at", "batt_dept_id", "dispatch_number"],
                "tabla_principal": "nfirs_notification"
            }
        }
    
    def create_modern_interface(self):
        """Crear la interfaz moderna"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Comparador de Campos Específicos V2", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Contenedor principal (sidebar + content)
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar izquierdo
        self.create_sidebar(content_frame)
        
        # Panel principal derecho
        self.create_main_panel(content_frame)
        
        # Footer con botón de ejecución
        self.create_footer(main_frame)
    
    def create_sidebar(self, parent):
        """Crear sidebar con iconos"""
        sidebar = tk.Frame(parent, bg='#34495e', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Título del sidebar
        sidebar_title = tk.Label(sidebar, text="NAVEGACIÓN", font=('Arial', 12, 'bold'), 
                                fg='white', bg='#34495e', pady=10)
        sidebar_title.pack(fill=tk.X)
        
        # Separador
        separator1 = tk.Frame(sidebar, height=2, bg='#2c3e50')
        separator1.pack(fill=tk.X, padx=10, pady=5)
        
        # ICONOS GENERALES
        general_label = tk.Label(sidebar, text="CONFIGURACIÓN GENERAL", 
                                font=('Arial', 10, 'bold'), fg='#ecf0f1', bg='#34495e')
        general_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Icono Config
        self.create_sidebar_button(sidebar, "🔧 Configuración", "config", 
                                  "Configurar credenciales y conexiones", '#3498db')
        
        # Icono Filtro
        self.create_sidebar_button(sidebar, "🔍 Filtros", "filter", 
                                  "Gestionar campos de comparación", '#e74c3c')
        
        # Separador
        separator2 = tk.Frame(sidebar, height=2, bg='#2c3e50')
        separator2.pack(fill=tk.X, padx=10, pady=10)
        
        # WORKFLOW STEPS
        workflow_label = tk.Label(sidebar, text="PASOS DEL WORKFLOW", 
                                 font=('Arial', 10, 'bold'), fg='#ecf0f1', bg='#34495e')
        workflow_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Pasos del workflow
        steps = [
            ("📁 1. Seleccionar JSON", "step1", "Elegir archivo JSON del cliente"),
            ("🔍 2. Buscar batt_dept_id", "step2", "Encontrar IDs en el JSON"),
            ("🛤️ 3. Buscar xpath", "step3", "Localizar rutas xref_id"),
            ("📄 4. Extraer xref_id", "step4", "Obtener valores del XML"),
            ("⬆️ 5. Subir SFTP", "step5", "Cargar archivos al servidor"),
            ("✅ 6. Verificar BD", "step6", "Confirmar registro en BD"),
            ("🎯 7. Filtrar registros", "step7", "Obtener datos específicos"),
            ("⚖️ 8. Comparar campos", "step8", "Ejecutar comparación final")
        ]
        
        for text, step_id, description in steps:
            self.create_sidebar_button(sidebar, text, step_id, description, '#27ae60')
    
    def create_sidebar_button(self, parent, text, step_id, description, color):
        """Crear botón del sidebar"""
        frame = tk.Frame(parent, bg='#34495e')
        frame.pack(fill=tk.X, padx=10, pady=2)
        
        button = tk.Button(frame, text=text, font=('Arial', 10), 
                          bg=color, fg='white', relief=tk.FLAT, 
                          cursor='hand2', anchor='w', padx=15, pady=8,
                          command=lambda: self.switch_view(step_id))
        button.pack(fill=tk.X)
        
        # Tooltip (descripción)
        self.create_tooltip(button, description)
    
    def create_tooltip(self, widget, text):
        """Crear tooltip para los botones"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background='#2c3e50', 
                           foreground='white', font=('Arial', 9), 
                           wraplength=200, justify='left')
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def create_main_panel(self, parent):
        """Crear panel principal derecho"""
        self.main_panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        self.main_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header del panel principal
        panel_header = tk.Frame(self.main_panel, bg='#ecf0f1', height=50)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        
        self.panel_title = tk.Label(panel_header, text="Seleccione una opción del menú", 
                                   font=('Arial', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        self.panel_title.pack(expand=True)
        
        # Contenido del panel
        self.content_frame = tk.Frame(self.main_panel, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Mostrar vista inicial
        self.show_welcome_view()
    
    def create_footer(self, parent):
        """Crear footer con botón de ejecución"""
        footer = tk.Frame(parent, bg='#34495e', height=60)
        footer.pack(fill=tk.X, pady=(10, 0))
        footer.pack_propagate(False)
        
        # Botón de ejecución
        self.execute_button = tk.Button(footer, text="▶ EJECUTAR", 
                                       font=('Arial', 12, 'bold'), 
                                       bg='#e74c3c', fg='white', 
                                       relief=tk.FLAT, cursor='hand2',
                                       padx=30, pady=10,
                                       command=self.execute_current_step)
        self.execute_button.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Estado actual
        self.status_label = tk.Label(footer, text="Listo", font=('Arial', 10), 
                                    fg='white', bg='#34495e')
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
    
    def switch_view(self, view_id):
        """Cambiar vista según el icono seleccionado"""
        self.current_step = view_id
        
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Mostrar vista correspondiente
        if view_id == "config":
            self.show_config_view()
        elif view_id == "filter":
            self.show_filter_view()
        elif view_id == "step1":
            self.show_step1_view()
        elif view_id == "step2":
            self.show_step2_view()
        elif view_id == "step3":
            self.show_step3_view()
        elif view_id == "step4":
            self.show_step4_view()
        elif view_id == "step5":
            self.show_step5_view()
        elif view_id == "step6":
            self.show_step6_view()
        elif view_id == "step7":
            self.show_step7_view()
        elif view_id == "step8":
            self.show_step8_view()
        
        # Actualizar botón de ejecución
        self.update_execute_button()
    
    def show_welcome_view(self):
        """Vista de bienvenida"""
        self.panel_title.config(text="Bienvenido al Comparador V2")
        
        welcome_text = """
        🎉 Bienvenido al Comparador de Campos Específicos V2
        
        Esta nueva versión incluye un workflow completo de 8 pasos:
        
        📋 CONFIGURACIÓN GENERAL:
        • 🔧 Configuración: Gestionar credenciales y conexiones
        • 🔍 Filtros: Administrar campos de comparación
        
        🔄 WORKFLOW COMPLETO:
        1. 📁 Seleccionar JSON del cliente
        2. 🔍 Buscar batt_dept_id en JSON
        3. 🛤️ Buscar xpath para xref_id
        4. 📄 Extraer xref_id del XML
        5. ⬆️ Subir archivos al SFTP
        6. ✅ Verificar registro en BD
        7. 🎯 Filtrar registros específicos
        8. ⚖️ Comparar campos finales
        
        👆 Seleccione una opción del menú lateral para comenzar.
        """
        
        text_widget = tk.Text(self.content_frame, font=('Arial', 11), 
                             wrap=tk.WORD, state=tk.DISABLED, 
                             bg='#f8f9fa', relief=tk.FLAT)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, welcome_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_config_view(self):
        """Vista de configuración"""
        self.panel_title.config(text="🔧 Configuración del Sistema")
        
        # Notebook para organizar configuraciones
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab Base de Datos
        db_frame = ttk.Frame(notebook)
        notebook.add(db_frame, text="Base de Datos")
        
        # Tab SFTP
        sftp_frame = ttk.Frame(notebook)
        notebook.add(sftp_frame, text="SFTP")
        
        # Configuración BD
        self.create_database_config(db_frame)
        
        # Configuración SFTP
        self.create_sftp_config(sftp_frame)
    
    def create_database_config(self, parent):
        """Crear configuración de base de datos"""
        tk.Label(parent, text="Configuración Base de Datos PostgreSQL", 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Frame para campos
        fields_frame = tk.Frame(parent)
        fields_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Campos de configuración
        db_config = self.config_data.get('database', {})
        
        self.db_entries = {}
        fields = [
            ("Servidor:", "server"),
            ("Puerto:", "port"),
            ("Base de Datos:", "database"),
            ("Usuario:", "username"),
            ("Contraseña:", "password")
        ]
        
        for i, (label, key) in enumerate(fields):
            tk.Label(fields_frame, text=label, font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', padx=5, pady=5)
            
            if key == "password":
                entry = tk.Entry(fields_frame, show="*", width=40)
            else:
                entry = tk.Entry(fields_frame, width=40)
            
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, str(db_config.get(key, "")))
            self.db_entries[key] = entry
        
        # Botón para probar conexión
        test_button = tk.Button(fields_frame, text="Probar Conexión", 
                               bg='#3498db', fg='white', relief=tk.FLAT,
                               command=self.test_database_connection)
        test_button.grid(row=len(fields), column=1, pady=20, sticky='w')
    
    def create_sftp_config(self, parent):
        """Crear configuración SFTP"""
        tk.Label(parent, text="Configuración SFTP", 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        tk.Label(parent, text="(Configuración SFTP pendiente de implementar)", 
                font=('Arial', 10), fg='gray').pack(pady=20)
    
    def show_filter_view(self):
        """Vista de filtros"""
        self.panel_title.config(text="🔍 Gestión de Filtros de Comparación")
        
        # Frame superior para campos actuales
        current_frame = tk.LabelFrame(self.content_frame, text="Campos de Comparación Actuales", 
                                     font=('Arial', 11, 'bold'))
        current_frame.pack(fill=tk.X, pady=10)
        
        # Lista de campos actuales
        self.fields_listbox = tk.Listbox(current_frame, height=6, font=('Arial', 10))
        self.fields_listbox.pack(fill=tk.X, padx=10, pady=10)
        
        # Cargar campos actuales
        self.refresh_fields_list()
        
        # Frame para agregar nuevos campos
        add_frame = tk.LabelFrame(self.content_frame, text="Agregar Nuevo Campo", 
                                 font=('Arial', 11, 'bold'))
        add_frame.pack(fill=tk.X, pady=10)
        
        # Campos para agregar
        input_frame = tk.Frame(add_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(input_frame, text="Nombre del Campo:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', padx=5, pady=5)
        self.field_name_entry = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.field_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(input_frame, text="XPath:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', padx=5, pady=5)
        self.xpath_entry = tk.Entry(input_frame, width=50, font=('Arial', 10))
        self.xpath_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Botones
        buttons_frame = tk.Frame(add_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        add_button = tk.Button(buttons_frame, text="➕ Agregar Campo", 
                              bg='#27ae60', fg='white', relief=tk.FLAT,
                              command=self.add_comparison_field)
        add_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = tk.Button(buttons_frame, text="➖ Eliminar Seleccionado", 
                                 bg='#e74c3c', fg='white', relief=tk.FLAT,
                                 command=self.remove_comparison_field)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Nota importante
        note_label = tk.Label(self.content_frame, 
                             text="⚠️ Nota: El campo 'batt_dept_id' siempre está incluido y no se puede eliminar", 
                             font=('Arial', 9), fg='#e74c3c')
        note_label.pack(pady=10)
    
    def show_step1_view(self):
        """Vista Paso 1: Seleccionar JSON"""
        self.panel_title.config(text="📁 Paso 1: Seleccionar Archivo JSON")
        
        # Recordatorio importante
        reminder_frame = tk.Frame(self.content_frame, bg='#fff3cd', relief=tk.RAISED, bd=1)
        reminder_frame.pack(fill=tk.X, pady=10)
        
        reminder_text = """
        ⚠️ RECORDATORIO IMPORTANTE:
        Asegúrese de descargar la versión más reciente del archivo JSON
        desde la tarea correspondiente en Monday.com antes de continuar.
        """
        
        tk.Label(reminder_frame, text=reminder_text, font=('Arial', 10, 'bold'), 
                bg='#fff3cd', fg='#856404', justify='left').pack(padx=15, pady=10)
        
        # Selección de archivo
        selection_frame = tk.LabelFrame(self.content_frame, text="Seleccionar Archivo JSON", 
                                       font=('Arial', 11, 'bold'))
        selection_frame.pack(fill=tk.X, pady=20)
        
        file_frame = tk.Frame(selection_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.json_file_label = tk.Label(file_frame, text="Ningún archivo seleccionado", 
                                       font=('Arial', 10), fg='gray')
        self.json_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = tk.Button(file_frame, text="📂 Examinar", 
                                 bg='#3498db', fg='white', relief=tk.FLAT,
                                 command=self.browse_json_file)
        browse_button.pack(side=tk.RIGHT, padx=10)
        
        # Vista previa del JSON
        preview_frame = tk.LabelFrame(self.content_frame, text="Vista Previa del JSON", 
                                     font=('Arial', 11, 'bold'))
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.json_preview = scrolledtext.ScrolledText(preview_frame, height=15, 
                                                     font=('Courier', 9), 
                                                     state=tk.DISABLED)
        self.json_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def show_step2_view(self):
        """Vista Paso 2: Buscar batt_dept_id"""
        self.panel_title.config(text="🔍 Paso 2: Buscar batt_dept_id en JSON")
        
        tk.Label(self.content_frame, text="Vista del Paso 2 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def show_step3_view(self):
        """Vista Paso 3: Buscar xpath"""
        self.panel_title.config(text="🛤️ Paso 3: Buscar xpath para xref_id")
        
        tk.Label(self.content_frame, text="Vista del Paso 3 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def show_step4_view(self):
        """Vista Paso 4: Extraer xref_id"""
        self.panel_title.config(text="📄 Paso 4: Extraer xref_id del XML")
        
        tk.Label(self.content_frame, text="Vista del Paso 4 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def show_step5_view(self):
        """Vista Paso 5: Subir SFTP"""
        self.panel_title.config(text="⬆️ Paso 5: Subir archivos al SFTP")
        
        tk.Label(self.content_frame, text="Vista del Paso 5 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def show_step6_view(self):
        """Vista Paso 6: Verificar BD"""
        self.panel_title.config(text="✅ Paso 6: Verificar registro en BD")
        
        tk.Label(self.content_frame, text="Vista del Paso 6 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def show_step7_view(self):
        """Vista Paso 7: Filtrar registros"""
        self.panel_title.config(text="🎯 Paso 7: Filtrar registros específicos")
        
        tk.Label(self.content_frame, text="Vista del Paso 7 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def show_step8_view(self):
        """Vista Paso 8: Comparar campos"""
        self.panel_title.config(text="⚖️ Paso 8: Comparar campos finales")
        
        tk.Label(self.content_frame, text="Vista del Paso 8 - En desarrollo", 
                font=('Arial', 14)).pack(expand=True)
    
    def refresh_fields_list(self):
        """Actualizar lista de campos"""
        self.fields_listbox.delete(0, tk.END)
        
        # Agregar batt_dept_id (siempre presente)
        self.fields_listbox.insert(tk.END, "batt_dept_id (obligatorio)")
        
        # Agregar otros campos de comparación
        for field in self.config_data.get('comparison', {}).get('campos_comparar', []):
            if field != 'batt_dept_id':
                self.fields_listbox.insert(tk.END, field)
    
    def add_comparison_field(self):
        """Agregar campo de comparación"""
        field_name = self.field_name_entry.get().strip()
        xpath = self.xpath_entry.get().strip()
        
        if not field_name or not xpath:
            messagebox.showwarning("Campos Incompletos", 
                                 "Por favor, complete tanto el nombre del campo como el XPath.")
            return
        
        # Agregar al config
        if 'comparison' not in self.config_data:
            self.config_data['comparison'] = {}
        if 'campos_comparar' not in self.config_data['comparison']:
            self.config_data['comparison']['campos_comparar'] = []
        if 'xml' not in self.config_data:
            self.config_data['xml'] = {}
        if 'xpath_mappings' not in self.config_data['xml']:
            self.config_data['xml']['xpath_mappings'] = {}
        
        # Agregar campo si no existe
        if field_name not in self.config_data['comparison']['campos_comparar']:
            self.config_data['comparison']['campos_comparar'].append(field_name)
        
        # Agregar xpath mapping
        self.config_data['xml']['xpath_mappings'][field_name] = xpath
        
        # Guardar configuración
        self.save_config()
        
        # Limpiar campos
        self.field_name_entry.delete(0, tk.END)
        self.xpath_entry.delete(0, tk.END)
        
        # Actualizar lista
        self.refresh_fields_list()
        
        messagebox.showinfo("Campo Agregado", f"Campo '{field_name}' agregado exitosamente.")
    
    def remove_comparison_field(self):
        """Eliminar campo de comparación seleccionado"""
        selection = self.fields_listbox.curselection()
        if not selection:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un campo para eliminar.")
            return
        
        selected_text = self.fields_listbox.get(selection[0])
        
        # No permitir eliminar batt_dept_id
        if "batt_dept_id" in selected_text:
            messagebox.showwarning("Campo Obligatorio", 
                                 "El campo 'batt_dept_id' es obligatorio y no se puede eliminar.")
            return
        
        field_name = selected_text.strip()
        
        # Eliminar del config
        if field_name in self.config_data.get('comparison', {}).get('campos_comparar', []):
            self.config_data['comparison']['campos_comparar'].remove(field_name)
        
        if field_name in self.config_data.get('xml', {}).get('xpath_mappings', {}):
            del self.config_data['xml']['xpath_mappings'][field_name]
        
        # Guardar configuración
        self.save_config()
        
        # Actualizar lista
        self.refresh_fields_list()
        
        messagebox.showinfo("Campo Eliminado", f"Campo '{field_name}' eliminado exitosamente.")
    
    def browse_json_file(self):
        """Examinar archivo JSON"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.selected_json_file = file_path
            self.json_file_label.config(text=os.path.basename(file_path), fg='black')
            self.load_json_preview(file_path)
    
    def load_json_preview(self, file_path):
        """Cargar vista previa del JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Mostrar preview formateado
            preview_text = json.dumps(json_data, indent=2, ensure_ascii=False)
            
            self.json_preview.config(state=tk.NORMAL)
            self.json_preview.delete(1.0, tk.END)
            self.json_preview.insert(tk.END, preview_text)
            self.json_preview.config(state=tk.DISABLED)
            
        except Exception as e:
            self.json_preview.config(state=tk.NORMAL)
            self.json_preview.delete(1.0, tk.END)
            self.json_preview.insert(tk.END, f"Error al cargar el archivo JSON:\n{str(e)}")
            self.json_preview.config(state=tk.DISABLED)
    
    def test_database_connection(self):
        """Probar conexión a la base de datos"""
        messagebox.showinfo("Prueba de Conexión", "Funcionalidad de prueba en desarrollo.")
    
    def save_config(self):
        """Guardar configuración"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {e}")
    
    def update_execute_button(self):
        """Actualizar botón de ejecución según el paso actual"""
        if not self.current_step:
            self.execute_button.config(text="▶ EJECUTAR", state=tk.DISABLED)
            return
        
        button_texts = {
            "config": "💾 GUARDAR CONFIGURACIÓN",
            "filter": "🔄 ACTUALIZAR FILTROS", 
            "step1": "📁 VALIDAR JSON",
            "step2": "🔍 BUSCAR BATT_DEPT_ID",
            "step3": "🛤️ BUSCAR XPATH",
            "step4": "📄 EXTRAER XREF_ID",
            "step5": "⬆️ SUBIR A SFTP",
            "step6": "✅ VERIFICAR BD",
            "step7": "🎯 FILTRAR REGISTROS",
            "step8": "⚖️ COMPARAR CAMPOS"
        }
        
        self.execute_button.config(text=button_texts.get(self.current_step, "▶ EJECUTAR"), 
                                  state=tk.NORMAL)
    
    def execute_current_step(self):
        """Ejecutar paso actual"""
        if not self.current_step:
            return
        
        self.status_label.config(text="Ejecutando...")
        self.root.update()
        
        try:
            if self.current_step == "config":
                self.execute_save_config()
            elif self.current_step == "filter":
                self.execute_update_filters()
            elif self.current_step == "step1":
                self.execute_step1()
            else:
                messagebox.showinfo("En Desarrollo", f"Funcionalidad del {self.current_step} en desarrollo.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando paso: {e}")
        
        finally:
            self.status_label.config(text="Listo")
    
    def execute_save_config(self):
        """Ejecutar guardado de configuración"""
        # Actualizar config con valores de BD
        for key, entry in self.db_entries.items():
            if 'database' not in self.config_data:
                self.config_data['database'] = {}
            self.config_data['database'][key] = entry.get()
        
        self.save_config()
        messagebox.showinfo("Configuración", "Configuración guardada exitosamente.")
    
    def execute_update_filters(self):
        """Ejecutar actualización de filtros"""
        messagebox.showinfo("Filtros", "Filtros actualizados. Use los botones ➕ y ➖ para gestionar campos.")
    
    def execute_step1(self):
        """Ejecutar validación de JSON"""
        if not self.selected_json_file:
            messagebox.showwarning("Archivo Requerido", "Por favor, seleccione un archivo JSON primero.")
            return
        
        try:
            with open(self.selected_json_file, 'r', encoding='utf-8') as f:
                json.load(f)  # Validar JSON
            
            messagebox.showinfo("Validación", "✅ Archivo JSON válido y listo para procesamiento.")
        
        except Exception as e:
            messagebox.showerror("JSON Inválido", f"Error en el archivo JSON:\n{e}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = ModernGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
