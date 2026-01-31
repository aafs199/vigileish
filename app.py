import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. DESIGN SYSTEM
st.set_page_config(page_title="VigiLeish Intelligence | One Health", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #fcfcfd;
    }
    
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3em; background-color: #ffffff;
        color: #0f172a; border: 1px solid #e2e8f0; text-align: left; transition: all 0.2s;
        margin-bottom: 5px;
    }
    div.stButton > button:hover { border-color: #d32f2f; color: #d32f2f; background-color: #fffafa; }
    
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS INTEGRADO (2007-2023)
@st.cache_data
def load_all_data():
    try:
        # --- DADOS HUMANOS ---
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df.columns = [c.strip() for c in df.columns]
        
        df['Ano_Num'] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
        df_hist = df[(df['Ano_Num'] >= 2007) & (df['Ano_Num'] <= 2023)].copy()
        df_hist = df_hist.iloc[:, :7]
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade']
        
        for c in ['Ano', 'Casos', 'Obitos', 'Letalidade']:
            df_hist[c] = pd.to_numeric(df_hist[c], errors='coerce').fillna(0).astype(int)
        
        # Regionais
        coords = {
            'Barreiro': [-19.974, -44.022], 'Centro Sul': [-19.933, -43.935], 'Leste': [-19.921, -43.902],
            'Nordeste': [-19.892, -43.911], 'Noroeste': [-19.914, -43.962], 'Norte': [-19.831, -43.918],
            'Oeste': [-19.952, -43.984], 'Pampulha': [-19.855, -43.971], 'Venda Nova': [-19.812, -43.955]
        }
        reg_list = []
        for reg, coord in coords.items():
            mask = df.iloc[:,0].str.contains(reg, na=False, case=False)
            if mask.any():
                row = df[mask].iloc[0]
                for i, ano in enumerate(range(2007, 2024)):
                    reg_list.append({
                        'Regional': reg, 'Ano': int(ano), 
                        'Casos': pd.to_numeric(row.iloc[i+1], errors='coerce'), 
                        'Lat': coord[0], 'Lon': coord[1]
                    })
        
        # --- DADOS CANINOS ---
        df_can = pd.read_csv('caninos.csv', sep=';', encoding='iso-8859-1')
        df_can.columns = ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']
        
        for col in ['Ano', 'Sorologias', 'Positivos', 'Eutanasiados', 'Borrifados']:
            df_can[col] = df_can[col].astype(str).str.replace('.', '').str.replace(',', '.')
            df_can[col] = pd.to_numeric(df_can[col], errors='coerce').fillna(0).astype(int)
        
        df_can = df_can[(df_can['Ano'] >= 2007) & (df_can['Ano'] <= 2023)]
        df_can['Taxa_Positividade'] = (df_can['Positivos'] / df_can['Sorologias'] * 100).fillna(0)

        return df_hist, pd.DataFrame(reg_list), df_can
    except Exception as e:
        st.error(f"Erro ao carregar arquivos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_h, df_m, df_can = load_all_data()

# 3. NAVEGAÇÃO E FILTRO
if 'segment' not in st.session_state: st.session_state.segment = "Geral"

st.sidebar.title("VigiLeish Navigator")
if st.sidebar.button("📊 Painel Geral"): st.session_state.segment = "Geral"
if st.sidebar.button("🗺️ Monitoramento Geográfico"): st.session_state.segment = "Mapa"
if st.sidebar.button("📈 Série Histórica"): st.session_state.segment = "Historico"
if st.sidebar.button("🐕 Vigilância Canina"): st.session_state.segment = "Canina"
if st.sidebar.button("📋 Diretrizes ODS 3"): st.session_state.segment = "Diretrizes"

st.sidebar.markdown("---")
anos_lista = sorted(df_m['Ano'].unique().tolist(), reverse=True)
ano_alvo = st.sidebar.selectbox("Filtro de Ano:", options=anos_lista, index=0)

# 4. EXIBIÇÃO
st.title("VigiLeish Intelligence System")

if st.session_state.segment == "Geral":
    st.subheader(f"Resumo Estratégico de Saúde Única | {ano_alvo}")
    df_ah = df_h[df_h['Ano'] == ano_alvo]
    df_ac = df_can[df_can['Ano'] == ano_alvo]

    col_h, col_c = st.columns(2)
    with col_h:
        st.markdown("#### 🏥 Indicadores Humanos")
        c1, c2, c3 = st.columns(3)
        if not df_ah.empty:
            c1.metric("Casos", f"{df_ah['Casos'].iloc[0]}")
            c2.metric("Óbitos", f"{df_ah['Obitos'].iloc[0]}")
            c3.metric("Letalidade", f"{(df_ah['Obitos'].iloc[0]/df_ah['Casos'].iloc[0]*100):.1f}%" if df_ah['Casos'].iloc[0]>0 else "0%")
    with col_c:
        st.markdown("#### 🐕 Indicadores Caninos")
        c4, c5, c6 = st.columns(3)
        if not df_ac.empty:
            c4.metric("Positivos", f"{df_ac['Positivos'].iloc[0]:,}".replace(',', '.'))
            c5.metric("Eutanasiados", f"{df_ac['Eutanasiados'].iloc[0]:,}".replace(',', '.'))
            c6.metric("Borrifados", f"{df_ac['Borrifados'].iloc[0]:,}".replace(',', '.'))
    
    st.write("---")
    st.markdown(f"**Análise de Esforço ({ano_alvo}):** Foram realizadas **{df_ac['Sorologias'].iloc[0]:,}** sorologias, resultando em uma taxa de positividade de **{df_ac['Taxa_Positividade'].iloc[0]:.1f}%**.".replace(',', '.'))

elif st.session_state.segment == "Canina":
    st.subheader("Vigilância Integrada: Cães, Testagem e Controle Ambiental")
    
    # --- GRÁFICO MISTO COMPLETO (SOLICITADO) ---
    st.markdown("#### Evolução: Testagem, Positividade e Prevenção")
    
    fig_misto = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras (Eixo Esquerdo - Cães)
    fig_misto.add_trace(go.Bar(x=df_can['Ano'], y=df_can['Positivos'], name="Cães Positivos", marker_color='#F59E0B', opacity=0.7), secondary_y=False)
    fig_misto.add_trace(go.Bar(x=df_can['Ano'], y=df_can['Eutanasiados'], name="Cães Eutanasiados", marker_color='#D32F2F', opacity=0.9), secondary_y=False)

    # Linhas (Eixo Direito - Esforço/Volume)
    fig_misto.add_trace(go.Scatter(x=df_can['Ano'], y=df_can['Sorologias'], name="Sorologias Realizadas", line=dict(color='#3B82F6', width=3), mode='lines+markers'), secondary_y=True)
    fig_misto.add_trace(go.Scatter(x=df_can['Ano'], y=df_can['Borrifados'], name="Imóveis Borrifados", line=dict(color='#334155', width=3, dash='dot'), mode='lines+markers'), secondary_y=True)

    fig_misto.update_layout(barmode='group', plot_bgcolor='white', xaxis_type='category', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_misto.update_yaxes(title_text="<b>Quantidade de Cães</b>", secondary_y=False)
    fig_misto.update_yaxes(title_text="<b>Volume (Sorologias/Borrifação)</b>", secondary_y=True)
    
    st.plotly_chart(fig_misto, use_container_width=True)
    
    st.info("💡 **Dica de Leitura:** As barras mostram a situação dos animais (doença). As linhas mostram o volume de trabalho realizado pela saúde pública (testes e borrifação).")

elif st.session_state.segment == "Mapa":
    st.subheader(f"Distribuição Geográfica de Casos | {ano_alvo}")
    df_map_filt = df_m[df_m['Ano'] == ano_alvo]
    col_a, col_b = st.columns([1.8, 1])
    with col_a:
        fig = px.scatter_mapbox(df_map_filt, lat="Lat", lon="Lon", size="Casos", color="Casos", size_max=35, zoom=10.5, color_continuous_scale="YlOrRd", mapbox_style="carto-positron")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.plotly_chart(px.bar(df_map_filt.sort_values('Casos'), x='Casos', y='Regional', color='Casos', color_continuous_scale="YlOrRd"), use_container_width=True)

elif st.session_state.segment == "Historico":
    st.subheader("Correlação Histórica: Ciclo Humano-Canino")
    df_h_m = df_h[['Ano', 'Casos']].copy(); df_c_m = df_can[['Ano', 'Positivos']].copy()
    df_merged = pd.merge(df_h_m, df_c_m, on='Ano').sort_values('Ano')
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(go.Scatter(x=df_merged['Ano'], y=df_merged['Positivos'], name="Cães Positivos", line=dict(color='#d32f2f', width=3)), secondary_y=False)
    fig_dual.add_trace(go.Scatter(x=df_merged['Ano'], y=df_merged['Casos'], name="Casos Humanos", line=dict(color='#334155', width=3, dash='dot')), secondary_y=True)
    fig_dual.update_layout(plot_bgcolor="white", xaxis_type='category')
    st.plotly_chart(fig_dual, use_container_width=True)

elif st.session_state.segment == "Diretrizes":
    st.subheader("Saúde e Bem-Estar (ODS 3)")
    st.info("Painel consolidado (2007-2023). A inclusão das Sorologias Realizadas permite avaliar se a queda nos casos positivos em certos anos foi real ou fruto de menor testagem.")

st.sidebar.markdown("---")
st.sidebar.caption("Analista: Aline Alice Ferreira da Silva | RU: 5277514")
