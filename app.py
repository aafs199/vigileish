import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DESIGN SYSTEM
st.set_page_config(page_title="VigiLeish | Intelligence Dashboard", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3 { color: #0f172a; font-weight: 600; letter-spacing: -0.02em; }
    
    /* Professional Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #0f172a;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #334155; border-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS (Robustez e Precisão)
@st.cache_data
def load_refined_data():
    try:
        # Carregamento com tratamento de encoding e separador
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df.columns = [c.strip() for c in df.columns]
        
        # Histórico Anual (2007 - 2024)
        df_hist = df.iloc[13:31].copy() # Ajuste para os anos conforme seu CSV
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df.columns[7:])
        
        # Limpeza Numérica
        for col in ['Casos', 'Obitos', 'Letalidade']:
            df_hist[col] = pd.to_numeric(df_hist[col], errors='coerce').fillna(0)
        
        # Dados Geográficos (Extração Dinâmica por Ano)
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
                    'Regional': reg,
                    'Ano': ano,
                    'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'),
                    'Lat': coords[reg][0], 'Lon': coords[reg][1]
                })
        return df_hist, pd.DataFrame(reg_list)
    except:
        st.error("Erro na leitura do arquivo 'dados.csv'.")
        return pd.DataFrame(), pd.DataFrame()

df_h, df_m = load_refined_data()

# 3. NAVEGAÇÃO E FILTROS
st.sidebar.markdown("### Centro de Comando")
ano_alvo = st.sidebar.select_slider("Período de Análise:", options=sorted(df_m['Ano'].unique()), value=2023)

st.sidebar.markdown("---")
st.sidebar.caption(f"Analista: Aline Alice Ferreira da Silva")
st.sidebar.caption(f"Registro: 5277514")

# 4. DASHBOARD INTERFACE
st.title("VigiLeish Intelligence")
st.markdown(f"Monitoramento Estratégico de Leishmaniose Visceral | Belo Horizonte | **{ano_alvo}**")

# Cálculo Dinâmico da Letalidade do Ano Selecionado
df_ano = df_h[df_h['Ano'].astype(str).str.contains(str(ano_alvo))]
if not df_ano.empty:
    casos_n = df_ano['Casos'].iloc[0]
    obitos_n = df_ano['Obitos'].iloc[0]
    # Correção do cálculo de letalidade
    letalidade_n = (obitos_n / casos_n * 100) if casos_n > 0 else 0
else:
    casos_n, obitos_n, letalidade_n = 0, 0, 0

# KPIs com Design Sofisticado
m1, m2, m3, m4 = st.columns(4)
m1.metric("Incidência Anual", f"{casos_n:.0f} casos")
m2.metric("Óbitos Confirmados", f"{obitos_n:.0f} óbitos")
m3.metric("Taxa de Letalidade", f"{letalidade_n:.2f}%")
m4.metric("Nível de Risco", "Crítico" if letalidade_n > 15 else "Controlado")

st.markdown("---")

# 5. MAPA E ANÁLISE GEOGRÁFICA (Visualização Clean)
col_a, col_b = st.columns([1.8, 1])

with col_a:
    st.subheader("Mapeamento Georreferenciado")
    df_map_filt = df_m[df_m['Ano'] == ano_alvo]
    
    # Mapa Light Sofisticado
    fig_map = px.scatter_mapbox(
        df_map_filt, lat="Lat", lon="Lon", size="Casos", color="Casos",
        hover_name="Regional", size_max=35, zoom=10.5,
        color_continuous_scale="Viridis", # Escala profissional e equilibrada
        mapbox_style="carto-positron" # Estilo de mapa claro e sofisticado
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

with col_b:
    st.subheader("Ranking por Regional")
    fig_rank = px.bar(df_map_filt.sort_values('Casos'), x='Casos', y='Regional', 
                     orientation='h', color='Casos', color_continuous_scale="Viridis")
    fig_rank.update_layout(plot_bgcolor="white", showlegend=False, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_rank, use_container_width=True)

st.markdown("---")

# 6. EVOLUÇÃO TEMPORAL (Gráfico Clínico)
st.subheader("Série Histórica e Tendências")
fig_line = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                  color_discrete_map={'Casos': '#334155', 'Obitos': '#ef4444'})
fig_line.update_layout(plot_bgcolor="white", legend_title=None, hovermode="x unified")
fig_line.update_xaxes(showgrid=False)
st.plotly_chart(fig_line, use_container_width=True)

# 7. SEÇÃO ESTRATÉGICA (ODS 3)
with st.expander("ℹ️ Diretrizes de Saúde Pública"):
    st.info("""
    **Estratégias de Intervenção Sugeridas:**
    * **Vigilância Ativa:** Monitoramento quinzenal em regionais com letalidade acima de 10%.
    * **Controle Vetorial:** Limpeza urbana focalizada e manejo de reservatórios orgânicos.
    * **Inclusão Digital:** Este painel atua como ferramenta de transparência e agilidade na resposta governamental.
    """)

# Download de Dados
st.sidebar.download_button("Exportar Dados (CSV)", df_h.to_csv(index=False).encode('utf-8'), "vigileish_data.csv", "text/csv")
