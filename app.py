import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import logging
import streamlit.components.v1 as components 
import numpy as np 

# --- 0. CONFIGURAÇÃO DE LOGGING ---
logging.basicConfig(level=logging.ERROR)

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="VigiLeish Dashboard", layout="wide", page_icon=None)

# --- 2. LOGO E SIDEBAR ---
with st.sidebar:
    st.image("dog.png", width=120) 
    
    st.markdown("### Preferências")
    
    # --- CONTROLE DE ACESSIBILIDADE ---
    st.markdown("#### Acessibilidade")
    tamanho_fonte = st.radio(
        "Tamanho do Texto:",
        ["Padrão", "Grande", "Extra Grande"],
        index=0
    )

    # Lógica de escala de fonte
    if tamanho_fonte == "Grande":
        css_root = "125%" 
        plotly_font = 16
    elif tamanho_fonte == "Extra Grande":
        css_root = "150%"
        plotly_font = 20
    else:
        css_root = "100%" 
        plotly_font = 14

    st.markdown("---")
    
    # CRÉDITOS
    st.link_button("Informações Oficiais (PBH)", "https://prefeitura.pbh.gov.br/saude/leishmaniose-visceral-canina", use_container_width=True)
    st.markdown("---")
    st.caption(f"Atualização: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption("O painel apresenta análise descritiva dos dados oficiais públicos, sem inferência causal, utilizando estatística básica e visualização interativa para apoio à vigilância epidemiológica.")
    st.caption("Fonte: DIZO/SUPVISA/SMSA/PBH")
    st.caption("Atividades Extensionistas II - Tecnologia Aplicada à Inclusão Digital - Projeto - UNINTER")
    st.caption("Analista: Aline Alice Ferreira da Silva | RU: 5277514")

# --- 3. CSS DINÂMICO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    
    html {{ font-size: {css_root} !important; }}

    .main .block-container {{ color: #1e293b; font-family: 'Lora', serif; }}
    h1, h2, h3, h4, h5, h6, p, div {{ font-family: 'Lora', serif !important; }}
    .main h2, .main h3, .main h4 {{ color: #064E3B !important; font-weight: 700 !important; }}
    
    [data-testid="stSidebar"] {{ background-color: #f7fcf9 !important; border-right: 1px solid #d1d5db; }}

    div.stButton > button {{
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid #064E3B;
        transition: all 0.3s;
    }}
    div.stButton > button[kind="secondary"] {{
        background-color: #ffffff;
        color: #064E3B;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: #064E3B !important;
        color: #ffffff !important;
        border-color: #064E3B !important;
    }}
    div.stButton > button:hover {{
        background-color: #f0fdf4 !important;
    }}

    div[data-baseweb="select"] > div {{ background-color: #ffffff !important; border-color: #5D3A9B !important; color: #1e293b !important; }}

    [data-testid="stMetric"] {{
        background-color: #ffffff; padding: 15px; border-radius: 8px;
        border: 1px solid #e2e8f0; border-left: 5px solid #5D3A9B;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .info-box {{
        background-color: #f0fdf4; border-left: 5px solid #117733; padding: 15px;
        border-radius: 5px; margin-bottom: 20px; color: #1e293b; font-size: 0.95rem;
        line-height: 1.6;
    }}
    .info-box ul {{ list-style-type: none !important; padding-left: 5px !important; margin-top: 10px !important; }}
    .info-box li {{ margin-bottom: 10px !important; }}
    .info-title {{ color: #117733; font-weight: bold; margin-bottom: 8px; display: block; font-size: 1.15rem; }}

    .header-container {{
        background-color: #064E3B; padding: 40px 20px; border-radius: 8px; margin-bottom: 30px;
        text-align: center; border-bottom: 4px solid #C2410C;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .header-title {{ color: #ffffff !important; font-size: 2.2rem !important; margin: 0 !important; font-weight: 700 !important; }}
    .header-subtitle {{ color: #dcfce7 !important; margin-top: 10px !important; font-size: 1.0rem; font-style: italic; }}
    .sidebar-logo {{ display: flex; justify-content: center; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    try:
        # A. HUMANOS
        df_h_raw = pd.read_csv('dados_novos.csv', skiprows=1, nrows=60, encoding='iso-8859-1', sep=None, engine='python')
        df_h_raw = df_h_raw.iloc[:, :7]
        df_h_raw.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade']
        df_h_raw['Ano'] = pd.to_numeric(df_h_raw['Ano'], errors='coerce')
        df_h_raw = df_h_raw.dropna(subset=['Ano'])
        df_h_raw['Ano'] = df_h_raw['Ano'].astype(int)
        
        media_let = df_h_raw['Letalidade'].mean()
        dp_let = df_h_raw['Letalidade'].std()
        limiar_letalidade = media_let + (2 * dp_let)

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
                        val_num = pd.to_numeric(val, errors='coerce')
                        if pd.isna(val_num): val_num = 0
                        regionais_lista.append({
                            'Regional': reg_nome, 'Ano': int(ano),
                            'Casos': val_num,
                            'Lat': coords[reg_nome][0], 'Lon': coords[reg_nome][1]
                        })
                    except: continue
        df_mapa = pd.DataFrame(regionais_lista)

        # C. CÃES
        df_c_raw = pd.read_csv('caninos_novos.csv', sep=';', encoding='iso-8859-1', dtype=str)
        df_c_raw.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados']
        for col in df_c_raw.columns:
            df_c_raw[col] = df_c_raw[col].str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_c_raw[col] = pd.to_numeric(df_c_raw[col], errors='coerce').fillna(0)
        df_c_raw['Ano'] = df_c_raw['Ano'].astype(int)
        df_c_clean = df_c_raw.copy()
        df_c_clean['Taxa_Positividade'] = np.where(df_c_clean['Sorologias'] > 0, (df_c_clean['Positivos'] / df_c_clean['Sorologias'] * 100), 0)

        # D. VETOR
        df_v_raw = pd.read_csv('vetor.csv', sep=';', encoding='iso-8859-1', dtype=str)
        df_v_raw = df_v_raw.iloc[:, :2]
        df_v_raw.columns = ['Ano', 'Borrifados']
        for col in df_v_raw.columns:
            df_v_raw[col] = df_v_raw[col].str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_v_raw[col] = pd.to_numeric(df_v_raw[col], errors='coerce').fillna(0)
        df_v_raw['Ano'] = df_v_raw['Ano'].astype(int)
        df_v_clean = df_v_raw.copy()

        min_ano_encontrado = int(df_h_raw['Ano'].min())
        min_ano_global = min(1994, min_ano_encontrado)
        max_ano_global = int(df_h_raw['Ano'].max())

        return df_h_raw, df_mapa, df_c_clean, df_v_clean, limiar_letalidade, min_ano_global, max_ano_global

    except Exception as e:
        logging.error(f"ERRO: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 10, 1994, 2025

df_h, df_m, df_c, df_v, limiar_stat, min_ano, max_ano = load_data()

# --- 5. CABEÇALHO ---
st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">VigiLeish: Painel de Monitoramento</h1>
        <p class="header-subtitle">Vigilância Epidemiológica de Leishmaniose Visceral em Belo Horizonte</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# GESTÃO DE ESTADO (MEMÓRIA)
# ---------------------------------------------------------------------

# 1. Navegação
if 'segment' not in st.session_state:
    st.session_state.segment = "Geral"

# 2. Ano Selecionado (Persistência)
# Garante que 'ano_selecionado' exista no session_state
if 'ano_selecionado' not in st.session_state:
    if not df_h.empty:
        # Define o ano mais recente como padrão inicial
        st.session_state.ano_selecionado = int(df_h['Ano'].max())
    else:
        st.session_state.ano_selecionado = 2025

# ---------------------------------------------------------------------
# BARRA DE NAVEGAÇÃO E FILTRO
# ---------------------------------------------------------------------
def get_btn_type(btn_name):
    return "primary" if st.session_state.segment == btn_name else "secondary"

c1, c2, c3, c4, c_ano = st.columns([1, 1, 1, 1, 1.5])

with c1:
    if st.button("Painel Geral", type=get_btn_type("Geral"), use_container_width=True):
        st.session_state.segment = "Geral"
        st.rerun()
with c2:
    if st.button("Mapa", type=get_btn_type("Mapa"), use_container_width=True):
        st.session_state.segment = "Mapa"
        st.rerun()
with c3:
    if st.button("Cães", type=get_btn_type("Canina"), use_container_width=True):
        st.session_state.segment = "Canina"
        st.rerun()
with c4:
    if st.button("Histórico", type=get_btn_type("Historico"), use_container_width=True):
        st.session_state.segment = "Historico"
        st.rerun()

with c_ano:
    if not df_h.empty:
        lista_anos = sorted(df_h['Ano'].unique().tolist(), reverse=True)
        
        try:
            indice_atual = lista_anos.index(st.session_state.ano_selecionado)
        except ValueError:
            indice_atual = 0 # Se der erro (ano não existe), pega o primeiro
         
        sel = st.selectbox(
            "Selecione o Ano:", 
            options=lista_anos, 
            index=indice_atual, # Força o valor visual a ser o que está na memória
            key="ano_widget",   # Nome interno do widget
            label_visibility="collapsed"
        )
        
        if sel != st.session_state.ano_selecionado:
            st.session_state.ano_selecionado = sel
            st.rerun() # Recarrega para aplicar o filtro
            
    else:
        st.session_state.ano_selecionado = 2025

ano_sel = st.session_state.ano_selecionado

# -----------------------------------------------------
# FIX DE SCROLL
# -----------------------------------------------------
components.html(
    f"""
        <script>
            window.parent.scrollTo(0, 0);
            var main = window.parent.document.querySelector(".main");
            if (main) {{ main.scrollTop = 0; }}
        </script>
        """,
    height=0,
    width=0
)

# --- 7. CONTEÚDO ---

if st.session_state.segment == "Geral":
    st.subheader(f"Visão Consolidada | {ano_sel}")

    st.markdown("""
    <div style="margin-bottom: 20px;">
        Abaixo apresentamos um resumo rápido da situação da doença no ano selecionado, dividido por categorias:
    </div>
    """, unsafe_allow_html=True)
    
    dh = df_h[df_h['Ano']==ano_sel]
    dc = df_c[df_c['Ano']==ano_sel]
    dv = df_v[df_v['Ano']==ano_sel]
    
    # --- BLOCO 1: SAÚDE HUMANA ---
    st.markdown("##### 1. Indicadores Humanos")
    st.markdown(f"""
    <div class="info-box">
        <ul>
            <li><strong>Casos Humanos:</strong> Quantas pessoas foram diagnosticadas com leishmaniose no ano selecionado.</li>
            <li><strong>Óbitos:</strong> Número de pessoas que faleceram em decorrência da doença.</li>
            <li><strong>Letalidade (%):</strong> Indica a gravidade dos casos. Se este número aumenta, significa que a doença está sendo mais fatal. <br><i><b>Nota:</b> Valores acima de {limiar_stat:.1f}% aparecem com alerta em laranja (Cálculo estatístico: Média + 2 Desvios Padrão).</i></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    if not dh.empty:
        col1.metric("Casos Humanos", f"{int(dh['Casos'].iloc[0])}")
        col2.metric("Óbitos", f"{int(dh['Obitos'].iloc[0])}")
        
        letalidade = dh['Letalidade'].iloc[0]
        if letalidade >= limiar_stat:
            cor_borda = "#C2410C" 
            icone = "ALTA"
            cor_texto = "#C2410C"
        else:
            cor_borda = "#1e293b"
            icone = "Estável"
            cor_texto = "#1e293b"

        col3.markdown(f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 6px solid {cor_borda};">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 5px; font-family: 'Lora', serif;">Letalidade</p>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <p style="color: {cor_texto}; font-size: 1.8rem; font-weight: 700; margin: 0; font-family: 'Lora', serif;">{letalidade:.1f}%</p>
                    <span style="font-size: 0.9rem; font-weight: bold; color: {cor_texto}; background: #fff3e0; padding: 2px 6px; border-radius: 4px;">{icone}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        col1.metric("Casos Humanos", "0"); col2.metric("Óbitos", "0"); col3.metric("Letalidade", "0%")

    st.markdown("---")

    # --- BLOCO 2: RESERVATÓRIO CANINO ---
    st.markdown("##### 2. Vigilância Canina")
    st.markdown("""
    <div class="info-box">
        <ul>
            <li><strong>Cães Positivos:</strong> Quantidade de animais que fizeram o exame e tiveram a doença confirmada.</li>
            <li><strong>Eutanásias:</strong> Medida de saúde pública recomendada para interromper o ciclo de transmissão da doença (cão infectado → mosquito → humano).</li>
            <li><strong>Taxa de Positividade (%):</strong> Proporção de cães doentes entre todos os que foram testados no ano. Funciona como um "termômetro". Se essa taxa sobe, é um sinal de que a leishmaniose está circulando com mais intensidade entre os animais.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    if not dc.empty:
        col4.metric("Cães Positivos", f"{int(dc['Positivos'].iloc[0]):,}".replace(',', '.'))
        col5.metric("Eutanásias", f"{int(dc['Eutanasiados'].iloc[0]):,}".replace(',', '.'))
        col6.metric("Taxa Positividade", f"{dc['Taxa_Positividade'].iloc[0]:.1f}%")
    else:
        col4.metric("Cães Positivos", "0"); col5.metric("Eutanásias", "0"); col6.metric("Taxa Positividade", "0.0%")

    st.markdown("---")

    # --- BLOCO 3: AÇÕES DE CONTROLE ---
    st.markdown("##### 3. Ações de Controle e Testes")
    st.markdown("""
    <div class="info-box">
        <ul>
            <li><strong>Total Sorologias (Testes):</strong> Representa o esforço da vigilância em testar a população canina para identificar os animais infectados.</li>
            <li><strong>Imóveis Borrifados:</strong> <b>Controle Vetorial</b>, ou seja, quantas casas receberam aplicação de inseticida (o famoso "fumacê" ou borrifação residual) para eliminar o mosquito palha transmissor da doença (vetor).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col7, col8 = st.columns(2)
    if not dc.empty:
        col7.metric("Total Sorologias (Testes)", f"{int(dc['Sorologias'].iloc[0]):,}".replace(',', '.'))
    else: col7.metric("Total Sorologias", "0")

    if not dv.empty:
        col8.metric("Imóveis Borrifados", f"{int(dv['Borrifados'].iloc[0]):,}".replace(',', '.'))
    else: col8.metric("Imóveis Borrifados", "0")

elif st.session_state.segment == "Canina":
    st.subheader("Vigilância Canina e Controle Vetorial")

    # --- PARTE 1: BARRAS ---
    st.markdown("""
    <div class="info-box">
        <span class="info-title">Por que monitoramos os cães?</span>
        Em áreas urbanas, o cão é a principal fonte de infecção. O mosquito pica o cão doente e depois transmite, através da picada, para o ser humano.
        <br><br>
        <b>Guia visual do gráfico:</b>
        <ul>
            <li><span style='color:#C2410C; font-weight:bold;'>■ Barras Laranjas:</span> <strong>Cães Positivos</strong> Cães que foram confirmados com a doença.</li>
            <li><span style='color:#5D3A9B; font-weight:bold;'>■ Barras Roxas:</span> <strong>Eutanásias:</strong> Medida de saúde pública para controle de reservatório. <br><i>(<b>Nota:</b> Embora controversa, é a medida técnica oficial vigente para interrupção do ciclo de transmissão em massa).</i>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Positivos'], name="Cães Positivos", marker_color='#C2410C'))
    fig_bar.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Eutanasiados'], name="Eutanásias", marker_color='#5D3A9B'))
    
    fig_bar.update_layout(height=400, plot_bgcolor='white', font_family="Lora", barmode='group',
                          font=dict(size=plotly_font),
                          title="Casos Positivos e Eutanásias em Cães",
                          legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center"))
    
    fig_bar.update_yaxes(tickformat=".,d", gridcolor='#f1f5f9', title_text="Qtd. Animais")
    fig_bar.update_xaxes(dtick=1, range=[min_ano-0.5, max_ano+0.5], title_text="Ano")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # --- PARTE 2: LINHA ---
    st.markdown("""
    <div class="info-box">
        <span class="info-title">Monitoramento de Testes</span>
        <ul>
            <li><span style='color:#117733; font-weight:bold;'>● Linha Verde:</span> <strong>Total de Testes</strong> Mostra o volume de trabalho da vigilância epidemiológica na busca por animais infectados. Quanto maior o número de testes, maior a capacidade de identificar e controlar a doença.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_c['Ano'], y=df_c['Sorologias'], name="Total de Testes", mode='lines+markers', line=dict(color='#117733', width=3)))
    
    fig_line.update_layout(height=400, plot_bgcolor='white', font_family="Lora",
                           font=dict(size=plotly_font),
                           title="Total de Sorologias (Testes) Realizados",
                           legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
    
    fig_line.update_yaxes(tickformat=".,d", gridcolor='#f1f5f9', title_text="Total Testes")
    fig_line.update_xaxes(dtick=1, range=[min_ano-0.5, max_ano+0.5], title_text="Ano")
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("---")
    
    # --- PARTE 3: BORRIFAÇÃO ---
    st.subheader("Controle Químico (Imóveis Borrifados)")
    
    st.markdown("""
    <div class="info-box">
        O gráfico abaixo mostra a evolução do <b>Controle Vetorial</b> (visitas para aplicação de inseticida).
    </div>
    """, unsafe_allow_html=True)

    fig_v = px.line(df_v, x='Ano', y='Borrifados', markers=True, color_discrete_sequence=['#374151'])
    fig_v.update_layout(plot_bgcolor='white', font_family="Lora", yaxis_title="Qtd. Imóveis",
                        font=dict(size=plotly_font),
                        legend=dict(orientation="h", y=1.1, x=0.5))
    fig_v.update_yaxes(tickformat=".,d") 
    fig_v.update_xaxes(dtick=1, range=[min_ano, max_ano])
    st.plotly_chart(fig_v, use_container_width=True)

elif st.session_state.segment == "Mapa":
    st.subheader(f"Distribuição Geográfica | {ano_sel}")

    st.markdown("""
    <div class="info-box">
        <span class="info-title">Como ler este mapa?</span>
        <ul>
            <li style="margin-bottom: 8px;">
                <span style='background-color: #FDE725; padding: 2px 6px; color: black; border-radius: 4px; font-weight: bold;'>Amarelo / Claro / Círculos menores:</span>
                Regiões com <b>menos casos</b>.
            </li>
            <li>
                <span style='background-color: #440154; padding: 2px 6px; color: white; border-radius: 4px; font-weight: bold;'>Roxo / Escuro / Círculos maiores:</span>
                Regiões com <b>maior concentração de casos</b> (Alerta).
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    df_f = df_m[df_m['Ano'] == ano_sel]
    if not df_f.empty:
        fig = px.scatter_mapbox(df_f, lat="Lat", lon="Lon", size="Casos", color="Casos", zoom=10, 
                                mapbox_style="carto-positron", 
                                color_continuous_scale="Viridis_r",
                                hover_name="Regional",
                                hover_data={"Lat": False, "Lon": False, "Casos": True}) 
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500, font=dict(size=plotly_font))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados regionais para o ano selecionado.")

    st.markdown("---")
    
    st.subheader("Histórico por Regional")

    st.markdown("""
    <div class="info-box">
        <span class="info-title">História da Regional</span>
        Este gráfico permite analisar o passado. Selecione uma regional na lista abaixo para ver se o número de casos aumentou ou diminuiu naquela área específica ao longo dos anos.
        <ul>
            <li><span style='color:#117733; font-weight:bold;'>● Linha Verde:</span> Mostra a variação dos casos confirmados.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if not df_m.empty:
        c_reg, c_slider = st.columns([1, 2])
        lista_regionais = sorted(df_m['Regional'].unique().tolist())
        min_ano_regional = 2007
        
        with c_reg:
            reg_sel = st.selectbox("Selecione a Regional:", options=lista_regionais)
        
        with c_slider:
            intervalo_anos = st.slider(
                "Filtrar Período (Anos):",
                min_value=min_ano_regional,
                max_value=max_ano,
                value=(min_ano_regional, max_ano)
            )
        
        df_reg_hist = df_m[
            (df_m['Regional'] == reg_sel) & 
            (df_m['Ano'] >= intervalo_anos[0]) & 
            (df_m['Ano'] <= intervalo_anos[1])
        ].sort_values('Ano')
        
        fig_hist_reg = px.line(df_reg_hist, x='Ano', y='Casos', markers=True,
                               title=f"Evolução dos Casos Humanos: {reg_sel} ({intervalo_anos[0]}-{intervalo_anos[1]})",
                               color_discrete_sequence=['#117733']) 
        fig_hist_reg.update_layout(plot_bgcolor='white', font_family="Lora", font=dict(size=plotly_font))
        fig_hist_reg.update_xaxes(dtick=1, range=[intervalo_anos[0]-0.5, intervalo_anos[1]+0.5]) 
        st.plotly_chart(fig_hist_reg, use_container_width=True)

elif st.session_state.segment == "Historico":
    st.subheader("Análise de Tendência: Humanos vs Caninos")

    st.markdown("""
    <div class="info-box">
        <span class="info-title">Correlação Histórica</span>
        Acompanhe a relação entre as populações ao longo das décadas.
        <ul>
            <li><span style='color:#C2410C; font-weight:bold;'>● Linha Laranja (Eixo Esquerdo):</span> <strong>Cães Positivos</strong>.</li>
            <li><span style='color:#5D3A9B; font-weight:bold;'>● Linha Roxa (Eixo Direito):</span> <strong>Casos Humanos</strong>.</li>
        </ul>
        Este gráfico permite visualizar a conexão ao longo do tempo. Geralmente, um aumento no número de cães infectados
        pode preceder ou acompanhar o aumento de casos em humanos. O controle da doença nos animais é essencial para proteger as pessoas.
    </div>
    """, unsafe_allow_html=True)
    
    df_merged = pd.merge(df_h[['Ano', 'Casos']], df_c[['Ano', 'Positivos']], on='Ano', how='outer').sort_values('Ano')
    df_merged = df_merged[(df_merged['Ano'] >= min_ano) & (df_merged['Ano'] <= max_ano)]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_merged['Ano'], y=df_merged['Positivos'], name="Cães Positivos",
            mode='lines+markers', line=dict(color='#C2410C', width=3), marker=dict(size=6)
        ), secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_merged['Ano'], y=df_merged['Casos'], name="Casos Humanos",
            mode='lines+markers', line=dict(color='#5D3A9B', width=3, dash='dot'), marker=dict(size=6)
        ), secondary_y=True
    )

    fig.update_layout(
        title="<b>Correlação: Humano vs Canino</b>",
        font_family="Lora", plot_bgcolor='white', hovermode="x unified",
        font=dict(size=plotly_font),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
    )
    
    fig.update_xaxes(title_text="Ano", dtick=1, range=[min_ano, max_ano], showgrid=False)
    fig.update_yaxes(title_text="Cães Positivos", tickformat=".,d", secondary_y=False, showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(title_text="Casos Humanos", tickformat=".,d", secondary_y=True, showgrid=False)

    st.plotly_chart(fig, use_container_width=True)



