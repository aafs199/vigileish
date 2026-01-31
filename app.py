import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DESIGN SYSTEM (Estética Premium)
st.set_page_config(page_title="VigiLeish | Intelligence System", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #fcfcfd;
    }
    
    /* Botões de Navegação Customizados */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        font-weight: 400;
        transition: all 0.2s;
        text-align: left;
    }
    div.stButton > button:hover {
        border-color: #d32f2f;
        color: #d32f2f;
        background-color: #fffafa;
    }
    
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS
@st.cache_data
def load_refined_data():
    try:
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df.columns = [c.strip() for c in df.columns]
        
        # Histórico (Ajustado para o intervalo 2007-2024 do seu arquivo)
        df_hist = df.iloc[13:31].copy()
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df.columns[7:])
        for c in ['Casos', 'Obitos', 'Letalidade']:
            df_hist[c] = pd.to_numeric(df_hist[c], errors='coerce').fillna(0)
        
        # Regionais
        reg_names = ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova']
        coords = {
            'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
            'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
            'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]
        }
        
        reg_list = []
        for reg in reg_names:
            row = df[df.iloc[:,0].str.contains(reg, na=False, case=False)].iloc[0]
            for i, ano in enumerate(range(2007, 2024)):
                reg_list.append({
                    'Regional': reg, 'Ano': ano,
                    'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'),
                    'Lat': coords[reg][0], 'Lon': coords[reg][1]
                })
        return df_hist, pd.DataFrame(reg_list)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_h, df_m = load_refined_data()

# 3. SIDEBAR: NAVEGAÇÃO E CONTROLES
st.sidebar.title("VigiLeish Navigator")

# Seleção de Setor (Navegação)
st.sidebar.markdown("### Setores de Informação")
if 'segment' not in st.session_state:
    st.session_state.segment = "Geral"

if st.sidebar.button("📊 Painel Geral"):
    st.session_state.segment = "Geral"
if st.sidebar.button("🗺️ Monitoramento Geográfico"):
    st.session_state.segment = "Mapa"
if st.sidebar.button("📈 Evolução Histórica"):
    st.session_state.segment = "Historico"
if st.sidebar.button("📋 Diretrizes Estratégicas"):
    st.session_state.segment = "Diretrizes"

st.sidebar.markdown("---")
ano_alvo = st.sidebar.select_slider("Ano de Referência:", options=sorted(df_m['Ano'].unique()), value=2023)

st.sidebar.markdown("---")
st.sidebar.caption(f"Responsável: Aline Alice Ferreira da Silva")
st.sidebar.caption(f"RU: 5277514")

# 4. LÓGICA DE EXIBIÇÃO POR SETOR
st.title("VigiLeish Intelligence")

# --- SETOR 1: PAINEL GERAL ---
if st.session_state.segment == "Geral":
    st.subheader(f"Visão Consolidada | Belo Horizonte {ano_alvo}")
    
    df_ano = df_h[df_h['Ano'].astype(str).str.contains(str(ano_alvo))]
    if not df_ano.empty:
        casos_n = df_ano['Casos'].iloc[0]
        obitos_n = df_ano['Obitos'].iloc[0]
        letalidade_n = (obitos_n / casos_n * 100) if casos_n > 0 else 0
    else:
        casos_n, obitos_n, letalidade_n = 0, 0, 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Incidência Anual", f"{casos_n:.0f}")
    m2.metric("Óbitos Confirmados", f"{obitos_n:.0f}")
    m3.metric("Taxa de Letalidade", f"{letalidade_n:.2f}%")
    m4.metric("Nível de Risco", "Crítico" if letalidade_n > 15 else "Alerta")
    
    st.markdown("---")
    st.info("Utilize o menu lateral para explorar os dados geográficos e as séries históricas detalhadas.")

# --- SETOR 2: ANÁLISE GEOGRÁFICA ---
elif st.session_state.segment == "Mapa":
    st.subheader(f"Mapeamento de Calor e Ranking Regional ({ano_alvo})")
    df_map_filt = df_m[df_m['Ano'] == ano_alvo]
    
    col_a, col_b = st.columns([1.8, 1])
    with col_a:
        # MAPA COM CORES TÉRMICAS (Solicitado: Amarelo -> Laranja -> Vermelho)
        fig_map = px.scatter_mapbox(
            df_map_filt, lat="Lat", lon="Lon", size="Casos", color="Casos",
            hover_name="Regional", size_max=35, zoom=10.5,
            color_continuous_scale="YlOrRd", # Escala Amarelo-Laranja-Vermelho
            mapbox_style="carto-positron"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map, use_container_width=True)

    with col_b:
        fig_rank = px.bar(df_map_filt.sort_values('Casos'), x='Casos', y='Regional', 
                         orientation='h', color='Casos', color_continuous_scale="YlOrRd")
        fig_rank.update_layout(plot_bgcolor="white", showlegend=False, xaxis_title="Total de Casos")
        st.plotly_chart(fig_rank, use_container_width=True)

# --- SETOR 3: SÉRIE HISTÓRICA ---
elif st.session_state.segment == "Historico":
    st.subheader("Tendências e Séries Históricas (2007 - 2024)")
    fig_line = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                      color_discrete_map={'Casos': '#334155', 'Obitos': '#d32f2f'})
    fig_line.update_layout(plot_bgcolor="white", hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

# --- SETOR 4: DIRETRIZES ODS 3 ---
elif st.session_state.segment == "Diretrizes":
    st.subheader("Diretrizes de Saúde Pública e Prevenção")
    st.markdown("#### Foco no ODS 3: Saúde e Bem-Estar")
    
    c1, c2 = st.columns(2)
    with c1:
        st.success("**Ações de Controle Vetorial:** Intensificar limpeza em áreas com alta densidade de matéria orgânica.")
    with c2:
        st.warning("**Vigilância em Cães:** Aumentar a cobertura de exames em regionais com incidência acima da média.")
    
    st.write("---")
    st.markdown("""
    **Notas Técnicas:**
    * Os dados são atualizados conforme o sistema SINAN.
    * A letalidade é o principal indicador de gravidade para intervenção imediata.
    """)

# Rodapé de exportação
st.sidebar.markdown("---")
st.sidebar.download_button("Exportar Dados (CSV)", df_h.to_csv(index=False).encode('utf-8'), "vigileish_bh.csv")
