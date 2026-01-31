import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DESIGN SYSTEM
st.set_page_config(page_title="VigiLeish Intelligence | One Health", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; background-color: #fcfcfd; }
    
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3em; background-color: #ffffff;
        color: #0f172a; border: 1px solid #e2e8f0; text-align: left; transition: all 0.2s;
    }
    div.stButton > button:hover { border-color: #d32f2f; color: #d32f2f; background-color: #fffafa; }
    
    .stMetric { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS INTEGRADO
@st.cache_data
def load_all_data():
    try:
        # --- DADOS HUMANOS ---
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df.columns = [c.strip() for c in df.columns]
        df_hist = df.iloc[13:31].copy()
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df.columns[7:])
        for c in ['Casos', 'Obitos', 'Letalidade']:
            df_hist[c] = pd.to_numeric(df_hist[c], errors='coerce').fillna(0)
        
        # Regionais (Humanos)
        reg_names = ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova']
        coords = {'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
                  'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
                  'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]}
        reg_list = []
        for reg in reg_names:
            row = df[df.iloc[:,0].str.contains(reg, na=False, case=False)].iloc[0]
            for i, ano in enumerate(range(2007, 2024)):
                reg_list.append({'Regional': reg, 'Ano': ano, 'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'), 'Lat': coords[reg][0], 'Lon': coords[reg][1]})
        
        # --- DADOS CANINOS ---
        # Lendo o novo arquivo enviado
        df_can = pd.read_csv('caninos.csv', sep=';', encoding='iso-8859-1')
        df_can.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']
        
        # Limpando os pontos de milhar do formato brasileiro (ex: 155.643 -> 155643)
        for col in ['Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']:
            df_can[col] = df_can[col].astype(str).str.replace('.', '').str.replace(',', '.')
            df_can[col] = pd.to_numeric(df_can[col], errors='coerce').fillna(0)
        
        df_can['Ano'] = pd.to_numeric(df_can['Ano'], errors='coerce')
        df_can['Taxa_Positividade'] = (df_can['Positivos'] / df_can['Sorologias'] * 100).fillna(0)

        return df_hist, pd.DataFrame(reg_list), df_can
    except Exception as e:
        st.error(f"Erro nos dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_can = load_all_data()

# 3. NAVEGAÇÃO
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

st.sidebar.title("VigiLeish Navigator")
if st.sidebar.button("📊 Painel Geral"): st.session_state.segment = "Geral"
if st.sidebar.button("🗺️ Monitoramento Geográfico"): st.session_state.segment = "Mapa"
if st.sidebar.button("📈 Série Histórica"): st.session_state.segment = "Historico"
if st.sidebar.button("🐕 Vigilância Canina"): st.session_state.segment = "Canina"
if st.sidebar.button("📋 Diretrizes ODS 3"): st.session_state.segment = "Diretrizes"

st.sidebar.markdown("---")
ano_alvo = st.sidebar.select_slider("Ano:", options=sorted(df_m['Ano'].unique()), value=2023)

# 4. EXIBIÇÃO
st.title("VigiLeish Intelligence")

if st.session_state.segment == "Geral":
    st.subheader(f"Status Epidemiológico | {ano_alvo}")
    df_ano = df_h[df_h['Ano'].astype(str).str.contains(str(ano_alvo))]
    c1, c2, c3 = st.columns(3)
    if not df_ano.empty:
        c1.metric("Casos Humanos", f"{df_ano['Casos'].iloc[0]:.0f}")
        c2.metric("Óbitos", f"{df_ano['Obitos'].iloc[0]:.0f}")
        c3.metric("Letalidade", f"{(df_ano['Obitos'].iloc[0]/df_ano['Casos'].iloc[0]*100):.1f}%" if df_ano['Casos'].iloc[0]>0 else "0%")

elif st.session_state.segment == "Mapa":
    st.subheader(f"Mapa de Calor Térmico ({ano_alvo})")
    df_map_filt = df_m[df_m['Ano'] == ano_alvo]
    ca, cb = st.columns([2, 1])
    with ca:
        fig = px.scatter_mapbox(df_map_filt, lat="Lat", lon="Lon", size="Casos", color="Casos",
                                 color_continuous_scale="YlOrRd", zoom=10.5, mapbox_style="carto-positron", height=500)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        st.plotly_chart(px.bar(df_map_filt.sort_values('Casos'), x='Casos', y='Regional', color='Casos', color_continuous_scale="YlOrRd"), use_container_width=True)

elif st.session_state.segment == "Canina":
    st.subheader(f"Vigilância Animal (LVC) | {ano_alvo}")
    df_can_ano = df_can[df_can['Ano'] == ano_alvo]
    
    if not df_can_ano.empty:
        ca, cb, cc = st.columns(3)
        ca.metric("Cães Positivos", f"{df_can_ano['Positivos'].iloc[0]:.0f}")
        cb.metric("Taxa de Positividade", f"{df_can_ano['Taxa_Positividade'].iloc[0]:.1f}%")
        cc.metric("Imóveis Borrifados", f"{df_can_ano['Borrifados'].iloc[0]:.0f}")
        
    st.markdown("### Correlação: Humanos vs Caninos")
    # Gráfico de correlação histórica
    df_merge = pd.merge(df_h[['Ano', 'Casos']], df_can[['Ano', 'Positivos']], on='Ano')
    fig_corr = px.line(df_merge, x='Ano', y=['Casos', 'Positivos'], 
                       labels={'value': 'Quantidade', 'variable': 'Tipo'},
                       color_discrete_map={'Casos': '#334155', 'Positivos': '#d32f2f'},
                       title="Aumento nos cães costuma preceder casos humanos")
    st.plotly_chart(fig_corr, use_container_width=True)

elif st.session_state.segment == "Historico":
    st.subheader("Séries Históricas Combinadas")
    st.plotly_chart(px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True, color_discrete_map={'Casos': '#334155', 'Obitos': '#ef4444'}), use_container_width=True)

elif st.session_state.segment == "Diretrizes":
    st.subheader("Foco ODS 3: Saúde e Bem-Estar")
    st.info("Estratégias: 1. Controle de Reservatórios (Cães) | 2. Manejo Ambiental | 3. Diagnóstico Precoce.")

st.sidebar.caption(f"Analista: Aline Alice Ferreira da Silva | RU: 5277514")
