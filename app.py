
import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO MODERNO
st.set_page_config(page_title="VigiLeish BH - Inteligência Geográfica", layout="wide", page_icon="🔬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; color: #2c3e50; }
    .stMetric { background-color: #f0f2f6; border-radius: 10px; padding: 15px; border-bottom: 5px solid #d32f2f; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #e1e4e8; }
    h1, h2, h3 { color: #1a1a1a; font-weight: 600; }
    .stButton>button { background-color: #d32f2f; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO E PROCESSAMENTO DOS DADOS REAIS
@st.cache_data
def get_data():
    try:
        # Lendo o arquivo (ajuste o nome se necessário no GitHub)
        df_raw = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        
        # --- TABELA 1: HISTÓRICO ANUAL ---
        df_hist = df_raw.iloc[0:32].copy() # Pega as primeiras 32 linhas
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df_raw.columns[7:])
        df_hist = df_hist[df_hist['Ano'].str.strip().str.match(r'^\d{4}$', na=False)]
        for c in ['Casos', 'Obitos', 'Letalidade']:
            df_hist[c] = pd.to_numeric(df_hist[c], errors='coerce').fillna(0)
            
        # --- TABELA 2: DADOS REGIONAIS POR ANO ---
        # No seu arquivo, a tabela regional começa na linha 38 (índice 39 no read_csv original)
        # Vamos processar as colunas de 2007 a 2024
        reg_names = ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova']
        coords = {
            'Barreiro': [-19.97, -44.02], 'Centro Sul': [-19.93, -43.93], 'Leste': [-19.92, -43.90],
            'Nordeste': [-19.89, -43.91], 'Noroeste': [-19.91, -43.96], 'Norte': [-19.83, -43.91],
            'Oeste': [-19.95, -43.98], 'Pampulha': [-19.85, -43.97], 'Venda Nova': [-19.81, -43.95]
        }
        
        # Extraindo dados da segunda tabela (Lógica específica para o seu CSV)
        df_reg_all = []
        for reg in reg_names:
            # Localiza a linha da regional no arquivo
            row = df_raw[df_raw.iloc[:,0].str.contains(reg, na=False, case=False)].iloc[0]
            for col_idx, ano in enumerate(range(2007, 2025)):
                df_reg_all.append({
                    'Regional': reg,
                    'Ano': ano,
                    'Casos': pd.to_numeric(row.iloc[col_idx + 1], errors='coerce'),
                    'Lat': coords[reg][0],
                    'Lon': coords[reg][1]
                })
        return df_hist, pd.DataFrame(df_reg_all)
    except Exception as e:
        st.error(f"Erro ao ler os dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_h, df_m = get_data()

# 3. BARRA LATERAL E FILTROS
st.sidebar.image("https://logodownload.org/wp-content/uploads/2017/10/uninter-logo.png", width=160)
st.sidebar.title("Configurações")

# --- SELECIONAR ANO (Ponto Principal solicitado) ---
ano_selecionado = st.sidebar.select_slider(
    "Selecione o Ano para Análise:",
    options=sorted(df_m['Ano'].unique().tolist()),
    value=2023
)

st.sidebar.markdown("---")
st.sidebar.write(f"**Estudante:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")

# 4. TÍTULO E NAVEGAÇÃO
st.title("🔬 VigiLeish: Monitoramento Epidemiológico")
st.write(f"Painel Estratégico de Vigilância Sanitária em Belo Horizonte | Foco no Ano **{ano_selecionado}**")

# 5. INDICADORES DINÂMICOS (Baseados no Ano Selecionado)
kpi_data = df_h[df_h['Ano'].astype(int) == ano_selecionado]
col1, col2, col3, col4 = st.columns(4)

if not kpi_data.empty:
    col1.metric("Novos Casos", f"{kpi_data['Casos'].iloc[0]:.0f}")
    col2.metric("Óbitos Registrados", f"{kpi_data['Obitos'].iloc[0]:.0f}")
    col3.metric("Taxa Letalidade", f"{kpi_data['Letalidade'].iloc[0]:.1f}%")
    col4.metric("Status", "Em Monitoramento" if kpi_data['Casos'].iloc[0] < 50 else "Alerta Máximo")

st.markdown("---")

# 6. MAPA DE CALOR MODERNO (CORRESPONDE AO ANO SOLICITADO)
st.subheader(f"🗺️ Distribuição Geográfica de Casos em {ano_selecionado}")
df_mapa_ano = df_m[df_m['Ano'] == ano_selecionado]

fig_map = px.scatter_mapbox(
    df_mapa_ano, lat="Lat", lon="Lon", size="Casos", color="Casos",
    hover_name="Regional", size_max=40, zoom=11,
    color_continuous_scale=px.colors.sequential.YlOrRd,
    mapbox_style="carto-darkmatter", # ESTILO DARK SOLICITADO
    height=550
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# 7. EVOLUÇÃO TEMPORAL E RANKING
c_left, c_right = st.columns([1.5, 1])

with c_left:
    st.subheader("📈 Tendência Histórica (Casos vs Óbitos)")
    fig_line = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                       color_discrete_map={'Casos': '#1f77b4', 'Obitos': '#d32f2f'})
    fig_line.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig_line, use_container_width=True)

with c_right:
    st.subheader(f"🏆 Ranking de Regionais ({ano_selecionado})")
    fig_bar = px.bar(df_mapa_ano.sort_values('Casos'), x='Casos', y='Regional', 
                     orientation='h', color='Casos', color_continuous_scale='Reds')
    fig_bar.update_layout(showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig_bar, use_container_width=True)

# 8. SEÇÃO ODS 3: SAÚDE E PREVENÇÃO (ORIENTAÇÃO PARA COMUNIDADE)
st.markdown("---")
st.subheader("🩺 Saúde e Bem-estar (ODS 3) - Prevenção")
p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("""<div class='card'><h4>🏠 Manejo Ambiental</h4>
    Mantenha quintais limpos, remova matéria orgânica e podas de árvores para evitar o criadouro do mosquito-palha.</div>""", unsafe_allow_html=True)
with p2:
    st.markdown("""<div class='card'><h4>🐕 Cuidado Animal</h4>
    Utilize coleiras repelentes em cães e realize exames periódicos. O cão é o principal reservatório em áreas urbanas.</div>""", unsafe_allow_html=True)
with p3:
    st.markdown("""<div class='card'><h4>⚠️ Atenção aos Sintomas</h4>
    Febre prolongada, perda de peso e aumento do volume abdominal. Procure o Centro de Saúde mais próximo.</div>""", unsafe_allow_html=True)

# 9. DOWNLOAD DE DADOS
st.markdown("---")
csv_data = df_h.to_csv(index=False).encode('iso-8859-1')
st.download_button(
    label="📥 Baixar Relatório Completo (CSV)",
    data=csv_data,
    file_name=f'vigileish_bh_relatorio_{ano_selecionado}.csv',
    mime='text/csv',
)

st.caption("Dados extraídos de fontes oficiais (SINAN/SMSA-PBH). Protótipo para Atividade Extensionista UNINTER.")
