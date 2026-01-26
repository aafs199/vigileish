import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ESTÉTICA E CONFIGURAÇÃO (UNINTER)
st.set_page_config(page_title="VigiLeish BH", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }
    .stMetric { background-color: #f8f9fa; border-radius: 4px; padding: 15px; border-top: 4px solid #d32f2f; }
    .nav-link { text-decoration: none; color: #d32f2f; font-weight: 600; padding: 10px; border: 1px solid #d32f2f; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DOS DADOS COM AUTO-DETECÇÃO (Resistente a erros)
@st.cache_data
def load_data():
    # Tenta ler detectando o separador (vírgula ou ponto-e-vírgula)
    try:
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1', on_bad_lines='skip')
    except:
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='utf-8', on_bad_lines='skip')
    
    # Filtra os anos de 2014 a 2023 (evita erro de coluna única)
    # Procuramos linhas onde a primeira célula é um ano de 4 dígitos
    mask = df.iloc[:, 0].astype(str).str.strip().str.match(r'^20[1-2][0-9]$')
    df_filtered = df[mask].copy()
    
    # Renomeia apenas o que existe para evitar o erro de 'Length Mismatch'
    new_names = {
        df.columns[0]: 'Ano',
        df.columns[1]: 'Casos',
        df.columns[5]: 'Obitos',
        df.columns[6]: 'Letalidade'
    }
    df_filtered = df_filtered.rename(columns=new_names)
    
    # Garante que os valores sejam números para o gráfico
    for col in ['Casos', 'Obitos', 'Letalidade']:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')
        
    return df_filtered

try:
    df_h = load_data()
    
    # Dados Regionais Reais (Totais extraídos do seu arquivo 'Regional 2007-2025')
    regionais_data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
        'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
        'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
        'Total': [102, 67, 114, 209, 178, 132, 100, 65, 168] # Números reais do seu CSV
    }
    df_m = pd.DataFrame(regionais_data)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.stop()

# 3. INTERFACE PRINCIPAL
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento da Leishmaniose Visceral em Belo Horizonte - MG")

# Menu de Navegação (Links âncoras para facilitar o uso)
st.markdown("""
<a href='#historico' class='nav-link'>📊 Evolução Histórica</a> &nbsp; 
<a href='#mapa' class='nav-link'>🗺️ Mapa de Risco</a>
<br><br>
""", unsafe_allow_html=True)

# KPIs
k1, k2, k3 = st.columns(3)
if not df_h.empty:
    k1.metric("Casos (Último Ano)", f"{df_h['Casos'].iloc[-1]:.0f}")
    k2.metric("Letalidade Média", f"{df_h['Letalidade'].mean():.1f}%")
    k3.metric("Status", "Monitoramento Ativo")

st.markdown("<div id='historico'></div>", unsafe_allow_html=True)
st.header("📈 Evolução: Casos vs Óbitos (2014-2023)")
fig_lin = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                  color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
fig_lin.update_layout(plot_bgcolor="white")
st.plotly_chart(fig_lin, use_container_width=True)

st.markdown("<div id='mapa'></div>", unsafe_allow_html=True)
st.header("🗺️ Análise por Regional")
c_map, c_rank = st.columns([1.5, 1])

with c_map:
    st.subheader("Mapa de Concentração")
    fig_map = px.scatter_mapbox(df_m, lat="Lat", lon="Lon", size="Total", color="Total",
                                 hover_name="Regional", color_continuous_scale="Reds",
                                 zoom=10, height=450)
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    # Interatividade: Captura clique no mapa
    map_select = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")

with c_rank:
    st.subheader("Ranking Histórico")
    fig_rank = px.bar(df_m.sort_values('Total'), x='Total', y='Regional', orientation='h',
                      color='Total', color_continuous_scale='Reds')
    fig_rank.update_layout(showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig_rank, use_container_width=True)

# Detalhamento ao clicar
st.markdown("---")
indices = map_select.get("selection", {}).get("point_indices", [])
if indices:
    reg = df_m.iloc[indices[0]]
    st.success(f"📍 Regional Selecionada: **{reg['Regional']}**")
    st.write(f"Total de casos acumulados: **{reg['Total']}**.")
else:
    st.info("💡 Clique em um ponto no mapa para ver o detalhamento aqui.")

# Sidebar
st.sidebar.markdown("---")
st.sidebar.write(f"**Aluna:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")
st.sidebar.caption("Dados Oficiais: SINAN / SMSA-BH")