import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.filters import get_date_filter_ui
from components.page_styles import apply_ultra_compact_css
from components.ui_elements import apply_modern_layout, render_chart_footer
from config.constants import STATION_MAP
from database.connection import run_query
from utils.analytics import calc_delta, get_scalar
from utils.helpers import map_stations
from utils.page import require_access, setup_page

setup_page(layout="wide")

apply_ultra_compact_css()

require_access(page_keys=["numeros"])

engine = st.session_state.get('db_loader').get_engine()

# ==========================================
# LÓGICA DO MODAL (VISÃO AMPLIADA)
# ==========================================
if st.session_state.get('show_expanded_num'):
    with st.container(border=True):
        col_t, col_b = st.columns([8, 2])
        with col_t:
            st.markdown(
                f"<h3 style='color:white; margin-top:5px;'>🔍 {st.session_state.get('expanded_num_title', 'Visão Ampliada')}</h3>",
                unsafe_allow_html=True,
            )
        with col_b:
            if st.button("❌ Fechar Ampliação", use_container_width=True, key="btn_fechar_exp_num"):
                st.session_state['show_expanded_num'] = False
                st.rerun()
        
        fig_large = go.Figure(st.session_state['expanded_num'])
        fig_large.update_layout(height=600)
        st.plotly_chart(fig_large, use_container_width=True)
    st.stop()

# --- TOPO SUPER COMPACTO ---
c_bt, c_tit, c_fil = st.columns([1, 7, 2])
with c_bt:
    if st.button("⬅️ Início", use_container_width=True): st.switch_page("app.py")
with c_fil:
    filters = get_date_filter_ui("numeros", show_labels=False)
with c_tit:
    st.markdown("<h4 style='color: #FFFFFF; margin-top:0px;'>🏛️ Metrô RMBH em Números (Ano Consolidado)</h4>", unsafe_allow_html=True)

ano_atual = filters['ano']
ano_start, ano_end = f"{ano_atual}-01-01", f"{ano_atual}-12-31"
ano_ant = ano_atual - 1
ano_ant_start, ano_ant_end = f"{ano_ant}-01-01", f"{ano_ant}-12-31"

# --- CÁLCULO DOS KPIs ---
v_med_mes = get_scalar(engine, f"WITH mensal AS (SELECT TO_CHAR(data, 'YYYY-MM') as mes, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{ano_start}' AND '{ano_end}' GROUP BY 1) SELECT AVG(qtd) FROM mensal")
v_med_mes_a = get_scalar(engine, f"WITH mensal AS (SELECT TO_CHAR(data, 'YYYY-MM') as mes, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{ano_ant_start}' AND '{ano_ant_end}' GROUP BY 1) SELECT AVG(qtd) FROM mensal")
dt1_txt, dt1_css = calc_delta(v_med_mes, v_med_mes_a)

v_corr = get_scalar(engine, f"SELECT SUM(total_manutencoes) FROM public.vw_resumo_manutencao WHERE data BETWEEN '{ano_start}' AND '{ano_end}' AND tipo_manutencao = 'CORRETIVA'")
v_corr_a = get_scalar(engine, f"SELECT SUM(total_manutencoes) FROM public.vw_resumo_manutencao WHERE data BETWEEN '{ano_ant_start}' AND '{ano_ant_end}' AND tipo_manutencao = 'CORRETIVA'")
dt2_txt, dt2_css = calc_delta(v_corr, v_corr_a, inv=True)

v_prev = get_scalar(engine, f"SELECT SUM(total_manutencoes) FROM public.vw_resumo_manutencao WHERE data BETWEEN '{ano_start}' AND '{ano_end}' AND tipo_manutencao = 'PREVENTIVA'")
v_prev_a = get_scalar(engine, f"SELECT SUM(total_manutencoes) FROM public.vw_resumo_manutencao WHERE data BETWEEN '{ano_ant_start}' AND '{ano_ant_end}' AND tipo_manutencao = 'PREVENTIVA'")
dt3_txt, dt3_css = calc_delta(v_prev, v_prev_a)

v_canc = get_scalar(engine, f"SELECT SUM(total_viagens) FROM public.vw_resumo_viagens WHERE data BETWEEN '{ano_start}' AND '{ano_end}' AND tipo_real in (9,10)")
v_canc_a = get_scalar(engine, f"SELECT SUM(total_viagens) FROM public.vw_resumo_viagens WHERE data BETWEEN '{ano_ant_start}' AND '{ano_ant_end}' AND tipo_real in (9,10)")
dt4_txt, dt4_css = calc_delta(v_canc, v_canc_a, inv=True)

