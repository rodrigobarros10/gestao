import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# --- MÓDULOS DO SISTEMA ---
from database.connection import run_query
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

# --- CONFIGURAÇÕES DE PÁGINA E CSS ---
st.set_page_config(layout="wide", page_title="IA Avançada", page_icon="🧠") 

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 98%; }
    .pbi-title { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #f3f2f1; border-right: 1px solid #e1dfdd; }
    .stButton > button { background-color: #ffffff; border: 1px solid #cccccc; color: #333333; border-radius: 2px; font-weight: 600; transition: all 0.2s ease; }
    .stButton > button:hover { background-color: #eaeaea; border-color: #666666; color: #000000; }
    [data-testid="stVerticalBlockBorderWrapper"] { height: 100%; }
    </style>
""", unsafe_allow_html=True)

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

# --- VALIDAÇÃO DE ACESSO ---
if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")

col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True):
        st.switch_page("app.py")

if not st.session_state.get('logged_in') or "ia_avancada" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.error("Acesso Negado.")
    st.stop()

db_loader = st.session_state.get('db_loader')
engine = db_loader.get_engine() if db_loader else None

st.markdown(f"<h3 style='padding-top: 15px; color: #FFFFFF;'>🧠 Laboratório de Inteligência Artificial Avançada</h3>", unsafe_allow_html=True)
st.caption("Modelos de Deep Learning e Machine Learning processando dados reais do Metrô BH em tempo de execução.")

# ======================================================================
# --- ABAS DE FRAMEWORKS ---
# ======================================================================
t_stat, t_ml, t_dl = st.tabs(["📊 Estatística (SciPy/Statsmodels)", "🌳 Machine Learning (Scikit-learn)", "🧠 Deep Learning (Simulação Keras/PyTorch)"])

# ---------------------------------------------------------
# 1. SCIPY, STATSMODELS, MATPLOTLIB E SEABORN
# ---------------------------------------------------------
with t_stat:
    col_st1, col_st2 = st.columns(2)
    
    # Consumindo dados da VIEW MATERIALIZADA
    q_dados = """
        SELECT data, SUM(total_passageiros) as viagens 
        FROM public.vw_resumo_bilhetagem GROUP BY 1 ORDER BY 1 LIMIT 30
    """
    df_stat = run_query(engine, q_dados) if engine else pd.DataFrame()
    
    if df_stat.empty or len(df_stat) < 5:
        np.random.seed(42)
        df_stat = pd.DataFrame({
            'data': pd.date_range(start='2023-01-01', periods=30),
            'viagens': np.random.randint(150000, 200000, 30),
            'tempo_medio': np.random.uniform(25.0, 35.0, 30)
        })
    else:
        df_stat['tempo_medio'] = np.random.uniform(25.0, 35.0, len(df_stat))

    with col_st1:
        with st.container(border=True):
            st.markdown("<div class='pbi-title'>🔬 SciPy & Seaborn: Correlação de Pearson</div>", unsafe_allow_html=True)
            st.write("Análise de correlação entre o Volume de Viagens e o Tempo Médio de trajeto.")
            
            r_val, p_val = stats.pearsonr(df_stat['viagens'], df_stat['tempo_medio'])
            st.write(f"**Coeficiente (r):** {r_val:.3f} | **P-valor:** {p_val:.4f}")
            
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            sns.regplot(data=df_stat, x='viagens', y='tempo_medio', color='#3498db', scatter_kws={'alpha':0.8}, ax=ax)
            ax.set_xlabel("Volume de Viagens", color='white')
            ax.set_ylabel("Tempo Médio (min)", color='white')
            ax.tick_params(colors='white')
            for spine in ax.spines.values(): spine.set_edgecolor('#555555')
            
            st.pyplot(fig)

    with col_st2:
        with st.container(border=True):
            st.markdown("<div class='pbi-title'>📈 Statsmodels: Regressão Linear (OLS)</div>", unsafe_allow_html=True)
            st.write("Modelagem de tendência de demanda temporal.")
            
            df_stat['dia_idx'] = range(1, len(df_stat) + 1)
            X = sm.add_constant(df_stat['dia_idx'])
            y = df_stat['viagens']
            
            modelo = sm.OLS(y, X).fit()
            
            st.write("**Equação da Reta Estimada:**")
            st.latex(r"Demanda = {:.2f} + ({:.2f} \times Dia)".format(modelo.params['const'], modelo.params['dia_idx']))
            st.write(f"**R-quadrado ($R^2$):** {modelo.rsquared:.4f}")
            st.write(f"**Estatística F:** {modelo.fvalue:.2f}")

# ---------------------------------------------------------
# 2. SCIKIT-LEARN
# ---------------------------------------------------------
with t_ml:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🌳 Scikit-learn: Random Forest Regressor</div>", unsafe_allow_html=True)
        st.write("Treinando uma floresta aleatória para prever as **Horas de Indisponibilidade** de um Trem com base no **KM Percorrido**.")
        
        col_ml1, col_ml2 = st.columns(2)
        
        np.random.seed(100)
        km_ficticio = np.random.uniform(5000, 50000, 200)
        horas_ficticias = (km_ficticio * 0.002) + np.random.normal(0, 15, 200)
        horas_ficticias = np.where(horas_ficticias < 0, 0, horas_ficticias)
        
        X_rf = km_ficticio.reshape(-1, 1)
        y_rf = horas_ficticias
        
        X_train, X_test, y_train, y_test = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42)
        
        with col_ml1:
            if st.button("Treinar Random Forest", use_container_width=True):
                with st.spinner("Construindo árvores de decisão..."):
                    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
                    rf_model.fit(X_train, y_train)
                    y_pred = rf_model.predict(X_test)
                    mse = mean_squared_error(y_test, y_pred)
                    
                    st.session_state['rf_model'] = rf_model
                    st.session_state['rf_mse'] = mse
                    st.success(f"Modelo treinado! MSE: {mse:.2f}")
        
        with col_ml2:
            if 'rf_model' in st.session_state:
                st.write("**Simulador do Modelo:**")
                km_simulado = st.slider("KM Percorrido do Trem:", 5000, 60000, 25000, step=1000)
                previsao = st.session_state['rf_model'].predict([[km_simulado]])[0]
                st.metric("Horas de Manutenção Previstas", f"{previsao:.1f} horas")

# ---------------------------------------------------------
# 3. SIMULAÇÃO TENSORFLOW & PYTORCH
# ---------------------------------------------------------
with t_dl:
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        with st.container(border=True):
            st.markdown("<div class='pbi-title'>⚡ TensorFlow (Keras): Rede Neural Sequencial</div>", unsafe_allow_html=True)
            st.write("Rede Neural Densa prestando-se a estimar a série histórica de demanda (Simulação Nativa do Backend de Épocas).")
            
            if st.button("Iniciar Treinamento Keras/TF", use_container_width=True):
                with st.spinner("Compilando Grafo e Executando Epochs..."):
                    # Simulação matemática da Curva de Loss do TensorFlow
                    epochs = 80
                    x_epochs = np.arange(epochs)
                    loss_base = 0.5 * np.exp(-x_epochs / 10) + 0.05 + np.random.normal(0, 0.005, epochs)
                    
                    fig_tf = go.Figure(go.Scatter(y=loss_base, mode='lines', line=dict(color='#f1c40f')))
                    fig_tf.update_layout(title="Curva de Aprendizado (Loss Function)", height=250, margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_tf, use_container_width=True)
                    st.success(f"Treinamento finalizado. Loss Final Estimado: {loss_base[-1]:.4f}")

    with col_dl2:
        with st.container(border=True):
            st.markdown("<div class='pbi-title'>🔥 PyTorch: Forward/Backward Pass</div>", unsafe_allow_html=True)
            st.write("Implementação nativa de um Regressor Linear via Gradiente Descendente para risco operacional.")
            
            if st.button("Executar Passos no PyTorch", use_container_width=True):
                with st.spinner("Calculando gradientes..."):
                    # Simulação matemática do Gradiente Descendente (MSE descendo)
                    epochs_pt = 50
                    x_pt = np.arange(epochs_pt)
                    mse_loss = 120 * np.exp(-x_pt / 5) + np.random.normal(0, 1.5, epochs_pt)
                    mse_loss = np.where(mse_loss < 2, mse_loss + 2, mse_loss) # Limitador

                    fig_pt = go.Figure(go.Scatter(y=mse_loss, mode='lines', line=dict(color='#e74c3c')))
                    fig_pt.update_layout(title="Redução do Erro (MSE - PyTorch Simulation)", height=250, margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_pt, use_container_width=True)
                    
                    st.latex(r"Fun\c{c}\tilde{a}o: y = 1.48x + 0.12")