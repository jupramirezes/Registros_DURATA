import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración
st.set_page_config(page_title="DURATA BI", page_icon="📊", layout="wide")

# Estilos
st.markdown("""
<style>
    .kpi-card {background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #0099CC; text-align: center;}
    .kpi-value {font-size: 2rem; font-weight: 700; color: #0099CC; margin: 0;}
    .kpi-label {font-size: 0.85rem; color: #666; margin: 5px 0 0 0;}
    .main-header {background: linear-gradient(135deg, #0099CC 0%, #007799 100%); color: white; padding: 20px 30px; border-radius: 12px; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

def format_currency(value):
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    return f"${value:,.0f}"

# Header
st.markdown('<div class="main-header"><h1>📊 DURATA BI</h1><p>Dashboard de Análisis Comercial</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📁 Cargar Datos")
    uploaded_file = st.file_uploader("Arrastra tu archivo Excel", type=['xlsx', 'xls'])
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")

# Sin archivo
if not uploaded_file:
    st.info("👈 Para comenzar, arrastra tu archivo Excel en el panel izquierdo")
    st.stop()

# Cargar datos
try:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    
    # Renombrar columnas
    rename_map = {
        'NOMBRE O RAZON SOCIAL': 'CLIENTE',
        'FECHA FINALIZACION': 'FECHA', 
        'NOMBRE COTIZADOR': 'COTIZADOR',
        'NUMERO COTIZACION': 'NUM_COT',
        'VALOR COTIZACIÓN ANTES DE IVA': 'VALOR_COTIZADO',
        'VALOR ADJUDICADO': 'VALOR_ADJUDICADO',
        'COTIZADA': 'ESTADO'
    }
    df = df.rename(columns=rename_map)
    
    # Limpiar datos
    df['VALOR_COTIZADO'] = pd.to_numeric(df['VALOR_COTIZADO'], errors='coerce').fillna(0)
    df['VALOR_ADJUDICADO'] = pd.to_numeric(df['VALOR_ADJUDICADO'], errors='coerce').fillna(0)
    df['ESTADO'] = df['ESTADO'].astype(str).str.strip().str.upper()
    df['ES_ADJUDICADA'] = df['ESTADO'].str.contains('ADJUDICADA', na=False)
    df = df[(df['AÑO'] >= 2019) & (df['AÑO'] <= 2026)]
    
except Exception as e:
    st.error(f"Error al cargar: {e}")
    st.stop()

# Filtros
st.subheader("🎛️ Filtros")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    años = st.multiselect("📅 Año", sorted(df['AÑO'].unique()), default=sorted(df['AÑO'].unique()))
with col_f2:
    cotizadores = st.multiselect("👤 Cotizador", sorted(df['COTIZADOR'].dropna().unique()), default=sorted(df['COTIZADOR'].dropna().unique()))
with col_f3:
    top_clientes = df['CLIENTE'].value_counts().head(30).index.tolist()
    clientes = st.multiselect("🏢 Cliente (Top 30)", top_clientes)

# Aplicar filtros
df_f = df[df['AÑO'].isin(años) & df['COTIZADOR'].isin(cotizadores)]
if clientes:
    df_f = df_f[df_f['CLIENTE'].isin(clientes)]

st.markdown("---")

# KPIs
total_cot = len(df_f)
total_adj = df_f['ES_ADJUDICADA'].sum()
valor_cot = df_f['VALOR_COTIZADO'].sum()
valor_adj = df_f['VALOR_ADJUDICADO'].sum()
conversion = (total_adj / total_cot * 100) if total_cot > 0 else 0
dias_prom = df_f['DIAS'].mean() if 'DIAS' in df_f.columns else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("📋 Cotizaciones", f"{total_cot:,}")
col2.metric("✅ Adjudicadas", f"{int(total_adj):,}")
col3.metric("📈 Conversión", f"{conversion:.1f}%")
col4.metric("💰 Cotizado", format_currency(valor_cot))
col5.metric("💵 Adjudicado", format_currency(valor_adj))
col6.metric("⏱️ Días Prom", f"{dias_prom:.0f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Por Año", "👤 Por Cotizador", "🏢 Por Cliente"])

with tab1:
    c1, c2 = st.columns(2)
    
    # Cotizaciones por año
    df_año = df_f.groupby('AÑO').agg(
        Cotizaciones=('NUM_COT', 'count'),
        Adjudicadas=('ES_ADJUDICADA', 'sum'),
        Valor_Cotizado=('VALOR_COTIZADO', 'sum')
    ).reset_index()
    df_año['Conversión'] = (df_año['Adjudicadas'] / df_año['Cotizaciones'] * 100).round(1)
    
    with c1:
        fig1 = px.bar(df_año, x='AÑO', y=['Cotizaciones', 'Adjudicadas'], barmode='group',
                      title='Cotizaciones vs Adjudicadas', color_discrete_sequence=['#0099CC', '#28a745'])
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with c2:
        fig2 = go.Figure()
        fig2.add_bar(x=df_año['AÑO'], y=df_año['Valor_Cotizado']/1e9, name='Cotizado (B)', marker_color='#0099CC')
        fig2.add_scatter(x=df_año['AÑO'], y=df_año['Conversión'], name='Conversión %', yaxis='y2', 
                        mode='lines+markers', line=dict(color='#dc3545', width=3))
        fig2.update_layout(
            title='Valor Cotizado y Conversión',
            yaxis=dict(title='Miles de Millones'),
            yaxis2=dict(title='%', overlaying='y', side='right'),
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Embudo
    fig_funnel = go.Figure(go.Funnel(
        y=['Cotizaciones', 'En proceso', 'Adjudicadas'],
        x=[total_cot, total_cot - total_adj, total_adj],
        textinfo="value+percent initial",
        marker=dict(color=['#0099CC', '#f0ad4e', '#28a745'])
    ))
    fig_funnel.update_layout(title='🔻 Embudo de Conversión', height=350)
    st.plotly_chart(fig_funnel, use_container_width=True)

with tab2:
    df_cot = df_f.groupby('COTIZADOR').agg(
        Cotizaciones=('NUM_COT', 'count'),
        Adjudicadas=('ES_ADJUDICADA', 'sum'),
        Valor=('VALOR_COTIZADO', 'sum')
    ).reset_index()
    df_cot['Conversión'] = (df_cot['Adjudicadas'] / df_cot['Cotizaciones'] * 100).round(1)
    df_cot = df_cot.sort_values('Cotizaciones', ascending=True)
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df_cot, y='COTIZADOR', x='Cotizaciones', orientation='h',
                     title='Cotizaciones por Cotizador', color_discrete_sequence=['#0099CC'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        fig = px.bar(df_cot, y='COTIZADOR', x='Conversión', orientation='h',
                     title='Conversión % por Cotizador', color='Conversión',
                     color_continuous_scale=['#dc3545', '#f0ad4e', '#28a745'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_cot.sort_values('Cotizaciones', ascending=False), use_container_width=True, hide_index=True)

with tab3:
    df_cli = df_f.groupby('CLIENTE').agg(
        Cotizaciones=('NUM_COT', 'count'),
        Adjudicadas=('ES_ADJUDICADA', 'sum'),
        Valor=('VALOR_COTIZADO', 'sum')
    ).reset_index()
    df_cli['Conversión'] = (df_cli['Adjudicadas'] / df_cli['Cotizaciones'] * 100).round(1)
    
    c1, c2 = st.columns(2)
    with c1:
        top15 = df_cli.nlargest(15, 'Cotizaciones').sort_values('Cotizaciones')
        fig = px.bar(top15, y='CLIENTE', x='Cotizaciones', orientation='h',
                     title='Top 15 Clientes por Cotizaciones', color='Conversión',
                     color_continuous_scale=['#dc3545', '#f0ad4e', '#28a745'])
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        top15_val = df_cli.nlargest(15, 'Valor').sort_values('Valor')
        fig = px.bar(top15_val, y='CLIENTE', x=top15_val['Valor']/1e9, orientation='h',
                     title='Top 15 Clientes por Valor', color_discrete_sequence=['#0099CC'])
        fig.update_layout(height=500, xaxis_title='Miles de Millones')
        st.plotly_chart(fig, use_container_width=True)
    
    # Buscador
    buscar = st.text_input("🔍 Buscar cliente:")
    if buscar:
        resultado = df_cli[df_cli['CLIENTE'].str.contains(buscar.upper(), na=False)]
        st.dataframe(resultado, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("💡 Para exportar a PDF: Ctrl+P → Guardar como PDF")


