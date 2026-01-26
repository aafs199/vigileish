import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página e Estilo Elegante
st.set_page_config(page_title="VigiLeish BH", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; color: #2c3e50; }
    .main { background-color: #ffffff; }
    .stMetric { background-color: #f8f9fa; border-radius: 4px; padding: 15px; border-top: 4px solid #d32f2f; }
    h1 { font-weight: 600; color: #1a1a1a; }
    </style>
    """, unsafe_allow_html=True)

# 2. Carregamento e Tratamento de Dados Reais
# Lendo os dados que você enviou
file_path = 'incidencialetalidadelv.xlsx - Planilha1.csv'
df_raw = pd.read_csv(file_path)

# Tratamento: Linha do Tempo (Últimos 10 anos: 2014-2023)
df_historico = df_raw.iloc[20:30].copy() 
df_historico.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df_raw.columns[7:])

# Tratamento: Dados Regionais Reais (Baseado na tabela final do seu arquivo)
regionais_reais = {
    'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
    'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
    'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
    'Total_Historico': [209, 67, 114, 209, 178, 132, 100, 65, 168]
}
df_mapa = pd.DataFrame(regionais_reais)

# 3. MENU DE NAVEGAÇÃO (Âncoras)
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Sistema de Monitoramento e Análise de Leishmaniose Visceral | Belo Horizonte - MG")

st.markdown("### Navegação Rápida")
c_nav1, c_nav2, c_nav3 = st.columns(3)
if c_nav1.button("📊 Ir para Linha do Tempo"):
    st.markdown("<script>window.scrollTo(0, 500);</script>", unsafe_allow_html=True) # Scroll simulado
if c_nav2.button("🗺️ Ir para Mapa de Risco"):
    st.write("Role para a seção de Monitoramento Geográfico.")
if c_nav3.button("📋 Planos de Ação"):
    st.write("Role para a seção final da página.")

st.markdown("---")

# 4. INDICADORES REAIS (Último Ano Disponível)
letalidade_atual = df_historico['Letalidade'].iloc[-1]
total_casos_ano = df_historico['Casos'].iloc[-1]

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Casos Incidentes (Ano Atual)", f"{total_casos_ano:.0f}")
kpi2.metric("Taxa de Letalidade", f"{letalidade_atual}%")
kpi3.metric("Status da Cidade", "Alerta Epidemiológico")

# 5. SEÇÃO: LINHA DO TEMPO
st.header("📈 Linha do Tempo Real (2014 - 2023)")
fig_relacao = px.line(df_historico, x='Ano', y=['Casos', 'Obitos'], 
                      markers=True, title="Relação: Casos vs Óbitos",
                      color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
fig_relacao.update_layout(plot_bgcolor="white", yaxis_title="Quantidade")
st.plotly_chart(fig_relacao, use_container_width=True)

st.markdown("---")

# 6. SEÇÃO: MAPA E RANKING REGIONAL
st.header("🗺️ Monitoramento Geográfico")
col_m, col_b = st.columns([1.5, 1])

with col_m:
    st.subheader("Mapa de Calor (Dados Históricos)")
    fig_m = px.scatter_mapbox(df_mapa, lat="Lat", lon="Lon", size="Total_Historico", 
                              color="Total_Historico", hover_name="Regional",
                              color_continuous_scale="Reds", zoom=10, height=450)
    fig_m.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_m, use_container_width=True)

with col_b:
    st.subheader("Ranking por Regional")
    fig_b = px.bar(df_mapa.sort_values('Total_Historico'), x='Total_Historico', y='Regional', 
                   orientation='h', color='Total_Historico', color_continuous_scale='Reds')
    fig_b.update_layout(showlegend=False, xaxis_title="Total de Casos (Histórico)")
    st.plotly_chart(fig_b, use_container_width=True)

# Sidebar de Identificação
st.sidebar.markdown("---")
st.sidebar.write(f"**Aluna:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")