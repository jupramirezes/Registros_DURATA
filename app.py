import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components

# Configuración de página profesional
st.set_page_config(
    page_title="Data Explorer Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo sobrio (Azules oscuros y grises)
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD; }
    header { background-color: #2C3E50 !important; }
    .stButton>button { background-color: #34495E; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Análisis Dinámico de Datos")

# Cargador de Excel en la barra lateral
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo REGISTRO_MAESTRO.xlsx", type=['xlsx'])

if uploaded_file:
    try:
        # Cargar datos
        df = pd.read_excel(uploaded_file)
        
        # Generar la interfaz de Power BI (PyGWalker)
        # Usamos el tema 'vega' para mantener la sobriedad
        pyg_html = pyg.to_html(df)
        
        # Renderizar en la web
        components.html(pyg_html, height=900, scrolling=True)
        
        st.sidebar.success("Datos cargados. Usa el panel superior para arrastrar campos.")
        
        # Instrucción para PDF
        st.sidebar.markdown("---")
        st.sidebar.info("💡 **Para exportar a PDF:** Una vez diseñado tu gráfico, presiona `Ctrl + P` en tu teclado y elige 'Guardar como PDF'.")

    except Exception as e:
        st.error(f"Hubo un problema al leer el Excel: {e}")
else:
    st.info("Para comenzar, arrastra el archivo de Excel en el panel de la izquierda.")
