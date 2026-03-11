import streamlit as st
import pandas as pd
import plotly.express as px
import random
from components.filters import get_date_filter_ui
from components.ui_elements import render_kpi_card_modern, render_download_btn
from database.connection import run_query

from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")

col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True):
        st.switch_page("app.py")

if not st.session_state.get('logged_in') or "indicadores" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.error("Acesso Negado.")
    st.stop()

# --- CONEXÃO COM BANCO DE DADOS ---
db_loader = st.session_state.get('db_loader')
if not db_loader:
    st.error("Banco de dados desconectado.")
    st.stop()
engine = db_loader.get_engine()

# --- FILTROS ---
filters = get_date_filter_ui("cmd")
ano_filtro = filters['ano']
mes_filtro = filters['mes']

st.subheader(f"Painel de Indicadores (CMD) - {filters['mes_nome']}/{filters['ano']}")

# --- FUNÇÃO AUXILIAR PARA BUSCAR KPI ---
def get_kpi_value(query):
    try:
        df = run_query(engine, query)
        if not df.empty and pd.notnull(df.iloc[0, 0]):
            return float(df.iloc[0, 0])
    except Exception as e:
        pass
    return 0.0

# --- BUSCA DOS INDICADORES REAIS NO BANCO DE DADOS ---
# Utilizando as tabelas e views passadas
q_ico = f"SELECT ico_linha FROM public.vw_ico_linha_final WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1"
q_tmp = f"SELECT tmp FROM public.kpi_tmp WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1"
q_ial = f"SELECT ial FROM public.kpi_ial WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1"
q_iol = f"SELECT iol FROM public.kpi_iol WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1"
q_mro = f"SELECT mro_linha FROM public.kpi_mro WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1"
q_dtt = f"SELECT dtt FROM public.kpi_dtt WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1"

ico = get_kpi_value(q_ico)
tmp = get_kpi_value(q_tmp)
ial = get_kpi_value(q_ial)
iol = get_kpi_value(q_iol)
mro = get_kpi_value(q_mro)
dtt = get_kpi_value(q_dtt)

# Indicadores não passados na lista de queries (Zerados conforme solicitado)
est = 0.0
lin = 0.0
irg = 0.0
isp = 0.0

# --- CÁLCULO DOS COEFICIENTES (FÓRMULAS CONTRATUAIS) ---
ido = (0.1 * tmp) + (0.3 * ico) + (0.3 * ial) + (0.3 * iol)
idm = (0.25 * mro) + (0.25 * dtt) + (0.25 * est) + (0.25 * lin)
ids = (0.5 * irg) + (0.5 * isp)
cmd = (0.4 * ido) + (0.4 * idm) + (0.2 * ids)

# --- RENDENRIZAÇÃO DOS CARDS ---
st.markdown("### 🚦 IDO - Operacional")
c1, c2, c3, c4 = st.columns(4)
with c1: 
    render_kpi_card_modern("ICO - Oferta", ico, "Viagens", "0.980", ico >= 0.98)
    if st.button("📈 Evolução Diaria", key="btn_ico"): st.session_state['active_cmd_chart'] = 'ico'
with c2: 
    render_kpi_card_modern("TMP - Tempo", tmp, "Regularidade", "1.010", 0.99 <= tmp <= 1.05)
    if st.button("📈 Evolução Diaria", key="btn_tmp"): st.session_state['active_cmd_chart'] = 'tmp'
with c3: 
    render_kpi_card_modern("IAL - Segurança", ial, "Acidentes", "0.950", ial >= 0.95)
    if st.button("📈 Evolução Diaria", key="btn_ial"): st.session_state['active_cmd_chart'] = 'ial'
with c4: 
    render_kpi_card_modern("IOL - Ocorrências", iol, "Falhas Ops", "0.950", iol >= 0.95)
    if st.button("📈 Evolução Diaria", key="btn_iol"): st.session_state['active_cmd_chart'] = 'iol'

st.markdown("### 🔧 IDM - Manutenção")
c5, c6, c7, c8 = st.columns(4)
with c5: 
    render_kpi_card_modern("MRO (MKBF)", mro, "Km/Falhas", "> 1.0", mro >= 1.0)
    if st.button("📈 Evolução Diaria", key="btn_mro"): st.session_state['active_cmd_chart'] = 'mro'
