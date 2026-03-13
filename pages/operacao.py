import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime
from functools import reduce

from components.filters import get_date_filter_ui
from components.ui_elements import render_download_btn
from database.connection import run_query
from config.constants import STATION_MAP
from utils.helpers import map_stations
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

st.set_page_config(layout="wide") 

# --- CSS ULTRA-COMPACTO E MODERNO ---
st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem !important; max-width: 100%; }
    header { visibility: hidden; height: 0px; }
    
    /* Layout dos KPIs em Grade HTML */
    .kpi-wrapper { display: flex; gap: 8px; justify-content: space-between; margin-bottom: 12px; margin-top: 5px; }
    .kpi-card { flex: 1; background: rgba(20, 20, 25, 0.6); border: 1px solid #333; border-radius: 8px; padding: 10px 5px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); backdrop-filter: blur(5px); transition: transform 0.2s; }
    .kpi-card:hover { transform: translateY(-2px); border-color: #555; }
    .kpi-title { font-family: 'Segoe UI', sans-serif; font-size: 11px; color: #aaa; font-weight: 600; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.5px; }
    .kpi-val { font-family: 'Segoe UI', sans-serif; font-size: 20px; color: #fff; font-weight: 800; margin: 2px 0; }
    .kpi-delta { font-size: 11px; font-weight: 700; }
    .d-pos { color: #2ecc71; }
    .d-neg { color: #e74c3c; }
    .d-neu { color: #f1c40f; }
    
    .pbi-title { font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; margin-bottom: 0px; color: #FFFFFF !important; }
    .stDataFrame { margin-top: 5px; }
    
    /* Ajuste fino dos botões de Download e Expansão para ficarem lado a lado */
    .stButton > button, .stDownloadButton > button { padding: 2px 10px !important; font-size: 12px !important; border-radius: 4px; }
    hr { margin: 8px 0px; opacity: 0.2; }
    </style>
""", unsafe_allow_html=True)

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in', False): st.switch_page("app.py")
if "operacao" not in st.session_state['permissions'].get(st.session_state['current_role'], []): st.stop()

engine = st.session_state.get('db_loader').get_engine()

# ==========================================
# LÓGICA DO MODAL (VISÃO AMPLIADA)
# ==========================================
if st.session_state.get('show_expanded_chart'):
    with st.container(border=True):
        col_t, col_b = st.columns([8, 2])
        with col_t:
            st.markdown(f"<h3 style='color:white; margin-top:5px;'>🔍 {st.session_state.get('expanded_title', 'Visão Ampliada')}</h3>", unsafe_allow_html=True)
        with col_b:
            if st.button("❌ Fechar Ampliação", use_container_width=True, key="btn_fechar_exp"):
                st.session_state['show_expanded_chart'] = False
                st.rerun()
        
        fig_large = go.Figure(st.session_state['expanded_chart'])
        fig_large.update_layout(height=600)
        st.plotly_chart(fig_large, use_container_width=True)
    
    st.stop() 
def render_chart_footer(df, file_name, fig, title, key):
    c1, c2 = st.columns([8, 2])
    with c1:
        render_download_btn(df, file_name)
    with c2:
        if st.button("⛶", key=key, help="Ampliar Gráfico", use_container_width=True):
            st.session_state['show_expanded_chart'] = True
            st.session_state['expanded_chart'] = fig
            st.session_state['expanded_title'] = title
            st.rerun()

# --- TOPO SUPER COMPACTO ---
c_bt, c_tit, c_fil = st.columns([1, 7, 2])
with c_bt:
    if st.button("⬅️ Início", use_container_width=True): st.switch_page("app.py")
with c_fil:
    filters = get_date_filter_ui("operacao_main", show_labels=False)
with c_tit:
    st.markdown(f"<h4 style='color: #FFFFFF; margin-top:0px;'>Painel de Operação - {filters['mes_nome']}/{filters['ano']}</h4>", unsafe_allow_html=True)

dt_s, dt_e = filters['dt_start'], filters['dt_end']
ano_ant, mes = filters['ano'] - 1, filters['mes']
dt_s_ant = f"{ano_ant}-{mes:02d}-01"
dt_e_ant = f"{ano_ant}-{mes:02d}-{calendar.monthrange(ano_ant, mes)[1]}"

# --- LÓGICA DE CÁLCULO PARA OS KPIs ---
def get_val(q):
    df = run_query(engine, q)
    return float(df.iloc[0,0]) if not df.empty and pd.notnull(df.iloc[0,0]) else 0.0

def calc_d(at, an, inv=False):
    if an == 0 and at > 0: val = 100.0
    elif an == 0 and at == 0: val = 0.0
    else: val = ((at - an) / an) * 100
    
    if val > 0: return f"+{val:.1f}%", "d-neg" if inv else "d-pos"
    elif val < 0: return f"{val:.1f}%", "d-pos" if inv else "d-neg"
    return "0.0%", "d-neu"

v_pax = get_val(f"SELECT SUM(total_passageiros) FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s}' AND '{dt_e}'")
v_pax_a = get_val(f"SELECT SUM(total_passageiros) FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
dp_txt, dp_css = calc_d(v_pax, v_pax_a)

v_rev = get_val(f"SELECT SUM(receita_total) FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s}' AND '{dt_e}'")
v_rev_a = get_val(f"SELECT SUM(receita_total) FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
dr_txt, dr_css = calc_d(v_rev, v_rev_a)

v_via = get_val(f"SELECT SUM(total_viagens) FROM public.vw_resumo_viagens WHERE data BETWEEN '{dt_s}' AND '{dt_e}'")
v_via_a = get_val(f"SELECT SUM(total_viagens) FROM public.vw_resumo_viagens WHERE data BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
dv_txt, dv_css = calc_d(v_via, v_via_a)

q_tmp = f"SELECT SUM(tempo_medio_minutos * total_viagens)/NULLIF(SUM(total_viagens),0) FROM public.vw_resumo_viagens WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND tipo_real=6 AND ((hora>=6 AND hora<8) OR (hora>=17 AND hora<19))"
v_tmp = get_val(q_tmp)
v_tmp_a = get_val(q_tmp.replace(dt_s, dt_s_ant).replace(dt_e, dt_e_ant))
dtm_txt, dtm_css = calc_d(v_tmp, v_tmp_a, inv=True)

v_km = get_val(f"SELECT SUM(km_total) FROM public.vw_resumo_frota WHERE mes_ref BETWEEN '{dt_s}' AND '{dt_e}'")
v_km_a = get_val(f"SELECT SUM(km_total) FROM public.vw_resumo_frota WHERE mes_ref BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
dk_txt, dk_css = calc_d(v_km, v_km_a)

v_ind = get_val(f"SELECT SUM(horas_indisp) FROM public.vw_resumo_frota WHERE mes_ref BETWEEN '{dt_s}' AND '{dt_e}'")
v_ind_a = get_val(f"SELECT SUM(horas_indisp) FROM public.vw_resumo_frota WHERE mes_ref BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
di_txt, di_css = calc_d(v_ind, v_ind_a, inv=True)

v_man = get_val(f"SELECT SUM(total_manutencoes) FROM public.vw_resumo_manutencao WHERE data BETWEEN '{dt_s}' AND '{dt_e}'")
v_man_a = get_val(f"SELECT SUM(total_manutencoes) FROM public.vw_resumo_manutencao WHERE data BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
dm_txt, dm_css = calc_d(v_man, v_man_a, inv=True)

v_oco = get_val(f"SELECT SUM(total_ocorrencias) FROM public.vw_resumo_ocorrencias WHERE data BETWEEN '{dt_s}' AND '{dt_e}'")
v_oco_a = get_val(f"SELECT SUM(total_ocorrencias) FROM public.vw_resumo_ocorrencias WHERE data BETWEEN '{dt_s_ant}' AND '{dt_e_ant}'")
do_txt, do_css = calc_d(v_oco, v_oco_a, inv=True)

# Renderiza os KPIs
st.markdown(f"""
<div class="kpi-wrapper">
    <div class="kpi-card"><div class="kpi-title">👥 Passageiros</div><div class="kpi-val">{v_pax/1000000:.3f}M</div><div class="kpi-delta {dp_css}">{dp_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">💰 Receita (R$)</div><div class="kpi-val">{v_rev/1000000:.3f}M</div><div class="kpi-delta {dr_css}">{dr_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">🚆 Viagens Realiz.</div><div class="kpi-val">{v_via:,.0f}</div><div class="kpi-delta {dv_css}">{dv_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">⏱️ TMP (Pico)</div><div class="kpi-val">{v_tmp:.1f}m</div><div class="kpi-delta {dtm_css}">{dtm_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">🛤️ KM Rodado</div><div class="kpi-val">{v_km/1000:.1f}k</div><div class="kpi-delta {dk_css}">{dk_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">📉 Indisp. (H)</div><div class="kpi-val">{v_ind:,.0f}h</div><div class="kpi-delta {di_css}">{di_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">🔧 Manutenções</div><div class="kpi-val">{v_man:,.0f}</div><div class="kpi-delta {dm_css}">{dm_txt}</div></div>
    <div class="kpi-card"><div class="kpi-title">⚠️ Ocorrências</div><div class="kpi-val">{v_oco:,.0f}</div><div class="kpi-delta {do_css}">{do_txt}</div></div>
</div>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO GLOBAL PLOTLY MODERNIZADA ---
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

# ==========================================
# FILEIRA 1: Evolução, Mapa e Raio-X
# ==========================================
c_evo, c_rx = st.columns([3.5, 4.5])

with c_evo:
    with st.container(border=True):
        cs1, cs2, cs3 = st.columns([1.5, 1.5, 1.5])
        with cs1: st.markdown("<div class='pbi-title'>📈 Análise Evolutiva</div>", unsafe_allow_html=True)
        with cs2: ind_sel = st.selectbox("", ["Passageiros", "Receita", "Viagens"], label_visibility="collapsed")
        with cs3: 
            filters_comp = get_date_filter_ui("operacao_comp", show_labels=False)
            nome_comp = f"{filters_comp['mes_nome']}/{filters_comp['ano']}"
        
        nome_atual = f"{filters['mes_nome']}/{filters['ano']}"
        col_db = {'Passageiros': 'total_passageiros', 'Receita': 'receita_total', 'Viagens': 'total_viagens'}
        tb_db = 'vw_resumo_viagens' if ind_sel == 'Viagens' else 'vw_resumo_bilhetagem'
        
        q_evo = f"SELECT EXTRACT(DAY FROM data) as dia, SUM({col_db[ind_sel]}) as qtd FROM public.{tb_db} WHERE data BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1"
        q_comp = f"SELECT EXTRACT(DAY FROM data) as dia, SUM({col_db[ind_sel]}) as qtd FROM public.{tb_db} WHERE data BETWEEN '{filters_comp['dt_start']}' AND '{filters_comp['dt_end']}' GROUP BY 1"
        
        df_evo = run_query(engine, q_evo)
        df_comp_evo = run_query(engine, q_comp)
        
        dfs = []
        if not df_evo.empty:
            df_evo['Período'] = f"Atual ({nome_atual})"
            dfs.append(df_evo)
        if not df_comp_evo.empty:
            df_comp_evo['Período'] = f"Comp. ({nome_comp})"
            dfs.append(df_comp_evo)
            
        if dfs:
            df_final = pd.concat(dfs).sort_values(by='dia')
            fig_evo = px.line(df_final, x='dia', y='qtd', color='Período', color_discrete_sequence=['#00F2FE', '#FA709A'])
            fig_evo.update_traces(line_shape='spline', marker=dict(size=6, color='#FFF'))
            st.plotly_chart(apply_modern_layout(fig_evo, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(df_final, f"evolucao_{ind_sel.lower()}", fig_evo, f"Análise Evolutiva: {ind_sel}", "exp_evo")

with c_rx:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🚈 Raio-X Integrado da Frota (Trens)</div>", unsafe_allow_html=True)
        df_fkm = run_query(engine, f"SELECT id_trem::text as \"Trem\", SUM(km_total) as km FROM public.vw_resumo_frota WHERE mes_ref BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1")
        df_fin = run_query(engine, f"SELECT id_trem::text as \"Trem\", SUM(horas_indisp) as hr FROM public.vw_resumo_frota WHERE mes_ref BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1")
        df_fpr = run_query(engine, f"SELECT id_tue::text as \"Trem\", SUM(total_manutencoes) as prev FROM public.vw_resumo_manutencao WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND tipo_manutencao='PREVENTIVA' GROUP BY 1")
        df_fco = run_query(engine, f"SELECT id_tue::text as \"Trem\", SUM(total_manutencoes) as corr FROM public.vw_resumo_manutencao WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND tipo_manutencao='CORRETIVA' GROUP BY 1")
        
        dfs = [df for df in [df_fkm, df_fin, df_fpr, df_fco] if not df.empty]
        if dfs:
            df_frota = reduce(lambda l, r: pd.merge(l, r, on='Trem', how='outer'), dfs).fillna(0)
            df_frota['Trem'] = "T" + df_frota['Trem']
            st.dataframe(
                df_frota,
                column_config={
                    "Trem": st.column_config.TextColumn("Trem"),
                    "km": st.column_config.ProgressColumn("KM Total", format="%d", min_value=0, max_value=df_frota['km'].max()),
                    "hr": st.column_config.ProgressColumn("Indisp (h)", format="%d", min_value=0, max_value=df_frota['hr'].max()),
                    "prev": st.column_config.ProgressColumn("Preventivas", format="%d", min_value=0, max_value=df_frota['prev'].max()),
                    "corr": st.column_config.ProgressColumn("Corretivas", format="%d", min_value=0, max_value=df_frota['corr'].max()),
                }, hide_index=True, use_container_width=True, height=185
            )
            render_download_btn(df_frota, "raio_x_frota")

# ==========================================
# FILEIRA 2: Estações, Oferta/Demanda e Turnos
# ==========================================
c_ve, c_odi, c_odv, c_tu = st.columns([2.5, 2.5, 2.5, 2.5])

with c_ve:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🏆 Volume por Estação</div>", unsafe_allow_html=True)
        df_rank = run_query(engine, f"SELECT id_estacao, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1 ORDER BY 2 ")
        if not df_rank.empty:
            df_rank = map_stations(df_rank, 'id_estacao', STATION_MAP)
            fig_r = px.bar(df_rank, x='qtd', y='id_estacao', orientation='h', color='qtd', color_continuous_scale='Tealgrn')
            fig_r.update_layout(coloraxis_showscale=False)
            st.plotly_chart(apply_modern_layout(fig_r), use_container_width=True)
            render_chart_footer(df_rank, "volume_por_estacao", fig_r, "Volume de Validações por Estação", "exp_rank")

# Lógica compartilhada Demanda x Oferta
CAP = 1000
num_dias = (datetime.strptime(dt_e, '%Y-%m-%d') - datetime.strptime(dt_s, '%Y-%m-%d')).days + 1
df_dem = run_query(engine, f"SELECT hora, id_estacao, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1, 2")
if not df_dem.empty:
    df_dem['id_estacao'] = pd.to_numeric(df_dem['id_estacao'], errors='coerce').fillna(10)
    df_dem['peso_ida'] = ((19 - df_dem['id_estacao']) / 10.0).clip(0, 1)
    df_dem['peso_volta'] = ((df_dem['id_estacao'] - 1) / 10.0).clip(0, 1)
    df_dem['pax_ida'], df_dem['pax_volta'] = df_dem['qtd'] * df_dem['peso_ida'], df_dem['qtd'] * df_dem['peso_volta']
    df_dem_agg = df_dem.groupby('hora')[['pax_ida', 'pax_volta']].sum().reset_index()
else: df_dem_agg = pd.DataFrame(columns=['hora', 'pax_ida', 'pax_volta'])

with c_odi:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>➡️ Oferta x Demanda (Ida)</div>", unsafe_allow_html=True)
        df_ida = run_query(engine, f"SELECT hora, SUM(total_viagens) as viagens FROM public.vw_resumo_viagens WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND origem IN ('Eldorado','ELD') AND destino IN ('VRO','ELD') AND tipo_real=6 GROUP BY 1")
        if not df_ida.empty and not df_dem_agg.empty:
            df_c_ida = pd.merge(df_ida, df_dem_agg, on='hora', how='outer').fillna(0).sort_values('hora')
            fig_i = go.Figure()
            fig_i.add_trace(go.Bar(x=df_c_ida['hora'], y=(df_c_ida['viagens']/num_dias).round(0)*CAP, name='Oferta', marker_color='rgba(46, 204, 113, 0.4)', marker_line_color='#2ecc71', marker_line_width=1))
            fig_i.add_trace(go.Scatter(x=df_c_ida['hora'], y=(df_c_ida['pax_ida']/num_dias).round(0), name='Demanda', line=dict(color='#FA709A', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(250, 112, 154, 0.1)'))
            st.plotly_chart(apply_modern_layout(fig_i, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(df_c_ida, "oferta_demanda_ida", fig_i, "Oferta x Demanda (Ida)", "exp_ida")

with c_odv:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⬅️ Oferta x Demanda (Volta)</div>", unsafe_allow_html=True)
        df_vol = run_query(engine, f"SELECT hora, SUM(total_viagens) as viagens FROM public.vw_resumo_viagens WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND origem IN ('Vilarinho','VRO') AND destino IN ('VRO','ELD') AND tipo_real=6 GROUP BY 1")
        if not df_vol.empty and not df_dem_agg.empty:
            df_c_vol = pd.merge(df_vol, df_dem_agg, on='hora', how='outer').fillna(0).sort_values('hora')
            fig_v = go.Figure()
            fig_v.add_trace(go.Bar(x=df_c_vol['hora'], y=(df_c_vol['viagens']/num_dias).round(0)*CAP, name='Oferta', marker_color='rgba(52, 152, 219, 0.4)', marker_line_color='#3498db', marker_line_width=1))
            fig_v.add_trace(go.Scatter(x=df_c_vol['hora'], y=(df_c_vol['pax_volta']/num_dias).round(0), name='Demanda', line=dict(color='#FEE140', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(254, 225, 64, 0.1)'))
            st.plotly_chart(apply_modern_layout(fig_v, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(df_c_vol, "oferta_demanda_volta", fig_v, "Oferta x Demanda (Volta)", "exp_vol")

with c_tu:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>☀️/🌙 Fluxo Turnos</div>", unsafe_allow_html=True)
        df_turno = run_query(engine, f"SELECT id_estacao, CASE WHEN hora < 12 THEN 'Manhã' ELSE 'Tarde' END as turno, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1, 2 ORDER BY 1, 2")
        if not df_turno.empty:
            df_turno = map_stations(df_turno, 'id_estacao', STATION_MAP)
            fig_t = px.bar(df_turno, x='id_estacao', y='qtd', color='turno', barmode='group', color_discrete_sequence=['#00F2FE', '#FA709A'])
            st.plotly_chart(apply_modern_layout(fig_t, show_legend=True), use_container_width=True)
            render_chart_footer(df_turno, "fluxo_turnos", fig_t, "Fluxo Manhã vs Tarde", "exp_tur")

# ==========================================
# FILEIRA 3: Headway, Ocorrências e Mix Pgto
# ==========================================
c_hw, c_oc, c_mx = st.columns([4, 3.5, 2.5])

with c_hw:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🕒 Headway Médio por Origem (Eldorado vs Vilarinho)</div>", unsafe_allow_html=True)
        df_hw = run_query(engine, f"SELECT hora, origem, ROUND(AVG(headway)::numeric, 2) as hw FROM public.vw_headway_diario_hora WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND ORIGEM IN ('Eldorado', 'ELD', 'Vilarinho', 'VRO') GROUP BY 1, 2 ORDER BY 1, 2")
        if not df_hw.empty:
            df_hw['origem'] = df_hw['origem'].replace({'Eldorado':'ELD', 'Vilarinho':'VRO'})
            fig_h = px.line(df_hw, x='hora', y='hw', color='origem')
            fig_h.update_traces(line_shape='spline', line_width=3, marker=dict(size=6))
            st.plotly_chart(apply_modern_layout(fig_h, show_x=True, show_legend=True), use_container_width=True)
            render_chart_footer(df_hw, "headway_medio", fig_h, "Headway Médio por Origem", "exp_hw")

with c_oc:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⚠️ Top Ocorrências Operacionais</div>", unsafe_allow_html=True)
        df_inc = run_query(engine, f"SELECT subtipo, SUM(total_ocorrencias) as qtd FROM public.vw_resumo_ocorrencias WHERE data BETWEEN '{dt_s}' AND '{dt_e}' AND subtipo NOT LIKE 'RECLAMAÇÃO' GROUP BY 1 ORDER BY 2 ASC LIMIT 6")
        if not df_inc.empty:
            fig_in = px.bar(df_inc, x='qtd', y='subtipo', orientation='h', color='qtd', color_continuous_scale='Reds')
            fig_in.update_layout(coloraxis_showscale=False)
            st.plotly_chart(apply_modern_layout(fig_in), use_container_width=True)
            render_chart_footer(df_inc, "top_ocorrencias", fig_in, "Ocorrências Operacionais Registradas", "exp_oco")

with c_mx:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>💳 Mix Receita</div>", unsafe_allow_html=True)
        df_pgto = run_query(engine, f"SELECT tipo_bilhetagem as forma_pgto, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data BETWEEN '{dt_s}' AND '{dt_e}' GROUP BY 1 ORDER BY 2 DESC LIMIT 15")
        if not df_pgto.empty:
            fig_p = px.pie(df_pgto, values='qtd', names='forma_pgto', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_p.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(apply_modern_layout(fig_p, show_legend=True), use_container_width=True)
            render_chart_footer(df_pgto, "mix_de_pagamento", fig_p, "Mix de Pagamento (Proporção da Receita)", "exp_mix")