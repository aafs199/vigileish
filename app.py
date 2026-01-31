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

# 2. MOTOR DE DADOS INTEGRADO
@st.cache_data
def load_all_data():
    try:
        # --- DADOS HUMANOS ---
        df = pd.read_csv('dados.csv', sep=None, engine='python', encoding='iso-8859-1')
        df.columns = [c.strip() for c in df.columns]
        
        # Filtrando estritamente entre 2007 e 2023
        df['Ano_Num'] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
        df_hist = df[(df['Ano_Num'] >= 2007) & (df['Ano_Num'] <= 2023)].copy()
        
        # Selecionando colunas base
        df_hist = df_hist.iloc[:, :7]
        df_hist.columns = ['Ano', 'Casos', 'Pop', 'Inc', 'Prev', 'Obitos', 'Letalidade']
        
        for c in ['Ano', 'Casos', 'Obitos', 'Letalidade']:
            df_hist[c] = pd.to_numeric(df_hist[c], errors='coerce').fillna(0).astype(int)
        
        # Coordenadas das Regionais
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
                # Coleta colunas de 2007 (índice 1) até 2023 (índice 17)
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
        
        # Mantendo apenas o intervalo solicitado
        df_can = df_can[(df_can['Ano'] >= 2007) & (df_can['Ano'] <= 2023)]
        df_can['Taxa_Positividade'] = (df_can['Positivos'] / df_can['Sorologias'] * 100).fillna(0)

        return df_hist, pd.DataFrame(reg_list), df_can
    except Exception as e:
        st.error(f"Erro ao carregar arquivos: {e}")
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
anos_disponiveis = sorted(df_m['Ano'].unique().tolist())
ano_alvo = st.sidebar.select_slider("Ano de Referência:", options=anos_disponiveis, value=max(anos_disponiveis) if anos_disponiveis else 2023)

# 4. EXIBIÇÃO
st.title("VigiLeish Intelligence System")

if st.session_state.segment == "Geral":
    st.subheader(f"Visão Consolidada | {ano_alvo}")
    df_ah = df_h[df_h['Ano'] == ano_alvo]
    df_ac = df_can[df_can['Ano'] == ano_alvo]
    c1, c2, c3, c4 = st.columns(4)
    if not df_ah.empty:
        c1.metric("Casos Humanos", f"{df_ah['Casos'].iloc[0]}")
        letalidade = (df_ah['Obitos'].iloc[0]/df_ah['Casos'].iloc[0]*100) if df_ah['Casos'].iloc[0]>0 else 0
        c2.metric("Taxa Letalidade", f"{letalidade:.1f}%")
    if not df_ac.empty:
        c3.metric("Cães Positivos", f"{df_ac['Positivos'].iloc[0]}")
        c4.metric("Positividade Canina", f"{df_ac['Taxa_Positividade'].iloc[0]:.1f}%")

elif st.session_state.segment == "Mapa":
    st.subheader(f"Mapeamento de Calor Regional ({ano_alvo})")
    df_map_filt = df_m[df_m['Ano'] == ano_alvo]
    col_a, col_b = st.columns([1.8, 1])
    with col_a:
        fig = px.scatter_mapbox(df_map_filt, lat="Lat", lon="Lon", size="Casos", color="Casos",
                                 size_max=35, zoom=10.5, color_continuous_scale="YlOrRd", mapbox_style="carto-positron")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.plotly_chart(px.bar(df_map_filt.sort_values('Casos'), x='Casos', y='Regional', color='Casos', color_continuous_scale="YlOrRd"), use_container_width=True)

elif st.session_state.segment == "Canina":
    st.subheader(f"Monitoramento Animal (2007-2023)")
    df_c_ano = df_can[df_can['Ano'] == ano_alvo]
    m1, m2, m3, m4, m5 = st.columns(5)
    if not df_c_ano.empty:
        m1.metric("Sorologias", f"{df_c_ano['Sorologias'].iloc[0]:.0f}")
        m2.metric("Positivos", f"{df_c_ano['Positivos'].iloc[0]:.0f}")
        m3.metric("Taxa Positividade", f"{df_c_ano['Taxa_Positividade'].iloc[0]:.1f}%")
        m4.metric("Eutanasiados", f"{df_c_ano['Eutanasiados'].iloc[0]:.0f}")
        m5.metric("Imóveis Borrifados", f"{df_c_ano['Borrifados'].iloc[0]:.0f}")

    st.markdown("---")
    st.subheader("Desfecho e Intervenção Canina")
    c1, c2 = st.columns(2)
    with c1:
        fig_des = go.Figure()
        fig_des.add_trace(go.Bar(x=df_can['Ano'], y=df_can['Positivos'], name='Positivos', marker_color='#F59E0B'))
        fig_des.add_trace(go.Bar(x=df_can['Ano'], y=df_can['Eutanasiados'], name='Eutanasiados', marker_color='#D32F2F'))
        fig_des.update_layout(barmode='group', plot_bgcolor='white', xaxis_type='category')
        st.plotly_chart(fig_des, use_container_width=True)
    with c2:
        fig_borr = px.line(df_can, x='Ano', y='Borrifados', markers=True, color_discrete_sequence=['#334155'])
        fig_borr.update_layout(plot_bgcolor='white', xaxis_type='category')
        st.plotly_chart(fig_borr, use_container_width=True)

    st.markdown("---")
    st.subheader("Tendência Comparativa: Humanos vs Caninos (Eixos Independentes)")
    df_h_merge = df_h[['Ano', 'Casos']].copy()
    df_c_merge = df_can[['Ano', 'Positivos']].copy()
    df_merge = pd.merge(df_h_merge, df_c_merge, on='Ano').sort_values('Ano')
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(go.Scatter(x=df_merge['Ano'], y=df_merge['Positivos'], name="Cães Positivos", line=dict(color='#d32f2f', width=3), mode='lines+markers'), secondary_y=False)
    fig_dual.add_trace(go.Scatter(x=df_merge['Ano'], y=df_merge['Casos'], name="Casos Humanos", line=dict(color='#334155', width=3, dash='dot'), mode='lines+markers'), secondary_y=True)
    fig_dual.update_yaxes(title_text="Cães Positivos", secondary_y=False, color='#d32f2f')
    fig_dual.update_yaxes(title_text="Casos Humanos", secondary_y=True, color='#334155')
    fig_dual.update_layout(plot_bgcolor="white", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_dual, use_container_width=True)

elif st.session_state.segment == "Historico":
    st.subheader("Evolução Histórica Humana (2007-2023)")
    fig_h_line = px.line(df_h, x='Ano', y=['Casos', 'Obitos'], markers=True, color_discrete_map={'Casos': '#334155', 'Obitos': '#ef4444'})
    fig_h_line.update_layout(plot_bgcolor="white", xaxis_type='category')
    st.plotly_chart(fig_h_line, use_container_width=True)

elif st.session_state.segment == "Diretrizes":
    st.subheader("Saúde e Bem-Estar (ODS 3)")
    st.info("Painel consolidado com dados de 2007 a 2023. A exclusão de 2024 e das somas totais garante a precisão técnica necessária para a análise acadêmica.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Analista: Aline Alice Ferreira da Silva | RU: 5277514")
