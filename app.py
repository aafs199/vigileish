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
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE LEITURA COM TRATAMENTO DE ACENTUAÇÃO (ENCODING)
@st.cache_data
def load_data():
    try:
        # Tenta ler com codificação padrão
        df = pd.read_csv('dados.csv', on_bad_lines='skip', encoding='utf-8')
    except UnicodeDecodeError:
        # Se falhar, tenta com codificação latina (comum em Excel/Windows)
        df = pd.read_csv('dados.csv', on_bad_lines='skip', encoding='iso-8859-1')
    
    # Identifica as linhas de 2014 a 2023
    df_timeline = df[df.iloc[:, 0].astype(str).str.match(r'^20[1-2][0-9]$')].copy()
    df_timeline.columns = ['Ano', 'Casos', 'Pop', 'Incidencia', 'Prevalencia', 'Obitos', 'Letalidade'] + list(df.columns[7:])
    
    # Garante que os anos e valores sejam tratados como números
    df_timeline = df_timeline[df_timeline['Ano'].astype(str).isin([str(a) for a in range(2014, 2024)])]
    df_timeline['Casos'] = pd.to_numeric(df_timeline['Casos'], errors='coerce')
    df_timeline['Obitos'] = pd.to_numeric(df_timeline['Obitos'], errors='coerce')
    df_timeline['Letalidade'] = pd.to_numeric(df_timeline['Letalidade'], errors='coerce')
    
    return df_timeline

try:
    df_h = load_data()
    
    # Dados Regionais Reais (conforme o seu arquivo)
    regionais_data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
        'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
        'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
        'Total': [209, 67, 114, 209, 178, 132, 100, 65, 168]
    }
    df_m = pd.DataFrame(regionais_data)

except Exception as e:
    st.error(f"Erro na leitura dos dados: {e}")
    st.info("Dica: Certifique-se de que o arquivo no GitHub se chama 'dados.csv'")
    st.stop()

# 3. INTERFACE DO USUÁRIO
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento da Leishmaniose Visceral | Belo Horizonte - MG")

st.markdown("---")

# KPIs Dinâmicos
k1, k2, k3 = st.columns(3)
if not df_h.empty:
    ultimo_caso = df_h['Casos'].iloc[-1]
    letalidade_media = df_h['Letalidade'].mean()
    k1.metric("Casos Incidentes (Ano Ref.)", f"{ultimo_caso:.0f}")
    k2.metric("Letalidade Média (10 anos)", f"{letalidade_media:.1f}%")
    k3.metric("Status", "Monitoramento Ativo")

# Gráfico de Linha (Evolução Temporal)
st.subheader("Evolução: Casos vs Óbitos (2014-2023)")
fig_l = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
fig_l.update_layout(plot_bgcolor="white", legend_title="Legenda")
st.plotly_chart(fig_l, use_container_width=True)

st.markdown("---")

# Mapa e Gráfico de Barras
col_map, col_rank = st.columns([1.5, 1])

with col_map:
    st.subheader("Distribuição Geográfica de Risco")
    fig_map = px.scatter_mapbox(df_m, lat="Lat", lon="Lon", size="Total", color="Total",
                                 hover_name="Regional", color_continuous_scale="Reds",
                                 zoom=10, height=450)
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with col_rank:
    st.subheader("Casos por Regional")
    fig_rank = px.bar(df_m.sort_values('Total'), x='Total', y='Regional', orientation='h',
                      color='Total', color_continuous_scale='Reds')
    fig_rank.update_layout(showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig_rank, use_container_width=True)

# Rodapé Académico
st.sidebar.markdown("---")
st.sidebar.write(f"**Aluna:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")
st.sidebar.caption("Fonte: SINAN / SMSA-BH")