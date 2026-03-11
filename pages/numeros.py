import streamlit as st
import pandas as pd
import plotly.express as px
from components.filters import get_date_filter_ui
from components.ui_elements import render_download_btn
from database.connection import run_query
from config.constants import STATION_MAP
from utils.helpers import map_stations
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")

col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True):
        st.switch_page("app.py")

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in') or "numeros" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.error("Acesso Negado.")
    st.stop()

db_loader = st.session_state.get('db_loader')
if not db_loader: st.stop()
engine = db_loader.get_engine()

filters = get_date_filter_ui("numeros")
st.markdown("### 🏛️ Painel Metrô da RMBH em Números")
st.markdown("*Visão consolidada de transparência e indicadores estratégicos com comparativo ao Ano Anterior (YoY).*")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

ano_atual = filters['ano']
ano_start = f"{ano_atual}-01-01"
ano_end = f"{ano_atual}-12-31"

ano_ant = ano_atual - 1
ano_ant_start = f"{ano_ant}-01-01"
ano_ant_end = f"{ano_ant}-12-31"

def calc_delta(atual, anterior):
    if anterior == 0 and atual > 0: return "100%"
    elif anterior == 0 and atual == 0: return "0%"
    else: return f"{(((atual - anterior) / anterior) * 100):.1f}% comparado ao Ano Anterior"

q_media_mes = f"WITH mensal AS (SELECT DATE_TRUNC('month', data_hora) as mes, COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{ano_start} 00:00:00' AND data_hora <= '{ano_end} 23:59:59' GROUP BY 1) SELECT AVG(qtd) FROM mensal"
df_med_mes = run_query(engine, q_media_mes)
val_med_mes = df_med_mes.iloc[0,0] if not df_med_mes.empty and df_med_mes.iloc[0,0] else 0

q_media_mes_ant = f"WITH mensal AS (SELECT DATE_TRUNC('month', data_hora) as mes, COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{ano_ant_start} 00:00:00' AND data_hora <= '{ano_ant_end} 23:59:59' GROUP BY 1) SELECT AVG(qtd) FROM mensal"
df_med_mes_ant = run_query(engine, q_media_mes_ant)
val_med_mes_ant = df_med_mes_ant.iloc[0,0] if not df_med_mes_ant.empty and df_med_mes_ant.iloc[0,0] else 0
col_kpi1.metric("Média Passageiros/Mês", f"{val_med_mes:,.0f}".replace(",", "."), delta=calc_delta(val_med_mes, val_med_mes_ant))

q_manut_corr = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_start}' AND data_abertura <= '{ano_end}' AND tipo_manutencao = 'CORRETIVA'"
val_corr_ano = run_query(engine, q_manut_corr).iloc[0,0] if not run_query(engine, q_manut_corr).empty else 0
q_manut_corr_ant = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_ant_start}' AND data_abertura <= '{ano_ant_end}' AND tipo_manutencao = 'CORRETIVA'"
val_corr_ano_ant = run_query(engine, q_manut_corr_ant).iloc[0,0] if not run_query(engine, q_manut_corr_ant).empty else 0
col_kpi2.metric("Manut. Corretivas (Ano)", f"{val_corr_ano:,.0f}".replace(",", "."), delta=calc_delta(val_corr_ano, val_corr_ano_ant), delta_color="inverse")

q_manut_prev = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_start}' AND data_abertura <= '{ano_end}' AND tipo_manutencao = 'PREVENTIVA'"
val_prev_ano = run_query(engine, q_manut_prev).iloc[0,0] if not run_query(engine, q_manut_prev).empty else 0
q_manut_prev_ant = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_ant_start}' AND data_abertura <= '{ano_ant_end}' AND tipo_manutencao = 'PREVENTIVA'"
val_prev_ano_ant = run_query(engine, q_manut_prev_ant).iloc[0,0] if not run_query(engine, q_manut_prev_ant).empty else 0
col_kpi3.metric("Manut. Preventivas (Ano)", f"{val_prev_ano:,.0f}".replace(",", "."), delta=calc_delta(val_prev_ano, val_prev_ano_ant))

q_canc = f"SELECT COUNT(*) FROM public.arq3_viagens WHERE data >= '{ano_start}' AND data <= '{ano_end}' AND tipo_real in (9,10)"
val_canc = run_query(engine, q_canc).iloc[0,0] if not run_query(engine, q_canc).empty else 0
q_canc_ant = f"SELECT COUNT(*) FROM public.arq3_viagens WHERE data >= '{ano_ant_start}' AND data <= '{ano_ant_end}' AND tipo_real in (9,10)"
val_canc_ant = run_query(engine, q_canc_ant).iloc[0,0] if not run_query(engine, q_canc_ant).empty else 0
col_kpi4.metric("Viagens Canceladas (Ano)", f"{val_canc:,.0f}".replace(",", "."), delta=calc_delta(val_canc, val_canc_ant), delta_color="inverse")

