import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuração da Página e Importação de Fontes Elegantes
st.set_page_config(page_title="VigiLeish BH", layout="wide")

# CSS para Fonte Profissional (Roboto/Open Sans) e Estilo Elegante
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
        border-radius: 5px; 
        padding: 20px; 
        border-left: 5px solid #d32f2f;
    }
    h1 { font-weight: 600; color: #1a1a1a; letter-spacing: -1px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Identificação Lateral (Exigência Acadêmica UNINTER)
st.sidebar.markdown("---")
st.sidebar.write("**Estudante:** Aline Alice Ferreira da Silva")
st.sidebar.write("**RU:** 5277514")
st.sidebar.write("**Curso:** Ciência de Dados")

# --- REMOVIDO ESCUDO E OBJETIVO ---
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento de Leishmaniose Visceral em Belo Horizonte - MG")

# --- DADOS PARA LINHA DO TEMPO E INTERATIVIDADE ---
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
dados_tempo = pd.DataFrame({
    'Mês': meses,
    'Casos': [15, 22, 45, 30, 18, 12, 10, 8, 25, 40, 55, 60]
})

regionais = ['Barreiro', 'Centro-Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova']
detalhes_prevecao = {
    'Barreiro': "Foco em limpeza de terrenos baldios e controle de reservatórios caninos.",
    'Pampulha': "Monitoramento intensivo devido à proximidade com áreas de vegetação e orla.",
    'Venda Nova': "Mutirões de conscientização sobre descarte de matéria orgânica.",
    'Norte': "Instalação de telas em canis públicos e residências vulneráveis."
}

# 3. DASHBOARD INTERATIVO
# KPIs Superiores
c1, c2, c3 = st.columns(3)
c1.metric("Acumulado Anual", "340 casos")
c2.metric("Tendência", "Alta", delta="15%")
c3.metric("Fator de Risco", "Médio-Alto")

st.markdown("---")

# 4. LINHA DO TEMPO (Adicionada)
st.subheader("Evolução Mensal de Casos")
fig_linha = px.line(dados_tempo, x='Mês', y='Casos', markers=True, 
                    line_shape="spline", color_discrete_sequence=['#d32f2f'])
fig_linha.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_linha, use_container_width=True)

st.markdown("---")

# 5. INTERATIVIDADE CLICÁVEL (Adicionada)
st.subheader("Intervenções por Regional")
st.write("Selecione uma regional para visualizar o plano de ação específico:")

# Botões clicáveis para simular interatividade de sistema profissional
escolha = st.selectbox("Selecione a Regional de Belo Horizonte:", regionais)

if escolha in detalhes_prevecao:
    st.success(f"**Plano de Ação para {escolha}:** {detalhes_prevecao[escolha]}")
else:
    st.info(f"Para a regional **{escolha}**, as ações seguem o protocolo padrão de vigilância epidemiológica municipal.")

st.markdown("---")
st.caption("Dados simulados para fins de demonstração técnica - Projeto de Extensão UNINTER.")