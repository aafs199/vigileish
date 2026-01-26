import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuração da Página
st.set_page_config(page_title="VigiLeish BH", layout="wide", page_icon="🏥")

# Estilização Profissional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIMULAÇÃO DE DADOS (Baseado em BH) ---
regionais = ['Barreiro', 'Centro-Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova']
df_casos = pd.DataFrame({
    'Regional': regionais,
    'Casos 2023': np.random.randint(50, 200, size=9),
    'Indice de Infestação': np.random.uniform(1.5, 5.0, size=9).round(2),
    'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
    'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95]
})

# --- HEADER ---
st.title("🛡️ VigiLeish: Vigilância da Leishmaniose")
st.subheader("Painel de Controle Epidemiológico - Belo Horizonte, MG")
st.info("Objetivo: Apoiar a gestão pública e informar a comunidade sobre áreas de risco.")

# --- DASHBOARD PRINCIPAL ---
col1, col2, col3 = st.columns(3)
col1.metric("Total de Casos (2023)", df_casos['Casos 2023'].sum(), "+12% vs 2022")
col2.metric("Média de Infestação", f"{df_casos['Indice de Infestação'].mean():.2f}%", "-0.5%")
col3.metric("Regional Crítica", df_casos.loc[df_casos['Casos 2023'].idxmax(), 'Regional'])

st.divider()

# --- MAPA E GRÁFICOS ---
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 🗺️ Mapa de Calor por Regional")
    fig_map = px.scatter_mapbox(df_casos, lat="Lat", lon="Lon", size="Casos 2023", 
                               color="Indice de Infestação", hover_name="Regional",
                               color_continuous_scale=px.colors.sequential.Reds,
                               zoom=10, height=500)
    fig_map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)

with c2:
    st.markdown("### 📊 Casos por Regional")
    fig_bar = px.bar(df_casos.sort_values('Casos 2023'), x='Casos 2023', y='Regional', 
                     orientation='h', color='Casos 2023', color_continuous_scale='Reds')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- SEÇÃO DE INCLUSÃO DIGITAL E PREVENÇÃO ---
st.divider()
st.header("💡 Espaço da Comunidade (Inclusão Digital)")
tab1, tab2 = st.tabs(["Guia de Prevenção", "Denúncia de Foco"])

with tab1:
    st.markdown("""
    #### Como proteger sua família e seu pet:
    1. **Limpeza de quintais:** Remova matéria orgânica (folhas, frutos, fezes de animais).
    2. **Cuidado com os cães:** Use coleiras repelentes e mantenha a vacinação em dia.
    3. **Telas:** Instale telas de malha fina em janelas e portas.
    """)
    st.image("https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/l/leishmaniose-visceral/folder-leishmaniose-visceral.png/@@images/image", width=600)

with tab2:
    st.write("Identificou um local com acúmulo de lixo ou possível foco do mosquito palha?")
    st.text_input("Endereço do local:")
    st.button("Enviar Alerta para a Zoonoses")

st.sidebar.markdown("---")
st.sidebar.write("**Desenvolvido por:** Aline Alice Ferreira da Silva")
st.sidebar.write("**RU:** 5277514")