st.divider()

c_mn1, c_mn2 = st.columns(2)
with c_mn1:
    st.markdown(f"##### 💳 Perfil de Bilhetagem ({ano_atual})")
    df_perfil = run_query(engine, f"SELECT tipo_bilhetagem, COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{ano_start} 00:00:00' AND data_hora <= '{ano_end} 23:59:59' GROUP BY 1 ORDER BY 2 DESC")
    if not df_perfil.empty: 
        st.plotly_chart(px.pie(df_perfil, values='qtd', names='tipo_bilhetagem', hole=0.5), use_container_width=True)
        render_download_btn(df_perfil, "perfil_bilhetagem")

with c_mn2:
    st.markdown(f"##### 🚉 Comparativo: Passageiros Mês/Estação ({ano_ant} vs {ano_atual})")
    q_est_media_comp = f"SELECT id_estacao, EXTRACT(YEAR FROM data_hora)::varchar as ano_ref, ROUND(COALESCE(COUNT(*)::float / NULLIF(COUNT(DISTINCT EXTRACT(MONTH FROM data_hora)), 0), 0)) as media_mensal FROM public.arq2_bilhetagem WHERE data_hora >= '{ano_ant_start} 00:00:00' AND data_hora <= '{ano_end} 23:59:59' GROUP BY 1, 2 ORDER BY 1, 2"
    df_est_med_comp = run_query(engine, q_est_media_comp)
    if not df_est_med_comp.empty:
        # AQUI ESTÁ A CORREÇÃO (ADICIONADO O STATION_MAP)
        df_est_med_comp = map_stations(df_est_med_comp, 'id_estacao', STATION_MAP)
        fig_comp = px.bar(df_est_med_comp, x='id_estacao', y='media_mensal', color='ano_ref', barmode='group', labels={'id_estacao': 'Estação', 'media_mensal': 'Média Mensal', 'ano_ref': 'Ano'})
        fig_comp.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
        st.plotly_chart(fig_comp, use_container_width=True)
        render_download_btn(df_est_med_comp, "comparativo_estacoes")

st.divider()

st.markdown(f"##### 🎟️ Consolidado de Bilhetagem por Estação e Tipo de Bilhete ({ano_atual})")
q_tipo_est = f"SELECT ap.nome, ap.id, tipo_bilhetagem, COUNT(*) as qtd FROM public.arq2_bilhetagem ab INNER JOIN public.arq7_paradas ap ON ab.id_estacao = ap.id WHERE tipo_bilhetagem IS NOT NULL AND data_hora BETWEEN '{ano_start} 00:00:00' AND '{ano_end} 23:59:59' GROUP BY ap.nome, ap.id, tipo_bilhetagem HAVING COUNT(*) > 1 ORDER BY ap.id, qtd DESC"
df_tipo_est = run_query(engine, q_tipo_est)
if not df_tipo_est.empty:
    fig_tipo_est = px.bar(df_tipo_est, x='nome', y='qtd', color='tipo_bilhetagem', barmode='stack', labels={'nome': '', 'qtd': 'Quantidade de Validações', 'tipo_bilhetagem': 'Tipo de Bilhete'})
    fig_tipo_est.update_xaxes(tickangle=-45)
    fig_tipo_est.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
    st.plotly_chart(fig_tipo_est, use_container_width=True)
    render_download_btn(df_tipo_est, "consolidado_tipo_bilhete")

st.divider()

st.markdown(f"##### 🎟️ Volume de Bilhetagem por Estação e Grupo de Bilhete ({ano_atual})")
q_grupo_est = f"SELECT ap.nome, ap.id, grupo_bilhetagem, COUNT(*) as qtd FROM public.arq2_bilhetagem ab INNER JOIN public.arq7_paradas ap ON ab.id_estacao = ap.id WHERE grupo_bilhetagem IS NOT NULL AND data_hora BETWEEN '{ano_start} 00:00:00' AND '{ano_end} 23:59:59' GROUP BY ap.nome, ap.id, grupo_bilhetagem HAVING COUNT(*) > 1 ORDER BY ap.id, qtd DESC"
df_grupo_est = run_query(engine, q_grupo_est)
if not df_grupo_est.empty:
    fig_grupo_est = px.bar(df_grupo_est, x='nome', y='qtd', color='grupo_bilhetagem', barmode='stack', labels={'nome': '', 'qtd': 'Quantidade de Validações', 'grupo_bilhetagem': 'Grupo de Bilhete'})
    fig_grupo_est.update_xaxes(tickangle=-45)
    fig_grupo_est.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
    st.plotly_chart(fig_grupo_est, use_container_width=True)
    render_download_btn(df_grupo_est, "consolidado_grupo_bilhete")