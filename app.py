import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. DESIGN SYSTEM - Estética Premium e Profissional
st.set_page_config(page_title="VigiLeish Intelligence | One Health", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #fcfcfd;
    }
    
    /* Estilo dos Botões de Navegação na Barra Lateral */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        font-weight: 400;
        text-align: left;
        transition: all 0.2s;
        margin-bottom: 5px;
    }
    div.stButton > button:hover {
        border-color: #d32f2f;
        color: #d32f2f;
        background-color: #fffafa;
    }
    
    /* Estilo dos Cards de Métricas */
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS INTEGRADO (Filtro 2007 - 2023)
@st.cache_data
def load_data():
    try:
        # --- DADOS HUMANOS ---
        df_h_raw = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df_h_raw.columns = [c.strip() for c in df_h_raw.columns]
        
        # Limpeza: Apenas anos entre 2007 e 2023 (remove totais e 2024)
        df_h_raw['Ano_Val'] = pd.to_numeric(df_h_raw.iloc[:, 0], errors='coerce')
        df_h_clean = df_h_raw[(df_h_raw['Ano_Val'] >= 2007) & (df_h_raw['Ano_Val'] <= 2023)].copy()
        
        # Estrutura Histórica Humana
        df_hist = df_h_clean.iloc[:, :7]
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade']
        for col in ['Ano', 'Casos', 'Obitos', 'Letalidade']:
            df_hist[col] = pd.to_numeric(df_hist[col], errors='coerce').fillna(0).astype(int)

        # Regionais (Mapeamento Geográfico)
        coords = {
            'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
            'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
            'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]
        }
        reg_data = []
        for reg, latlon in coords.items():
            mask = df_h_raw.iloc[:,0].str.contains(reg, na=False, case=False)
            if mask.any():
                row = df_h_raw[mask].iloc[0]
                for i, ano in enumerate(range(2007, 2024)):
                    reg_data.append({
                        'Regional': reg, 'Ano': int(ano),
                        'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'),
                        'Lat': latlon[0], 'Lon': latlon[1]
                    })
        
        # --- DADOS CANINOS ---
        df_c_raw = pd.read_csv('caninos.csv', sep=';', encoding='iso-8859-1')
        df_c_raw.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']
        
        for col in df_c_raw.columns:
            df_c_raw[col] = df_c_raw[col].astype(str).str.replace('.', '').str.replace(',', '.')
            df_c_raw[col] = pd.to_numeric(df_c_raw[col], errors='coerce').fillna(0).astype(int)
        
        # Filtro 2007-2023 para caninos
        df_c_clean = df_c_raw[(df_c_raw['Ano'] >= 2007) & (df_c_raw['Ano'] <= 2023)].copy()
        df_c_clean['Taxa_Positividade'] = (df_c_clean['Positivos'] / df_c_clean['Sorologias'] * 100).fillna(0)

        return df_hist, pd.DataFrame(reg_data), df_c_clean
    except Exception as e:
        st.error(f"Erro no carregamento: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_c = load_data()

# 3. NAVEGAÇÃO E FILTROS
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

st.sidebar.title("VigiLeish Navigator")
if st.sidebar.button("📊 Painel Geral"): st.session_state.segment = "Geral"
if st.sidebar.button("🗺️ Monitoramento Geográfico"): st.session_state.segment = "Mapa"
if st.sidebar.button("📈 Histórico & Tendências"): st.session_state.segment = "Historico"
if st.sidebar.button("🐕 Vigilância Canina"): st.session_state.segment = "Canina"
if st.sidebar.button("📋 Diretrizes de Saúde"): st.session_state.segment = "Diretrizes"

st.sidebar.markdown("---")
st.sidebar.subheader("Filtro Temporal")
anos_disponiveis = sorted(df_m['Ano'].unique().tolist(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", options=anos_disponiveis, index=0)

# 4. EXIBIÇÃO DE CONTEÚDO
st.title("VigiLeish Intelligence System")
st.markdown(f"Análise Epidemiológica de Belo Horizonte | Período de Referência: **{ano_selecionado}**")

# --- SETOR 1: PAINEL GERAL ---
if st.session_state.segment == "Geral":
    st.subheader("Visão Consolidada de Saúde Única")
    
    # Filtros locais
    data_h = df_h[df_h['Ano'] == ano_selecionado]
    data_c = df_c[df_c['Ano'] == ano_selecionado]

    # Humanos
    st.markdown("#### 🏥 Indicadores Humanos")
    col1, col2, col3 = st.columns(3)
    if not data_h.empty:
        col1.metric("Casos Confirmados", f"{data_h['Casos'].iloc[0]}")
        col2.metric("Óbitos", f"{data_h['Obitos'].iloc[0]}")
        letalidade = (data_h['Obitos'].iloc[0]/data_h['Casos'].iloc[0]*100) if data_h['Casos'].iloc[0] > 0 else 0
        col3.metric("Taxa de Letalidade", f"{letalidade:.1f}%")

    # Caninos
    st.markdown("#### 🐕 Indicadores Caninos e Controle")
    col4, col5, col6, col7 = st.columns(4)
    if not data_c.empty:
        col4.metric("Cães Positivos", f"{data_c['Positivos'].iloc[0]:,}".replace(',', '.'))
        col5.metric("Taxa Positividade", f"{data_c['Taxa_Positividade'].iloc[0]:.1f}%")
        col6.metric("Cães Eutanasiados", f"{data_c['Eutanasiados'].iloc[0]:,}".replace(',', '.'))
        col7.metric("Imóveis Borrifados", f"{data_c['Borrifados'].iloc[0]:,}".replace(',', '.'))
    
    st.info(f"**Nota de Esforço:** Em {ano_selecionado}, foram realizadas {data_c['Sorologias'].iloc[0]:,} sorologias caninas no município.".replace(',', '.'))

# --- SETOR 2: MONITORAMENTO GEOGRÁFICO ---
elif st.session_state.segment == "Mapa":
    st.subheader(f"Distribuição Regional de Casos ({ano_selecionado})")
    df_map_filt = df_m[df_m['Ano'] == ano_selecionado]
    
    col_map, col_rank = st.columns([1.8, 1])
    with col_map:
        fig_map = px.scatter_mapbox(
            df_map_filt, lat="Lat", lon="Lon", size="Casos", color="Casos",
            hover_name="Regional", size_max=35, zoom=10.5,
            color_continuous_scale="YlOrRd", mapbox_style="carto-positron"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map, use_container_width=True)
    with col_rank:
        st.plotly_chart(px.bar(df_map_filt.sort_values('Casos'), x='Casos', y='Regional', color='Casos', color_continuous_scale="YlOrRd"), use_container_width=True)

# --- SETOR 3: HISTÓRICO & TENDÊNCIAS ---
elif st.session_state.segment == "Historico":
    st.subheader("Evolução Histórica e Correlação (2007-2023)")
    
    # Correlação Duplo Eixo
    df_merged = pd.merge(df_h[['Ano', 'Casos']], df_c[['Ano', 'Positivos']], on='Ano').sort_values('Ano')
    fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
    fig_corr.add_trace(go.Scatter(x=df_merged['Ano'], y=df_merged['Positivos'], name="Cães Positivos", line=dict(color='#d32f2f', width=3)), secondary_y=False)
    fig_corr.add_trace(go.Scatter(x=df_merged['Ano'], y=df_merged['Casos'], name="Casos Humanos", line=dict(color='#334155', width=3, dash='dot')), secondary_y=True)
    fig_corr.update_yaxes(title_text="Cães Positivos", secondary_y=False, color='#d32f2f')
    fig_corr.update_yaxes(title_text="Casos Humanos", secondary_y=True, color='#334155')
    fig_corr.update_layout(plot_bgcolor="white", xaxis_type='category', title="Impacto do Reservatório Animal na Transmissão Humana")
    st.plotly_chart(fig_corr, use_container_width=True)

# --- SETOR 4: VIGILÂNCIA CANINA ---
elif st.session_state.segment == "Canina":
    st.subheader("Vigilância Integrada: Cães, Testagem e Controle Ambiental")
    
    fig_misto = make_subplots(specs=[[{"secondary_y": True}]])
    # Barras: Impacto
    fig_misto.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Positivos'], name="Cães Positivos", marker_color='#F59E0B', opacity=0.7), secondary_y=False)
    fig_misto.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Eutanasiados'], name="Cães Eutanasiados", marker_color='#D32F2F', opacity=0.9), secondary_y=False)
    # Linhas: Esforço
    fig_misto.add_trace(go.Scatter(x=df_c['Ano'], y=df_c['Sorologias'], name="Sorologias Realizadas", line=dict(color='#3B82F6', width=2)), secondary_y=True)
    fig_misto.add_trace(go.Scatter(x=df_c['Ano'], y=df_c['Borrifados'], name="Imóveis Borrifados", line=dict(color='#334155', width=2, dash='dot')), secondary_y=True)

    fig_misto.update_layout(barmode='group', plot_bgcolor='white', xaxis_type='category', title="Esforço de Vigilância vs Carga da Doença")
    fig_misto.update_yaxes(title_text="Cães", secondary_y=False)
    fig_misto.update_yaxes(title_text="Volume (Testes/Borrifação)", secondary_y=True)
    st.plotly_chart(fig_misto, use_container_width=True)

# --- SETOR 5: DIRETRIZES DE SAÚDE ---
elif st.session_state.segment == "Diretrizes":
    st.subheader("📋 Diretrizes e Prevenção (ODS 3)")
    st.markdown("Informações baseadas no Manual de Vigilância e Controle da Leishmaniose Visceral.")

    col_h, col_c = st.columns(2)
    with col_h:
        with st.expander("👤 Sintomas em Humanos", expanded=True):
            st.markdown("""
            * **Febre:** Longa duração e irregular.
            * **Abdômen:** Aumento do volume (**baço e fígado**).
            * **Geral:** Perda de peso, palidez (anemia) e fraqueza.
            """)
    with col_c:
        with st.expander("🐕 Sintomas em Cães", expanded=True):
            st.markdown("""
            * **Pele:** Feridas no focinho e orelhas, descamação.
            * **Unhas:** Crescimento exagerado (**Onicogrifose**).
            * **Olhos:** Secreções e conjuntivite.
            """)

    st.markdown("### 🛡️ Formas de Prevenção")
    p1, p2, p3 = st.columns(3)
    p1.info("**Manejo Ambiental:** Limpeza de quintais, eliminação de matéria orgânica e frutas caídas.")
    p2.success("**Proteção:** Telas finas em janelas e evitar exposição ao ar livre no crepúsculo.")
    p3.warning("**Posse Responsável:** Uso de coleiras com inseticida e exames periódicos em cães.")

st.sidebar.markdown("---")
st.sidebar.caption("Analista Responsável")
st.sidebar.caption("RU: [Seu Registro Aqui]")
