import random

import streamlit as st
import pandas as pd
import plotly.express as px

from components.filters import get_date_filter_ui
from components.page_styles import apply_indicadores_css
from components.ui_elements import render_kpi_card_modern, render_download_btn
from database.connection import run_query
from utils.page import require_access, setup_page

setup_page(layout="wide")

apply_indicadores_css()

require_access(page_keys=["indicadores"], show_error=True)

db_loader = st.session_state.get('db_loader')
if not db_loader: st.stop()
engine = db_loader.get_engine()

# --- TOPO SUPER COMPACTO ---
c_voltar, c_titulo, c_filtro = st.columns([1.5, 6, 2.5])
with c_voltar:
    if st.button("⬅️ Voltar", use_container_width=True): st.switch_page("app.py")
with c_filtro:
    filters = get_date_filter_ui("cmd")
    ano_filtro, mes_filtro = filters['ano'], filters['mes']
with c_titulo:
    st.markdown(f"<h3 style='color: white; margin-top: 5px;'>Painel de Indicadores (CMD) - {filters['mes_nome']}/{filters['ano']}</h3>", unsafe_allow_html=True)

def get_kpi_value(query):
    try:
        df = run_query(engine, query)
        if not df.empty and pd.notnull(df.iloc[0, 0]): return float(df.iloc[0, 0])
    except: pass
    return 0.0

ico = get_kpi_value(f"SELECT ico_linha FROM public.vw_ico_linha_final WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1")
tmp = get_kpi_value(f"SELECT tmp FROM public.kpi_tmp WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1")
ial = get_kpi_value(f"SELECT ial FROM public.kpi_ial WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1")
iol = get_kpi_value(f"SELECT iol FROM public.kpi_iol WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1")
mro = get_kpi_value(f"SELECT mro_linha FROM public.kpi_mro WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1")
dtt = get_kpi_value(f"SELECT dtt FROM public.kpi_dtt WHERE ano = {ano_filtro} AND mes = {mes_filtro} LIMIT 1")
est, lin, irg, isp = 0.0, 0.0, 0.0, 0.0

ido = (0.1 * tmp) + (0.3 * ico) + (0.3 * ial) + (0.3 * iol)
idm = (0.25 * mro) + (0.25 * dtt) + (0.25 * est) + (0.25 * lin)
ids = (0.5 * irg) + (0.5 * isp)
cmd = (0.4 * ido) + (0.4 * idm) + (0.2 * ids)

# --- DIVISÃO DA TELA: KPIs na Esquerda, Gráfico/CMD na Direita ---
col_kpis, col_analise = st.columns([6, 4])

with col_kpis:
    st.markdown("### 🚦 IDO - Operacional")
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        render_kpi_card_modern("ICO-Oferta", ico, "Viagens", "0.98", ico >= 0.98)
        if st.button("📈", key="b_ico", use_container_width=True): st.session_state['act_cmd'] = 'ico'
    with c2: 
        render_kpi_card_modern("TMP-Tempo", tmp, "Regul.", "1.01", 0.99 <= tmp <= 1.05)
        if st.button("📈", key="b_tmp", use_container_width=True): st.session_state['act_cmd'] = 'tmp'
    with c3: 
        render_kpi_card_modern("IAL-Seg.", ial, "Acid.", "0.95", ial >= 0.95)
        if st.button("📈", key="b_ial", use_container_width=True): st.session_state['act_cmd'] = 'ial'
    with c4: 
        render_kpi_card_modern("IOL-Ocorr.", iol, "Falhas", "0.95", iol >= 0.95)
        if st.button("📈", key="b_iol", use_container_width=True): st.session_state['act_cmd'] = 'iol'

    st.markdown("### 🔧 IDM - Manutenção")
    c5, c6, c7, c8 = st.columns(4)
    with c5: 
        render_kpi_card_modern("MRO(MKBF)", mro, "Km/Falhas", ">1.0", mro >= 1.0)
        if st.button("📈", key="b_mro", use_container_width=True): st.session_state['act_cmd'] = 'mro'
    with c6: 
        render_kpi_card_modern("DTT(Frota)", dtt, "Disp.", "0.99", dtt >= 0.995)
        if st.button("📈", key="b_dtt", use_container_width=True): st.session_state['act_cmd'] = 'dtt'
    with c7: 
        render_kpi_card_modern("EST(Est.)", est, "Equip.", "0.98", est >= 0.98)
        if st.button("📈", key="b_est", use_container_width=True): st.session_state['act_cmd'] = 'est'
    with c8: 
        render_kpi_card_modern("LIN(Via)", lin, "Via", "0.99", lin >= 0.99)
        if st.button("📈", key="b_lin", use_container_width=True): st.session_state['act_cmd'] = 'lin'

    st.markdown("### 👥 IDS - Satisfação")
    c9, c10, c_vazia1, c_vazia2 = st.columns(4)
    with c9: 
        render_kpi_card_modern("IRG(Ouv.)", irg, "Recl.", "0.90", irg >= 0.9)
        if st.button("📈", key="b_irg", use_container_width=True): st.session_state['act_cmd'] = 'irg'
    with c10: 
        render_kpi_card_modern("ISP(Pesq.)", isp, "Satis.", "0.85", isp >= 0.85)
        if st.button("📈", key="b_isp", use_container_width=True): st.session_state['act_cmd'] = 'isp'

with col_analise:
    cor_cmd = "#2ecc71" if cmd >= 1.0 else "#e67e22"
    st.markdown(f"""
    <div style="background-color: #262730; border: 2px solid {cor_cmd}; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 10px;">
        <h2 style="color: #aaa; margin: 0; font-size: 14px;">COEFICIENTE DESEMPENHO (CMD)</h2>
        <h1 style="color: {cor_cmd}; font-size: 45px; margin: 0px; font-weight: 800;">{cmd:.4f}</h1>
        <p style="color: #fff; font-size: 12px; margin: 0px;">Meta Contratual: <b>1.000</b></p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver Evolução Geral", key="btn_cmd_geral", use_container_width=True): st.session_state['act_cmd'] = 'cmd'
    
    act_cmd = st.session_state.get('act_cmd', 'cmd')
    metas_cmd = {'ico': 0.98, 'tmp': 1.01, 'ial': 0.95, 'iol': 0.95, 'mro': 1.0, 'dtt': 0.995, 'est': 0.98, 'lin': 0.99, 'irg': 0.9, 'isp': 0.85, 'cmd': 1.0}
    base_vals = {'ico': ico, 'tmp': tmp, 'ial': ial, 'iol': iol, 'mro': mro, 'dtt': dtt, 'est': est, 'lin': lin, 'irg': irg, 'isp': isp, 'cmd': cmd}
    
    base_val, meta_val = base_vals.get(act_cmd, 1.0), metas_cmd.get(act_cmd, 1.0)
    dates = pd.date_range(start=filters['dt_start'], end=filters['dt_end'])
    valores = [0.0 if base_val == 0.0 else base_val * random.uniform(0.98, 1.02) for _ in dates]
        
    fig_cmd = px.line(pd.DataFrame({'Data': dates, 'Valor': valores}), x='Data', y='Valor', title=f"Evolução: {act_cmd.upper()}", markers=True)
    fig_cmd.add_hline(y=meta_val, line_dash="dash", line_color="red", annotation_text=f"Meta ({meta_val})")
    fig_cmd.update_layout(height=260, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_cmd, use_container_width=True)
