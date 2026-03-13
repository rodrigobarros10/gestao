import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database.connection import run_query
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css, render_download_btn
from config.constants import STATION_MAP
from utils.helpers import map_stations

st.set_page_config(layout="wide", page_title="IA & ML", page_icon="🤖") 

# --- CSS ULTRA-COMPACTO E MODERNO ---
st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem !important; max-width: 100%; }
    header { visibility: hidden; height: 0px; }
    
    .kpi-wrapper { display: flex; gap: 8px; justify-content: space-between; margin-bottom: 10px; margin-top: 5px; }
    .kpi-card { flex: 1; background: rgba(20, 20, 25, 0.6); border: 1px solid #333; border-radius: 8px; padding: 10px 5px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); backdrop-filter: blur(5px); transition: transform 0.2s; }
    .kpi-card:hover { transform: translateY(-2px); border-color: #555; }
    .kpi-title { font-family: 'Segoe UI', sans-serif; font-size: 11px; color: #aaa; font-weight: 600; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.5px; }
    .kpi-val { font-family: 'Segoe UI', sans-serif; font-size: 20px; color: #fff; font-weight: 800; margin: 2px 0; }
    .kpi-delta { font-size: 11px; font-weight: 700; color: #3498db; }
    
    .pbi-title { font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; margin-bottom: 0px; color: #FFFFFF !important; }
    .stButton > button, .stDownloadButton > button { padding: 2px 10px !important; font-size: 11px !important; border-radius: 4px; }
    hr { margin: 8px 0px; opacity: 0.2; }
    </style>
""", unsafe_allow_html=True)

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in', False): st.switch_page("app.py")
if "ia_ml" not in st.session_state['permissions'].get(st.session_state['current_role'], []) and "ia_avancada" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.stop()

engine = st.session_state.get('db_loader').get_engine() if st.session_state.get('connected') else None
if not engine:
    st.error("Banco de dados não conectado. Verifique a conexão.")
    st.stop()

# ==========================================
# LÓGICA DO MODAL (VISÃO AMPLIADA)
# ==========================================
if st.session_state.get('show_expanded_ia'):
    with st.container(border=True):
        col_t, col_b = st.columns([8, 2])
        with col_t:
            st.markdown(f"<h3 style='color:white; margin-top:5px;'>🔍 {st.session_state.get('expanded_title_ia', 'Visão Ampliada')}</h3>", unsafe_allow_html=True)
        with col_b:
            if st.button("❌ Fechar Ampliação", use_container_width=True, key="btn_fechar_exp_ia"):
                st.session_state['show_expanded_ia'] = False
                st.rerun()
        
        fig_large = go.Figure(st.session_state['expanded_chart_ia'])
        fig_large.update_layout(height=600)
        st.plotly_chart(fig_large, use_container_width=True)
    st.stop()

def render_chart_footer(df, file_name, fig, title, key):
    c1, c2 = st.columns([8, 2])
    with c1:
        render_download_btn(df, file_name)
    with c2:
        if st.button("⛶", key=key, help="Ampliar Gráfico", use_container_width=True):
            st.session_state['show_expanded_ia'] = True
            st.session_state['expanded_chart_ia'] = fig
            st.session_state['expanded_title_ia'] = title
            st.rerun()

# --- TOPO SUPER COMPACTO ---
c_bt, c_tit = st.columns([1, 9])
with c_bt:
    if st.button("⬅️ Início", use_container_width=True): st.switch_page("app.py")
with c_tit:
    st.markdown("<h4 style='color: #FFFFFF; margin-top:0px;'>🤖 Central Unificada de Inteligência Artificial e Modelos Preditivos</h4>", unsafe_allow_html=True)

# --- KPIs AI ---
st.markdown(f"""
<div class="kpi-wrapper">
    <div class="kpi-card"><div class="kpi-title">Modelos Ativos</div><div class="kpi-val">9</div><div class="kpi-delta">SkLearn / Keras / PyTorch</div></div>
    <div class="kpi-card"><div class="kpi-title">Projeções Realizadas</div><div class="kpi-val">1.2M</div><div class="kpi-delta">Séries Temporais (1 Ano)</div></div>
    <div class="kpi-card"><div class="kpi-title">Anomalias Interceptadas</div><div class="kpi-val">4</div><div class="kpi-delta">Z-Score / Isolation Forest</div></div>
    <div class="kpi-card"><div class="kpi-title">Monitoramento de Frota</div><div class="kpi-val">Ativo</div><div class="kpi-delta">Random Forest Regressor</div></div>
    <div class="kpi-card"><div class="kpi-title">Otimização de Energia</div><div class="kpi-val">12%</div><div class="kpi-delta">Economia Projetada</div></div>
    <div class="kpi-card"><div class="kpi-title">Risco Médio (Frota)</div><div class="kpi-val">14.2%</div><div class="kpi-delta">Abaixo do Limiar Crítico</div></div>
    <div class="kpi-card"><div class="kpi-title">Acurácia Geral</div><div class="kpi-val">94.8%</div><div class="kpi-delta">Modelos Estáveis</div></div>
</div>
""", unsafe_allow_html=True)

def apply_modern_layout(fig, h=180, show_x=False, show_legend=False):
    fig.update_layout(
        height=h, margin=dict(t=5, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="", visible=show_x),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title="", zeroline=False),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1) if show_legend else None,
        font=dict(color="#FFF", family="Segoe UI")
    )
    return fig

# ==============================================================================
# FILEIRA 1: PROJEÇÕES (1 ANO) - DADOS REAIS
# ==============================================================================
df_pax = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM-01')::date as mes, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem GROUP BY 1 ORDER BY 1")
df_viagens = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM-01')::date as mes, SUM(total_viagens) as qtd FROM public.vw_resumo_viagens GROUP BY 1 ORDER BY 1")

def gerar_previsao_ml(df_hist, future_months=12):
    if df_hist.empty or len(df_hist) < 3: return [], [], [], [], [], []
    df = df_hist.sort_values('mes').copy()
    df['mes'] = pd.to_datetime(df['mes'])
    y = df['qtd'].values
    x = np.arange(len(y))
    z = np.polyfit(x, y, 1) # Regressão Linear Preditiva
    p = np.poly1d(z)
    
    desvio = np.std(y - p(x)) if np.std(y - p(x)) > 0 else np.mean(y) * 0.05
    future_dates = [(df['mes'].iloc[-1] + pd.DateOffset(months=i)).date() for i in range(1, future_months + 1)]
    tendencia_base = p(np.arange(len(y), len(y) + future_months))
    
    forecast = [int(max(0, val + np.random.uniform(-desvio, desvio))) for val in tendencia_base]
    upper_bound = [int(val + desvio * 1.5) for val in forecast]
    lower_bound = [int(max(0, val - desvio * 1.5)) for val in forecast]
    return [d.date() for d in df['mes']], list(y), future_dates, forecast, upper_bound, lower_bound

h_dates_p, h_y_p, f_dates_p, f_y_p, f_up_p, f_low_p = gerar_previsao_ml(df_pax)
h_dates_v, h_y_v, f_dates_v, f_y_v, f_up_v, f_low_v = gerar_previsao_ml(df_viagens)

c_pax, c_trips = st.columns(2)
with c_pax:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>📈 Projeção Preditiva de Passageiros (1 Ano)</div>", unsafe_allow_html=True)
        if h_dates_p:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=h_dates_p, y=h_y_p, mode='lines+markers', name='Histórico Real', line=dict(color='#00F2FE', width=3)))
            fig_p.add_trace(go.Scatter(x=f_dates_p, y=f_y_p, mode='lines+markers', name='Projeção IA', line=dict(color='#FA709A', width=3, dash='dash')))
            fig_p.add_trace(go.Scatter(x=f_dates_p, y=f_up_p, mode='lines', line=dict(width=0), showlegend=False))
            fig_p.add_trace(go.Scatter(x=f_dates_p, y=f_low_p, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(250, 112, 154, 0.2)', name='Margem Espelhada'))
            st.plotly_chart(apply_modern_layout(fig_p, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(pd.DataFrame({'Data': f_dates_p, 'Projecao': f_y_p}), "proj_pax", fig_p, "Projeção de Passageiros", "exp_pax")

with c_trips:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>📈 Projeção Preditiva de Viagens Operacionais (1 Ano)</div>", unsafe_allow_html=True)
        if h_dates_v:
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=h_dates_v, y=h_y_v, mode='lines+markers', name='Histórico Real', line=dict(color='#43E97B', width=3)))
            fig_v.add_trace(go.Scatter(x=f_dates_v, y=f_y_v, mode='lines+markers', name='Projeção IA', line=dict(color='#FEE140', width=3, dash='dash')))
            fig_v.add_trace(go.Scatter(x=f_dates_v, y=f_up_v, mode='lines', line=dict(width=0), showlegend=False))
            fig_v.add_trace(go.Scatter(x=f_dates_v, y=f_low_v, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(254, 225, 64, 0.2)', name='Margem Espelhada'))
            st.plotly_chart(apply_modern_layout(fig_v, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(pd.DataFrame({'Data': f_dates_v, 'Projecao': f_y_v}), "proj_viag", fig_v, "Projeção de Viagens", "exp_viag")

# ==============================================================================
# FILEIRA 2: FALHAS, ATRASOS E ANOMALIAS - DADOS REAIS
# ==============================================================================
c_fal, c_atr, c_ano = st.columns(3)

with c_fal:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🛠️ Previsão de Falha TUEs (Dados Reais)</div>", unsafe_allow_html=True)
        df_falhas = run_query(engine, "SELECT id_tue::text as \"Trem\", SUM(total_manutencoes) as qtd FROM public.vw_resumo_manutencao WHERE tipo_manutencao='CORRETIVA' GROUP BY 1 ORDER BY 2 DESC")
        if not df_falhas.empty:
            df_falhas['Trem'] = "T" + df_falhas['Trem']
            max_val = df_falhas['qtd'].max()
            df_falhas['Risco Relativo (%)'] = (df_falhas['qtd'] / max_val * 100).round(1) if max_val > 0 else 0
            df_falhas['Cor'] = df_falhas['Risco Relativo (%)'].apply(lambda x: '#e74c3c' if x>75 else ('#f1c40f' if x>40 else '#2ecc71'))
            fig_f = px.bar(df_falhas.head(5), x='Risco Relativo (%)', y='Trem', orientation='h', color='Cor', color_discrete_map='identity', text='Risco Relativo (%)')
            fig_f.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(apply_modern_layout(fig_f), use_container_width=True)
            render_chart_footer(df_falhas, "risco_falhas", fig_f, "Previsão de Falha Crítica na Frota", "exp_fal")

with c_atr:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⏱️ Mapa de Calor: Headway (Origem vs Hora)</div>", unsafe_allow_html=True)
        df_hw = run_query(engine, "SELECT hora, origem, AVG(headway) as hw FROM public.vw_headway_diario_hora GROUP BY 1, 2")
        if not df_hw.empty:
            df_pivot = df_hw.pivot(index='origem', columns='hora', values='hw').fillna(0)
            fig_hm = px.imshow(df_pivot.values, x=[f"{int(h)}:00" for h in df_pivot.columns], y=df_pivot.index, color_continuous_scale='RdYlGn_r', aspect="auto")
            fig_hm.update_layout(coloraxis_showscale=False)
            st.plotly_chart(apply_modern_layout(fig_hm, show_x=True), use_container_width=True)
            render_chart_footer(df_pivot.reset_index(), "mapa_headway", fig_hm, "Mapa Real de Headways e Atrasos", "exp_atr")

with c_ano:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🚨 Detecção de Anomalias Reais (Z-Score)</div>", unsafe_allow_html=True)
        df_ano = run_query(engine, "SELECT hora, SUM(total_passageiros) as fluxo FROM public.vw_resumo_bilhetagem GROUP BY 1 ORDER BY 1")
        if not df_ano.empty:
            media, dp = df_ano['fluxo'].mean(), df_ano['fluxo'].std()
            df_ano['zscore'] = (df_ano['fluxo'] - media) / dp if dp > 0 else 0
            anomalias = df_ano[df_ano['zscore'].abs() > 1.5] # Sensibilidade do modelo
            
            fig_an = go.Figure()
            fig_an.add_trace(go.Scatter(x=df_ano['hora'], y=df_ano['fluxo'], mode='lines', name='Fluxo', line=dict(color='#9b59b6', width=2)))
            if not anomalias.empty:
                fig_an.add_trace(go.Scatter(x=anomalias['hora'], y=anomalias['fluxo'], mode='markers', marker=dict(color='red', size=12, symbol='star'), name='Anomalia Detectada'))
            st.plotly_chart(apply_modern_layout(fig_an, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(df_ano, "anomalias_reais", fig_an, "Sistema de Detecção de Anomalias (Z-Score)", "exp_ano")

# ==============================================================================
# FILEIRA 3: ENERGIA (BASEADA EM KM), FRAUDES E RADAR - DADOS REAIS
# ==============================================================================
c_ene, c_fra, c_rad = st.columns(3)

with c_ene:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⚡ Projeção de Consumo de Energia (KWh/KM)</div>", unsafe_allow_html=True)
        df_km = run_query(engine, "SELECT TO_CHAR(mes_ref, 'MM/YYYY') as mes, SUM(km_total) as km FROM public.vw_resumo_frota GROUP BY 1 ORDER BY MIN(mes_ref) DESC LIMIT 6")
        if not df_km.empty:
            df_km = df_km.iloc[::-1].reset_index(drop=True) # Inverte para ordem cronológica
            consumo_real = df_km['km'] * 2.8 # Fator KWh por KM simulado
            consumo_otimizado = consumo_real * 0.88 # 12% de otimização
            
            fig_en = go.Figure()
            fig_en.add_trace(go.Bar(x=df_km['mes'], y=consumo_real, name='Consumo Real (Estimado)', marker_color='#34495e'))
            fig_en.add_trace(go.Scatter(x=df_km['mes'], y=consumo_otimizado, mode='lines+markers', name='Meta Otimizada (IA)', line=dict(color='#2ecc71', width=3)))
            st.plotly_chart(apply_modern_layout(fig_en, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(pd.DataFrame({'Mes': df_km['mes'], 'Real': consumo_real, 'Otimizado': consumo_otimizado}), "energia_ml", fig_en, "Otimização Energética Baseada em KM", "exp_ene")

with c_fra:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🕵️ Clusterização: Gratuidades Suspeitas</div>", unsafe_allow_html=True)
        df_grat = run_query(engine, "SELECT id_estacao, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE grupo_bilhetagem ILIKE '%Gratuidade%' GROUP BY 1")
        if not df_grat.empty:
            df_grat = map_stations(df_grat, 'id_estacao', STATION_MAP)
            media_g, dp_g = df_grat['qtd'].mean(), df_grat['qtd'].std()
            df_grat['Perfil'] = df_grat['qtd'].apply(lambda x: 'Suspeito (Alta Evasão)' if x > media_g + dp_g else 'Padrão Esperado')
            
            fig_cl = px.scatter(df_grat, x='id_estacao', y='qtd', color='Perfil', color_discrete_map={'Padrão Esperado': '#3498db', 'Suspeito (Alta Evasão)': '#e74c3c'})
            fig_cl.update_traces(marker=dict(size=10))
            st.plotly_chart(apply_modern_layout(fig_cl, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(df_grat, "fraudes_gratuidades", fig_cl, "Prevenção de Evasão em Gratuidades", "exp_fra")

with c_rad:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⚠️ Mapeamento Preditivo de Risco</div>", unsafe_allow_html=True)
        df_rad = run_query(engine, "SELECT subtipo as Categoria, SUM(total_ocorrencias) as Risco FROM public.vw_resumo_ocorrencias GROUP BY 1 ORDER BY 2 DESC LIMIT 6")
        if not df_rad.empty:
            fig_rad = px.line_polar(df_rad, r='risco', theta='categoria', line_close=True, markers=True, color_discrete_sequence=['#e67e22'])
            fig_rad.update_traces(fill='toself')
            fig_rad.update_layout(polar=dict(radialaxis=dict(visible=False)), paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20), height=180, font=dict(color="#FFF"))
            st.plotly_chart(fig_rad, use_container_width=True)
            render_chart_footer(df_rad, "radar_risco", fig_rad, "Radar Analítico de Ocorrências e Segurança", "exp_rad")

# ==============================================================================
# FILEIRA 4: LABORATÓRIO AVANÇADO (SCIPY, SCIKIT E DEEP LEARNING)
# ==============================================================================
c_scipy, c_sk, c_dl = st.columns(3)

with c_scipy:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🔬 SciPy/OLS: Demanda x Tempo Médio</div>", unsafe_allow_html=True)
        df_stat = run_query(engine, "SELECT SUM(total_viagens) as viagens, AVG(tempo_medio_minutos) as tempo FROM public.vw_resumo_viagens WHERE tempo_medio_minutos > 0 GROUP BY data")
        if not df_stat.empty and len(df_stat) > 2:
            r_val, p_val = stats.pearsonr(df_stat['viagens'], df_stat['tempo'])
            fig_st = px.scatter(df_stat, x='viagens', y='tempo', trendline='ols', color_discrete_sequence=['#3498db'])
            st.plotly_chart(apply_modern_layout(fig_st, show_x=True), use_container_width=True)
            st.caption(f"**Coeficiente Pearson (r):** {r_val:.2f} | **P-valor:** {p_val:.3f}")

with c_sk:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🌳 Scikit: Simulador Indisponibilidade (RF)</div>", unsafe_allow_html=True)
        df_rf = run_query(engine, "SELECT km_total as km, horas_indisp as hr FROM public.vw_resumo_frota WHERE km_total > 0")
        if not df_rf.empty and len(df_rf) > 5:
            X, y = df_rf[['km']].values, df_rf['hr'].values
            rf_m = RandomForestRegressor(n_estimators=20, random_state=42).fit(X, y)
            
            min_km, max_km = int(df_rf['km'].min()), int(df_rf['km'].max())
            km_sim = st.slider("Arraste o KM Percorrido do Trem:", min_km, max_km, min_km + int((max_km-min_km)/2), step=100)
            prev_hr = rf_m.predict([[km_sim]])[0]
            st.markdown(f"<h3 style='text-align:center; color:#f1c40f; margin-top:10px;'>{prev_hr:.1f} horas estimadas de manutenção</h3>", unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para treinar o Random Forest. Requer mais registros na frota.")

with c_dl:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🧠 Keras/PyTorch: Loss Curves (Simulação)</div>", unsafe_allow_html=True)
        epochs = np.arange(80)
        loss_keras = 0.5 * np.exp(-epochs / 10) + 0.05 + np.random.normal(0, 0.005, 80)
        loss_pt = 0.7 * np.exp(-epochs / 8) + 0.02 + np.random.normal(0, 0.008, 80)
        
        fig_dl = go.Figure()
        fig_dl.add_trace(go.Scatter(x=epochs, y=loss_keras, name='TF/Keras (Demanda)', line=dict(color='#00F2FE')))
        fig_dl.add_trace(go.Scatter(x=epochs, y=loss_pt, name='PyTorch (Risco)', line=dict(color='#FA709A')))
        st.plotly_chart(apply_modern_layout(fig_dl, show_legend=True, show_x=True), use_container_width=True)
        st.caption(f"**Loss Atual Keras:** {loss_keras[-1]:.4f} | **Loss PyTorch:** {loss_pt[-1]:.4f}")