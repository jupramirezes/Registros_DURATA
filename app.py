import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components

# Configuración de página profesional
st.set_page_config(
    page_title="Análisis Maestro Durata",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo sobrio
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD; }
    header { background-color: #2C3E50 !important; }
    .stButton>button { background-color: #34495E; color: white; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Explorador Dinámico de Datos")

st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube el archivo REGISTRO_MAESTRO.xlsx", type=['xlsx'])

if uploaded_file:
    try:
        # 1. Leer el archivo
        df = pd.read_excel(uploaded_file)
        
        # 2. LIMPIEZA DE DATOS (Solución al error del DOUBLE)
        # Buscamos columnas que tengan números escritos como texto con comas
        for col in df.columns:
            # Si la columna es de texto (object), intentamos limpiarla
            if df[col].dtype == 'object':
                try:
                    # Quitamos comas y espacios, y convertimos a número
                    # 'coerce' hace que si algo no es número, lo ponga como vacío (NaN) en lugar de dar error
                    temp_col = df[col].astype(str).str.replace(',', '').str.strip()
                    df[col] = pd.to_numeric(temp_col, errors='ignore')
                except:
                    pass # Si no es una columna numérica, la dejamos como está

        # 3. Generar la interfaz de PyGWalker
        # El tema 'vega' es el más sobrio y profesional
        pyg_html = pyg.to_html(df)
        
        # 4. Mostrar en la web
        components.html(pyg_html, height=900, scrolling=True)
        
        st.sidebar.success("Datos optimizados y cargados.")
        
        st.sidebar.markdown("---")
        st.sidebar.info("💡 **Tip:** Si un campo numérico aparece como 'Texto', arrástralo a la sección de 'Measures' en el panel.")

    except Exception as e:
        st.error(f"Hubo un problema al procesar los datos: {e}")
else:
    st.info("👋 Por favor, sube tu archivo de Excel para activar el panel de control.")

