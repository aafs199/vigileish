
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ESTÉTICA E CONFIGURAÇÃO
st.set_page_config(page_title="VigiLeish BH", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }
    .stMetric { background-color: #f8f9fa; border-radius: 4px; padding: 15px; border-top: 4px solid #d32f2f; }
    .nav-link { text-decoration: none; color: #d32f2f; font-weight: 600; padding: 10px; border: 1px solid #d32f2f; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO INTELIGENTE
@st.cache_data
def load_data():
    # Detecta o separador automaticamente
    try:
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
    except:
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='utf-8')
    
    # Limpa nomes de colunas (remove espaços extras)
    df.columns = [c.strip() for c in df.columns]
    
    # Filtra os anos de 2014 a 2023
    df['Ano_Str'] = df.iloc[:, 0].astype(str).str.strip()
    anos_desejados = [str(a) for a in range(2014, 2024)]
    df_filtered = df[df['Ano_Str'].isin(anos_desejados)].copy()
    
    # Mapeamento manual baseado no seu arquivo para garantir a leitura
    # 'Ano', 'Casos incidentes', 'Óbitos incidentes', 'Letalidade incidentes (%)'
    df_final = pd.DataFrame()
    df_final['Ano'] = df_filtered.iloc[:, 0]
    df_final['Casos'] = pd.to_numeric(df_filtered.iloc[:, 1], errors='coerce')
    df_final['Obitos'] = pd.to_numeric(df_filtered.iloc[:, 5], errors='coerce')
    df_final['Letalidade'] = pd.to_numeric(df_filtered.iloc[:, 6], errors='coerce')
    
    return df_final

try:
    df_h = load_data()
    
    # Dados Regionais Reais (Fixos para evitar erros de leitura da segunda tabela)
    regionais_data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
        'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
        'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
        'Total': [102, 67, 114, 209, 178, 132, 100, 65, 168]
    }
    df_m = pd.DataFrame(regionais_data)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.info("Verifique se o arquivo no GitHub se chama 'dados.csv' e se ele possui as colunas de Ano, Casos e Óbitos.")
    st.stop()

# 3. INTERFACE
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento da Leishmaniose Visceral | Belo Horizonte - MG")

# Navegação
st.markdown("""
<a href='#historico' class='nav-link'>📊 Histórico</a> &nbsp; <a href='#mapa' class='nav-link'>🗺️ Mapa</a>
<br><br>""", unsafe_allow_html=True)

# KPIs
if not df_h.empty:
    k1, k2, k3 = st.columns(3)
    k1.metric("Casos (2023)", f"{df_h['Casos'].iloc[-1]:.0f}")
    k2.metric("Letalidade Média", f"{df_h['Letalidade'].mean():.1f}%")
    k3.metric("Status", "Monitoramento Ativo")

st.markdown("<div id='historico'></div>", unsafe_allow_html=True)
st.header("📈 Evolução Temporal (2014-2023)")
fig_lin = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                  color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
fig_lin.update_layout(plot_bgcolor="white", xaxis_title="Ano", yaxis_title="Quantidade")
st.plotly_chart(fig_lin, use_container_width=True)

st.markdown("<div id='mapa'></div>", unsafe_allow_html=True)
st.header("🗺️ Análise por Regional")
c_map, c_rank = st.columns([1.5, 1])

with c_map:
    fig_map = px.scatter_mapbox(df_m, lat="Lat", lon="Lon", size="Total", color="Total",
                                 hover_name="Regional", color_continuous_scale="Reds",
                                 zoom=10, height=450)
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    map_select = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")

with c_rank:
    fig_rank = px.bar(df_m.sort_values('Total'), x='Total', y='Regional', orientation='h',
                      color='Total', color_continuous_scale='Reds')
    fig_rank.update_layout(showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig_rank, use_container_width=True)

# Detalhamento
indices = map_select.get("selection", {}).get("point_indices", [])
if indices:
    reg = df_m.iloc[indices[0]]
    st.success(f"📍 Regional Selecionada: **{reg['Regional']}** | Total Histórico: {reg['Total']} casos.")

st.sidebar.write(f"**Aluna:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")