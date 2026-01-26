import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ESTÉTICA PROFISSIONAL (Padrão Acadêmico)
st.set_page_config(page_title="VigiLeish BH", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; color: #2c3e50; }
    .stMetric { background-color: #f8f9fa; border-radius: 4px; padding: 15px; border-top: 4px solid #d32f2f; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: 600; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DOS DADOS (Usando o nome simplificado)
file_path = 'dados.csv'

try:
    df_raw = pd.read_csv(file_path)
    # Selecionando dados de 2014 a 2023 (linhas 20 a 30 do seu arquivo)
    df_historico = df_raw.iloc[20:30].copy()
    df_historico.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df_raw.columns[7:])
    
    # Dados Regionais Reais (Totais do seu arquivo)
    regionais_data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
        'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
        'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
        'Total': [209, 67, 114, 209, 178, 132, 100, 65, 168]
    }
    df_mapa = pd.DataFrame(regionais_data)
except:
    st.error("Erro: O arquivo 'dados.csv' não foi encontrado no GitHub. Por favor, renomeie o arquivo no GitHub para dados.csv")
    st.stop()

# 3. CABEÇALHO E NAVEGAÇÃO
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento de Leishmaniose Visceral | Belo Horizonte - MG")

st.sidebar.write(f"**Estudante:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")

st.markdown("### Navegação")
n1, n2, n3 = st.columns(3)
with n1: st.button("📊 Histórico")
with n2: st.button("🗺️ Mapa")
with n3: st.button("📑 Detalhes")

st.markdown("---")

# 4. DASHBOARD
k1, k2, k3 = st.columns(3)
k1.metric("Casos (2023)", f"{df_historico['Casos'].iloc[-1]:.0f}")
k2.metric("Letalidade Média", f"{df_historico['Letalidade'].astype(float).mean():.1f}%")
k3.metric("Status", "Monitoramento Ativo")

st.header("Evolução Temporal (2014-2023)")
fig_lin = px.line(df_historico, x='Ano', y=['Casos', 'Obitos'], markers=True,
                  color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
st.plotly_chart(fig_lin, use_container_width=True)

st.markdown("---")
st.header("Análise Geográfica")
c_map, c_rank = st.columns([1.5, 1])

with c_map:
    fig_m = px.scatter_mapbox(df_mapa, lat="Lat", lon="Lon", size="Total", color="Total",
                               hover_name="Regional", color_continuous_scale="Reds",
                               zoom=10, height=400)
    fig_m.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_m, use_container_width=True)

with c_rank:
    fig_r = px.bar(df_mapa.sort_values('Total'), x='Total', y='Regional', orientation='h', color='Total', color_continuous_scale='Reds')
    st.plotly_chart(fig_r, use_container_width=True)

st.caption("Dados Oficiais: SINAN/SMSA-BH.")