# Renderiza KPIs
st.markdown(f"""
<div class="kpi-wrapper">
    <div class="kpi-card"><div class="kpi-title">Média Passageiros/Mês</div><div class="kpi-val">{v_med_mes:,.0f}</div><div class="kpi-delta {dt1_css}">{dt1_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">Manutenções Corretivas</div><div class="kpi-val">{v_corr:,.0f}</div><div class="kpi-delta {dt2_css}">{dt2_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">Manutenções Preventivas</div><div class="kpi-val">{v_prev:,.0f}</div><div class="kpi-delta {dt3_css}">{dt3_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">Viagens Canceladas</div><div class="kpi-val">{v_canc:,.0f}</div><div class="kpi-delta {dt4_css}">{dt4_txt}</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# FILEIRA 1: PERFIL E ESTAÇÕES
# ==========================================
c_mn1, c_mn2 = st.columns(2)

with c_mn1:
    with st.container(border=True):
        st.markdown(f"<div class='pbi-title'>💳 Perfil de Bilhetagem ({ano_atual})</div>", unsafe_allow_html=True)
        df_perfil = run_query(engine, f"SELECT tipo_bilhetagem, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{ano_start}' AND '{ano_end}' GROUP BY 1 ORDER BY 2 DESC")
        if not df_perfil.empty: 
            fig_perf = px.pie(df_perfil, values='qtd', names='tipo_bilhetagem', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_perf.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(apply_modern_layout(fig_perf, h=250), use_container_width=True)
            render_chart_footer(df_perfil, "perfil_bilhetagem", fig_perf, "Perfil de Bilhetagem (Participação)", "exp_n_perf", state_prefix="expanded_num")

with c_mn2:
    with st.container(border=True):
        st.markdown(f"<div class='pbi-title'>🚉 Comparativo: Passageiros Mês/Estação ({ano_ant} vs {ano_atual})</div>", unsafe_allow_html=True)
        q_est_media_comp = f"SELECT id_estacao, EXTRACT(YEAR FROM data)::varchar as ano_ref, ROUND(COALESCE(SUM(total_passageiros)::float / NULLIF(COUNT(DISTINCT EXTRACT(MONTH FROM data)), 0), 0)) as media_mensal FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{ano_ant_start}' AND '{ano_end}' GROUP BY 1, 2 ORDER BY 1, 2"
        df_est_med_comp = run_query(engine, q_est_media_comp)
        if not df_est_med_comp.empty:
            df_est_med_comp = map_stations(df_est_med_comp, 'id_estacao', STATION_MAP)
            fig_comp = px.bar(df_est_med_comp, x='id_estacao', y='media_mensal', color='ano_ref', barmode='group', color_discrete_sequence=['#FA709A', '#00F2FE'])
            st.plotly_chart(apply_modern_layout(fig_comp, h=250, show_legend=True, show_x=True), use_container_width=True)
            render_chart_footer(df_est_med_comp, "comp_estacao", fig_comp, "Média Mensal de Passageiros por Estação", "exp_n_comp", state_prefix="expanded_num")

# ==========================================
# FILEIRA 2: VOLUME POR TIPO E GRUPO
# ==========================================
c_cons1, c_cons2 = st.columns(2)

with c_cons1:
    with st.container(border=True):
        st.markdown(f"<div class='pbi-title'>🎟️ Volume por Tipo de Bilhete nas Estações ({ano_atual})</div>", unsafe_allow_html=True)
        q_tipo_est = f"SELECT ap.nome, ap.id, tipo_bilhetagem, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem ab INNER JOIN public.arq7_paradas ap ON ab.id_estacao = ap.id WHERE tipo_bilhetagem IS NOT NULL AND data BETWEEN '{ano_start}' AND '{ano_end}' GROUP BY ap.nome, ap.id, tipo_bilhetagem HAVING SUM(total_passageiros) > 1 ORDER BY ap.id, qtd DESC"
        df_tipo_est = run_query(engine, q_tipo_est)
        if not df_tipo_est.empty:
            fig_tipo_est = px.bar(df_tipo_est, x='nome', y='qtd', color='tipo_bilhetagem', color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(apply_modern_layout(fig_tipo_est, h=250, show_legend=True, show_x=True), use_container_width=True)
            render_chart_footer(df_tipo_est, "tipo_bilhete_estacao", fig_tipo_est, "Volume de Validações por Tipo de Bilhete", "exp_n_tipo_est", state_prefix="expanded_num")

with c_cons2:
    with st.container(border=True):
        st.markdown(f"<div class='pbi-title'>🎟️ Volume por Grupo de Bilhete nas Estações ({ano_atual})</div>", unsafe_allow_html=True)
        q_grupo_est = f"SELECT ap.nome, ap.id, grupo_bilhetagem, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem ab INNER JOIN public.arq7_paradas ap ON ab.id_estacao = ap.id WHERE grupo_bilhetagem IS NOT NULL AND data BETWEEN '{ano_start}' AND '{ano_end}' GROUP BY ap.nome, ap.id, grupo_bilhetagem HAVING SUM(total_passageiros) > 1 ORDER BY ap.id, qtd DESC"
        df_grupo_est = run_query(engine, q_grupo_est)
        if not df_grupo_est.empty:
            fig_grupo_est = px.bar(df_grupo_est, x='nome', y='qtd', color='grupo_bilhetagem', color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(apply_modern_layout(fig_grupo_est, h=250, show_legend=True, show_x=True), use_container_width=True)
            render_chart_footer(df_grupo_est, "grupo_bilhete_estacao", fig_grupo_est, "Volume de Validações por Grupo de Bilhete", "exp_n_grp_est", state_prefix="expanded_num")

st.markdown("<h4 style='color: #FFFFFF; margin-top:15px;'>📈 Evolução Histórica (Série Temporal)</h4>", unsafe_allow_html=True)

# ==========================================
# FILEIRA 3: SÉRIES HISTÓRICAS (1/2)
# ==========================================
ch1, ch2, ch3 = st.columns(3)

with ch1:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>👥 Passageiros Totais (Mês)</div>", unsafe_allow_html=True)
        df_pass_mes = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM') as mes, SUM(total_passageiros) as total FROM public.vw_resumo_bilhetagem GROUP BY 1 ORDER BY 1")
        if not df_pass_mes.empty:
            fig_pass_mes = px.line(df_pass_mes, x='mes', y='total')
            fig_pass_mes.update_traces(line_shape='spline', line=dict(color='#00F2FE', width=3), fill='tozeroy', fillcolor='rgba(0, 242, 254, 0.2)')
            st.plotly_chart(apply_modern_layout(fig_pass_mes, h=180, show_x=True), use_container_width=True)
            render_chart_footer(df_pass_mes, "hist_passageiros", fig_pass_mes, "Evolução Histórica de Passageiros", "exp_n_pax", state_prefix="expanded_num")

with ch2:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🎟️ Evolução por Tipo de Bilhete</div>", unsafe_allow_html=True)
        df_tipo_mes = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM') as mes, tipo_bilhetagem, SUM(total_passageiros) as total FROM public.vw_resumo_bilhetagem WHERE tipo_bilhetagem IS NOT NULL GROUP BY 1, 2 ORDER BY 1, 2")
        if not df_tipo_mes.empty:
            fig_tipo_mes = px.line(df_tipo_mes, x='mes', y='total', color='tipo_bilhetagem')
            fig_tipo_mes.update_traces(line_shape='spline', line_width=2)
            st.plotly_chart(apply_modern_layout(fig_tipo_mes, h=180, show_legend=True, show_x=True), use_container_width=True)
            render_chart_footer(df_tipo_mes, "hist_tipo_bilhete", fig_tipo_mes, "Evolução Temporal: Tipo de Bilhete", "exp_n_tpm", state_prefix="expanded_num")

with ch3:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🚉 Viagens Realizadas (Mês)</div>", unsafe_allow_html=True)
        df_viagens_mes = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM') as mes, SUM(total_viagens) as total FROM public.vw_resumo_viagens WHERE tipo_real NOT IN (9,10) GROUP BY 1 ORDER BY 1")
        if not df_viagens_mes.empty:
            fig_viagens_mes = px.line(df_viagens_mes, x='mes', y='total')
            fig_viagens_mes.update_traces(line_shape='spline', line=dict(color='#43E97B', width=3), fill='tozeroy', fillcolor='rgba(67, 233, 123, 0.2)')
            st.plotly_chart(apply_modern_layout(fig_viagens_mes, h=180, show_x=True), use_container_width=True)
            render_chart_footer(df_viagens_mes, "hist_viagens", fig_viagens_mes, "Evolução Histórica de Viagens", "exp_n_vreal", state_prefix="expanded_num")

# ==========================================
# FILEIRA 4: SÉRIES HISTÓRICAS (2/2)
# ==========================================
ch4, ch5, ch6 = st.columns(3)

with ch4:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⚠️ Viagens Canceladas (Mês)</div>", unsafe_allow_html=True)
        df_falhas_mes = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM') as mes, SUM(total_viagens) as total FROM public.vw_resumo_viagens WHERE tipo_real IN (9,10) GROUP BY 1 ORDER BY 1")
        if not df_falhas_mes.empty:
            fig_falhas_mes = px.line(df_falhas_mes, x='mes', y='total')
            fig_falhas_mes.update_traces(line_shape='spline', line=dict(color='#FA709A', width=3), fill='tozeroy', fillcolor='rgba(250, 112, 154, 0.2)')
            st.plotly_chart(apply_modern_layout(fig_falhas_mes, h=180, show_x=True), use_container_width=True)
            render_chart_footer(df_falhas_mes, "hist_canceladas", fig_falhas_mes, "Evolução Histórica de Cancelamentos", "exp_n_vcanc", state_prefix="expanded_num")

with ch5:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🛤️ KM Rodado (Mês)</div>", unsafe_allow_html=True)
        try:
            df_km_mes = run_query(engine, "SELECT mes, SUM(total_km) as total_km FROM public.vw_resumo_km_percorrida GROUP BY 1 ORDER BY 1")
            if not df_km_mes.empty:
                fig_km_mes = px.line(df_km_mes, x='mes', y='total_km')
                fig_km_mes.update_traces(line_shape='spline', line=dict(color='#FEE140', width=3), fill='tozeroy', fillcolor='rgba(254, 225, 64, 0.2)')
                st.plotly_chart(apply_modern_layout(fig_km_mes, h=180, show_x=True), use_container_width=True)
                render_chart_footer(df_km_mes, "hist_km", fig_km_mes, "Evolução Histórica de Quilometragem", "exp_n_km", state_prefix="expanded_num")
        except Exception:
            st.info("⚠️ View não encontrada.")

with ch6:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🚑 Acidentes (Mês)</div>", unsafe_allow_html=True)
        try:
            df_acid_mes = run_query(engine, "SELECT TO_CHAR(data, 'YYYY-MM') as mes, SUM(total_ocorrencias) as total FROM public.vw_resumo_ocorrencias where tipo = 'SEGURANÇA' GROUP BY 1 ORDER BY 1")
            if not df_acid_mes.empty:
                fig_acid_mes = px.bar(df_acid_mes, x='mes', y='total', color_discrete_sequence=['#e74c3c'])
                st.plotly_chart(apply_modern_layout(fig_acid_mes, h=180, show_x=True), use_container_width=True)
                render_chart_footer(df_acid_mes, "hist_acidentes", fig_acid_mes, "Evolução Histórica de Acidentes", "exp_n_aci", state_prefix="expanded_num")
        except Exception:
            st.info("⚠️ View não encontrada.")

# ==========================================
# FILEIRA 5: HEADWAY LARGURA TOTAL
# ==========================================
with st.container(border=True):
    st.markdown("<div class='pbi-title'>⏱️ Headway Médio nos Horários de Pico (Mensal)</div>", unsafe_allow_html=True)
    try:
        df_headway_mes = run_query(engine, "SELECT mes, ROUND(AVG(headway_medio_minutos), 1) as media_headway FROM public.vw_headway_mes_hora WHERE hora IN (6, 7, 8, 17, 18, 19) GROUP BY 1 ORDER BY 1")
        if not df_headway_mes.empty:
            fig_headway_mes = px.line(df_headway_mes, x='mes', y='media_headway')
            fig_headway_mes.update_traces(line_shape='spline', line=dict(color='#9b59b6', width=3), marker=dict(size=8, color='#FFF'))
            st.plotly_chart(apply_modern_layout(fig_headway_mes, h=200, show_x=True), use_container_width=True)
            render_chart_footer(df_headway_mes, "hist_headway", fig_headway_mes, "Headway Médio Consolidado", "exp_n_hwm", state_prefix="expanded_num")
    except Exception:
        st.info("⚠️ View de Headway não encontrada.")
