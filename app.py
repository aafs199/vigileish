
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# 1. DESIGN SYSTEM - Focado em Responsividade
st.set_page_config(page_title="VigiLeish Intelligence Dashboard", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; background-color: #fcfcfd; }
    
    /* Botões de Navegação adaptados para toque */
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3.5em; background-color: #ffffff;
        color: #0f172a; border: 1px solid #e2e8f0; text-align: left; margin-bottom: 8px;
    }
    div.stButton > button:hover { border-color: #d32f2f; color: #d32f2f; }
    
    /* Ajuste de métricas para telas pequenas */
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS (Intervalo 2007-2023)
@st.cache_data
def load_data():
    try:
        # Dados Humanos
        df_h_raw = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df_h_raw.columns = [c.strip() for c in df_h_raw.columns]
        df_h_raw['Ano_Val'] = pd.to_numeric(df_h_raw.iloc[:, 0], errors='coerce')
        df_h_clean = df_h_raw[(df_h_raw['Ano_Val'] >= 2007) & (df_h_raw['Ano_Val'] <= 2023)].copy()
        
        df_hist = df_h_clean.iloc[:, :7]
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade']
        for col in ['Ano', 'Casos', 'Obitos', 'Letalidade']:
            df_hist[col] = pd.to_numeric(df_hist[col], errors='coerce').fillna(0).astype(int)

        # Regionais (Mapeamento)
        coords = {
            'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
            'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
            'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]
        }
        reg_data = []
        for reg, latlon in coords.items():
            mask = df_h_raw.iloc[:,0].str.contains(reg, na=False, case=False)
            if mask.any():
                row = df_h_raw[mask].iloc[0]
                for i, ano in enumerate(range(2007, 2024)):
                    reg_data.append({
                        'Regional': reg, 'Ano': int(ano),
                        'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'),
                        'Lat': latlon[0], 'Lon': latlon[1]
                    })
        
        # Dados Caninos
        df_c_raw = pd.read_csv('caninos.csv', sep=';', encoding='iso-8859-1')
        df_c_raw.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']
        for col in df_c_raw.columns:
            df_c_raw[col] = df_c_raw[col].astype(str).str.replace('.', '').str.replace(',', '.')
            df_c_raw[col] = pd.to_numeric(df_c_raw[col], errors='coerce').fillna(0).astype(int)
        
        df_c_clean = df_c_raw[(df_c_raw['Ano'] >= 2007) & (df_c_raw['Ano'] <= 2023)].copy()
        df_c_clean['Taxa_Positividade'] = (df_c_clean['Positivos'] / df_c_clean['Sorologias'] * 100).fillna(0)

        return df_hist, pd.DataFrame(reg_data), df_c_clean
    except Exception as e:
        st.error(f"Erro no carregamento: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_c = load_data()

# 3. NAVEGAÇÃO
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

st.sidebar.title("VigiLeish Menu")
if st.sidebar.button("📊 Painel Geral"): st.session_state.segment = "Geral"
if st.sidebar.button("🗺️ Mapa Regional"): st.session_state.segment = "Mapa"
if st.sidebar.button("🐕 Vigilância Canina"): st.session_state.segment = "Canina"
if st.sidebar.button("📈 Tendências"): st.session_state.segment = "Historico"
if st.sidebar.button("📋 Diretrizes"): st.session_state.segment = "Diretrizes"

st.sidebar.markdown("---")
anos_disponiveis = sorted(df_m['Ano'].unique().tolist(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Filtro de Ano:", options=anos_disponiveis, index=0)

# 4. EXIBIÇÃO
st.title("VigiLeish Intelligence")

# --- PAINEL GERAL ---
if st.session_state.segment == "Geral":
    st.subheader(f"Visão Consolidada | {ano_selecionado}")
    dh = df_h[df_h['Ano'] == ano_selecionado]
    dc = df_c[df_c['Ano'] == ano_selecionado]
    
    st.markdown("#### 🏥 Humanos")
    c1, c2, c3 = st.columns(3)
    if not dh.empty:
        c1.metric("Casos", f"{dh['Casos'].iloc[0]}")
        c2.metric("Óbitos", f"{dh['Obitos'].iloc[0]}")
        c3.metric("Letalidade", f"{(dh['Obitos'].iloc[0]/dh['Casos'].iloc[0]*100):.1f}%" if dh['Casos'].iloc[0]>0 else "0%")
    
    st.markdown("#### 🐕 Caninos")
    c4, c5, c6 = st.columns(3)
    c7, c8 = st.columns(2)
    if not dc.empty:
        c4.metric("Positivos", f"{dc['Positivos'].iloc[0]:,}".replace(',', '.'))
        c5.metric("Eutanasiados", f"{dc['Eutanasiados'].iloc[0]:,}".replace(',', '.'))
        c6.metric("Taxa Posit.", f"{dc['Taxa_Positividade'].iloc[0]:.1f}%")
        c7.metric("Sorologias", f"{dc['Sorologias'].iloc[0]:,}".replace(',', '.'))
        c8.metric("Borrifados", f"{dc['Borrifados'].iloc[0]:,}".replace(',', '.'))

# --- VIGILÂNCIA CANINA (Gráficos com Legenda Embaixo) ---
elif st.session_state.segment == "Canina":
    st.subheader("Vigilância Integrada: Cães e Controle")
    
    # Gráfico Misto Original com Legenda Inferior
    fig_misto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_misto.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Positivos'], name="Positivos", marker_color='#F59E0B'), secondary_y=False)
    fig_misto.add_trace(go.Bar(x=df_c['Ano'], y=df_c['Eutanasiados'], name="Eutanasiados", marker_color='#D32F2F'), secondary_y=False)
    fig_misto.add_trace(go.Scatter(x=df_c['Ano'], y=df_c['Sorologias'], name="Sorologias", line=dict(color='#3B82F6', width=2)), secondary_y=True)
    fig_misto.add_trace(go.Scatter(x=df_c['Ano'], y=df_c['Borrifados'], name="Borrifação", line=dict(color='#334155', width=2, dash='dot')), secondary_y=True)

    fig_misto.update_layout(
        barmode='group', plot_bgcolor='white', xaxis_type='category', height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_misto, use_container_width=True)

# --- HISTÓRICO / TENDÊNCIAS (Legenda Embaixo) ---
elif st.session_state.segment == "Historico":
    st.subheader("Correlação: Humano vs Canino")
    
    df_merged = pd.merge(df_h[['Ano', 'Casos']], df_c[['Ano', 'Positivos']], on='Ano').sort_values('Ano')
    fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
    fig_corr.add_trace(go.Scatter(x=df_merged['Ano'], y=df_merged['Positivos'], name="Cães Positivos", line=dict(color='#d32f2f', width=3)), secondary_y=False)
    fig_corr.add_trace(go.Scatter(x=df_merged['Ano'], y=df_merged['Casos'], name="Casos Humanos", line=dict(color='#334155', width=3, dash='dot')), secondary_y=True)
    
    fig_corr.update_layout(
        plot_bgcolor="white", xaxis_type='category', height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# --- MAPA ---
elif st.session_state.segment == "Mapa":
    st.subheader(f"Mapa de Calor Regional | {ano_selecionado}")
    df_filt = df_m[df_m['Ano'] == ano_selecionado]
    fig = px.scatter_mapbox(df_filt, lat="Lat", lon="Lon", size="Casos", color="Casos", size_max=30, zoom=10, color_continuous_scale="YlOrRd", mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- DIRETRIZES ---
elif st.session_state.segment == "Diretrizes":
    st.subheader("Manual de Prevenção")
    with st.expander("👤 Humanos", expanded=True):
        st.write("**Sintomas:** Febre, baço/fígado aumentado, palidez.")
    with st.expander("🐕 Cães", expanded=True):
        st.write("**Sintomas:** Unhas grandes, feridas no focinho, emagrecimento.")
    st.success("Limpe o quintal e use coleiras repelentes nos cães!")

st.sidebar.markdown("---")
st.sidebar.caption(f"Analista: Aline Alice Ferreira da Silva | RU: 5277514")
