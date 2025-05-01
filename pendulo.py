import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.colors as mcolors
from PIL import Image, ImageTk
import webbrowser

class PendulumSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("🌀 Simulador Avanzado de Péndulo con Amortiguamiento")
        
        # Configuración de tamaño adaptable con tema oscuro
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)
        self.root.geometry(f"{window_width}x{window_height}+{int((screen_width-window_width)/2)}+{int((screen_height-window_height)/2)}")
        self.root.minsize(1000, 700)
        
        # Estilo moderno
        self.setup_styles()
        self.root.configure(bg='#2e2e2e')
        
        # Icono de la aplicación
        try:
            self.root.iconbitmap('pendulum_icon.ico')  # Puedes crear o descargar un icono apropiado
        except:
            pass
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Parámetros iniciales
        self.g = 9.81
        self.L = 1.0
        self.m = 1.0
        self.b = 0.1
        self.theta0 = np.pi/4
        self.omega0 = 0.0
        self.t_max = 10.0
        self.dt = 0.02
        self.is_running = False
        self.ani = None
        self.pendulum_color = '#FF6B6B'
        self.trace_color = '#4ECDC4'
        self.angle_line_color = '#45B7D1'
        self.kinetic_color = '#FF9E44'
        self.potential_color = '#1AA7EC'
        self.total_color = '#6A0572'
        self.bg_color = '#2e2e2e'
        self.text_color = '#ffffff'
        self.accent_color = '#3a7bf7'
        
        # Inicializar arrays de simulación
        self.t = np.array([])
        self.theta = np.array([])
        self.omega = np.array([])
        self.x = np.array([])
        self.y = np.array([])
        self.kinetic = np.array([])
        self.potential = np.array([])
        self.total_energy = np.array([])
        
        self.setup_ui()
        
    def setup_styles(self):
        """Configura estilos modernos para la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('.', background='#2e2e2e', foreground='#ffffff')
        style.configure('TFrame', background='#2e2e2e')
        style.configure('TLabel', background='#2e2e2e', foreground='#ffffff', font=('Segoe UI', 10))
        style.configure('TButton', background='#3a7bf7', foreground='#ffffff', 
                       font=('Segoe UI', 10, 'bold'), borderwidth=1)
        style.map('TButton', background=[('active', '#2a5bc0')])
        style.configure('TScale', background='#2e2e2e')
        style.configure('TCombobox', fieldbackground='#3e3e3e', foreground='#ffffff')
        style.configure('TLabelFrame', background='#3e3e3e', foreground='#ffffff', 
                        font=('Segoe UI', 10, 'bold'))
        style.configure('TNotebook', background='#2e2e2e')
        style.configure('TNotebook.Tab', background='#3e3e3e', foreground='#ffffff', 
                       padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#3a7bf7')])
        
    def setup_ui(self):
        # Frame principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de simulación
        sim_tab = ttk.Frame(self.notebook)
        self.notebook.add(sim_tab, text='📊 Simulación')
        
        # Frame principal dentro de la pestaña
        main_frame = ttk.Frame(sim_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de controles (ahora con dos partes)
        control_container = ttk.Frame(main_frame, width=300)
        control_container.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Frame de parámetros con efecto acordeón
        param_frame = ttk.LabelFrame(control_container, text="⚙️ Parámetros del Péndulo", padding=(15, 10))
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sliders - Ángulo máximo limitado a 89° para mantener la física predecible
        self.create_slider(param_frame, "Longitud (m):", 'L', 0.1, 3.0, self.L, 0, '%.2f')
        self.create_slider(param_frame, "Masa (kg):", 'm', 0.1, 5.0, self.m, 1, '%.2f')
        self.create_slider(param_frame, "Gravedad (m/s²):", 'g', 1.0, 20.0, self.g, 2, '%.2f')
        self.create_slider(param_frame, "Ángulo inicial (°):", 'theta0', 0, 89, np.degrees(self.theta0), 3, '%.1f')
        self.create_slider(param_frame, "Amortiguamiento:", 'b', 0.0, 2.0, self.b, 4, '%.2f')
        
        # Frame de control de simulación
        control_frame = ttk.LabelFrame(control_container, text="🎮 Control de Simulación", padding=(15, 10))
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones con iconos modernos
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.start_btn = ttk.Button(btn_frame, text="▶ Iniciar Simulación", command=self.start_simulation, 
                                style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.pause_btn = ttk.Button(btn_frame, text="⏸ Pausar", command=self.pause_simulation)
        self.pause_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        btn_frame2 = ttk.Frame(control_frame)
        btn_frame2.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_btn = ttk.Button(btn_frame2, text="↻ Reiniciar", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.export_btn = ttk.Button(btn_frame2, text="💾 Exportar Datos", command=self.export_data)
        self.export_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Selector de colores con pestañas
        color_notebook = ttk.Notebook(control_container)
        color_notebook.pack(fill=tk.X, padx=5, pady=5)
        
        color_tab1 = ttk.Frame(color_notebook)
        color_tab2 = ttk.Frame(color_notebook)
        data_tab = ttk.Frame(color_notebook)  # Nueva pestaña para datos en tiempo real
        
        color_notebook.add(color_tab1, text='🎨 Colores')
        color_notebook.add(color_tab2, text='⚡ Energías')
        color_notebook.add(data_tab, text='📊 Datos Reales')  # Añadimos la nueva pestaña
        
        # Configuración de colores principales
        color_frame = ttk.LabelFrame(color_tab1, text="Personalización Visual", padding=(10, 5))
        color_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(color_frame, text="Color del péndulo:").grid(row=0, column=0, sticky='w', pady=2)
        self.color_pendulum = ttk.Combobox(color_frame, values=list(mcolors.CSS4_COLORS.keys()))
        self.color_pendulum.set(self.pendulum_color)
        self.color_pendulum.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.color_pendulum.bind('<<ComboboxSelected>>', self.update_colors)
        
        ttk.Label(color_frame, text="Color de rastro:").grid(row=1, column=0, sticky='w', pady=2)
        self.color_trace = ttk.Combobox(color_frame, values=list(mcolors.CSS4_COLORS.keys()))
        self.color_trace.set(self.trace_color)
        self.color_trace.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.color_trace.bind('<<ComboboxSelected>>', self.update_colors)
        
        ttk.Label(color_frame, text="Color de ángulo:").grid(row=2, column=0, sticky='w', pady=2)
        self.color_angle = ttk.Combobox(color_frame, values=list(mcolors.CSS4_COLORS.keys()))
        self.color_angle.set(self.angle_line_color)
        self.color_angle.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.color_angle.bind('<<ComboboxSelected>>', self.update_colors)
        
        # Configuración de colores de energía
        energy_frame = ttk.LabelFrame(color_tab2, text="Colores de Energía", padding=(10, 5))
        energy_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(energy_frame, text="Energía cinética:").grid(row=0, column=0, sticky='w', pady=2)
        self.color_kinetic = ttk.Combobox(energy_frame, values=list(mcolors.CSS4_COLORS.keys()))
        self.color_kinetic.set(self.kinetic_color)
        self.color_kinetic.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.color_kinetic.bind('<<ComboboxSelected>>', self.update_colors)
        
        ttk.Label(energy_frame, text="Energía potencial:").grid(row=1, column=0, sticky='w', pady=2)
        self.color_potential = ttk.Combobox(energy_frame, values=list(mcolors.CSS4_COLORS.keys()))
        self.color_potential.set(self.potential_color)
        self.color_potential.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.color_potential.bind('<<ComboboxSelected>>', self.update_colors)
        
        ttk.Label(energy_frame, text="Energía total:").grid(row=2, column=0, sticky='w', pady=2)
        self.color_total = ttk.Combobox(energy_frame, values=list(mcolors.CSS4_COLORS.keys()))
        self.color_total.set(self.total_color)
        self.color_total.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.color_total.bind('<<ComboboxSelected>>', self.update_colors)
        
        # Frame para datos en tiempo real en la nueva pestaña
        data_frame = ttk.LabelFrame(data_tab, text="📊 Datos en Tiempo Real", padding=(10, 5))
        data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Etiquetas para mostrar los datos con estilo mejorado
        data_style = ttk.Style()
        data_style.configure('Data.TLabel', background='#3e3e3e', foreground='#ffffff', 
                        font=('Segoe UI', 9), padding=5, relief='solid', borderwidth=1)
        
        self.pendulum_data_label = ttk.Label(data_frame, text="⏲ Péndulo:\n\nÁngulo: 0.0°\nVelocidad: 0.0 rad/s\nAceleración: 0.0 rad/s²", 
                                            justify=tk.LEFT, style='Data.TLabel')
        self.pendulum_data_label.pack(fill=tk.X, padx=5, pady=5)
        
        self.energy_data_label = ttk.Label(data_frame, text="⚡ Energías:\n\nCinética: 0.0 J\nPotencial: 0.0 J\nTotal: 0.0 J\nConservación: 100.0%", 
                                        justify=tk.LEFT, style='Data.TLabel')
        self.energy_data_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame de gráficos
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar figura con tema oscuro
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(10, 6), facecolor='#2e2e2e', edgecolor='#3a7bf7')
        gs = self.fig.add_gridspec(2, 2, width_ratios=[1, 1.5], height_ratios=[3, 1])
        
        # Gráfico del péndulo
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax1.set_facecolor('#3e3e3e')
        self.ax1.set_xlim(-1.2, 1.2)
        self.ax1.set_ylim(-1.2, 1.2)
        self.ax1.set_aspect('equal')
        self.ax1.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax1.set_title('Simulación del Péndulo', pad=20, color=self.text_color, fontweight='bold')
        
        # Dibujar el punto de anclaje
        self.ax1.plot(0, 0, 'o', markersize=8, color='#ffffff')
        
        self.line, = self.ax1.plot([], [], '-', lw=2, color=self.pendulum_color)
        self.mass = self.ax1.plot([], [], 'o', markersize=15, color=self.pendulum_color)[0]
        self.trace, = self.ax1.plot([], [], '-', lw=1, alpha=0.5, color=self.trace_color)
        self.trace_x = []
        self.trace_y = []
        
        # Gráfico del ángulo vs tiempo
        self.ax2 = self.fig.add_subplot(gs[:, 1])
        self.ax2.set_facecolor('#3e3e3e')
        self.ax2.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax2.set_title('Ángulo vs Tiempo', pad=15, color=self.text_color, fontweight='bold')
        self.ax2.set_xlabel('Tiempo (s)', fontsize=10, color=self.text_color)
        self.ax2.set_ylabel('Ángulo (°)', fontsize=10, color=self.text_color)
        self.ax2.set_xlim(0, self.t_max)
        self.ax2.set_ylim(-90, 90)
        self.angle_line, = self.ax2.plot([], [], '-', lw=2, color=self.angle_line_color)
        
        # Gráfico de energía
        self.ax3 = self.fig.add_subplot(gs[1, 0])
        self.ax3.set_facecolor('#3e3e3e')
        self.ax3.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax3.set_title('Energía del Sistema', pad=15, color=self.text_color, fontweight='bold')
        self.ax3.set_xlabel('Tiempo (s)', fontsize=10, color=self.text_color)
        self.ax3.set_ylabel('Energía (J)', fontsize=10, color=self.text_color)
        self.ax3.set_xlim(0, self.t_max)
        
        self.kinetic_line, = self.ax3.plot([], [], '-', lw=1.5, color=self.kinetic_color, label='Energía Cinética')
        self.potential_line, = self.ax3.plot([], [], '-', lw=1.5, color=self.potential_color, label='Energía Potencial')
        self.total_line, = self.ax3.plot([], [], '-', lw=2, color=self.total_color, label='Energía Total')
        
        # Leyenda fuera del gráfico
        self.ax3.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., 
                        facecolor='#3e3e3e', edgecolor='none', labelcolor=self.text_color)
        
        # Añadir texto de licencia y autor en el pie de página
        self.fig.text(0.5, 0.01, "© 2025 Simulador de Péndulo | GPL-3.0 License | @diegodebian2025 | profediegoparra01@gmail.com", 
                    ha='center', va='bottom', fontsize=8, color='#AAAAAA')
        
        self.fig.tight_layout(pad=3.0, rect=[0, 0.03, 1, 0.95])
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de información/ayuda
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text='ℹ️ Información')
        
        # Contenido de la pestaña de información
        self.setup_info_tab(info_tab)
        
    def setup_info_tab(self, parent):
        """Configura la pestaña de información/ayuda"""
        # Frame de desplazamiento
        canvas = tk.Canvas(parent, bg='#2e2e2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido informativo
        title_style = {'font': ('Segoe UI', 14, 'bold'), 'fg': self.accent_color, 'bg': '#2e2e2e'}
        text_style = {'font': ('Segoe UI', 10), 'fg': self.text_color, 'bg': '#2e2e2e', 'wraplength': 650, 'justify': 'left'}
        link_style = {'font': ('Segoe UI', 10, 'underline'), 'fg': '#3a7bf7', 'bg': '#2e2e2e', 'cursor': 'hand2'}
        
        # Logo o título
        logo_label = tk.Label(scrollable_frame, text="🌀 Simulador Avanzado de Péndulo", **title_style)
        logo_label.pack(pady=(10, 20))
        
        # Descripción
        desc_text = """
        Esta aplicación simula el movimiento de un péndulo simple con amortiguamiento, mostrando 
        visualizaciones en tiempo real del movimiento, ángulo y energías del sistema.
        
        Puedes ajustar todos los parámetros físicos y personalizar los colores de la visualización.
        """
        desc_label = tk.Label(scrollable_frame, text=desc_text, **text_style)
        desc_label.pack(pady=(0, 20), padx=20)
        
        # Características
        features = [
            "✔ Simulación física precisa del péndulo con amortiguamiento",
            "✔ Visualización en tiempo real del movimiento",
            "✔ Gráficos de ángulo vs tiempo y energías del sistema",
            "✔ Ajuste interactivo de parámetros físicos",
            "✔ Personalización completa de colores",
            "✔ Exportación de datos para análisis posterior"
        ]
        
        for feature in features:
            tk.Label(scrollable_frame, text=feature, **text_style).pack(anchor='w', pady=2, padx=20)
        
        # Separador
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=20, padx=20)
        
        # Instrucciones
        tk.Label(scrollable_frame, text="📌 Instrucciones de Uso", **title_style).pack(pady=(0, 10))
        
        instructions = [
            "1. Ajusta los parámetros del péndulo usando los controles deslizantes",
            "2. Presiona 'Iniciar Simulación' para comenzar la animación",
            "3. Usa 'Pausar' y 'Reiniciar' según necesites",
            "4. Personaliza los colores en la pestaña de configuración",
            "5. Exporta los datos para análisis externo si lo deseas"
        ]
        
        for instruction in instructions:
            tk.Label(scrollable_frame, text=instruction, **text_style).pack(anchor='w', pady=2, padx=20)
        
        # Separador
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=20, padx=20)
        
        # Créditos
        tk.Label(scrollable_frame, text="👨‍💻 Créditos y Licencia", **title_style).pack(pady=(0, 10))
        
        credit_text = """
        Desarrollado por Diego Parra (@diegodebian2025)
        
        Este software se distribuye bajo licencia GPL-3.0. 
        El código fuente está disponible para su modificación y distribución.
        """
        credit_label = tk.Label(scrollable_frame, text=credit_text, **text_style)
        credit_label.pack(pady=(0, 10), padx=20)
        
        # Enlace al repositorio (simulado)
        repo_link = tk.Label(scrollable_frame, text="🔗 Visitar repositorio en GitHub", **link_style)
        repo_link.pack(pady=(0, 20))
        repo_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/diegodebian/pendulum-simulator"))
        
        # Contacto
        contact_text = "📧 Contacto: profediegoparra01@gmail.com"
        contact_label = tk.Label(scrollable_frame, text=contact_text, **text_style)
        contact_label.pack(pady=(0, 20), padx=20)
        
    def create_slider(self, frame, label, param, from_, to, value, row, fmt):
        """Crea un control deslizante con estilo mejorado"""
        slider_frame = ttk.Frame(frame)
        slider_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=(5, 10))
        
        # Etiqueta del parámetro
        ttk.Label(slider_frame, text=label, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Control deslizante
        slider = ttk.Scale(slider_frame, from_=from_, to=to, value=value, 
                          command=lambda v, p=param: self.update_param(p, float(v)))
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Valor numérico
        value_label = ttk.Label(slider_frame, text=fmt % value, width=6, 
                               font=('Segoe UI', 9, 'bold'), anchor='e')
        value_label.pack(side=tk.LEFT)
        
        setattr(self, f"{param}_slider", slider)
        setattr(self, f"{param}_value", value_label)
    
    def update_param(self, param, value):
        if param == 'theta0':
            # Limitar el ángulo máximo a 89° para mantener la física predecible
            value = min(value, 89)
            value = max(value, 0)
            value_rad = np.radians(value)
            self.theta0_value.config(text=f"{value:.1f}")
            setattr(self, param, value_rad)
        elif param == 'L':
            self.L_value.config(text=f"{value:.2f}")
            self.ax1.set_xlim(-value*1.2, value*1.2)
            self.ax1.set_ylim(-value*1.2, value*1.2)
            setattr(self, param, value)
        elif param == 'g':
            self.g_value.config(text=f"{value:.2f}")
            setattr(self, param, value)
        elif param == 'm':
            self.m_value.config(text=f"{value:.2f}")
            setattr(self, param, value)
        elif param == 'b':
            self.b_value.config(text=f"{value:.2f}")
            setattr(self, param, value)
    
    def update_colors(self, event=None):
        """Actualiza los colores de los elementos gráficos"""
        self.pendulum_color = self.color_pendulum.get()
        self.trace_color = self.color_trace.get()
        self.angle_line_color = self.color_angle.get()
        self.kinetic_color = self.color_kinetic.get()
        self.potential_color = self.color_potential.get()
        self.total_color = self.color_total.get()
        
        # Actualizar elementos gráficos
        self.line.set_color(self.pendulum_color)
        self.mass.set_color(self.pendulum_color)
        self.trace.set_color(self.trace_color)
        self.angle_line.set_color(self.angle_line_color)
        self.kinetic_line.set_color(self.kinetic_color)
        self.potential_line.set_color(self.potential_color)
        self.total_line.set_color(self.total_color)
        
        self.canvas.draw()
    
    def pendulum_eq(self, y, t, L, g, b):
        theta, omega = y
        dydt = [omega, -(g/L) * np.sin(theta) - b*omega]
        return dydt
    
    def solve_pendulum(self):
        """Resuelve las ecuaciones diferenciales del péndulo"""
        self.t = np.arange(0, self.t_max, self.dt)
        y0 = [self.theta0, self.omega0]
        sol = odeint(self.pendulum_eq, y0, self.t, args=(self.L, self.g, self.b))
        self.theta = sol[:, 0]
        self.omega = sol[:, 1]
        self.x = self.L * np.sin(self.theta)
        self.y = -self.L * np.cos(self.theta)
        
        # Calcular aceleración angular (nuevo)
        self.alpha = np.gradient(self.omega, self.t)
        
        # Calcular energías
        self.kinetic = 0.5 * self.m * (self.L * self.omega)**2
        self.potential = self.m * self.g * self.L * (1 - np.cos(self.theta))
        self.total_energy = self.kinetic + self.potential
        
        if len(self.total_energy) > 0:
            energy_deviation = 100 * (np.max(self.total_energy) - np.min(self.total_energy)) / np.mean(self.total_energy)
            print(f"Desviación de energía: {energy_deviation:.4f}% (Con amortiguamiento: {self.b:.2f})")
        
        self.trace_x = []
        self.trace_y = []
    
    def init_animation(self):
        """Inicializa la animación"""
        self.line.set_data([], [])
        self.mass.set_data([], [])
        self.trace.set_data([], [])
        self.angle_line.set_data([], [])
        self.kinetic_line.set_data([], [])
        self.potential_line.set_data([], [])
        self.total_line.set_data([], [])
        
        # Actualizar datos en los labels
        self.pendulum_data_label.config(text="⏲ Péndulo:\n\nÁngulo: 0.0°\nVelocidad: 0.0 rad/s\nAceleración: 0.0 rad/s²")
        self.energy_data_label.config(text="⚡ Energías:\n\nCinética: 0.0 J\nPotencial: 0.0 J\nTotal: 0.0 J\nConservación: 100.0%")
        
        return (self.line, self.mass, self.trace, self.angle_line, 
                self.kinetic_line, self.potential_line, self.total_line)
    
    def animate(self, i):
        """Actualiza la animación en cada frame"""
        if i >= len(self.t) or len(self.x) == 0 or len(self.y) == 0:
            return (self.line, self.mass, self.trace, self.angle_line, 
                    self.kinetic_line, self.potential_line, self.total_line)
        
        # Actualizar péndulo
        self.line.set_data([0, self.x[i]], [0, self.y[i]])
        self.mass.set_data([self.x[i]], [self.y[i]])
        
        # Actualizar rastro
        self.trace_x.append(self.x[i])
        self.trace_y.append(self.y[i])
        if len(self.trace_x) > 50:
            self.trace_x.pop(0)
            self.trace_y.pop(0)
        self.trace.set_data(self.trace_x, self.trace_y)
        
        # Actualizar gráficos
        self.angle_line.set_data(self.t[:i+1], np.degrees(self.theta[:i+1]))
        
        # Actualizar gráfico de energía
        self.kinetic_line.set_data(self.t[:i+1], self.kinetic[:i+1])
        self.potential_line.set_data(self.t[:i+1], self.potential[:i+1])
        self.total_line.set_data(self.t[:i+1], self.total_energy[:i+1])
        
        # Ajustar límites de energía dinámicamente
        if i > 0:
            max_energy = max(np.max(self.kinetic[:i+1]), np.max(self.potential[:i+1]), np.max(self.total_energy[:i+1]))
            min_energy = min(np.min(self.kinetic[:i+1]), np.min(self.potential[:i+1]), np.min(self.total_energy[:i+1]))
            self.ax3.set_ylim(min_energy - 0.3, max_energy + 0.3)
        
        # Calcular conservación de energía (nuevo)
        if i > 0:
            initial_energy = self.total_energy[0]
            current_energy = self.total_energy[i]
            conservation = 100 * (1 - abs(initial_energy - current_energy) / initial_energy)
        else:
            conservation = 100.0
        
        # Actualizar datos en los labels
        self.pendulum_data_label.config(
            text=f"⏲ Péndulo:\n\nÁngulo: {np.degrees(self.theta[i]):.1f}°\nVelocidad: {self.omega[i]:.2f} rad/s\nAceleración: {self.alpha[i]:.2f} rad/s²"
        )
        self.energy_data_label.config(
            text=f"⚡ Energías:\n\nCinética: {self.kinetic[i]:.3f} J\nPotencial: {self.potential[i]:.3f} J\nTotal: {self.total_energy[i]:.3f} J\nConservación: {conservation:.1f}%"
        )
        
        return (self.line, self.mass, self.trace, self.angle_line, 
                self.kinetic_line, self.potential_line, self.total_line)
    
    def start_simulation(self):
        """Inicia la simulación"""
        if not self.is_running:
            self.solve_pendulum()
            self.ani = FuncAnimation(
                self.fig, self.animate, frames=len(self.t),
                init_func=self.init_animation, blit=True, interval=self.dt*1000,
                cache_frame_data=False
            )
            self.is_running = True
            self.canvas.draw()
    
    def pause_simulation(self):
        """Pausa la simulación"""
        if self.is_running and self.ani:
            self.ani.event_source.stop()
            self.is_running = False
    
    def reset_simulation(self):
        """Reinicia la simulación"""
        if self.ani:
            self.ani.event_source.stop()
            self.is_running = False
        self.init_animation()
        self.canvas.draw()
    
    def export_data(self):
        """Exporta los datos de la simulación a un archivo CSV"""
        try:
            if len(self.t) == 0:
                messagebox.showwarning("Advertencia", "No hay datos para exportar. Ejecuta la simulación primero.")
                return
                
            import csv
            from datetime import datetime
            
            filename = f"pendulum_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Tiempo (s)', 'Ángulo (rad)', 'Velocidad (rad/s)', 
                               'Posición X (m)', 'Posición Y (m)', 
                               'Energía Cinética (J)', 'Energía Potencial (J)', 'Energía Total (J)'])
                
                for i in range(len(self.t)):
                    writer.writerow([
                        self.t[i], self.theta[i], self.omega[i],
                        self.x[i], self.y[i],
                        self.kinetic[i], self.potential[i], self.total_energy[i]
                    ])
            
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar los datos:\n{str(e)}")
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres cerrar la aplicación?"):
            if self.ani:
                self.ani.event_source.stop()
            plt.close('all')
            self.root.destroy()
    
    def cleanup(self):
        """Limpia los recursos"""
        if hasattr(self, 'ani') and self.ani:
            self.ani.event_source.stop()
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'fig'):
            plt.close(self.fig)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Mostrar splash screen mientras se carga
    splash = tk.Toplevel(root)
    splash.title("Cargando Simulador de Péndulo")
    splash.geometry("400x200+500+300")
    splash.overrideredirect(True)
    
    # Contenido del splash
    splash_bg = '#2e2e2e'
    splash.configure(bg=splash_bg)
    
    tk.Label(splash, text="🌀", font=('Arial', 40), bg=splash_bg, fg='#3a7bf7').pack(pady=(20, 0))
    tk.Label(splash, text="Simulador de Péndulo", font=('Segoe UI', 16, 'bold'), 
            bg=splash_bg, fg='#ffffff').pack(pady=(10, 0))
    tk.Label(splash, text="Cargando...", font=('Segoe UI', 10), 
            bg=splash_bg, fg='#aaaaaa').pack(pady=(20, 0))
    
    progress = ttk.Progressbar(splash, orient='horizontal', mode='indeterminate', length=300)
    progress.pack(pady=(20, 0))
    progress.start()
    
    root.withdraw()
    splash.update()
    
    # Crear la aplicación
    app = PendulumSimulator(root)
    
    # Cerrar splash y mostrar ventana principal
    splash.destroy()
    root.deiconify()
    
    try:
        root.mainloop()
    finally:
        app.cleanup()