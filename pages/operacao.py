import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime

from components.filters import get_date_filter_ui
from components.ui_elements import render_download_btn
from database.connection import run_query
from config.constants import STATION_MAP
from utils.helpers import map_stations
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

st.set_page_config(layout="wide") 

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 98%; }
    .pbi-title { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #f3f2f1; border-right: 1px solid #e1dfdd; }
    .stButton > button { background-color: #ffffff; border: 1px solid #cccccc; color: #333333; border-radius: 2px; font-weight: 600; transition: all 0.2s ease; }
    .stButton > button:hover { background-color: #eaeaea; border-color: #666666; color: #000000; }
    .stDownloadButton button { padding: 2px 10px; font-size: 12px; border-radius: 2px; }
    [data-testid="stVerticalBlockBorderWrapper"] { height: 100%; }
    [data-testid="stMetricValue"] { font-size: 26px; font-weight: 700; color: #FFFFFF !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stMetricLabel"] p { font-size: 14px; color: #FFFFFF !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .section-title { font-size: 20px; font-weight: 600; color: #FFFFFF; padding-top: 15px; padding-bottom: 5px; border-bottom: 1px solid #555; margin-bottom: 15px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in', False): st.switch_page("app.py")

col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True): st.switch_page("app.py")

if not st.session_state.get('logged_in') or "operacao" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.error("Acesso Negado.")
    st.stop()

db_loader = st.session_state.get('db_loader')
if not db_loader: st.stop()
engine = db_loader.get_engine()

col_title, col_filter = st.columns([8, 2])
with col_filter:
    with st.container(border=True):
        st.markdown("<div class='pbi-title' style='font-size: 13px; margin-bottom: 0px;'>⚙️ Período</div>", unsafe_allow_html=True)
        filters = get_date_filter_ui("operacao_main")

with col_title:
    st.markdown(f"<h3 style='padding-top: 15px; color: #FFFFFF;'>Painel Integrado de Operação - {filters['mes_nome']}/{filters['ano']}</h3>", unsafe_allow_html=True)

ano_ant = filters['ano'] - 1
mes = filters['mes']
last_day_ant = calendar.monthrange(ano_ant, mes)[1]
dt_start_ant = f"{ano_ant}-{mes:02d}-01"
dt_end_ant = f"{ano_ant}-{mes:02d}-{last_day_ant}"

def calc_delta(atual, anterior):
    try:
        atual = float(atual)
        anterior = float(anterior)
    except:
        return "0% vs Ano Ant."
    if anterior == 0 and atual > 0: return "100% vs Ano Ant."
    elif anterior > 0: return f"{((atual - anterior) / anterior) * 100:.1f}% vs Ano Ant."
    return "0% vs Ano Ant."


# ==========================================
# BLOCO 1: DEMANDA, RECEITA E VIAGENS
# ==========================================
st.markdown("<div class='section-title'>👥 Demanda, Receita e Viagens</div>", unsafe_allow_html=True)

c_kpi1, c_kpi2, c_kpi3 = st.columns(3)

# KPI 1: Passageiros
df_pax = run_query(engine, f"SELECT SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'")
val_pax = df_pax.iloc[0,0] if not df_pax.empty and pd.notnull(df_pax.iloc[0,0]) else 0
val_pax_ant = run_query(engine, f"SELECT SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}'").iloc[0,0]
val_pax_ant = val_pax_ant if pd.notnull(val_pax_ant) else 0
with c_kpi1:
    with st.container(border=True):
        st.metric("Total de Passageiros", f"{val_pax:,.0f}".replace(",", "."), delta=calc_delta(val_pax, val_pax_ant))
        df_dl_pax = run_query(engine, f"SELECT data, SUM(total_passageiros) as passageiros FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_pax, "evolucao_diaria_passageiros")

# KPI 2: Receita
df_rev = run_query(engine, f"SELECT SUM(receita_total) as val FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'")
val_rev = df_rev.iloc[0,0] if not df_rev.empty and pd.notnull(df_rev.iloc[0,0]) else 0
df_rev_ant = run_query(engine, f"SELECT SUM(receita_total) as val FROM public.vw_resumo_bilhetagem WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}'")
val_rev_ant = df_rev_ant.iloc[0,0] if not df_rev_ant.empty and pd.notnull(df_rev_ant.iloc[0,0]) else 0
with c_kpi2:
    with st.container(border=True):
        st.metric("Receita Total", f"R$ {val_rev:,.2f}".replace(".", ","), delta=calc_delta(val_rev, val_rev_ant))
        df_dl_rev = run_query(engine, f"SELECT data, SUM(receita_total) as receita FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_rev, "evolucao_diaria_receita")

# KPI 3: Viagens Realizadas
df_real = run_query(engine, f"SELECT SUM(total_viagens) as qtd FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'")
val_real = df_real.iloc[0,0] if not df_real.empty and pd.notnull(df_real.iloc[0,0]) else 0
df_real_ant = run_query(engine, f"SELECT SUM(total_viagens) as qtd FROM public.vw_resumo_viagens WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}'")
val_real_ant = df_real_ant.iloc[0,0] if not df_real_ant.empty and pd.notnull(df_real_ant.iloc[0,0]) else 0
with c_kpi3:
    with st.container(border=True):
        st.metric("Viagens Realizadas", f"{val_real:,.0f}", delta=calc_delta(val_real, val_real_ant))
        df_dl_real = run_query(engine, f"SELECT data, SUM(total_viagens) as viagens FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_real, "evolucao_diaria_viagens_real")

# Gráficos de Demanda e Receita
col_chart, col_map = st.columns([2, 1])
with col_chart:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>📈 Análise Evolutiva</div>", unsafe_allow_html=True)
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            grafico_selecionado = st.selectbox("Selecione o Indicador:", ["Passageiros", "Receita", "Viagens Realizadas", "Ocultar Gráfico"], label_visibility="collapsed")

        if grafico_selecionado != "Ocultar Gráfico":
            with col_sel2:
                filters_comp = get_date_filter_ui("operacao_comp", show_labels=False)
                nome_comp = f"{filters_comp['mes_nome']}/{filters_comp['ano']}"
            
            nome_atual = f"{filters['mes_nome']}/{filters['ano']}"
            
            if grafico_selecionado == 'Passageiros':
                q_evo = f"SELECT EXTRACT(DAY FROM data) as dia, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1"
                q_comp = f"SELECT EXTRACT(DAY FROM data) as dia, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters_comp['dt_start']}' AND data <= '{filters_comp['dt_end']}' GROUP BY 1"
            elif grafico_selecionado == 'Receita':
                q_evo = f"SELECT EXTRACT(DAY FROM data) as dia, SUM(receita_total) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1"
                q_comp = f"SELECT EXTRACT(DAY FROM data) as dia, SUM(receita_total) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters_comp['dt_start']}' AND data <= '{filters_comp['dt_end']}' GROUP BY 1"
            else:
                q_evo = f"SELECT EXTRACT(DAY FROM data) as dia, SUM(total_viagens) as qtd FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1"
                q_comp = f"SELECT EXTRACT(DAY FROM data) as dia, SUM(total_viagens) as qtd FROM public.vw_resumo_viagens WHERE data >= '{filters_comp['dt_start']}' AND data <= '{filters_comp['dt_end']}' GROUP BY 1"

            df_evo = run_query(engine, q_evo)
            df_comp_evo = run_query(engine, q_comp)
            
            dfs = []
            if not df_evo.empty:
                df_evo['Período'] = f"Atual ({nome_atual})"
                dfs.append(df_evo)
            if not df_comp_evo.empty:
                df_comp_evo['Período'] = f"Comparação ({nome_comp})"
                dfs.append(df_comp_evo)
                
            if dfs:
                df_final = pd.concat(dfs).sort_values(by='dia')
                fig = px.line(df_final, x='dia', y='qtd', color='Período', markers=True)
                fig.update_layout(height=340, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="Volume", legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF")), xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                fig.update_xaxes(dtick=1)
                st.plotly_chart(fig, use_container_width=True)
                render_download_btn(df_final, f"evolucao_{grafico_selecionado.lower().replace(' ', '_')}")

with col_map:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🗺️ Mapa da Linha 1</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True) 

        map_data = pd.DataFrame([{'Estação': 'Eldorado', 'lat': -19.93796, 'lon': -44.02777}, {'Estação': 'Cidade Industrial', 'lat': -19.94444, 'lon': -44.01322}, {'Estação': 'Vila Oeste', 'lat': -19.93811, 'lon': -44.00130}, {'Estação': 'Gameleira', 'lat': -19.92728, 'lon': -43.98730}, {'Estação': 'Calafate', 'lat': -19.92184, 'lon': -43.96960}, {'Estação': 'Carlos Prates', 'lat': -19.91700, 'lon': -43.95556}, {'Estação': 'Lagoinha', 'lat': -19.91251, 'lon': -43.94117}, {'Estação': 'Central', 'lat': -19.91693, 'lon': -43.93288}, {'Estação': 'Santa Efigênia', 'lat': -19.91952, 'lon': -43.92211}, {'Estação': 'Santa Tereza', 'lat': -19.91730, 'lon': -43.91187}, {'Estação': 'Horto', 'lat': -19.90555, 'lon': -43.91310}, {'Estação': 'Santa Inês', 'lat': -19.89472, 'lon': -43.90895}, {'Estação': 'José Cândido', 'lat': -19.88302, 'lon': -43.91330}, {'Estação': 'Minas Shopping', 'lat': -19.87193, 'lon': -43.92511}, {'Estação': 'São Gabriel', 'lat': -19.86256, 'lon': -43.92547}, {'Estação': 'Primeiro de Maio', 'lat': -19.85729, 'lon': -43.93402}, {'Estação': 'Waldomiro Lobo', 'lat': -19.84781, 'lon': -43.93265}, {'Estação': 'Floramar', 'lat': -19.83290, 'lon': -43.94025}, {'Estação': 'Vilarinho', 'lat': -19.81974, 'lon': -43.94783}])

        q_map_vol = f"SELECT id_estacao, SUM(total_passageiros) as volume FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1"
        df_map_vol = run_query(engine, q_map_vol)

        if not df_map_vol.empty:
            df_map_vol['id_estacao'] = pd.to_numeric(df_map_vol['id_estacao'], errors='coerce')
            df_map_vol['Estação'] = df_map_vol['id_estacao'].map(STATION_MAP)
            map_data = pd.merge(map_data, df_map_vol[['Estação', 'volume']], on='Estação', how='left').fillna(0)
        else:
            map_data['volume'] = 0

        max_vol = map_data['volume'].max()
        map_data['marker_size'] = (map_data['volume'] / max_vol * 22) + 6 if max_vol > 0 else 10
        map_data['volume_fmt'] = map_data['volume'].apply(lambda x: f"{int(x):,}").str.replace(',', '.')

        fig_map = px.line_map(map_data, lat="lat", lon="lon", zoom=9.8, height=340, color_discrete_sequence=["#3498db"])
        fig_map.add_trace(go.Scattermap(lat=map_data['lat'], lon=map_data['lon'], mode='markers+text', marker=go.scattermap.Marker(size=map_data['marker_size'], color='#2ecc71', opacity=0.8), text=map_data['Estação'], textposition="top right", customdata=map_data[['Estação', 'volume_fmt']], hovertemplate="<b>%{customdata[0]}</b><br>Fluxo: %{customdata[1]}<extra></extra>"))
        fig_map.update_layout(map_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_map, use_container_width=True)
        render_download_btn(map_data, "dados_mapa_estacoes")

# Volume por Estação e Mix de Pagamento
col_c1, col_c2 = st.columns(2)
with col_c1:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🏆 Volume por Estação</div>", unsafe_allow_html=True)
        df_rank = run_query(engine, f"SELECT id_estacao, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 2 DESC")
        if not df_rank.empty:
            df_rank = map_stations(df_rank, 'id_estacao', STATION_MAP)
            fig_r = px.bar(df_rank, x='qtd', y='id_estacao', orientation='h', color='qtd', color_continuous_scale='Viridis')
            fig_r.update_layout(height=350, margin=dict(t=10, b=0, l=0, r=0), yaxis_title="", xaxis_title="Passageiros", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_r, use_container_width=True)
            render_download_btn(df_rank, "volume_por_estacao")

with col_c2:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>💳 Mix de Pagamento (Receita)</div>", unsafe_allow_html=True)
        df_pgto = run_query(engine, f"SELECT forma_pgto, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        if not df_pgto.empty:
            fig_p = px.pie(df_pgto, values='qtd', names='forma_pgto', hole=0.4)
            fig_p.update_layout(height=350, margin=dict(t=10, b=10, l=0, r=0), legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF")), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_p, use_container_width=True)
            render_download_btn(df_pgto, "mix_de_pagamento")


# ==========================================
# BLOCO 2: OPERAÇÃO E NÍVEL DE SERVIÇO
# ==========================================
st.markdown("<div class='section-title'>🚆 Operação e Nível de Serviço</div>", unsafe_allow_html=True)

c_kpi4, c_espaco1, c_espaco2 = st.columns(3)

# KPI 4: Tempo Médio
q_tempo = f"SELECT SUM(tempo_medio_minutos * total_viagens) / NULLIF(SUM(total_viagens), 0) as tmp FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tipo_real = 6 AND dia_semana in (1,2,3,4,5) AND ((hora >= 6 AND hora < 8) OR (hora >= 17 AND hora < 19))"
df_tempo = run_query(engine, q_tempo)
val_tempo = df_tempo.iloc[0,0] if not df_tempo.empty and pd.notnull(df_tempo.iloc[0,0]) else 0
df_tempo_ant = run_query(engine, q_tempo.replace(filters['dt_start'], dt_start_ant).replace(filters['dt_end'], dt_end_ant))
val_tempo_ant = df_tempo_ant.iloc[0,0] if not df_tempo_ant.empty and pd.notnull(df_tempo_ant.iloc[0,0]) else 0
with c_kpi4:
    with st.container(border=True):
        st.metric("Tempo Médio (Pico)", f"{val_tempo:.1f} min", delta=calc_delta(val_tempo, val_tempo_ant), delta_color="inverse")
        df_dl_tempo = run_query(engine, f"SELECT data, SUM(tempo_medio_minutos * total_viagens) / NULLIF(SUM(total_viagens), 0) as tempo_medio FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tipo_real = 6 AND dia_semana in (1,2,3,4,5) AND ((hora >= 6 AND hora < 8) OR (hora >= 17 AND hora < 19)) GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_tempo, "evolucao_diaria_tempo_pico")

# Gráficos de Oferta x Demanda
CAPACIDADE_TREM = 1000
q_oferta_ida = f"SELECT hora, SUM(total_viagens) as viagens FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND (origem = 'Eldorado' OR origem = 'ELD') AND (destino = 'VRO' OR destino = 'ELD') AND tipo_real = 6 GROUP BY 1"
q_oferta_volta = f"SELECT hora, SUM(total_viagens) as viagens FROM public.vw_resumo_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND (origem = 'Vilarinho' OR origem = 'VRO') AND (destino = 'VRO' OR destino = 'ELD') AND tipo_real = 6 GROUP BY 1"
q_demanda_dir = f"SELECT hora, id_estacao, SUM(total_passageiros) as qtd FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1, 2"

df_ida = run_query(engine, q_oferta_ida)
df_volta = run_query(engine, q_oferta_volta)
df_demanda_dir = run_query(engine, q_demanda_dir)
num_dias = (datetime.strptime(filters['dt_end'], '%Y-%m-%d') - datetime.strptime(filters['dt_start'], '%Y-%m-%d')).days + 1

if not df_demanda_dir.empty:
    df_demanda_dir['id_estacao'] = pd.to_numeric(df_demanda_dir['id_estacao'], errors='coerce').fillna(10)
    df_demanda_dir['peso_ida'] = ((19 - df_demanda_dir['id_estacao']) / 10.0).clip(0, 1)
    df_demanda_dir['peso_volta'] = ((df_demanda_dir['id_estacao'] - 1) / 10.0).clip(0, 1)
    df_demanda_dir['pax_ida'] = df_demanda_dir['qtd'] * df_demanda_dir['peso_ida']
    df_demanda_dir['pax_volta'] = df_demanda_dir['qtd'] * df_demanda_dir['peso_volta']
    df_demanda_agg = df_demanda_dir.groupby('hora')[['pax_ida', 'pax_volta']].sum().reset_index()
else:
    df_demanda_agg = pd.DataFrame(columns=['hora', 'pax_ida', 'pax_volta'])

col_ida, col_volta = st.columns(2)
with col_ida:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>➡️ Oferta x Demanda (Ida)</div>", unsafe_allow_html=True)
        if not df_ida.empty and not df_demanda_agg.empty:
            df_comb_ida = pd.merge(df_ida, df_demanda_agg, on='hora', how='outer').fillna(0)
            # Arredondando viagens por dia PRIMEIRO e só depois multiplicando por 1000
            df_comb_ida['cap_media'] = (df_comb_ida['viagens'] / num_dias).round(0) * CAPACIDADE_TREM
            df_comb_ida['pax_estimado'] = (df_comb_ida['pax_ida'] / num_dias).round(0) 
            fig_ida = go.Figure()
            fig_ida.add_trace(go.Bar(x=df_comb_ida['hora'], y=df_comb_ida['cap_media'], name='Oferta', marker_color='rgba(46, 204, 113, 0.4)'))
            fig_ida.add_trace(go.Scatter(x=df_comb_ida['hora'], y=df_comb_ida['pax_estimado'], name='Demanda', mode='lines+markers', line=dict(color='#e74c3c')))
            fig_ida.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF")), xaxis_title="Hora do Dia", yaxis_title="Passageiros / Lugares", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_ida, use_container_width=True)
            render_download_btn(df_comb_ida, "oferta_demanda_ida")

with col_volta:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⬅️ Oferta x Demanda (Volta)</div>", unsafe_allow_html=True)
        if not df_volta.empty and not df_demanda_agg.empty:
            df_comb_volta = pd.merge(df_volta, df_demanda_agg, on='hora', how='outer').fillna(0)
            # Arredondando viagens por dia PRIMEIRO e só depois multiplicando por 1000
            df_comb_volta['cap_media'] = (df_comb_volta['viagens'] / num_dias).round(0) * CAPACIDADE_TREM
            df_comb_volta['pax_estimado'] = (df_comb_volta['pax_volta'] / num_dias).round(0)
            fig_volta = go.Figure()
            fig_volta.add_trace(go.Bar(x=df_comb_volta['hora'], y=df_comb_volta['cap_media'], name='Oferta', marker_color='rgba(52, 152, 219, 0.4)'))
            fig_volta.add_trace(go.Scatter(x=df_comb_volta['hora'], y=df_comb_volta['pax_estimado'], name='Demanda', mode='lines+markers', line=dict(color='#e67e22')))
            fig_volta.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF")), xaxis_title="Hora do Dia", yaxis_title="", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_volta, use_container_width=True)
            render_download_btn(df_comb_volta, "oferta_demanda_volta")

# Headway Médio e Fluxo Manhã vs Tarde na mesma linha
# Headway Médio (Ocupando a largura total)
with st.container(border=True):
    st.markdown("<div class='pbi-title'>🕒 Headway Médio por Origem</div>", unsafe_allow_html=True)
    q_hw = f"""
    SELECT 
        hora, 
        origem,
        ROUND(AVG(headway)::numeric, 2) as headway 
    FROM public.vw_headway_diario_hora 
    WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND ORIGEM IN ('Eldorado', 'ELD', 'Vilarinho', 'VRO')
    GROUP BY 1, 2
    ORDER BY 1, 2;
    """
    df_hw = run_query(engine, q_hw)
    if not df_hw.empty:
        df_hw['headway_texto'] = df_hw['headway'].apply(lambda x: f"{int(x)}m {int((x * 60) % 60):02d}s")
        
        fig_hw = px.line(df_hw, x='hora', y='headway', color='origem', markers=True, text='headway_texto')
        fig_hw.update_traces(textposition="top center", textfont=dict(color="#FFFFFF"))
        
        fig_hw.update_layout(
            height=350, 
            margin=dict(l=0, r=0, t=10, b=0), 
            legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF"), title=None), 
            xaxis_title="Hora do Dia", 
            yaxis_title="Tempo de Intervalo", 
            xaxis=dict(color="#FFFFFF", tickmode='linear'), 
            yaxis=dict(color="#FFFFFF"), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_hw, use_container_width=True)
        render_download_btn(df_hw, "headway_medio_por_origem")

# Fluxo Manhã vs Tarde (Ocupando a largura total)
with st.container(border=True):
    st.markdown("<div class='pbi-title'>☀️/🌙 Fluxo Manhã vs Tarde</div>", unsafe_allow_html=True)
    q_turno = f"""SELECT id_estacao, CASE WHEN hora < 12 THEN 'Manhã' ELSE 'Tarde' END as turno, SUM(total_passageiros) as qtd
                  FROM public.vw_resumo_bilhetagem WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1, 2 ORDER BY 1, 2"""
    df_turno = run_query(engine, q_turno)
    if not df_turno.empty:
            df_turno = map_stations(df_turno, 'id_estacao', STATION_MAP)
            fig_turno = px.bar(df_turno, x='id_estacao', y='qtd', color='turno', barmode='group')
            fig_turno.update_layout(height=350, margin=dict(t=10, b=0, l=0, r=0), legend=dict(font=dict(color="#FFFFFF")), xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_turno, use_container_width=True)
            render_download_btn(df_turno, "fluxo_turnos")


# ==========================================
# BLOCO 3: FROTA, MANUTENÇÃO E OCORRÊNCIAS
# ==========================================
st.markdown("<div class='section-title'>🛠️ Frota, Manutenção e Ocorrências</div>", unsafe_allow_html=True)

c_kpi5, c_kpi8, c_kpi7, c_kpi6 = st.columns(4)

# KPI 5: KM Percorrida
df_mkbf = run_query(engine, f"SELECT SUM(km_total) as km FROM public.vw_resumo_frota WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}'")
km = df_mkbf.iloc[0]['km'] if not df_mkbf.empty and pd.notnull(df_mkbf.iloc[0]['km']) else 0
df_mkbf_ant = run_query(engine, f"SELECT SUM(km_total) as km FROM public.vw_resumo_frota WHERE mes_ref >= '{dt_start_ant}' AND mes_ref <= '{dt_end_ant}'")
km_ant = df_mkbf_ant.iloc[0]['km'] if not df_mkbf_ant.empty and pd.notnull(df_mkbf_ant.iloc[0]['km']) else 0
with c_kpi5:
    with st.container(border=True):
        st.metric("Total KM Percorrida", f"{km:,.0f} KM".replace(",", "."), delta=calc_delta(km, km_ant))
        df_dl_km = run_query(engine, f"SELECT mes_ref as data, SUM(km_total) as km FROM public.vw_resumo_frota WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_km, "evolucao_diaria_km")

# KPI 8: Indisponibilidade
df_indisp_total = run_query(engine, f"SELECT SUM(horas_indisp) as horas FROM public.vw_resumo_frota WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}'")
val_indisp = df_indisp_total.iloc[0,0] if not df_indisp_total.empty and pd.notnull(df_indisp_total.iloc[0,0]) else 0
df_indisp_ant = run_query(engine, f"SELECT SUM(horas_indisp) as horas FROM public.vw_resumo_frota WHERE mes_ref >= '{dt_start_ant}' AND mes_ref <= '{dt_end_ant}'")
val_indisp_ant = df_indisp_ant.iloc[0,0] if not df_indisp_ant.empty and pd.notnull(df_indisp_ant.iloc[0,0]) else 0
with c_kpi8:
    with st.container(border=True):
        st.metric("Indisponibilidade(H)", f"{val_indisp:,.0f} h", delta=calc_delta(val_indisp, val_indisp_ant), delta_color="inverse")
        df_dl_indisp = run_query(engine, f"SELECT mes_ref as data, SUM(horas_indisp) as horas_indisponiveis FROM public.vw_resumo_frota WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_indisp, "evolucao_diaria_indisponibilidade")

# KPI 7: Manutenções
df_manut = run_query(engine, f"SELECT SUM(total_manutencoes) as qtd FROM public.vw_resumo_manutencao WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'")
val_manut = df_manut.iloc[0,0] if not df_manut.empty and pd.notnull(df_manut.iloc[0,0]) else 0
df_manut_ant = run_query(engine, f"SELECT SUM(total_manutencoes) as qtd FROM public.vw_resumo_manutencao WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}'")
val_manut_ant = df_manut_ant.iloc[0,0] if not df_manut_ant.empty and pd.notnull(df_manut_ant.iloc[0,0]) else 0
with c_kpi7:
    with st.container(border=True):
        st.metric("Registros Manutenção", f"{val_manut:,.0f}", delta=calc_delta(val_manut, val_manut_ant), delta_color="inverse")
        df_dl_manut = run_query(engine, f"SELECT data, SUM(total_manutencoes) as manutencoes FROM public.vw_resumo_manutencao WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_manut, "evolucao_diaria_manutencoes")

# KPI 6: Ocorrências
df_ocorr = run_query(engine, f"SELECT SUM(total_ocorrencias) as qtd FROM public.vw_resumo_ocorrencias WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'")
val_ocorr = df_ocorr.iloc[0,0] if not df_ocorr.empty and pd.notnull(df_ocorr.iloc[0,0]) else 0
df_ocorr_ant = run_query(engine, f"SELECT SUM(total_ocorrencias) as qtd FROM public.vw_resumo_ocorrencias WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}'")
val_ocorr_ant = df_ocorr_ant.iloc[0,0] if not df_ocorr_ant.empty and pd.notnull(df_ocorr_ant.iloc[0,0]) else 0
with c_kpi6:
    with st.container(border=True):
        st.metric("Total de Ocorrências", f"{val_ocorr:,.0f}", delta=calc_delta(val_ocorr, val_ocorr_ant), delta_color="inverse")
        df_dl_ocorr = run_query(engine, f"SELECT data, SUM(total_ocorrencias) as ocorrencias FROM public.vw_resumo_ocorrencias WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 1")
        render_download_btn(df_dl_ocorr, "evolucao_diaria_ocorrencias")

# Gráficos de Frota e Ocorrências
col_f1, col_f2, col_f3 = st.columns(3)

df_frota_km = run_query(engine, f"SELECT id_trem, SUM(km_total) as prod_km FROM public.vw_resumo_frota WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1")

with col_f1:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🔝 Operação (KM)</div>", unsafe_allow_html=True)
        if not df_frota_km.empty:
            df_top_op = df_frota_km.sort_values('prod_km', ascending=False).head(10)
            df_top_op['Trem'] = "T" + df_top_op['id_trem'].astype(str)
            fig_top = px.bar(df_top_op, x='Trem', y='prod_km', color_discrete_sequence=['#2ecc71'])
            fig_top.update_layout(height=320, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="Quilometragem", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_top, use_container_width=True)
            render_download_btn(df_top_op, "operacao_km")
        
with col_f2:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>📉 Indisponível (Horas)</div>", unsafe_allow_html=True)
        df_indisp = run_query(engine, f"SELECT id_trem, SUM(horas_indisp) as horas FROM public.vw_resumo_frota WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        if not df_indisp.empty:
            df_indisp['Trem'] = "T" + df_indisp['id_trem'].astype(str)
            fig_ind = px.bar(df_indisp, x='Trem', y='horas', color_discrete_sequence=['#e74c3c'])
            fig_ind.update_layout(height=320, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="Horas Paradas", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_ind, use_container_width=True)
            render_download_btn(df_indisp, "indisponivel_horas")

with col_f3:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>⚠️ Top Ocorrências</div>", unsafe_allow_html=True)
        df_inc = run_query(engine, f"SELECT subtipo, SUM(total_ocorrencias) as qtd FROM public.vw_resumo_ocorrencias WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND subtipo NOT LIKE 'RECLAMAÇÃO' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        if not df_inc.empty:
            fig_inc = px.bar(df_inc, x='subtipo', y='qtd', orientation='v')
            fig_inc.update_layout(height=320, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="Tipo de Ocorrência", yaxis_title="Qtd", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_inc, use_container_width=True)
            render_download_btn(df_inc, "top_ocorrencias")

col_m1, col_m2 = st.columns(2)
with col_m1:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🔧 Prev. por Trem</div>", unsafe_allow_html=True)
        df_prev = run_query(engine, f"SELECT id_tue, SUM(total_manutencoes) as qtd FROM public.vw_resumo_manutencao WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tipo_manutencao = 'PREVENTIVA' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        if not df_prev.empty:
            df_prev['Trem'] = "T" + df_prev['id_tue'].astype(str)
            fig_prev = px.bar(df_prev, x='Trem', y='qtd', color_discrete_sequence=['#3498db'])
            fig_prev.update_layout(height=320, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="Qtd Preventivas", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_prev, use_container_width=True)
            render_download_btn(df_prev, "preventivas_por_trem")

with col_m2:
    with st.container(border=True):
        st.markdown("<div class='pbi-title'>🚨 Corr. por Trem</div>", unsafe_allow_html=True)
        df_corr = run_query(engine, f"SELECT id_tue, SUM(total_manutencoes) as qtd FROM public.vw_resumo_manutencao WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tipo_manutencao = 'CORRETIVA' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        if not df_corr.empty:
            df_corr['Trem'] = "T" + df_corr['id_tue'].astype(str)
            fig_corr = px.bar(df_corr, x='Trem', y='qtd', color_discrete_sequence=['#9b59b6'])
            fig_corr.update_layout(height=320, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="Qtd Corretivas", xaxis=dict(color="#FFFFFF"), yaxis=dict(color="#FFFFFF"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_corr, use_container_width=True)
            render_download_btn(df_corr, "corretivas_por_trem")

st.markdown("<br>", unsafe_allow_html=True)