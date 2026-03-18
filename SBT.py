import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import os # Añade esto al inicio del archivo
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  # Requiere: pip install Pillow

class AppHiltiSBT:
    def __init__(self, root):
        self.root = root
        self.root.title("Ingeniería de Fachadas - Verificación Hilti S-BT")
        self.root.geometry("1300x850")
        self.root.configure(bg="#f4f6f8")

        # --- Base de Datos (Tabla 3.2.2 Design Resistance) ---
        self.data_hilti = {
            "Acero S235/A36": {
                "Pilot hole (tII >= 6mm)": (2.5, 3.6, 9.8),
                "Drill through (3mm <= tII < 5mm)": (1.4, 2.1, 9.8)
            },
            "Acero S355/Gr 50": {
                "Pilot hole (tII >= 6mm)": (3.2, 4.5, 9.8),
                "Drill through (3mm <= tII < 5mm)": (1.8, 2.7, 9.8)
            },
            "Aluminio (Rm >= 270 N/mm2)": {
                "Pilot hole (tII >= 6mm)": (1.4, 2.1, 6.7)
            }
        }

        # Variables de control
        self.mat_var = tk.StringVar(value="Acero S235/A36")
        self.hole_var = tk.StringVar(value="Pilot hole (tII >= 6mm)")
        self.nsd = tk.DoubleVar(value=0.5)
        self.vsd = tk.DoubleVar(value=0.8)
        self.msd = tk.DoubleVar(value=1.0)
        
        self.nrd = tk.DoubleVar()
        self.vrd = tk.DoubleVar()
        self.mrd = tk.DoubleVar()

        self.setup_ui()
        self.on_material_change() # Inicializa combos y parámetros

    def setup_ui(self):
        # Panel Izquierdo: Inputs
        sidebar = tk.Frame(self.root, width=350, bg="#1a3a5c", padx=20, pady=20)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="CONFIGURACIÓN TÉCNICA", fg="white", bg="#1a3a5c", font=("Arial", 11, "bold")).pack(pady=(0, 15))
        
        tk.Label(sidebar, text="Base Material:", fg="white", bg="#1a3a5c").pack(anchor="w")
        self.cb_mat = ttk.Combobox(sidebar, textvariable=self.mat_var, values=list(self.data_hilti.keys()), state="readonly")
        self.cb_mat.pack(fill="x", pady=5)
        self.cb_mat.bind("<<ComboboxSelected>>", self.on_material_change)

        tk.Label(sidebar, text="Drill Hole Type / Thickness:", fg="white", bg="#1a3a5c").pack(anchor="w")
        self.cb_hole = ttk.Combobox(sidebar, textvariable=self.hole_var, state="readonly")
        self.cb_hole.pack(fill="x", pady=5)
        self.cb_hole.bind("<<ComboboxSelected>>", lambda e: self.actualizar_parametros())

        # Parámetros Resistentes (Bloqueados)
        tk.Label(sidebar, text="DESIGN RESISTANCE (Rd)", fg="#aab7b8", bg="#1a3a5c", font=("Arial", 9, "italic")).pack(pady=(20, 5))
        self.crear_label_dato(sidebar, "NRd [kN]:", self.nrd)
        self.crear_label_dato(sidebar, "VRd [kN]:", self.vrd)
        self.crear_label_dato(sidebar, "MRd [Nm]:", self.mrd)

        # Cargas de Diseño (Usuario)
        tk.Label(sidebar, text="LOADS (Solicitaciones)", fg="white", bg="#1a3a5c", font=("Arial", 11, "bold")).pack(pady=(25, 10))
        self.crear_input(sidebar, "N_sd (Tensión) [kN]:", self.nsd)
        self.crear_input(sidebar, "V_sd (Corte) [kN]:", self.vsd)
        self.crear_input(sidebar, "M_sd (Momento) [Nm]:", self.msd)

        tk.Button(sidebar, text="EJECUTAR VERIFICACIÓN", command=self.graficar, 
                  bg="#d52b1e", fg="white", font=("Arial", 10, "bold"), pady=12, cursor="hand2").pack(fill="x", pady=30)

        # Panel Derecho: Gráficos e Imágenes
        self.main_area = tk.Frame(self.root, bg="#ecf0f1")
        self.main_area.pack(side="right", fill="both", expand=True)



        # Espacio para imágenes (Carga de F.png con ruta absoluta)
        self.img_frame = tk.Frame(self.main_area, bg="#d6dbdf", height=220)
        self.img_frame.pack(fill="x", padx=15, pady=15)
        self.img_frame.pack_propagate(False)

        try:
            # Obtiene la ruta absoluta de la carpeta donde está este script
            directorio_script = os.path.dirname(os.path.abspath(__file__))
            ruta_imagen = os.path.join(directorio_script, "F.png")
            
            img_fp = Image.open(ruta_imagen)
            
            # Redimensionar dinámicamente manteniendo aspecto
            ratio = 200 / img_fp.size[1]
            new_size = (int(img_fp.size[0] * ratio), 200)
            img_res = img_fp.resize(new_size, Image.Resampling.LANCZOS)
            self.photo_f = ImageTk.PhotoImage(img_res)
            
            tk.Label(self.img_frame, image=self.photo_f, bg="#d6dbdf").pack(expand=True)
            
        except Exception as e:
            tk.Label(self.img_frame, text=f"Error: {e}\nRuta intentada: {ruta_imagen}", 
                     bg="#d6dbdf", fg="#c0392b", font=("Arial", 8)).place(relx=0.5, rely=0.5, anchor="center")


        # Gráficos
        self.fig, self.axs = plt.subplots(1, 3, figsize=(15, 5))
        self.fig.patch.set_facecolor('#ecf0f1')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_area)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=10)

    def crear_label_dato(self, p, l, v):
        f = tk.Frame(p, bg="#1a3a5c")
        f.pack(fill="x", pady=2)
        tk.Label(f, text=l, fg="white", bg="#1a3a5c", width=12, anchor="w").pack(side="left")
        tk.Entry(f, textvariable=v, state="readonly", readonlybackground="#1a3a5c", 
                 fg="#2ecc71", font=("Arial", 10, "bold"), borderwidth=0).pack(side="left", fill="x")

    def crear_input(self, p, l, v):
        tk.Label(p, text=l, fg="white", bg="#1a3a5c").pack(anchor="w")
        tk.Entry(p, textvariable=v, font=("Arial", 10)).pack(fill="x", pady=(0, 8))

    def on_material_change(self, event=None):
        opciones = list(self.data_hilti[self.mat_var.get()].keys())
        self.cb_hole['values'] = opciones
        self.hole_var.set(opciones[0])
        self.actualizar_parametros()

    def actualizar_parametros(self):
        mat = self.mat_var.get()
        hole = self.hole_var.get()
        res = self.data_hilti[mat][hole]
        self.nrd.set(res[0])
        self.vrd.set(res[1])
        self.mrd.set(res[2])
        self.graficar()

    def graficar(self):
        try:
            nr, vr, mr = self.nrd.get(), self.vrd.get(), self.mrd.get()
            ns, vs, ms = self.nsd.get(), self.vsd.get(), self.msd.get()
            
            # Datos para gráficos: (Título, Solicitación X, Solicitación Y, Resistencia X, Resistencia Y, Label X, Label Y)
            plots = [
                ("Interacción N - V", vs, ns, vr, nr, "V [kN]", "N [kN]"),
                ("Interacción V - M", ms, vs, mr, vr, "M [Nm]", "V [kN]"),
                ("Interacción N - M", ms, ns, mr, nr, "M [Nm]", "N [kN]")
            ]

            for i, (titulo, sx, sy, rx, ry, lx, ly) in enumerate(plots):
                ax = self.axs[i]
                ax.clear()
                
                # Dibujar línea de interacción lineal (X/Rx + Y/Ry = 1)
                x_vals = np.linspace(0, rx, 100)
                y_lim = ry * (1 - x_vals/rx)
                
                ax.fill_between(x_vals, 0, y_lim, color='#d5f5e3', alpha=0.5, label='Seguro')
                ax.plot(x_vals, y_lim, color='#27ae60', lw=2)
                
                # Punto de solicitación
                k = (sx/rx) + (sy/ry)
                color_punto = 'red' if k > 1.0 else '#1a3a5c'
                ax.plot(sx, sy, marker='o', markersize=8, color=color_punto, label=f'Utiliz: {k:.1%}')
                
                ax.set_title(titulo, fontsize=10, fontweight='bold', color='#1a3a5c')
                ax.set_xlabel(lx); ax.set_ylabel(ly)
                ax.set_xlim(0, rx * 1.2); ax.set_ylim(0, ry * 1.2)
                ax.grid(True, linestyle=':', alpha=0.6)
                ax.legend(fontsize=8)

            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error en graficación: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppHiltiSBT(root)
    root.mainloop()