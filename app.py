
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

# 2. FUNÇÃO DE CARREGAMENTO ULTRA RESILIENTE
@st.cache_data
def load_data():
    encodings = ['utf-8', 'iso-8859-1', 'latin-1', 'cp1252']
    seps = [',', ';']
    df = None
    
    # Tenta várias combinações de codificação e separador
    for encoding in encodings:
        for sep in seps:
            try:
                temp_df = pd.read_csv('dados.csv', sep=sep, encoding=encoding, on_bad_lines='skip')
                if len(temp_df.columns) > 1: # Se encontrou colunas, deu certo
                    df = temp_df
                    break
            except:
                continue
        if df is not None: break

    if df is None:
        raise Exception("Não foi possível ler o arquivo 'dados.csv'. Verifique o formato.")

    # Limpeza de colunas
    df.columns = [str(c).strip() for c in df.columns]
    
    # Filtra os anos de 2014 a 2023
    # Usamos o nome da primeira coluna (que deve ser Ano)
    col_ano = df.columns[0]
    df[col_ano] = df[col_ano].astype(str).str.strip()
    anos_vaildos = [str(a) for a in range(2014, 2024)]
    df_filtered = df[df[col_ano].isin(anos_vaildos)].copy()
    
    # Cria um DataFrame limpo com nomes padronizados
    df_final = pd.DataFrame()
    df_final['Ano'] = df_filtered.iloc[:, 0]
    df_final['Casos'] = pd.to_numeric(df_filtered.iloc[:, 1], errors='coerce')
    df_final['Obitos'] = pd.to_numeric(df_filtered.iloc[:, 5], errors='coerce')
    df_final['Letalidade'] = pd.to_numeric(df_filtered.iloc[:, 6], errors='coerce')
    
    return df_final

try:
    df_h = load_data()
    
    # Dados Regionais (Estáticos para garantir que o mapa sempre funcione)
    regionais_data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova'],
        'Lat': [-19.97, -19.93, -19.92, -19.89, -19.91, -19.83, -19.95, -19.85, -19.81],
        'Lon': [-44.02, -43.93, -43.90, -43.91, -43.96, -43.91, -43.98, -43.97, -43.95],
        'Total': [102, 67, 114, 209, 178, 132, 100, 65, 168]
    }
    df_m = pd.DataFrame(regionais_data)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.info("💡 Dica: Verifique se o arquivo no GitHub se chama exatamente 'dados.csv' (tudo minúsculo).")
    st.stop()

# 3. INTERFACE VISUAL
st.title("VigiLeish: Vigilância Epidemiológica")
st.write("Monitoramento da Leishmaniose Visceral | Belo Horizonte - MG")

st.markdown("---")

# KPIs
if not df_h.empty:
    k1, k2, k3 = st.columns(3)
    # Último ano disponível (2023)
    k1.metric("Casos Incidentes (2023)", f"{df_h['Casos'].iloc[-1]:.0f}")
    k2.metric("Letalidade Média (10 anos)", f"{df_h['Letalidade'].mean():.1f}%")
    k3.metric("Status Epidemiológico", "Monitoramento Ativo")

# Gráfico de Linha
st.header("📈 Evolução Temporal (2014-2023)")
fig_lin = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True,
                  color_discrete_map={'Casos': '#d32f2f', 'Obitos': '#333333'})
fig_lin.update_layout(plot_bgcolor="white", xaxis_title="Ano", yaxis_title="Quantidade")
st.plotly_chart(fig_lin, use_container_width=True)

st.markdown("---")

# Mapa e Ranking
st.header("🗺️ Análise Geográfica por Regional")
c_map, c_rank = st.columns([1.5, 1])

with c_map:
    fig_map = px.scatter_mapbox(df_m, lat="Lat", lon="Lon", size="Total", color="Total",
                                 hover_name="Regional", color_continuous_scale="Reds",
                                 zoom=10, height=450)
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    # Habilita a seleção para interatividade
    map_selection = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")

with c_rank:
    fig_rank = px.bar(df_m.sort_values('Total'), x='Total', y='Regional', orientation='h',
                      color='Total', color_continuous_scale='Reds')
    fig_rank.update_layout(showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig_rank, use_container_width=True)

# Detalhamento interativo
indices = map_selection.get("selection", {}).get("point_indices", [])
if indices:
    reg = df_m.iloc[indices[0]]
    st.success(f"📍 **Regional: {reg['Regional']}** | Total Histórico: {reg['Total']} casos.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.write(f"**Aluna:** Aline Alice Ferreira da Silva")
st.sidebar.write(f"**RU:** 5277514")
st.sidebar.caption("Dados: SINAN / SMSA-BH")
