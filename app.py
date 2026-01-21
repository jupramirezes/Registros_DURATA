import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="DURATA BI - Análisis Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Tema DURATA */
    .stApp { background-color: #f5f5f5; }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #0099CC;
        margin-bottom: 10px;
    }
    .kpi-card.alert { border-left-color: #dc3545; background: #fff5f5; }
    .kpi-card.success { border-left-color: #28a745; background: #f0fff4; }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0099CC;
        margin: 0;
    }
    .kpi-card.alert .kpi-value { color: #dc3545; }
    .kpi-card.success .kpi-value { color: #28a745; }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 5px 0 0 0;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0099CC 0%, #007799 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p { margin: 5px 0 0 0; opacity: 0.9; }
    
    /* Filtros activos */
    .filter-badge {
        background: #0099CC;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 5px;
        display: inline-block;
    }
    
    /* Sidebar */
    .css-1d391kg { background-color: #ffffff; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0099CC !important;
        color: white !important;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .kpi-value { font-size: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES ====================

def load_data(uploaded_file):
    """Carga y limpia los datos del Excel"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.replace('\n', ' ').str.strip()
        
        # Renombrar columnas para facilitar uso
        column_mapping = {
            'NOMBRE O RAZON SOCIAL': 'CLIENTE',
            'FECHA FINALIZACION': 'FECHA',
            'NOMBRE COTIZADOR': 'COTIZADOR',
            'NUMERO COTIZACION': 'NUM_COTIZACION',
            'VALOR COTIZACIÓN ANTES DE IVA': 'VALOR_COTIZADO',
            'VALOR ADJUDICADO': 'VALOR_ADJUDICADO',
            'COTIZADA': 'ESTADO'
        }
        df = df.rename(columns=column_mapping)
        
        # Convertir valores numéricos
        df['VALOR_COTIZADO'] = pd.to_numeric(df['VALOR_COTIZADO'], errors='coerce').fillna(0)
        df['VALOR_ADJUDICADO'] = pd.to_numeric(df['VALOR_ADJUDICADO'], errors='coerce').fillna(0)
        
        # Limpiar estado
        df['ESTADO'] = df['ESTADO'].astype(str).str.strip().str.upper()
        df['ES_ADJUDICADA'] = df['ESTADO'].str.contains('ADJUDICADA', na=False)
        
        # Filtrar años válidos
        df = df[(df['AÑO'] >= 2019) & (df['AÑO'] <= 2026)]
        
        # Convertir fecha
        df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
        
        # Limpiar cotizador
        df['COTIZADOR'] = df['COTIZADOR'].astype(str).str.strip()
        df = df[df['COTIZADOR'] != '0']
        
        return df, None
    except Exception as e:
        return None, str(e)

def format_currency(value, decimals=0):
    """Formatea valores en pesos colombianos"""
    if value >= 1e9:
        return f"${value/1e9:.{decimals}f}B"
    elif value >= 1e6:
        return f"${value/1e6:.{decimals}f}M"
    else:
        return f"${value:,.0f}"

def create_kpi_card(value, label, card_type="normal"):
    """Crea una tarjeta KPI con HTML"""
    class_name = f"kpi-card {card_type}" if card_type != "normal" else "kpi-card"
    return f"""
    <div class="{class_name}">
        <p class="kpi-value">{value}</p>
        <p class="kpi-label">{label}</p>
    </div>
    """

# ==================== SIDEBAR ====================

with st.sidebar:
    st.image("https://via.placeholder.com/200x60/0099CC/FFFFFF?text=DURATA", width=200)
    st.markdown("---")
    
    st.header("📁 Cargar Datos")
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo Excel aquí",
        type=['xlsx', 'xls'],
        help="Sube el archivo REGISTRO_MAESTRO.xlsx o similar"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
    
    st.markdown("---")
    st.markdown("""
    ### 📖 Instrucciones
    1. **Sube** tu archivo Excel
    2. **Filtra** por año, cotizador o cliente
    3. **Haz click** en las barras para filtrar
    4. **Exporta** a PDF con Ctrl+P
    
    ### 🔗 Links útiles
    - [Dashboard de Proyectos](#)
    - [Manual de uso](#)
    """)

# ==================== MAIN ====================

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 DURATA BI - Análisis Comercial</h1>
    <p>Dashboard interactivo de cotizaciones y conversión</p>
</div>
""", unsafe_allow_html=True)

if uploaded_file is None:
    # Pantalla de bienvenida
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 12px; margin: 20px 0;">
        <h2 style="color: #333;">👋 Bienvenido al Dashboard de DURATA</h2>
        <p style="color: #666; font-size: 1.1rem; margin: 20px 0;">
            Para comenzar, arrastra tu archivo <strong>Excel</strong> en el panel izquierdo.
        </p>
        <div style="background: #f0f7ff; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 500px;">
            <p style="margin: 0; color: #0099CC;">
                📄 Formatos soportados: <strong>.xlsx, .xls</strong><br>
                📊 Archivo esperado: <strong>REGISTRO_MAESTRO.xlsx</strong>
            </p>
        </div>
        <img src="https://via.placeholder.com/400x200/f5f5f5/999999?text=Arrastra+tu+Excel+aquí" style="border-radius: 8px; margin-top: 20px;">
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Cargar datos
df, error = load_data(uploaded_file)

if error:
    st.error(f"❌ Error al cargar el archivo: {error}")
    st.stop()

# ==================== FILTROS ====================

st.markdown("### 🎛️ Filtros")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    años_disponibles = sorted(df['AÑO'].unique())
    años_seleccionados = st.multiselect(
        "📅 Año",
        options=años_disponibles,
        default=años_disponibles,
        key="filtro_año"
    )

with col_f2:
    cotizadores_disponibles = sorted(df['COTIZADOR'].unique())
    cotizadores_seleccionados = st.multiselect(
        "👤 Cotizador",
        options=cotizadores_disponibles,
        default=cotizadores_disponibles,
        key="filtro_cotizador"
    )

with col_f3:
    # Top 20 clientes por cotizaciones
    top_clientes = df['CLIENTE'].value_counts().head(50).index.tolist()
    cliente_seleccionado = st.multiselect(
        "🏢 Cliente (Top 50)",
        options=top_clientes,
        default=[],
        key="filtro_cliente"
    )

with col_f4:
    meses_disponibles = df['MES'].dropna().unique().tolist()
    meses_seleccionados = st.multiselect(
        "📆 Mes",
        options=meses_disponibles,
        default=meses_disponibles,
        key="filtro_mes"
    )

# Aplicar filtros
df_filtered = df.copy()
df_filtered = df_filtered[df_filtered['AÑO'].isin(años_seleccionados)]
df_filtered = df_filtered[df_filtered['COTIZADOR'].isin(cotizadores_seleccionados)]
df_filtered = df_filtered[df_filtered['MES'].isin(meses_seleccionados)]

if cliente_seleccionado:
    df_filtered = df_filtered[df_filtered['CLIENTE'].isin(cliente_seleccionado)]

# Mostrar filtros activos
filtros_activos = []
if len(años_seleccionados) < len(años_disponibles):
    filtros_activos.append(f"Años: {', '.join(map(str, años_seleccionados))}")
if len(cotizadores_seleccionados) < len(cotizadores_disponibles):
    filtros_activos.append(f"Cotizadores: {', '.join(cotizadores_seleccionados)}")
if cliente_seleccionado:
    filtros_activos.append(f"Clientes: {len(cliente_seleccionado)} seleccionados")

if filtros_activos:
    badges = " ".join([f'<span class="filter-badge">{f}</span>' for f in filtros_activos])
    st.markdown(f"**Filtros activos:** {badges}", unsafe_allow_html=True)

st.markdown("---")

# ==================== KPIs ====================

# Calcular métricas
total_cotizaciones = len(df_filtered)
total_adjudicadas = df_filtered['ES_ADJUDICADA'].sum()
valor_cotizado = df_filtered['VALOR_COTIZADO'].sum()
valor_adjudicado = df_filtered['VALOR_ADJUDICADO'].sum()
tasa_conversion = (total_adjudicadas / total_cotizaciones * 100) if total_cotizaciones > 0 else 0
tasa_conversion_valor = (valor_adjudicado / valor_cotizado * 100) if valor_cotizado > 0 else 0
ticket_promedio = valor_cotizado / total_cotizaciones if total_cotizaciones > 0 else 0
dias_promedio = df_filtered['DIAS'].mean() if 'DIAS' in df_filtered.columns else 0

# Mostrar KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(create_kpi_card(f"{total_cotizaciones:,}", "Cotizaciones"), unsafe_allow_html=True)

with col2:
    st.markdown(create_kpi_card(f"{int(total_adjudicadas):,}", "Adjudicadas"), unsafe_allow_html=True)

with col3:
    card_type = "success" if tasa_conversion > 10 else "alert" if tasa_conversion < 5 else "normal"
    st.markdown(create_kpi_card(f"{tasa_conversion:.1f}%", "Conversión (cantidad)", card_type), unsafe_allow_html=True)

with col4:
    st.markdown(create_kpi_card(format_currency(valor_cotizado), "Valor Cotizado"), unsafe_allow_html=True)

with col5:
    st.markdown(create_kpi_card(format_currency(valor_adjudicado), "Valor Adjudicado"), unsafe_allow_html=True)

with col6:
    st.markdown(create_kpi_card(f"{dias_promedio:.0f} días", "Tiempo Promedio"), unsafe_allow_html=True)

st.markdown("---")

# ==================== TABS ====================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "👤 Por Cotizador", "🏢 Por Cliente", "📈 Tendencias"])

# Colores DURATA
colors_durata = ['#0099CC', '#28a745', '#dc3545', '#f0ad4e', '#6c757d', '#17a2b8', '#007799', '#5cb85c']

# ==================== TAB 1: RESUMEN ====================
with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Cotizaciones por año
        df_año = df_filtered.groupby('AÑO').agg({
            'NUM_COTIZACION': 'count',
            'ES_ADJUDICADA': 'sum',
            'VALOR_COTIZADO': 'sum',
            'VALOR_ADJUDICADO': 'sum'
        }).reset_index()
        df_año.columns = ['Año', 'Cotizaciones', 'Adjudicadas', 'Valor Cotizado', 'Valor Adjudicado']
        df_año['Conversión %'] = (df_año['Adjudicadas'] / df_año['Cotizaciones'] * 100).round(1)
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df_año['Año'],
            y=df_año['Cotizaciones'],
            name='Cotizaciones',
            marker_color='#0099CC',
            text=df_año['Cotizaciones'],
            textposition='auto'
        ))
        fig1.add_trace(go.Bar(
            x=df_año['Año'],
            y=df_año['Adjudicadas'],
            name='Adjudicadas',
            marker_color='#28a745',
            text=df_año['Adjudicadas'],
            textposition='auto'
        ))
        fig1.update_layout(
            title='📊 Cotizaciones vs Adjudicadas por Año',
            barmode='group',
            height=400,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Evento de click
        selected_points = st.plotly_chart(fig1, use_container_width=True, key="chart_año")
    
    with col_chart2:
        # Embudo de conversión
        fig2 = go.Figure(go.Funnel(
            y=['Cotizaciones', 'En proceso', 'Adjudicadas'],
            x=[total_cotizaciones, total_cotizaciones - total_adjudicadas, total_adjudicadas],
            textinfo="value+percent initial",
            marker=dict(color=['#0099CC', '#f0ad4e', '#28a745'])
        ))
        fig2.update_layout(
            title='🔻 Embudo de Conversión',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Segunda fila
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        # Valor por año
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=df_año['Año'],
            y=df_año['Valor Cotizado'] / 1e9,
            name='Cotizado',
            marker_color='#0099CC'
        ))
        fig3.add_trace(go.Scatter(
            x=df_año['Año'],
            y=df_año['Conversión %'],
            name='Conversión %',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#dc3545', width=3),
            marker=dict(size=10)
        ))
        fig3.update_layout(
            title='💰 Valor Cotizado y Tasa de Conversión',
            yaxis=dict(title='Valor Cotizado (Miles de Millones)', side='left'),
            yaxis2=dict(title='Conversión %', side='right', overlaying='y', showgrid=False),
            height=400,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_chart4:
        # Por mes
        df_mes = df_filtered.groupby('MES').agg({
            'NUM_COTIZACION': 'count',
            'VALOR_COTIZADO': 'sum'
        }).reset_index()
        df_mes.columns = ['Mes', 'Cotizaciones', 'Valor']
        
        # Ordenar meses
        meses_orden = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
                       'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
        df_mes['Mes_num'] = df_mes['Mes'].apply(lambda x: meses_orden.index(x) if x in meses_orden else 99)
        df_mes = df_mes.sort_values('Mes_num')
        
        fig4 = px.bar(
            df_mes,
            x='Mes',
            y='Cotizaciones',
            color='Valor',
            color_continuous_scale=['#b3e0f2', '#0099CC', '#004d66'],
            title='📅 Estacionalidad por Mes'
        )
        fig4.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig4, use_container_width=True)

# ==================== TAB 2: POR COTIZADOR ====================
with tab2:
    col_cot1, col_cot2 = st.columns(2)
    
    with col_cot1:
        # Productividad por cotizador
        df_cot = df_filtered.groupby('COTIZADOR').agg({
            'NUM_COTIZACION': 'count',
            'ES_ADJUDICADA': 'sum',
            'VALOR_COTIZADO': 'sum',
            'VALOR_ADJUDICADO': 'sum'
        }).reset_index()
        df_cot.columns = ['Cotizador', 'Cotizaciones', 'Adjudicadas', 'Valor Cotizado', 'Valor Adjudicado']
        df_cot['Conversión %'] = (df_cot['Adjudicadas'] / df_cot['Cotizaciones'] * 100).round(1)
        df_cot = df_cot.sort_values('Cotizaciones', ascending=True)
        
        fig_cot1 = go.Figure()
        fig_cot1.add_trace(go.Bar(
            y=df_cot['Cotizador'],
            x=df_cot['Cotizaciones'],
            name='Cotizaciones',
            orientation='h',
            marker_color='#0099CC',
            text=df_cot['Cotizaciones'],
            textposition='auto'
        ))
        fig_cot1.update_layout(
            title='👤 Cotizaciones por Cotizador',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig_cot1, use_container_width=True)
    
    with col_cot2:
        # Conversión por cotizador
        fig_cot2 = go.Figure()
        fig_cot2.add_trace(go.Bar(
            y=df_cot['Cotizador'],
            x=df_cot['Conversión %'],
            orientation='h',
            marker_color=df_cot['Conversión %'].apply(
                lambda x: '#28a745' if x > 10 else '#f0ad4e' if x > 5 else '#dc3545'
            ),
            text=df_cot['Conversión %'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto'
        ))
        fig_cot2.update_layout(
            title='📈 Tasa de Conversión por Cotizador',
            height=400,
            template='plotly_white',
            xaxis_title='Conversión %'
        )
        st.plotly_chart(fig_cot2, use_container_width=True)
    
    # Tabla detallada
    st.markdown("#### 📋 Detalle por Cotizador")
    df_cot_display = df_cot.copy()
    df_cot_display['Valor Cotizado'] = df_cot_display['Valor Cotizado'].apply(lambda x: format_currency(x))
    df_cot_display['Valor Adjudicado'] = df_cot_display['Valor Adjudicado'].apply(lambda x: format_currency(x))
    df_cot_display = df_cot_display.sort_values('Cotizaciones', ascending=False)
    st.dataframe(df_cot_display, use_container_width=True, hide_index=True)

# ==================== TAB 3: POR CLIENTE ====================
with tab3:
    col_cli1, col_cli2 = st.columns(2)
    
    with col_cli1:
        # Top clientes por cotizaciones
        df_cli = df_filtered.groupby('CLIENTE').agg({
            'NUM_COTIZACION': 'count',
            'ES_ADJUDICADA': 'sum',
            'VALOR_COTIZADO': 'sum'
        }).reset_index()
        df_cli.columns = ['Cliente', 'Cotizaciones', 'Adjudicadas', 'Valor Cotizado']
        df_cli['Conversión %'] = (df_cli['Adjudicadas'] / df_cli['Cotizaciones'] * 100).round(1)
        
        top_cli = df_cli.nlargest(15, 'Cotizaciones')
        
        fig_cli1 = px.bar(
            top_cli.sort_values('Cotizaciones'),
            y='Cliente',
            x='Cotizaciones',
            orientation='h',
            color='Conversión %',
            color_continuous_scale=['#dc3545', '#f0ad4e', '#28a745'],
            title='🏆 Top 15 Clientes por Cotizaciones'
        )
        fig_cli1.update_layout(height=500, template='plotly_white')
        st.plotly_chart(fig_cli1, use_container_width=True)
    
    with col_cli2:
        # Top clientes por valor
        top_cli_valor = df_cli.nlargest(15, 'Valor Cotizado')
        
        fig_cli2 = px.bar(
            top_cli_valor.sort_values('Valor Cotizado'),
            y='Cliente',
            x=top_cli_valor['Valor Cotizado'] / 1e9,
            orientation='h',
            color='Cotizaciones',
            color_continuous_scale=['#b3e0f2', '#0099CC', '#004d66'],
            title='💰 Top 15 Clientes por Valor Cotizado'
        )
        fig_cli2.update_layout(
            height=500,
            template='plotly_white',
            xaxis_title='Valor (Miles de Millones)'
        )
        st.plotly_chart(fig_cli2, use_container_width=True)
    
    # Buscador de cliente
    st.markdown("#### 🔍 Buscar Cliente")
    cliente_buscar = st.text_input("Escribe el nombre del cliente:")
    
    if cliente_buscar:
        df_busqueda = df_cli[df_cli['Cliente'].str.contains(cliente_buscar.upper(), na=False)]
        if len(df_busqueda) > 0:
            df_busqueda['Valor Cotizado'] = df_busqueda['Valor Cotizado'].apply(lambda x: format_currency(x))
            st.dataframe(df_busqueda, use_container_width=True, hide_index=True)
        else:
            st.warning("No se encontraron clientes con ese nombre")

# ==================== TAB 4: TENDENCIAS ====================
with tab4:
    col_trend1, col_trend2 = st.columns(2)
    
    with col_trend1:
        # Evolución mensual
        df_filtered['AÑO_MES'] = df_filtered['AÑO'].astype(str) + '-' + df_filtered['MES'].astype(str).str[:3]
        df_trend = df_filtered.groupby(['AÑO', 'MES']).agg({
            'NUM_COTIZACION': 'count',
            'VALOR_COTIZADO': 'sum'
        }).reset_index()
        df_trend.columns = ['Año', 'Mes', 'Cotizaciones', 'Valor']
        
        fig_trend1 = px.line(
            df_trend,
            x='Mes',
            y='Cotizaciones',
            color='Año',
            markers=True,
            title='📈 Evolución de Cotizaciones por Mes y Año'
        )
        fig_trend1.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig_trend1, use_container_width=True)
    
    with col_trend2:
        # Ticket promedio por año
        df_ticket = df_filtered.groupby('AÑO').agg({
            'VALOR_COTIZADO': 'sum',
            'NUM_COTIZACION': 'count'
        }).reset_index()
        df_ticket['Ticket Promedio'] = df_ticket['VALOR_COTIZADO'] / df_ticket['NUM_COTIZACION']
        
        fig_trend2 = go.Figure()
        fig_trend2.add_trace(go.Scatter(
            x=df_ticket['AÑO'],
            y=df_ticket['Ticket Promedio'] / 1e6,
            mode='lines+markers+text',
            text=df_ticket['Ticket Promedio'].apply(lambda x: format_currency(x)),
            textposition='top center',
            line=dict(color='#0099CC', width=3),
            marker=dict(size=12)
        ))
        fig_trend2.update_layout(
            title='🎫 Ticket Promedio por Año',
            yaxis_title='Millones de Pesos',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig_trend2, use_container_width=True)
    
    # Días promedio de entrega
    if 'DIAS' in df_filtered.columns:
        df_dias = df_filtered.groupby('AÑO')['DIAS'].mean().reset_index()
        
        fig_dias = px.bar(
            df_dias,
            x='AÑO',
            y='DIAS',
            color='DIAS',
            color_continuous_scale=['#28a745', '#f0ad4e', '#dc3545'],
            title='⏱️ Días Promedio de Entrega por Año'
        )
        fig_dias.update_layout(height=350, template='plotly_white')
        st.plotly_chart(fig_dias, use_container_width=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>DURATA BI</strong> - Dashboard de Análisis Comercial</p>
    <p style="font-size: 0.8rem;">💡 Para exportar a PDF: Presiona <strong>Ctrl + P</strong> y selecciona "Guardar como PDF"</p>
    <p style="font-size: 0.8rem;">📊 Datos actualizados según archivo cargado</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR: ESTADÍSTICAS ====================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📈 Resumen Rápido")
    st.metric("Total Cotizaciones", f"{total_cotizaciones:,}")
    st.metric("Tasa Conversión", f"{tasa_conversion:.1f}%", 
              delta=f"{tasa_conversion - 5:.1f}%" if tasa_conversion > 5 else f"{tasa_conversion - 5:.1f}%")
    st.metric("Valor Cotizado", format_currency(valor_cotizado))


