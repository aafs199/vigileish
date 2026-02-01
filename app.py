import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="VigiLeish Intelligence Dashboard", layout="wide", page_icon="🧬")

# --- 2. ESTILO CSS (VISUAL VERDE + CAIXAS EXPLICATIVAS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    
    /* Fonte Geral */
    .main .block-container { color: #1e293b; font-family: 'Lora', serif; }
    h1, h2, h3, h4, h5, h6, p, div { font-family: 'Lora', serif !important; }
    
    /* Títulos */
    .main h2, .main h3, .main h4 { color: #064E3B !important; font-weight: 700 !important; }
    
    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #f7fcf9 !important;
        border-right: 1px solid #d1d5db;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #064E3B !important;
    }
    
    /* --- FILTROS (Selectbox) --- */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: #86efac !important;
        color: #1e293b !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #2E7D32 !important;
    }
    div[data-baseweb="select"]:focus-within > div {
        border-color: #2E7D32 !important;
        box-shadow: 0 0 0 1px #2E7D32 !important;
    }
    ul[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #dcfce7 !important;
        color: #064E3B !important;
    }

    /* --- BOTÕES --- */
    div.stButton > button, div.stLinkButton > a {
        background-color: #ffffff !important; 
        color: #064E3B !important;
        border: 1px solid #2E7D32 !important; 
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover, div.stLinkButton > a:hover {
        background-color: #2E7D32 !important; 
        color: white !important;
        border-color: #2E7D32 !important;
        transform: translateY(-1px);
    }

    /* --- MÉTRICAS --- */
    [data-testid="stMetric"] {
        background-color: #ffffff; padding: 15px; border-radius: 8px;
        border: 1px solid #e2e8f0; border-left: 5px solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] { color: #2E7D32 !important; font-weight: 700 !important; }

    /* --- CAIXAS EXPLICATIVAS (SEM ÍCONES) --- */
    .info-box {
        background-color: #ecfdf5; /* Verde muito claro */
        border-left: 5px solid #059669; /* Verde médio */
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        color: #1e293b;
        font-size: 0.95rem;
    }
    .info-title {
        color: #064E3B;
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
        font-size: 1.1rem;
    }

    /* --- CABEÇALHO --- */
    .header-container {
        background-color: #064E3B; padding: 40px 20px; border-radius: 8px; margin-bottom: 30px;
        text-align: center; border-bottom: 4px solid #4ade80; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-title { color: #ffffff !important; font-size: 2.2rem !important; margin: 0 !important; font-weight: 700 !important; }
    .header-subtitle { color: #dcfce7 !important; margin-top: 10px !important; font-size: 1.0rem; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    try:
        # A. HUMANOS
        df_h_raw = pd.read_csv('dados_novos.csv', skiprows=1, nrows=32, encoding='iso-8859-1', sep=None, engine='python')
        df_h_raw = df_h_raw.iloc[:, :7]
        df_h_raw.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade']
        df_h_raw['Ano'] = pd.to_numeric(df_h_raw['Ano'], errors='coerce')
        df_h_raw = df_h_raw.dropna(subset=['Ano'])
        
        # B. REGIONAIS
        df_reg_raw = pd.read_csv('dados_novos.csv', skiprows=39, nrows=11, encoding='iso-8859-1', sep=None, engine='python')
        coords = {
            'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
            'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
            'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]
        }
        regionais_lista = []
        for index, row in df_reg_raw.iterrows():
            reg_nome = str(row.iloc[0]).strip()
            if reg_nome in coords:
                for i in range(1, len(row)): 
                    try:
                        ano = 2006 + i 
                        val = row.iloc[i]
                        regionais_lista.append({
                            'Regional': reg_nome, 'Ano': int(ano),
                            'Casos': pd.to_numeric(val, errors='coerce') or 0,
                            'Lat': coords[reg_nome][0], 'Lon': coords[reg_nome][1]
                        })
                    except: continue
        df_mapa = pd.DataFrame(regionais_lista)

        # C. CANINOS
        df_c_raw = pd.read_csv('caninos_novos.csv', sep=';', encoding='iso-8859-1', dtype=str)
        df_c_raw.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados']
        for col in df_c_raw.columns:
            df_c_raw[col] = df_c_raw[col].str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_c_raw[col] = pd.to_numeric(df_c_raw[col], errors='coerce').fillna(0).astype(int)
        df_c_clean = df_c_raw.copy()
        df_c_clean['Taxa_Positividade'] = (df_c_clean['Positivos'] / df_c_clean['Sorologias'] * 100).fillna(0)

        # D. VETOR
        df_v_raw = pd.read_csv('vetor.csv', sep=';', encoding='iso-8859-1', dtype=str)
        df_v_raw = df_v_raw.iloc[:, :2]
        df_v_raw.columns = ['Ano', 'Borrifados']
        for col in df_v_raw.columns:
            df_v_raw[col] = df_v_raw[col].str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_v_raw[col] = pd.to_numeric(df_v_raw[col], errors='coerce').fillna(0).astype(int)
        df_v_clean = df_v_raw.copy()

        # FILTRO FINAL DE SEGURANÇA: MÁXIMO 2025
        df_h_raw = df_h_raw[df_h_raw['Ano'] <= 2025]
        if not df_mapa.empty:
            df_mapa = df_mapa[df_mapa['Ano'] <= 2025]
        df_c_clean = df_c_clean[df_c_clean['Ano'] <= 2025]
        df_v_clean = df_v_clean[df_v_clean['Ano'] <= 2025]

        return df_h_raw, df_mapa, df_c_clean, df_v_clean
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_c, df_v = load_data()

# --- 4. MENU LATERAL ---
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

st.sidebar.markdown("### Navegação")
if st.sidebar.button("Painel Geral", use_container_width=True): st.session_state.segment = "Geral"
if st.sidebar.button("Mapa Regional", use_container_width=True): st.session_state.segment = "Mapa"
if st.sidebar.button("Vigilância Canina", use_container_width=True): st.session_state.segment = "Canina"
if st.sidebar.button("Tendências Históricas", use_container_width=True): st.session_state.segment = "Historico"

st.sidebar.link_button("Leishmaniose Canina (PBH)", "https://prefeitura.pbh.gov.br/saude/leishmaniose-visceral-canina", use_container_width=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

if not df_h.empty:
    anos = sorted(df_h['Ano'].unique().tolist(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano de análise:", options=anos, index=0)
else:
    ano_sel = 2025

st.sidebar.markdown("---")
st.sidebar.caption(f"Fonte: DIZO/SUPVISA/SMSA/PBH")
st.sidebar.caption(f"Analista: Aline Alice Ferreira da Silva | RU: 5277514")

# --- 5. CABEÇALHO ---
st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">VigiLeish: Painel de Monitoramento</h1>
        <p class="header-subtitle">Vigilância Epidemiológica de Leishmaniose Visceral em Belo Horizonte</p>
    </div>
    """, unsafe_allow_html=True)

# --- 6. CONTEÚDO ---
if st.session_state.segment == "Geral":
    st.subheader(f"Visão Consolidada | {ano_sel}")

    # Texto Explicativo (SEM ÍCONE)
    st.markdown("""
    <div class="info-box">
        <span class="info-title">Entenda os Dados</span>
        Aqui você tem um resumo rápido da situação da doença neste ano:
        <ul>
            <li><strong>Casos Humanos:</strong> Quantas pessoas foram diagnosticadas com Leishmaniose.</li>
            <li><strong>Letalidade:</strong> A gravidade da doença (porcentagem de pessoas que faleceram em relação aos casos).</li>
            <li><strong>Cães Positivos:</strong> Quantos cães fizeram o exame e tiveram o resultado confirmado para a doença.</li>
            <li><strong>Imóveis Borrifados:</strong> Casas que receberam aplicação de inseticida para matar o mosquito.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    dh = df_h[df_h['Ano']==ano_sel]
    dc = df_c[df_c['Ano']==ano_sel]
    dv = df_v[df_v['Ano']==ano_sel]
    
    st.markdown("##### Indicadores Humanos")
    col1, col2, col3 = st.columns(3)
    if not dh.empty:
        col1.metric("Casos Humanos", f"{dh['Casos'].iloc[0]}")
        col2.metric("Óbitos", f"{dh['Obitos'].iloc[0]}")
        col3.metric("Letalidade", f"{dh['Letalidade'].iloc[0]:.1f}%")
    else:
        col1.metric("Casos Humanos", "0")
        col2.metric("Óbitos", "0")
        col3.metric("Letalidade", "0%")

    st.markdown("---")

    st.markdown("##### Vigilância Canina")
    col4, col5, col6 = st.columns(3)
    if not dc.empty:
        col4.metric("Cães Positivos", f"{dc['Positivos'].iloc[0]:,}".replace(',', '.'))
        col5.metric("Eutanásias", f"{dc['Eutanasiados'].iloc[0]:,}".replace(',', '.'))
        col6.metric("Taxa Positividade", f"{dc['Taxa_Positividade'].iloc[0]:.1f}%")
    else:
        col4.metric("Cães Positivos", "0")
        col5.metric("Eutanásias", "0")
        col6.metric("Taxa Positividade", "0.0%")

    st.markdown("---")

    st.markdown("##### Testes e Controle Vetorial")
    col7, col8 = st.columns(2)
    if not dc.empty:
        col7.metric("Total Sorologias (Testes)", f"{dc['Sorologias'].iloc[0]:,}".replace(',', '.'))
    else:
        col7.metric("Total Sorologias", "0")

    if not dv.empty:
        col8.metric("Imóveis Borrifados", f"{dv['Borrifados'].iloc[0]:,}".replace(',', '.'))
    else:
        col8.metric("Imóveis Borrifados", "0")

elif st.session_state.segment == "Canina":
    st.subheader("Vigilância Canina e Controle Vetorial")

    # Texto Explicativo (SEM ÍCONE)
    st.markdown("""
    <div class="info-box">
        <span class="info-title">Por que monitoramos os cães?</span>
        Em áreas urbanas, o cão é a principal fonte de infecção. O mosquito pica o cão doente e depois transmite para o ser humano.
        <ul>
            <li><strong>Testes (Sorologias):</strong> Quantidade de exames realizados pelos agentes de saúde.</li>
            <li><strong>Positivos:</strong> Cães que foram confirmados com a doença.</li>
            <li><strong>Eutanásias:</strong> Medida de controle recomendada pelo Ministério da Saúde para cães positivos, visando reduzir a transmissão.</li>
            <li><strong>Borrifação:</strong> Controle químico aplicado nos imóveis para eliminar o mosquito vetor.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Eixo Esquerdo (Barras)
    fig.add_trace(go.Bar(
        x=df_c['Ano'], y=df_c['Positivos'], name="Cães Positivos", marker_color='#F59E0B'
    ), secondary_y=False)
    
    fig.add_trace(go.Bar(
        x=df_c['Ano'], y=df_c['Eutanasiados'], name="Eutanásias", marker_color='#B91C1C'
    ), secondary_y=False)
    
    # Eixo Direito (Linha)
    fig.add_trace(go.Scatter(
        x=df_c['Ano'], y=df_c['Sorologias'], name="Total de Testes", 
        mode='lines+markers', line=dict(color='#2E7D32', width=3)
    ), secondary_y=True)
    
    fig.update_layout(
        title="<b>Monitoramento do Reservatório Canino (1994-2025)</b>", 
        plot_bgcolor='white', 
        font_family="Lora",
        barmode='group',
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
    )
    
    fig.update_xaxes(dtick=1, range=[1993.5, 2025.5], title_text="Ano")
    fig.update_yaxes(title_text="Qtd. Animais", secondary_y=False, showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(title_text="Total Testes", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Controle Químico (Imóveis Borrifados)")
    fig_v = px.line(df_v, x='Ano', y='Borrifados', markers=True, color_discrete_sequence=['#374151'])
    fig_v.update_layout(plot_bgcolor='white', font_family="Lora", yaxis_title="Qtd. Imóveis")
    fig_v.update_xaxes(dtick=1, range=[1994, 2025])
    st.plotly_chart(fig_v, use_container_width=True)

elif st.session_state.segment == "Mapa":
    st.subheader(f"Distribuição Geográfica | {ano_sel}")

    # Texto Explicativo (SEM ÍCONE)
    st.markdown("""
    <div class="info-box">
        <span class="info-title">Onde a doença acontece?</span>
        O mapa abaixo mostra como os casos estão distribuídos pelas regionais de Belo Horizonte.
        <br>Círculos <strong>maiores e mais escuros</strong> indicam um número maior de pessoas doentes naquela região.
    </div>
    """, unsafe_allow_html=True)
    
    df_f = df_m[df_m['Ano'] == ano_sel]
    if not df_f.empty:
        fig = px.scatter_mapbox(df_f, lat="Lat", lon="Lon", size="Casos", color="Casos", zoom=10, mapbox_style="carto-positron", color_continuous_scale="Greens")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados regionais para o ano selecionado.")

    st.markdown("---")
    
    st.subheader("Histórico por Regional")
    if not df_m.empty:
        lista_regionais = sorted(df_m['Regional'].unique().tolist())
        reg_sel = st.selectbox("Selecione a Regional:", options=lista_regionais)
        
        df_reg_hist = df_m[df_m['Regional'] == reg_sel].sort_values('Ano')
        
        fig_hist_reg = px.line(df_reg_hist, x='Ano', y='Casos', markers=True,
                               title=f"Evolução dos Casos Humanos: {reg_sel}",
                               color_discrete_sequence=['#2E7D32'])
        fig_hist_reg.update_layout(plot_bgcolor='white', font_family="Lora")
        fig_hist_reg.update_xaxes(dtick=1, range=[2007, 2025]) 
        st.plotly_chart(fig_hist_reg, use_container_width=True)

elif st.session_state.segment == "Historico":
    st.subheader("Análise de Tendência: Humanos vs Caninos")

    # Texto Explicativo (SEM ÍCONE)
    st.markdown("""
    <div class="info-box">
        <span class="info-title">Qual a relação entre cães e humanos?</span>
        Este gráfico permite visualizar a conexão ao longo do tempo. Geralmente, um aumento no número de cães infectados (Linha Verde)
        pode preceder ou acompanhar o aumento de casos em humanos (Linha Pontilhada). O controle da doença nos animais é essencial para proteger as pessoas.
    </div>
    """, unsafe_allow_html=True)
    
    # Merge com outer para garantir todo o histórico desde 1994
    df_merged = pd.merge(df_h[['Ano', 'Casos']], df_c[['Ano', 'Positivos']], on='Ano', how='outer').sort_values('Ano')
    df_merged = df_merged[(df_merged['Ano'] >= 1994) & (df_merged['Ano'] <= 2025)]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Linha Cães Positivos (Verde)
    fig.add_trace(
        go.Scatter(
            x=df_merged['Ano'], 
            y=df_merged['Positivos'], 
            name="Cães Positivos",
            mode='lines+markers',
            line=dict(color='#2E7D32', width=3),
            marker=dict(size=6)
        ),
        secondary_y=False
    )

    # 2. Linha Casos Humanos (Pontilhado)
    fig.add_trace(
        go.Scatter(
            x=df_merged['Ano'], 
            y=df_merged['Casos'], 
            name="Casos Humanos",
            mode='lines+markers',
            line=dict(color='#1f2937', width=3, dash='dot'), 
            marker=dict(size=6)
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="<b>Correlação: Humano vs Canino (1994-2025)</b>",
        font_family="Lora",
        plot_bgcolor='white',
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.3, x=0.3)
    )
    
    fig.update_xaxes(title_text="Ano", dtick=1, range=[1994, 2025], showgrid=False)
    fig.update_yaxes(title_text="Cães Positivos", secondary_y=False, showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(title_text="Casos Humanos", secondary_y=True, showgrid=False)

    st.plotly_chart(fig, use_container_width=True)
