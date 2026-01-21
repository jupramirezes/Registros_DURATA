import streamlit as st
import pandas as pd
import pygwalker as pyg
from streamlit_pygwalker import pyg_html

# Configuración de página (Sobria y Profesional)
st.set_page_config(
    page_title="Analizador Maestro de Datos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado (Colores sobrios)
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stButton>button { background-color: #2C3E50; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Explorador Dinámico de Cotizaciones")
st.subheader("Interfaz de Autoservicio (Power BI Style)")

# 1. Cargador de archivos Excel
uploaded_file = st.sidebar.file_uploader("Arrastra aquí tu archivo de Excel (.xlsx)", type=['xlsx'])

if uploaded_file:
    try:
        # Lectura de datos
        df = pd.read_excel(uploaded_file)
        
        st.sidebar.success("Archivo cargado correctamente")
        
        # 2. Motor de Visualización (PyGWalker)
        # Esto genera la interfaz de "arrastrar y soltar"
        pyg_config = {
            "theme": "vega", # Estilo limpio y profesional
        }
        
        # Renderizar la interfaz de exploración
        # Permite crear gráficos, filtros y dashboards dinámicos
        walker_html = pyg.to_html(df)
        st.components.v1.html(walker_html, height=800, scrolling=True)
        
        # 3. Opción de Exportación
        st.sidebar.markdown("---")
        st.sidebar.write("### Exportación")
        if st.sidebar.button("Preparar Informe para PDF"):
            st.sidebar.info("Para exportar: Usa el atajo Ctrl+P (Imprimir) y selecciona 'Guardar como PDF'. La interfaz está optimizada para capturar los gráficos actuales.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

else:
    st.info("👋 Por favor, carga el archivo REGISTRO_MAESTRO.xlsx en el panel de la izquierda para comenzar a graficar.")
    
    # Preview de cómo se vería la estructura con datos de ejemplo si no hay archivo
    st.image("https://raw.githubusercontent.com/Kanaries/pygwalker/main/docs/images/pygwalker-ui.png", 
             caption="Ejemplo de la interfaz de arrastre de campos que obtendrás.")