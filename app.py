import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA E ESTÉTICA PROFISSIONAL
# Definido conforme os princípios de Design Universal (Intuitivo e de Fácil Percepção)
st.set_page_config(page_title="VigiLeish BH", layout="wide", page_icon="🏥")

# CSS personalizado para fonte elegante (Open Sans) e visual clean
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
        color: #2c3e50;
    }
    .main { background-color: #ffffff; }
    .stMetric { 
        background-color: #f8f9fa; 
        border-radius: 4px; 
        padding: 15px; 
        border-top: 4px solid #d32f2f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1 { font-weight: 600; color: #1a1a1a; letter-spacing: -0.5px; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. TRATAMENTO DOS DADOS REAIS
# O arquivo deve estar no mesmo diretório no GitHub
file_path = 'incidencialetalidadelv.xlsx - Planilha1.csv'

try:
    df_raw = pd.read_csv(file_path)
    
    # Tratamento da Linha do Tempo (Últimos 10 anos reais: 2014-2023)
    # Selecionando as linhas correspondentes aos anos no arquivo enviado
    df_historico = df_raw.iloc[20:30].copy()
    df_historico.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df_raw.columns[7:])
    df_historico['Ano'] = df_historico['Ano'].astype(str)
    
    # Tratamento dos Dados Regionais (Totais reais do arquivo)
    regionais_reais = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
        'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
        'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
        'Total': [209, 67, 114, 209, 178, 132, 100, 65, 168]
    }
    df_mapa = pd.DataFrame(regionais_reais)
    
except Exception as e:
    st.error(f"Erro ao carregar os dados reais: {e}")
    st.stop()

# 3. IDENTIFICAÇÃO E NAVEGAÇÃO (Sidebar e Âncoras)
st.sidebar.image("https://logodownload.org/wp-content/uploads/2017/10/uninter-logo.png", width=150)
st.sidebar.markdown("---")
st.sidebar.write(f"**Estudante:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")
st.sidebar.write("**Projeto:** VigiLeish BH")

st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento e Prevenção da Leishmaniose Visceral em Belo Horizonte - MG")

# Menu de Navegação Superior (Interatividade solicitada)
st.markdown("### Navegação Rápida")
n1, n2, n3 = st.columns(3)
with n1:
    if st.button("📊 Evolução Temporal"):
        st.info("Role para baixo para visualizar a seção: Evolução Histórica.")
with n2:
    if st.button("🗺️ Monitoramento Geográfico"):
        st.info("Role para baixo para visualizar a seção: Mapa de Risco.")
with n3:
    if st.button("📑 Detalhamento Regional"):
        st.info("Utilize a ferramenta de seleção no mapa para ver detalhes.")

st.markdown("---")

# 4. INDICADORES PRINCIPAIS (KPIs)
# Extraídos diretamente dos dados reais de 2023
total_casos_atual = df_historico['Casos'].iloc[-1]
letalidade_atual = df_historico['Letalidade'].iloc[-1]

k1, k2, k3 = st.columns(3)
k1.metric("Casos Incidentes (2023)", f"{total_casos_atual:.0f}")
k2.metric("Taxa de Letalidade", f"{letalidade_atual}%")
k3.metric("Fator de Risco", "Alerta Moderado")

st.markdown("---")

# 5. LINHA DO TEMPO: RELAÇÃO CASOS VS ÓBITOS
st.header("Evolução Histórica (Últimos 10 Anos)")
fig_linha = px.line(df_historico, x='Ano', y=['Casos', 'Obitos'], 
                    markers=True, color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
fig_linha.update_layout(plot_bgcolor="white", xaxis_title="Ano de Referência", yaxis_title="Quantidade")
st.plotly_chart(fig_linha, use_container_width=True)

st.markdown("---")

# 6. MAPA DE CALOR E RANKING (Interatividade Clicável)
st.header("Monitoramento Geográfico e Georreferenciamento")
col_mapa, col_rank = st.columns([1.5, 1])

with col_mapa:
    st.subheader("Mapa de Calor: Concentração de Casos")
    fig_m = px.scatter_mapbox(df_mapa, lat="Lat", lon="Lon", size="Total", color="Total",
                               hover_name="Regional", color_continuous_scale="Reds",
                               zoom=10, height=500)
    fig_m.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    
    # Interatividade clicável no mapa
    map_event = st.plotly_chart(fig_m, use_container_width=True, on_select="rerun")

with col_rank:
    st.subheader("Ranking Regional Histórico")
    fig_r = px.bar(df_mapa.sort_values('Total'), x='Total', y='Regional', 
                   orientation='h', color='Total', color_continuous_scale='Reds')
    fig_r.update_layout(showlegend=False, plot_bgcolor="white", xaxis_title="Total de Casos (2007-2025)")
    st.plotly_chart(fig_r, use_container_width=True)

# 7. DETALHAMENTO DINÂMICO AO CLICAR NO MAPA
st.markdown("---")
st.subheader("Análise Detalhada por Regional")

selected_points = map_event.get("selection", {}).get("point_indices", [])

if selected_points:
    index = selected_points[0]
    reg_nome = df_mapa.iloc[index]['Regional']
    reg_total = df_mapa.iloc[index]['Total']
    
    st.success(f"📌 **Regional Selecionada: {reg_nome}**")
    st.write(f"Esta regional registrou um acumulado de **{reg_total} casos** no período monitorado.")
    st.info("**Ação Estratégica:** Intensificar a vigilância ambiental e o manejo de reservatórios domésticos nesta área.")
else:
    st.info("💡 **Dica de Interatividade:** Utilize a ferramenta de seleção no topo do mapa para clicar em um ponto e visualizar o detalhamento regional aqui.")

st.markdown("---")
st.caption("Protótipo desenvolvido para a Atividade Extensionista IV - UNINTER. Dados extraídos de Fontes Oficiais: SINAN-MS/SMSA-PBH.")