import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import logging

# --- 0. CONFIGURAÇÃO DE LOGGING (Engenharia de Software) ---
# Erros técnicos vão para o console, não para a tela do usuário
logging.basicConfig(level=logging.ERROR)

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="VigiLeish Intelligence Dashboard", layout="wide", page_icon="dog.png")

# --- 2. LOGO E MENU LATERAL (Início) ---
with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("dog.png", width=120) 
    st.markdown('</div>', unsafe_allow_html=True)

    # --- CONTROLE DE ACESSIBILIDADE (Visual) ---
    st.markdown("### 👁️ Acessibilidade")
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

# --- 3. ESTILO CSS DINÂMICO ---
# Injetamos a variável {css_root} para alterar o tamanho de tudo proporcionalmente
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    
    html {{ font-size: {css_root} !important; }}

    /* Fonte Geral */
    .main .block-container {{ color: #1e293b; font-family: 'Lora', serif; }}
    h1, h2, h3, h4, h5, h6, p, div {{ font-family: 'Lora', serif !important; }}
    
    /* Títulos */
    .main h2, .main h3, .main h4 {{ color: #064E3B !important; font-weight: 700 !important; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: #f7fcf9 !important; border-right: 1px solid #d1d5db; }}
    
    /* Filtros e Botões */
    div[data-baseweb="select"] > div {{ background-color: #ffffff !important; border-color: #5D3A9B !important; color: #1e293b !important; }}
    div.stButton > button, div.stLinkButton > a {{
        background-color: #ffffff !important; color: #064E3B !important; border: 1px solid #2E7D32 !important; 
        border-radius: 6px !important; font-weight: 600 !important;
    }}
    
    /* Métricas */
    [data-testid="stMetric"] {{
        background-color: #ffffff; padding: 15px; border-radius: 8px;
        border: 1px solid #e2e8f0; border-left: 5px solid #5D3A9B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    /* Caixas Explicativas */
    .info-box {{
        background-color: #f0fdf4; border-left: 5px solid #117733; padding: 15px;
        border-radius: 5px; margin-bottom: 20px; color: #1e293b; font-size: 0.95rem;
        line-height: 1.6;
    }}
    .info-title {{ color: #117733; font-weight: bold; margin-bottom: 8px; display: block; font-size: 1.15rem; }}

    /* Cabeçalho */
    .header-container {{
        background-color: #064E3B; padding: 40px 20px; border-radius: 8px; margin-bottom: 30px;
        text-align: center; border-bottom: 4px solid #C2410C; /* Laranja Acessível */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .header-title {{ color: #ffffff !important; font-size: 2.2rem !important; margin: 0 !important; font-weight: 700 !important; }}
    .header-subtitle {{ color: #dcfce7 !important; margin-top: 10px !important; font-size: 1.0rem; font-style: italic; }}
    
    .sidebar-logo {{ display: flex; justify-content: center; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CARREGAMENTO DE DADOS (Com Logs e Validação) ---
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

        # FILTROS E VALIDAÇÃO DE FAIXAS (Sanity Check)
        df_h_raw = df_h_raw[df_h_raw['Ano'] <= 2025]
        # Evitar erros de plotagem com dados negativos
        df_h_raw = df_h_raw[df_h_raw['Casos'] >= 0] 
        
        if not df_mapa.empty: df_mapa = df_mapa[df_mapa['Ano'] <= 2025]
        df_c_clean = df_c_clean[df_c_clean['Ano'] <= 2025]
        df_v_clean = df_v_clean[df_v_clean['Ano'] <= 2025]

        return df_h_raw, df_mapa, df_c_clean, df_v_clean

    except Exception as e:
        # LOGGING: Registra o erro no terminal, mas não quebra o site
        logging.error(f"ERRO CRÍTICO NO CARREGAMENTO DE DADOS: {e}")
        st.warning("⚠️ O sistema encontrou uma instabilidade ao carregar os dados. Algumas visualizações podem estar indisponíveis.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_c, df_v = load_data()

# --- 5. CONTINUAÇÃO DO MENU LATERAL ---
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

with st.sidebar:
    st.markdown("### Menu de Navegação")
    
    if not df_h.empty:
        anos = sorted(df_h['Ano'].unique().tolist(), reverse=True)
        ano_sel = st.selectbox("Selecione o ano:", options=anos, index=0)
    else:
        ano_sel = 2025

    if st.button("Painel Geral", use_container_width=True): st.session_state.segment = "Geral"
    if st.button("Mapa Regional", use_container_width=True): st.session_state.segment = "Mapa"
    if st.button("Vigilância Canina", use_container_width=True): st.session_state.segment = "Canina"
    if st.button("Tendências Históricas", use_container_width=True): st.session_state.segment = "Historico"

    st.link_button("Informações (PBH)", "https://prefeitura.pbh.gov.br/saude/leishmaniose-visceral-canina", use_container_width=True)

    st.markdown("---")
    st.caption(f"📅 Atualização: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption(f"Fonte: DIZO/SUPVISA/SMSA/PBH")
    st.caption(f"Projeto: Tecnologia Aplicada à Inclusão Digital - UNINTER")
    st.caption(f"Analista: Aline Alice Ferreira da Silva | RU: 5277514")

# --- 6. CABEÇALHO ---
st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">VigiLeish: Painel de Monitoramento</h1>
        <p class="header-subtitle">Vigilância Epidemiológica de Leishmaniose Visceral em Belo Horizonte</p>
    </div>
    """, unsafe_allow_html=True)

# --- 7. CONTEÚDO ---
if st.session_state.segment == "Geral":
    st.subheader(f"Visão Consolidada | {ano_sel}")

    st.markdown("""
    <div class="info-box">
        <span class="info-title">Entenda os Dados</span>
        Abaixo apresentamos um resumo da situação da Leishmaniose Visceral neste ano. O objetivo é facilitar o entendimento sobre a gravidade e o controle da doença:
        <ul>
            <li><strong>Casos Humanos:</strong> Total de pessoas diagnosticadas com a doença no ano selecionado.</li>
            <li><strong>Letalidade (%):</strong> Indica a gravidade dos casos. Se este número aumenta, significa que a doença está sendo mais fatal, muitas vezes por demora na busca por ajuda médica. <br><i><b>Nota:</b> Valores acima de 10% aparecem com alerta em laranja ⚠️.</i></li>
            <li><strong>Cães Positivos:</strong> Quantidade de animais que fizeram o exame e tiveram a doença confirmada.</li>
            <li><strong>Taxa de Positividade (%):</strong> Funciona como um "termômetro". Ela mostra a porcentagem de exames que deram positivo. Se essa taxa sobe, é sinal de que o parasita está circulando com força entre os cães da região.</li>
            <li><strong>Imóveis Borrifados:</strong> Número de casas que receberam a aplicação de inseticida para eliminar o mosquito palha (vetor da doença).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    dh = df_h[df_h['Ano']==ano_sel]
    dc = df_c[df_c['Ano']==ano_sel]
    dv = df_v[df_v['Ano']==ano_sel]
    
    st.markdown("##### Indicadores Humanos")
    col1, col2, col3 = st.columns(3)
    if not dh.empty:
        col1.metric("Casos Humanos", f"{int(dh['Casos'].iloc[0])}")
        col2.metric("Óbitos", f"{int(dh['Obitos'].iloc[0])}")
        
        # ALERTA DE LETALIDADE COM COR ACESSÍVEL (#C2410C)
        letalidade = dh['Letalidade'].iloc[0]
        if letalidade > 10:
            cor_borda = "#C2410C" 
            icone = "⚠️ ALTA"
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

    st.markdown("##### Vigilância Canina")
    col4, col5, col6 = st.columns(3)
    if not dc.empty:
        col4.metric("Cães Positivos", f"{int(dc['Positivos'].iloc[0]):,}".replace(',', '.'))
        col5.metric("Eutanásias", f"{int(dc['Eutanasiados'].iloc[0]):,}".replace(',', '.'))
        col6.metric("Taxa Positividade", f"{dc['Taxa_Positividade'].iloc[0]:.1f}%")
    else:
        col4.metric("Cães Positivos", "0"); col5.metric("Eutanásias", "0"); col6.metric("Taxa Positividade", "0.0%")

    st.markdown("---")

    st.markdown("##### Testes e Controle Vetorial")
    col7, col8 = st.columns(2)
    if not dc.empty:
        col7.metric("Total Sorologias (Testes)", f"{int(dc['Sorologias'].iloc[0]):,}".replace(',', '.'))
    else: col7.metric("Total Sorologias", "0")

    if not dv.empty:
        col8.metric("Imóveis Borrifados", f"{int(dv['Borrifados'].iloc[0]):,}".replace(',', '.'))
    else: col8.metric("Imóveis Borrifados", "0")

elif st.session_state.segment == "Canina":
    st.subheader("Vigilância Canina e Controle Vetorial")

    st.markdown("""
    <div class="info-box">
        <span class="info-title">Por que monitoramos os cães?</span>
        Em áreas urbanas, o cão é o principal <b>reservatório</b> da doença. O monitoramento contínuo permite ações rápidas.
        <br><br>
        <b>Guia visual do gráfico:</b>
        <ul>
            <li><span style='color:#C2410C; font-weight:bold;'>■ Barras Laranjas:</span> <strong>Cães Positivos</strong> (Confirmados com a doença).</li>
            <li><span style='color:#5D3A9B; font-weight:bold;'>■ Barras Roxas:</span> <strong>Eutanásias</strong> (Controle de reservatório).</li>
            <li><span style='color:#117733; font-weight:bold;'>● Linha Verde:</span> <strong>Total de Testes</strong> (Volume de trabalho da vigilância).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    dc_ano = df_c[df_c['Ano'] == ano_sel]
    col1, col2, col3 = st.columns(3)
    if not dc_ano.empty:
        col1.metric("Cães Positivos", f"{int(dc_ano['Positivos'].iloc[0]):,}".replace(',', '.'))
        col2.metric("Eutanásias", f"{int(dc_ano['Eutanasiados'].iloc[0]):,}".replace(',', '.'))
        col3.metric("Taxa Positividade", f"{dc_ano['Taxa_Positividade'].iloc[0]:.1f}%")
    else:
        col1.metric("Cães Positivos", "0"); col2.metric("Eutanásias", "0"); col3.metric("Taxa Positividade", "0.0%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # GRÁFICO COM COR ACESSÍVEL (#C2410C)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1,
                        subplot_titles=("Positivos e Eutanásias (Qtd. Animais)", "Total de Testes Realizados"))

    fig.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Positivos'], name="Cães Positivos", marker_color='#C2410C'), row=1, col=1)
    fig.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Eutanasiados'], name="Eutanásias", marker_color='#5D3A9B'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c['Ano'], y=df_c['Sorologias'], name="Total de Testes", mode='lines+markers', line=dict(color='#117733', width=3)), row=2, col=1)
    
    fig.update_layout(height=700, plot_bgcolor='white', font_family="Lora", barmode='group',
                      font=dict(size=plotly_font),
                      legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center")) 
    
    fig.update_yaxes(tickformat=".,d", gridcolor='#f1f5f9')
    fig.update_xaxes(dtick=1, range=[1993.5, 2025.5])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
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
    fig_v.update_xaxes(dtick=1, range=[1994, 2025])
    st.plotly_chart(fig_v, use_container_width=True)

elif st.session_state.segment == "Mapa":
    st.subheader(f"Distribuição Geográfica | {ano_sel}")

    st.markdown("""
    <div class="info-box">
        <span class="info-title">Como ler este mapa?</span>
        Utilizamos uma escala de cores segura (Viridis) para identificar onde a doença está mais ativa.
        <ul>
            <li><span style='background-color: #FDE725; padding: 0 5px; color: black;'><b>Amarelo / Claro:</b></span> Regiões com <b>menos casos</b>.</li>
            <li><span style='background-color: #440154; padding: 0 5px; color: white;'><b>Roxo / Escuro:</b></span> Regiões com <b>maior concentração de casos</b> (Alerta).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    df_f = df_m[df_m['Ano'] == ano_sel]
    if not df_f.empty:
        fig = px.scatter_mapbox(df_f, lat="Lat", lon="Lon", size="Casos", color="Casos", zoom=10, 
                                mapbox_style="carto-positron", 
                                color_continuous_scale="Viridis_r") 
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500, font=dict(size=plotly_font))
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
                               color_discrete_sequence=['#117733']) 
        fig_hist_reg.update_layout(plot_bgcolor='white', font_family="Lora", font=dict(size=plotly_font))
        fig_hist_reg.update_xaxes(dtick=1, range=[2007, 2025]) 
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
        Observe como as curvas frequentemente se acompanham.
    </div>
    """, unsafe_allow_html=True)
    
    df_merged = pd.merge(df_h[['Ano', 'Casos']], df_c[['Ano', 'Positivos']], on='Ano', how='outer').sort_values('Ano')
    df_merged = df_merged[(df_merged['Ano'] >= 1994) & (df_merged['Ano'] <= 2025)]
    
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
        title="<b>Correlação: Humano vs Canino (1994-2025)</b>",
        font_family="Lora", plot_bgcolor='white', hovermode="x unified",
        font=dict(size=plotly_font),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
    )
    
    fig.update_xaxes(title_text="Ano", dtick=1, range=[1994, 2025], showgrid=False)
    fig.update_yaxes(title_text="Cães Positivos", tickformat=".,d", secondary_y=False, showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(title_text="Casos Humanos", tickformat=".,d", secondary_y=True, showgrid=False)

    st.plotly_chart(fig, use_container_width=True)
