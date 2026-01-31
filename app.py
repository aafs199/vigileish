import streamlit as st
import pandas as pd
import plotly.express as px

# 1. DESIGN SYSTEM (Estética Profissional)
st.set_page_config(page_title="VigiLeish Intelligence | One Health", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #fcfcfd;
    }
    
    /* Menu Lateral Customizado */
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3em; background-color: #ffffff;
        color: #0f172a; border: 1px solid #e2e8f0; text-align: left; transition: all 0.2s;
        margin-bottom: 5px;
    }
    div.stButton > button:hover { border-color: #d32f2f; color: #d32f2f; background-color: #fffafa; }
    
    /* Cards de Métricas */
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS INTEGRADO
@st.cache_data
def load_all_data():
    try:
        # --- DADOS HUMANOS ---
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df.columns = [c.strip() for c in df.columns]
        
        # Histórico (2007-2024)
        df_hist = df.iloc[13:31].copy()
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade'] + list(df.columns[7:])
        for c in ['Casos', 'Obitos', 'Letalidade']:
            df_hist[c] = pd.to_numeric(df_hist[c], errors='coerce').fillna(0)
        
        # Regionais
        reg_names = ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova']
        coords = {'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
                  'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
                  'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]}
        
        reg_list = []
        for reg in reg_names:
            row = df[df.iloc[:,0].str.contains(reg, na=False, case=False)].iloc[0]
            for i, ano in enumerate(range(2007, 2024)):
                reg_list.append({
                    'Regional': reg, 'Ano': ano, 
                    'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'), 
                    'Lat': coords[reg][0], 'Lon': coords[reg][1]
                })
        
        # --- DADOS CANINOS ---
        df_can = pd.read_csv('caninos.csv', sep=';', encoding='iso-8859-1')
        df_can.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']
        
        # Limpeza de formato (remover pontos de milhar)
        for col in ['Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']:
            df_can[col] = df_can[col].astype(str).str.replace('.', '').str.replace(',', '.')
            df_can[col] = pd.to_numeric(df_can[col], errors='coerce').fillna(0)
        
        df_can['Ano'] = pd.to_numeric(df_can['Ano'], errors='coerce')
        df_can['Taxa_Positividade'] = (df_can['Positivos'] / df_can['Sorologias'] * 100).fillna(0)

        return df_hist, pd.DataFrame(reg_list), df_can
    except Exception as e:
        st.error(f"Erro ao carregar arquivos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_can = load_all_data()

# 3. NAVEGAÇÃO E FILTROS
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

st.sidebar.title("VigiLeish Navigator")
if st.sidebar.button("📊 Painel Geral"): st.session_state.segment = "Geral"
if st.sidebar.button("🗺️ Monitoramento Geográfico"): st.session_state.segment = "Mapa"
if st.sidebar.button("📈 Série Histórica"): st.session_state.segment = "Historico"
if st.sidebar.button("🐕 Vigilância Canina"): st.session_state.segment = "Canina"
if st.sidebar.button("📋 Diretrizes ODS 3"): st.session_state.segment = "Diretrizes"

st.sidebar.markdown("---")
anos_disponive