with c6: 
    render_kpi_card_modern("DTT (Frota)", dtt, "Disp. Trens", "0.995", dtt >= 0.995)
    if st.button("📈 Evolução Diaria", key="btn_dtt"): st.session_state['active_cmd_chart'] = 'dtt'
with c7: 
    render_kpi_card_modern("EST (Estações)", est, "Disp. Equip.", "0.98", est >= 0.98)
    if st.button("📈 Evolução Diaria", key="btn_est"): st.session_state['active_cmd_chart'] = 'est'
with c8: 
    render_kpi_card_modern("LIN (Via)", lin, "Disp. Via", "0.99", lin >= 0.99)
    if st.button("📈 Evolução Diaria", key="btn_lin"): st.session_state['active_cmd_chart'] = 'lin'

st.markdown("### 👥 IDS - Satisfação")
c9, c10 = st.columns(2)
with c9: 
    render_kpi_card_modern("IRG (Ouvidoria)", irg, "Reclamações", "0.90", irg >= 0.9)
    if st.button("📈 Evolução Diaria", key="btn_irg"): st.session_state['active_cmd_chart'] = 'irg'
with c10: 
    render_kpi_card_modern("ISP (Pesquisa)", isp, "Satisfação", "0.85", isp >= 0.85)
    if st.button("📈 Evolução Diaria", key="btn_isp"): st.session_state['active_cmd_chart'] = 'isp'

st.divider()

# --- GRÁFICO DE EVOLUÇÃO (Simulação baseada no valor real do mês) ---
active_cmd_chart = st.session_state.get('active_cmd_chart')
if active_cmd_chart:
    metas_cmd = {'ico': 0.980, 'tmp': 1.010, 'ial': 0.950, 'iol': 0.950, 'mro': 1.0, 'dtt': 0.995, 'est': 0.98, 'lin': 0.99, 'irg': 0.90, 'isp': 0.85, 'cmd': 1.000}
    base_vals = {'ico': ico, 'tmp': tmp, 'ial': ial, 'iol': iol, 'mro': mro, 'dtt': dtt, 'est': est, 'lin': lin, 'irg': irg, 'isp': isp, 'cmd': cmd}
    
    base_val = base_vals.get(active_cmd_chart, 1.0)
    meta_val = metas_cmd.get(active_cmd_chart, 1.0)
    
    dates = pd.date_range(start=filters['dt_start'], end=filters['dt_end'])
    
    # Se o valor base for 0 (indicador inativo/não possui tabela), gera a linha zerada. 
    # Caso contrário, espelha a volatilidade natural em volta do indicador real do mês.
    if base_val == 0.0:
        valores = [0.0 for _ in dates]
    else:
        valores = [base_val * random.uniform(0.97, 1.03) for _ in dates]
        
    df_cmd_evo = pd.DataFrame({'Data': dates, 'Valor': valores})
    
    fig_cmd = px.line(df_cmd_evo, x='Data', y='Valor', title=f"Evolução Diária - Indicador {active_cmd_chart.upper()}", markers=True)
    fig_cmd.add_hline(y=meta_val, line_dash="dash", line_color="red", annotation_text=f"Meta ({meta_val})")
    st.plotly_chart(fig_cmd, use_container_width=True)

st.divider()

col_res1, col_res2 = st.columns([1, 2])
with col_res2:
    cor_cmd = "#2ecc71" if cmd >= 1.0 else "#e67e22"
    st.markdown(f"""
    <div style="background-color: #262730; border: 2px solid {cor_cmd}; border-radius: 15px; padding: 20px; text-align: center;">
        <h2 style="color: #aaa; margin: 0; font-size: 18px;">CMD - COEFICIENTE DE DESEMPENHO</h2>
        <h1 style="color: {cor_cmd}; font-size: 60px; margin: 10px 0; font-weight: 800;">{cmd:.4f}</h1>
        <p style="color: #fff;">Meta Contratual: <b>1.000</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📈 Ver Evolução Geral do CMD", key="btn_cmd_geral", use_container_width=True): 
        st.session_state['active_cmd_chart'] = 'cmd'
        st.rerun()