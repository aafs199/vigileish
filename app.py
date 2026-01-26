import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuração da Página e Estética Profissional
st.set_page_config(page_title="VigiLeish BH", layout="wide")

# CSS para Fonte Open Sans, visual 'Clean' e Cards Modernos
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
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
    </style>
    """, unsafe_allow_html=True)

# 2. Dados de Belo Horizonte (Coordenadas Reais Aproximadas)
regionais_data = {
    'Regional': ['Barreiro', 'Centro-Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
    'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
    'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
    'Casos': [112, 45, 67, 89, 74, 156, 58, 142, 98],
    'Risco': [3.2, 1.5, 2.1, 2.8, 2.4, 4.8, 1.9, 4.5, 3.1]
}
df = pd.DataFrame(regionais_data)

# Dados para Linha do Tempo
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
df_tempo = pd.DataFrame({'Mês': meses, 'Casos': [15, 22, 45, 30, 18, 12, 10, 8, 25, 40, 55, 60]})

# 3. Título (Sem escudo e com fonte elegante)
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento e Prevenção da Leishmaniose | Belo Horizonte - MG")

# 4. Indicadores (KPIs)
c1, c2, c3 = st.columns(3)
c1.metric("Acumulado Anual", f"{df['Casos'].sum()} casos")
c2.metric("Média de Risco", f"{df['Risco'].mean():.1f}")
c3.metric("Foco de Atenção", "Regional Norte")

st.markdown("---")

# 5. Evolução Temporal (Linha)
st.subheader("Evolução Temporal de Casos")
fig_linha = px.line(df_tempo, x='Mês', y='Casos', markers=True, color_discrete_sequence=['#d32f2f'])
fig_linha.update_layout(plot_bgcolor="white", xaxis_title="", yaxis_title="Nº de Casos")
st.plotly_chart(fig_linha, use_container_width=True)

st.markdown("---")

# 6. Mapa de Calor e Gráfico de Barras (Lado a Lado)
col_mapa, col_barra = st.columns([1.5, 1])

with col_mapa:
    st.subheader("Mapa de Calor: Concentração de Risco")
    # Mapa interativo que permite "seleção"
    fig_mapa = px.scatter_mapbox(df, lat="Lat", lon="Lon", size="Casos", color="Risco",
                                 hover_name="Regional", color_continuous_scale="Reds",
                                 zoom=10, height=450)
    fig_mapa.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    
    # Captura de clique (Interatividade)
    event_dict = st.plotly_chart(fig_mapa, use_container_width=True, on_select="rerun")

with col_barra:
    st.subheader("Ranking por Regional")
    fig_barra = px.bar(df.sort_values('Casos'), x='Casos', y='Regional', orientation='h',
                       color='Risco', color_continuous_scale='Reds')
    fig_barra.update_layout(plot_bgcolor="white", showlegend=False, xaxis_title="Total de Casos")
    st.plotly_chart(fig_barra, use_container_width=True)

# 7. Interatividade: Dados ao Clicar/Selecionar
st.markdown("---")
st.subheader("Detalhamento por Regional")

# Lógica para mostrar dados da regional clicada no mapa
selected_indices = event_dict.get("selection", {}).get("point_indices", [])

if selected_indices:
    idx = selected_indices[0]
    regional_nome = df.iloc[idx]['Regional']
    casos_val = df.iloc[idx]['Casos']
    risco_val = df.iloc[idx]['Risco']
    
    st.success(f"📌 **Regional Selecionada: {regional_nome}**")
    col_a, col_b = st.columns(2)
    col_a.write(f"**Total de Casos:** {casos_val}")
    col_b.write(f"**Nível de Infestação:** {risco_val}")
    st.write("**Ação Recomendada:** Intensificar borrifação residual e mutirão de limpeza urbana.")
else:
    st.info("💡 **Dica de Usabilidade:** Use a ferramenta de seleção no topo do mapa para clicar em uma regional e ver os dados detalhados aqui.")

# Sidebar (Identificação)
st.sidebar.markdown("---")
st.sidebar.write(f"**Aluna:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")