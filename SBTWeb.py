import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# Configuración de la página
st.set_page_config(page_title="Hilti S-BT | Verificación Estructural", layout="wide")

def main():
    st.title("🏗️ Ingeniería de Fachadas: Verificación Hilti S-BT")
    st.markdown("---")

    # --- Base de Datos (Tabla 3.2.2 Design Resistance) ---
    data_hilti = {
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

    # Sidebar: Configuración Técnica y Solicitaciones
    with st.sidebar:
        st.header("⚙️ CONFIGURACIÓN TÉCNICA")
        
        material = st.selectbox("Base Material:", list(data_hilti.keys()))
        hole_type = st.selectbox("Drill Hole Type / Thickness:", list(data_hilti[material].keys()))
        
        # Obtener resistencias de diseño (Rd) correspondientes
        nrd, vrd, mrd = data_hilti[material][hole_type]
        
        st.markdown("---")
        st.subheader("📊 DESIGN RESISTANCE (Rd)")
        st.info(f"**NRd:** {nrd} kN | **VRd:** {vrd} kN | **MRd:** {mrd} Nm")
        
        st.markdown("---")
        st.header("📥 LOADS (Solicitaciones)")
        nsd = st.number_input("N_sd (Tensión) [kN]:", value=0.5, step=0.1)
        vsd = st.number_input("V_sd (Corte) [kN]:", value=0.8, step=0.1)
        msd = st.number_input("M_sd (Momento) [Nm]:", value=1.0, step=0.1)

    # Cuerpo Principal: Imagen y Gráficos
    col_img, col_graph = st.columns([1, 2])

    with col_img:
        st.subheader("🔍 Detalle de Instalación")
        img_path = "F.png"
        if os.path.exists(img_path):
            image = Image.open(img_path)
            st.image(image, caption=f"Configuración: {hole_type}", use_container_width=True)
        else:
            st.warning(f"⚠️ No se encontró {img_path}. Asegúrate de subirlo a GitHub.")

    st.markdown("### 📈 Análisis de Interacción")
    
    # Lógica de Graficación
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('#f4f6f8')
    
    plots = [
        ("Interacción N - V", vsd, nsd, vrd, nrd, "V [kN]", "N [kN]"),
        ("Interacción V - M", msd, vsd, mrd, vrd, "M [Nm]", "V [kN]"),
        ("Interacción N - M", msd, nsd, mrd, nrd, "M [Nm]", "N [kN]")
    ]

    for i, (titulo, sx, sy, rx, ry, lx, ly) in enumerate(plots):
        ax = axs[i]
        x_vals = np.linspace(0, rx, 100)
        y_lim = ry * (1 - x_vals/rx)
        
        ax.fill_between(x_vals, 0, y_lim, color='#d5f5e3', alpha=0.5, label='Seguro')
        ax.plot(x_vals, y_lim, color='#27ae60', lw=2)
        
        # Cálculo de utilización
        utilizacion = (sx/rx) + (sy/ry)
        color_punto = 'red' if utilizacion > 1.0 else '#1a3a5c'
        ax.plot(sx, sy, marker='o', markersize=8, color=color_punto, label=f'Utiliz: {utilizacion:.1%}')
        
        ax.set_title(titulo, fontsize=10, fontweight='bold')
        ax.set_xlabel(lx)
        ax.set_ylabel(ly)
        ax.set_xlim(0, rx * 1.2)
        ax.set_ylim(0, ry * 1.2)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(fontsize=8)

    st.pyplot(fig)

    # Mensaje de validación final
    max_util = max([(vsd/vrd + nsd/nrd), (vsd/vrd + msd/mrd), (nsd/nrd + msd/mrd)])
    if max_util > 1.0:
        st.error(f"❌ FALLA: Utilización máxima del {max_util:.1%} supera el límite permitido.")
    else:
        st.success(f"✅ CUMPLE: Utilización máxima del {max_util:.1%}.")

if __name__ == "__main__":
    main()