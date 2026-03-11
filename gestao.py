import streamlit as st
import pandas as pd
import os
import plotly.io as pio
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime, date, timedelta
import base64
import random
import numpy as np

st.set_page_config(
    page_title="GESTÃO DE DADOS OPERACIONAIS - METRO BH",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚇"
)

@st.cache_data
def convert_df_to_csv(df):
    # Converte o DataFrame para CSV no padrão brasileiro (separador ponto-e-vírgula e vírgula decimal)
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

def render_download_btn(df, filename_prefix):
    """Gera um botão de download padronizado dentro de um expander para não poluir a UI"""
    if df is not None and not df.empty:
        with st.expander("📥 Donwload"):
            csv = convert_df_to_csv(df)
            data_atual = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label="Clique para Baixar",
                data=csv,
                file_name=f"{filename_prefix}_{data_atual}.csv",
                mime='text/csv',
                use_container_width=True
            )

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""

img_base64 = get_base64_of_bin_file('/Users/Documents/GitHub/etl_metro_bh_v2/fundo_metro.jpeg')

pio.templates.default = "plotly_dark"
load_dotenv()

STATION_MAP = {
   0:'Novo Eldorado', 1: 'Eldorado', 2: 'Cidade Industrial', 3: 'Vila Oeste', 4: 'Gameleira', 
    5: 'Calafate', 6: 'Carlos Prates', 7: 'Lagoinha', 8: 'Central', 
    9: 'Santa Efigênia', 10: 'Santa Tereza', 11: 'Horto', 12: 'Santa Inês', 
    13: 'José Cândido', 14: 'Minas Shopping', 15: 'São Gabriel', 
    16: 'Primeiro de Maio', 17: 'Waldomiro Lobo', 18: 'Floramar', 19: 'Vilarinho'
}

STATION_NAME_TO_ID = {v: k for k, v in STATION_MAP.items()}

DEFAULT_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5434'),
    'dbname': os.getenv('DB_NAME', 'metro_bh'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASS', 'Seinfra2025'), 
    'schema': os.getenv('DB_SCHEMA', 'migracao')
}

# --- SUBSTITUA O SEU BLOCO st.markdown("<style>...") POR ESTE ---
st.markdown(f"""
<style>
    /* CONFIGURAÇÃO DA IMAGEM DE FUNDO LOCAL */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
        url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;            
        background-position: center;      
        background-repeat: no-repeat;      
        background-attachment: fixed;      
    }}

    /* Seus estilos originais continuam aqui embaixo... */
    .main .block-container {{ padding-top: 1rem; padding-bottom: 2rem; }}
    .kpi-card-container {{
        background-color: #262730;
        border: 1px solid #464b5d;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }}
    .kpi-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
    .kpi-title {{ font-size: 14px; color: #9ca3af; font-weight: 600; text-transform: uppercase; margin: 0; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: #ffffff; margin: 5px 0; }}
    .kpi-subtitle {{ font-size: 12px; color: #9ca3af; }}
    .kpi-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; }}
    .badge-success {{ background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }}
    .badge-danger {{ background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid #e74c3c; }}
    .status-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        padding-top: 20px; 
    }}
    .status-indicator {{ 
        padding: 8px 15px; 
        border-radius: 20px; 
        font-weight: bold; 
        text-align: center; 
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .status-on {{ background-color: #2ecc71; color: #1e1e1e; border: 1px solid #27ae60; }}
    .status-off {{ background-color: #e74c3c; color: white; border: 1px solid #c0392b; }}
</style>
""", unsafe_allow_html=True)

def map_stations(df, col_name):
    if df is not None and not df.empty and col_name in df.columns:
        df[col_name] = df[col_name].map(STATION_MAP).fillna(df[col_name])
    return df

def detect_delimiter(file):
    try:
        sample = file.read(2048).decode('utf-8', errors='ignore')
        file.seek(0)
        delimiters = [';', ',', '\t', '|']
        counts = {d: sample.count(d) for d in delimiters}
        return max(counts, key=counts.get) if max(counts.values()) > 0 else ';'
    except: return ';'

def convert_data_types(df, table_name):
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_object_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].str.strip()
            df_copy[col].replace(['', 'nan', 'NaN', 'None', 'NULL'], None, inplace=True)
    return df_copy

def render_kpi_card_modern(title, value, subtitle, target, is_good, footer=""):
    badge_class = "badge-success" if is_good else "badge-danger"
    badge_icon = "✔" if is_good else "✗"
    badge_text = "Na Meta" if is_good else "Abaixo"
    val_fmt = f"{value:.3f}" if isinstance(value, float) else str(value)

    html = f"""
    <div class="kpi-card-container">
        <div class="kpi-header">
            <p class="kpi-title">{title}</p>
            <span class="kpi-badge {badge_class}">{badge_icon} {badge_text}</span>
        </div>
        <div class="kpi-value">{val_fmt}</div>
        <div class="kpi-subtitle">{subtitle}</div>
        <div class="kpi-footer" style="font-size: 11px; margin-top:5px; color:#666;">
            Meta: <b>{target}</b><br>{footer}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

TABLES_CONFIG = {
    'tab01': ['mesref', 'tipo_dia', 'fx_hora', 'viagens', 'tempo_percurso', 'disp_frota'],
    'tab02': ['data_completa', 'hora_completa', 'entrada_id', 'cod_estacao', 'bloqueio_id',
                         'dbd_num', 'grupo_bilhete', 'forma_pagamento', 'tipo_bilhete', 'user_id', 'valor'],
    'tab02_temp2': ['data_hora_corrigida', 'estacao', 'bloqueio', 'grupo_bilhete', 'forma_pagamento',
                    'tipo_de_bilhete'],
    'tab02_marco': ['entrada_id', 'hora_completa', 'cod_estacao', 'bloqueio_id', 'dbd_num', 'grupo_bilhete',
                    'forma_pagamento', 'tipo_bilhete', 'user_id', 'data_completa', 'valor'],
    'tab03_old': ['ordem', 'dia', 'viagem', 'origemprevista', 'origemreal', 'destinoprevisto', 'destinoreal',
              'horainicioreal', 'horainicioprevista', 'horafimprevista', 'horafimreal', 'trem', 'status',
              'stat_desc', 'picovale', 'incidenteleve', 'incidentegrave', 'viagem_interrompida', 'id_ocorr',
              'id_interrupcao', 'id_linha', 'lotacao'],
    'tab03': ['id','ordem', 'dia', 'viagem', 'origemreal', 'destinoreal', 'horainicioreal', 'horafimreal', 'trem', 'status', 'incidenteleve', 'incidentegrave',
              'stat_desc',  'id_ocorr', 'id_interrupcao', 'id_linha', 'horainicioprevista', 'horafimprevista',  'lotacao'],
    'arq3_dadosviagens': ['ordem', 'dia', 'viagem', 'origem', 'destino', 'hora_inicio', 'hora_fim', 'veiculo',
                          'tipo_real', 'incidente_leve', 'incidente_grave', 'viagem_interrompida'],
    'tab04': ['id', 'tipo', 'subtipo', 'data', 'horaini', 'horafim', 'motivo', 'local', 'env_usuario',
              'env_veiculo', 'bo'],
    'tab05': ['nome_linha', 'status_linha', 'fim_operacao', 'cod_estacao', 'grupo_bilhete', 'ini_operacao',
              'num_estacao', 'max_valor'],
    'tab06': ['ordem', 'emissao', 'data', 'hora', 'tipo', 'trem', 'cdv', 'estacao', 'via', 'viagem', 'causa',
              'excluir', 'motivo_da_exclusao'],
    'tab07': ['linha', 'cod_estacao', 'estacao', 'bloqueio', 'c_empresa_validador', 'dbd_num', 'dbd_data',
              'valid_ex_emp', 'valid_ex_num', 'valid_ex_data'],
    'tab08': ['equipamento', 'descricao', 'modelo', 'serie', 'data_inicio_operacao', 'data_fim_operacao'],
    'tab09': ['tue', 'data', 'hora_inicio', 'hora_fim', 'origem', 'destino', 'descricao', 'status', 'km'],
    'tab14': ['composicao', 'data_abertura', 'data_fechamento', 'tipo_manutencao', 'tipo_desc', 'tipo_falha'],
    'arq15_tueoperacoes': ['tue', 'data', 'hora_inicio', 'hora_fim', 'origem', 'destino', 'descricao'],
    'tab12': ['referencia', 'num_instalacao', 'tipo', 'total_kwh', 'local', 'endereco'],
    'tab13': ['cdv', 'sent_normal_circ', 'comprimento', 'cod_velo_max', 'plat_est', 'temp_teor_perc',
              'temp_med_perc', 'tempoocup'],
    'arq1_resumoviagensfrota ': ['mesref', 'dia', 'hora', 'viagens', 'tempo_percurso', 'disp_frota'],
    'arq02_bilhetagem': ['entrada_id', 'hora_completa', 'cod_estacao', 'bloqueio', 'dbd_num',
                         'grupo_bilhetagem', 'forma_pagamento', 'tipo_de_bilhete', 'user_id', 'data_completa', 'valor'],
    'arq04_ocorrencias': ['id', 'tipo', 'subtipo', 'data', 'horaini', 'horafim', 'motivo', 'local',
                          'env_usuario', 'env_veiculo', 'bo'],
    'arq4_1_reclamacoesusuarios': ['tipo', 'dt', 'motivo'],
    'arq4_2_manutencao': ['tipo', 'data', 'subtipo', 'hora', 'local'],
    'arq4_3_seguranca': ['tipo', 'data', 'hora_inicio', 'hora_fim', 'local'],
    'arq5_1_falhasmanutencao': ['data_abertura', 'composicao', 'data_fechamento', 'tipo_manutencao', 'tipo_de_falha'],
    'arq05_8_nece_disp': ['ordem', 'data', 'hora', 'necessidade', 'disponibilidade'],
    'arq07_linhas': ['num_estacao', 'nome_linha', 'ini_operacao', 'status_linha', 'fim_operacao', 'cod_estacao',
                     'max_valor', 'grupo_bilhete'],
    'arq07_paradas': ['num_estacao', 'estacao', 'cod_estacao', 'sistemas_que_operam'],
    'arq8_statusviagens ': ['ordem', 'dia', 'viagem', 'origem_prevista', 'origem_real', 'destino_previsto',
                            'destino_real', 'hora_inicio_prevista', 'hora_inicio_real', 'hora_fim_prevista',
                            'hora_fim_real', 'trem', 'status', 'pico_vale'],
    'arq9_validacaobilhetes ': ['estacao', 'dbd_id', 'data_hora_corrigida', 'forma_pagamento', 'tipo_de_bilhete'],
    'arq08_03_11_15_viagens': ['ordem', 'dia', 'viagem', 'origem_previa', 'origem_real', 'destino_previo',
                               'destino_real', 'hora_ini_prevista', 'hora_ini_real', 'hora_fim_prevista',
                               'hora_fim_real', 'trem', 'status', 'desc_status', 'pico_vale', 'incidente_leve',
                               'incidente_grave', 'viagem_interrompida', 'id_ocorrencia', 'id_interrupcao',
                               'id_linha', 'lotacao'],
    'arq11_detalhesviagens': ['data', 'id_viagem', 'hora_inicio_programada', 'hora_fim_programada',
                              'hora_inicio_realizada', 'status', 'interrupcao', 'lotacao_maxima', 'tpppm', 'tprpm',
                              'tpppt', 'tprpt', 'tppfp', 'tprfp'],
    'arq12': ['ordem', '"emissao"', 'data', 'hora', 'tipo', 'trem', 'cdv', 'estacao', 'via', 'viagem', 'causa',
              'excluir', 'motivo'],
    'arq16_bloqueios': ['cod_estacao', 'estacao', 'bloqueio', 'dbd_id', 'data_pass', 'qtd_passageiros',
                        'max_num_est', 'min_bloqueio'],
    'tab_06_validadores': ['linha', 'cod_est', 'estacao', 'bloqueio', 'dbd_emp', 'dbd_num', 'dbd_data',
                           'valid_ext_emp', 'valida_ext_data'],
    'tab_13_cdv': ['cdv', 'sentido_circulacao', 'comprimento', 'cod_vel_max', 'plataforma_estacao',
                   'tempo_teorico_perc', 'tempo_medido_perc', 'tempo_ocupacao'],
    'tab_consumo_energia': ['referencia', 'num_instalacao', 'tipo', 'total_kwh', 'local', 'endereco'],
}

INSERTS_PREDEFINIDOS = [
    {
        'nome': "Padronização de Nomes",
        'sql': """
            update migracao.tab01 set tipo_dia = 'Domingos e Feriados' where tipo_dia = 'domingo e feriado';
            update migracao.tab01 set tipo_dia = 'Sabados' where tipo_dia = 'sabado';
            update migracao.tab01 set tipo_dia = 'Dias Uteis' where tipo_dia = 'Dia util' or tipo_dia = 'Dia Util' or tipo_dia = 'dia util' or tipo_dia = 'util';
            update migracao.tab01 set mesref = replace (mesref,'/','-');
            update migracao.tab01 set viagens  = replace (viagens,'.0','');
            update migracao.tab02 set dbd_num = id from public.validador i where dbd_num = i.dbd_id;
            update migracao.tab02_marco set dbd_num = id from public.validador i where dbd_num = i.dbd_id;
            update migracao.tab01 set tempo_percurso  = '00:00:00' where tempo_percurso ='nan' ;
            update migracao.tab01 set disp_frota  = '0' where disp_frota  ='nan';
            update migracao.tab09 set tue = t.id from public.frota t where tue = t.cod_trem ;
            update migracao.tab09 set tue = t.id from public.frota t where tue = t.cod_trem ;
            update migracao.tab14 a set composicao = t.id from public.frota t where a.composicao = t.cod_trem;   
            update migracao.tab02 set cod_estacao = 1 where cod_estacao ='ELD';
            update migracao.tab02 set cod_estacao = 2 where cod_estacao = 'CID'; 
            update migracao.tab02 set cod_estacao = 3 where cod_estacao = 'VOS';
            update migracao.tab02 set cod_estacao = 4 where cod_estacao = 'GAM';
            update migracao.tab02 set cod_estacao = 5 where cod_estacao = 'CAL';
            update migracao.tab02 set cod_estacao = 6 where cod_estacao = 'CAP';
            update migracao.tab02 set cod_estacao = 7 where cod_estacao ='LAG';
            update migracao.tab02 set cod_estacao = 8 where cod_estacao = 'CNT';
            update migracao.tab02 set cod_estacao = 9 where cod_estacao = 'SAE';
            update migracao.tab02 set cod_estacao = 10 where cod_estacao = 'SAT';
            update migracao.tab02 set cod_estacao = 11 where cod_estacao = 'HOT';
            update migracao.tab02 set cod_estacao = 12 where cod_estacao = 'SAI';
            update migracao.tab02 set cod_estacao = 13 where cod_estacao = 'JCS';
            update migracao.tab02 set cod_estacao = 14 where cod_estacao = 'MSH';
            update migracao.tab02 set cod_estacao = 15 where cod_estacao = 'SGB';
            update migracao.tab02 set cod_estacao = 16 where cod_estacao = 'PRM';
            update migracao.tab02 set cod_estacao = 17 where cod_estacao = 'WLB';
            update migracao.tab02 set cod_estacao = 18 where cod_estacao = 'FLO';
            update migracao.tab02 set cod_estacao = 19 where cod_estacao = 'VRO';
            update migracao.tab02 set valor  = '5.50'  where valor = '5,5';
            update migracao.tab02_marco set cod_estacao = 1 where cod_estacao ='ELD';
            update migracao.tab02_marco set cod_estacao = 2 where cod_estacao = 'CID';  
            update migracao.tab02_marco set cod_estacao = 3 where cod_estacao = 'VOS';
            update migracao.tab02_marco set cod_estacao = 4 where cod_estacao = 'GAM';
            update migracao.tab02_marco set cod_estacao = 5 where cod_estacao = 'CAL';
            update migracao.tab02_marco set cod_estacao = 6 where cod_estacao = 'CAP';
            update migracao.tab02_marco set cod_estacao = 7 where cod_estacao ='LAG';
            update migracao.tab02_marco set cod_estacao = 8 where cod_estacao = 'CNT';
            update migracao.tab02_marco set cod_estacao = 9 where cod_estacao = 'SAE';
            update migracao.tab02_marco set cod_estacao = 10 where cod_estacao = 'SAT';
            update migracao.tab02_marco set cod_estacao = 11 where cod_estacao = 'HOT';
            update migracao.tab02_marco set cod_estacao = 12 where cod_estacao = 'SAI';
            update migracao.tab02_marco set cod_estacao = 13 where cod_estacao = 'JCS';
            update migracao.tab02_marco set cod_estacao = 14 where cod_estacao = 'MSH';
            update migracao.tab02_marco set cod_estacao = 15 where cod_estacao = 'SGB';
            update migracao.tab02_marco set cod_estacao = 16 where cod_estacao = 'PRM';
            update migracao.tab02_marco set cod_estacao = 17 where cod_estacao = 'WLB';
            update migracao.tab02_marco set cod_estacao = 18 where cod_estacao = 'FLO';
            update migracao.tab02_marco set cod_estacao = 19 where cod_estacao = 'VRO';
            update migracao.tab02_marco set valor  = '5.50'  where valor = '5,5';
            update migracao.tab07  set cod_estacao = 1 where cod_estacao ='ELD';
            update migracao.tab07 set cod_estacao = 2 where cod_estacao = 'CID';    
            update migracao.tab07 set cod_estacao = 3 where cod_estacao = 'VOS';
            update migracao.tab07 set cod_estacao = 4 where cod_estacao = 'GAM';
            update migracao.tab07 set cod_estacao = 5 where cod_estacao = 'CAL';
            update migracao.tab07 set cod_estacao = 6 where cod_estacao = 'CAP';
            update migracao.tab07 set cod_estacao = 7 where cod_estacao = 'LAG';
            update migracao.tab07 set cod_estacao = 8 where cod_estacao = 'CNT';
            update migracao.tab07 set cod_estacao = 9 where cod_estacao = 'SAE';
            update migracao.tab07 set cod_estacao = 10 where cod_estacao = 'SAT';
            update migracao.tab07 set cod_estacao = 11 where cod_estacao = 'HOT';
            update migracao.tab07 set cod_estacao = 12 where cod_estacao = 'SAI';
            update migracao.tab07 set cod_estacao = 13 where cod_estacao = 'JCS';
            update migracao.tab07 set cod_estacao = 14 where cod_estacao = 'MSH';
            update migracao.tab07 set cod_estacao = 15 where cod_estacao = 'SGB';
            update migracao.tab07 set cod_estacao = 16 where cod_estacao = 'PRM';
            update migracao.tab07 set cod_estacao = 17 where cod_estacao = 'WLB';
            update migracao.tab07 set cod_estacao = 18 where cod_estacao = 'FLO';
            update migracao.tab07 set cod_estacao = 19 where cod_estacao = 'VRO';
            update migracao.tab14 set composicao = replace(composicao, 'TUE ','T');
            update migracao.tab14 T set composicao = ID from public.frota where T.composicao = COD_TREM;
            update migracao.tab03 set trem = i.id from public.frota i where trem = i.cod_trem;
            update migracao.arq8_statusviagens  set trem  = i.id from public.frota i where trem = i.cod_trem;
            update migracao.arq3_dadosviagens  set veiculo  = i.id from public.frota i where veiculo = i.cod_trem;
            delete from migracao.tab03 where status = '12';
            update migracao.tab09 set tue = t.id from public.frota t where tue = t.cod_trem ;
            update migracao.tab09 set hora_inicio = '00:00' where hora_inicio = '';
            update migracao.tab09 set hora_inicio = '00:00' where hora_inicio = ':';
            update migracao.tab09 set hora_fim  = '00:00' where hora_fim = ':';
            update migracao.tab09 set hora_fim  = '00:00' where hora_fim = '';
            update migracao.tab06 t set trem = f.id::varchar from public.frota f where f.cod_trem = t.trem ;
            delete from migracao.tab01 where mesref is null and tipo_dia is null and fx_hora is null   ;      
            update migracao.tab01 set viagens = 0 where viagens is null; 
            update migracao.tab01 set tempo_percurso  = '00:00:00' where tempo_percurso  is null; 
        """,
    },
    {
        'nome': "Validadores",
        'sql': """
            INSERT INTO public.mov_dbd
            (linha, cod_estacao, estacao, bloqueio, c_empresa_validador, dbd_num, dbd_data, valid_ex_emp, valid_ex_num, valid_ex_data)
            SELECT t1.linha::int, t1.cod_estacao::int, t1.estacao, t1.bloqueio::int, t1.c_empresa_validador, t1.dbd_num, TO_CHAR(TO_DATE(t1.dbd_data, 'DD/MM/YYYY'), 'YYYY-MM-DD')::date,
            t1.valid_ex_emp, t1.valid_ex_num::int, TO_CHAR(TO_DATE(t1.valid_ex_data, 'DD/MM/YYYY'), 'YYYY-MM-DD')::date
            FROM migracao.tab07 AS t1
            WHERE NOT EXISTS (
                SELECT 1 FROM public.mov_dbd AS t2
                WHERE t2.linha = t1.linha::int AND t2.cod_estacao = t1.cod_estacao::int AND t2.dbd_num = t1.dbd_num
            );
            INSERT INTO public.validador (dbd_id, bloqueio, validador, tipo)
            SELECT DISTINCT dbd_num, bloqueio_id::INT, 'SEM_DADO', 'MOVIMENTACAO' 
            FROM migracao.tab02
            ON CONFLICT (dbd_id) DO NOTHING;

            update migracao.tab02 v set dbd_num = m.id  from public.validador m where v.dbd_num = m.dbd_id;
            update migracao.tab02_marco  v set dbd_num = m.id  from public.validador m where v.dbd_num = m.dbd_id;
        """,
    },
    {
        'nome': "Quadro de Viagens",
        'sql': """
            INSERT INTO public.ARQ1_PROGPLAN(MESREF, TIPO_DIA, FX_HORA, VIAGENS, TEMPO_PRECURSO, DISP_FROTA)
            SELECT (MESREF || '-01')::date, TIPO_DIA, FX_HORA::TIME, VIAGENS::INT, TEMPO_PERCURSO::TIME, DISP_FROTA::INT
            FROM migracao.tab01 AR;
            
            update public.arq1_progplan set tipo_dia ='Dias Uteis' where tipo_dia = 'Dia Uteis';  
            update public.arq1_progplan set intervalo = '00:07:00' where viagens  = 8;
            update public.arq1_progplan set intervalo = '00:03:30' where viagens  = 16;
            update public.arq1_progplan set intervalo = '00:03:30' where viagens  = 18;
            update public.arq1_progplan set intervalo = '00:03:30' where viagens  = 17;
            update public.arq1_progplan set intervalo = '00:04:00' where viagens  = 15;
            update public.arq1_progplan set intervalo = '00:09:00' where viagens  = 7;
            update public.arq1_progplan set intervalo = '00:30:00' where viagens  = 2;
            update public.arq1_progplan set intervalo = '00:15:00' where viagens  = 4;
            update public.arq1_progplan set intervalo = '00:06:00' where viagens  = 10;
            update public.arq1_progplan set intervalo = '00:03:00' where viagens  = 19;
            update public.arq1_progplan set intervalo = '00:06:30' where viagens  = 9;
            update public.arq1_progplan set intervalo = '00:04:20' where viagens  = 14;
            update public.arq1_progplan set intervalo = '00:04:40' where viagens  = 13;
            update public.arq1_progplan set intervalo = '01:00:00' where viagens  = 0;
            update public.arq1_progplan set intervalo = '00:20:00' where viagens  = 3;
            update public.arq1_progplan set intervalo = '00:05:30' where viagens  = 11;
            update public.arq1_progplan set intervalo = '00:10:00' where viagens  = 6;
            update public.arq1_progplan set intervalo = '00:20:00' where viagens  = 3;
            update public.arq1_progplan set intervalo = '00:05:30' where viagens  = 11;
            update public.arq1_progplan set intervalo = '00:05:00' where viagens  = 12;
            update public.arq1_progplan set intervalo = '00:03:00' where viagens  = 20;
            update public.arq1_progplan set intervalo = '00:12:00' where viagens  = 5;
            update public.arq1_progplan set intervalo = '01:00:00' where viagens  = 1;
            update public.arq1_progplan set intervalo = '00:00:00', tempo_precurso = '00:00:00' where viagens  = 0;
            update public.arq1_progplan set viagens = 0 where viagens is null;
        """,
    },
    {
        'nome': "Bilhetagem",
        'sql': """
            insert into public.arq2_bilhetagem (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM,id_validador,VALOR,USUARIO)
            select CONCAT(ab.data_completa, ' ', ab.hora_completa)::timestamp, ab.cod_estacao ::INT,ab.bloqueio_id::INT,ab.grupo_bilhete ,ab.forma_pagamento ,ab.tipo_bilhete,null,ab.valor ::numeric(3,2),ab.user_id 
            from migracao.tab02 ab 
            ON CONFLICT (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM) DO NOTHING;
            
            insert into public.arq2_bilhetagem (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM,id_validador,VALOR,USUARIO)
            select CONCAT(ab.data_completa, ' ', ab.hora_completa)::timestamp,ab.cod_estacao ::INT,ab.bloqueio_id::INT,ab.grupo_bilhete ,ab.forma_pagamento ,ab.tipo_bilhete,null,ab.valor ::numeric(3,2),ab.user_id 
            from migracao.tab02_marco ab 
            ON CONFLICT (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM) DO NOTHING;                             
        """,
    },
    {
        'nome': "Viagens",
        'sql': """
            insert into public.arq3_viagens (ordem, "data",viagem ,origem, destino, hora_ini, hora_fim,tipo_real,id_veiculo,incidente_leve,incidente_grave,viagem_interrompida,id_ocorrencia, id_interrupcao,id_linha,hora_ini_plan,hora_fim_plan,lotacao,tempo_prog,tempo_real,mtrp,dia_semana,atraso,intervalo)
            select s.ordem::int ,s.dia::date,s.viagem::int,s.origem_prevista,s.destino_real , s.hora_inicio_real::time, s.hora_fim_real::time ,d.tipo_real::int , s.trem::int, case when d.incidente_leve = 'SIM' then true else false end as incleve , case when d.incidente_grave = 'SIM' then true else false end as incgrave , d.viagem_interrompida, null, null, 1, s.hora_inicio_prevista::time , s.hora_fim_prevista::time , null, null, null,null,null,null,null 
            from  migracao.arq8_statusviagens s inner join migracao.arq3_dadosviagens d on s.viagem = d.viagem  and s.dia = d.dia and s.trem = d.veiculo
            ON CONFLICT (ordem,data,viagem,origem,destino,hora_ini,hora_fim) DO NOTHING;      
            insert into public.arq3_viagens (ordem,"data",viagem,origem,destino,hora_ini,hora_fim,tipo_real,id_veiculo,incidente_leve,incidente_grave,viagem_interrompida,id_ocorrencia,id_interrupcao,id_linha,hora_ini_plan,hora_fim_plan )      
            select ordem::int,dia::date,   viagem::int,   origemreal ,   destinoreal ,  horainicioreal::time  ,    horafimreal::time ,    status::int,   trem::int, case when incidenteleve = '' then false    when incidenteleve is null then false  when incidenteleve = 'nao' then false else true    end as inc_leve,   case when incidentegrave = '' then false when incidentegrave is null then false when incidentegrave = 'nao' then false else true  end as inc_grave,  stat_desc ,    id_ocorr::int, id_interrupcao::int,   id_linha::int, t.horainicioprevista::time,    t.horafimprevista::time from migracao.tab03 t
            ON CONFLICT (ordem,data,viagem,origem,destino,hora_ini,hora_fim) DO NOTHING;
            update public.arq3_viagens set viagem_interrompida = 'Sem Interrupcao' where viagem_interrompida = 'Executada';
            update public.arq3_viagens set viagem_interrompida = 'Cancelada Totalmente' where viagem_interrompida = 'Cancelada';
            update public.arq3_viagens set viagem_interrompida = 'Cancelada Parcial' where viagem_interrompida = 'Interrompida';
            delete from public.arq3_viagens where viagem_interrompida in ('Injecao','Recolhimento');
            update public.arq3_viagens set tempo_prog = hora_fim_plan - hora_ini_plan;
            update public.arq3_viagens set tempo_real = hora_fim - hora_ini;
            update public.arq3_viagens set dia_semana = c.dia_semana from public.calendario c where "data" = c.data_calendario;
            update public.arq3_viagens set mtrp = EXTRACT(EPOCH FROM  tempo_real ) /  nullif(EXTRACT(EPOCH FROM  tempo_prog ),0);
            update public.arq3_viagens set dia_semana = 99 where "data" in (select  f.data_feriado from public.feriados f);
            update public.arq3_viagens v set intervalo = p.intervalo  from public.arq1_progplan p where v.dia_semana in (1,2,3,4,5) and extract(hour  from  p.fx_hora) = extract (hour from v.hora_ini) and extract(month from p.mesref) = extract(month from  v."data") and extract(year from v."data") = extract(year from p.mesref) and p.tipo_dia = 'Dias Uteis';
            update public.arq3_viagens v set intervalo = p.intervalo  from public.arq1_progplan p where v.dia_semana in (0,99) and extract(hour  from  p.fx_hora) = extract (hour from v.hora_ini) and extract(month from p.mesref) = extract(month from  v."data") and extract(year from v."data") = extract(year from p.mesref) and p.tipo_dia = 'Domingos e Feriados';
            update public.arq3_viagens v set intervalo = p.intervalo  from public.arq1_progplan p where v.dia_semana in (6) and extract(hour  from  p.fx_hora) = extract (hour from v.hora_ini) and extract(month from p.mesref) = extract(month from  v."data") and extract(year from v."data") = extract(year from p.mesref) and p.tipo_dia = 'Sabados';
            update public.arq3_viagens av set atraso = 0.5 where (av.tempo_prog - av.tempo_real) >= intervalo * 2 and (av.tempo_prog - av.tempo_real) <= intervalo * 3;
            update public.arq3_viagens av set atraso = 0.0 where (av.tempo_prog - av.tempo_real) < intervalo * 2;
            update public.arq3_viagens av set atraso = 0.0 where av.tempo_prog > av.tempo_real;
            update public.arq3_viagens av set atraso = 0.5 where (av.tempo_prog - av.tempo_real) > intervalo * 2 and (av.tempo_prog - av.tempo_real) <= intervalo * 3;
            update public.arq3_viagens av set atraso = 1.0 where (av.tempo_prog - av.tempo_real) > intervalo * 3;
            update public.arq3_viagens  set atraso = 2.0 where incidente_leve is true;
            update public.arq3_viagens set atraso = 4.0 where incidente_grave is true;
        """,
    },
    {
        'nome': "Interrupções de Viagem",
        'sql': """
            INSERT INTO ARQ12_INTERRUPCOES (ID_VIAGEM, ID_OCORRENCIA, ID_VEICULO, TIPO_INCIDENTE, ORIGEM_FALHA, TEMPO_INTERRUPCAO, AMEACAS, DATA_HORA, ID_LOCAL, REFERENCIA, VIA, DESCRICAO, ABONO, JUSTIFICATIVA)
            sELECT a.viagem::int, 0, a.trem::int, 'INTERRUPCAO', a.estacao , a.hora::interval , false , (a."data"  || ' ' || a.hora  )::timestamp  , 0 , a.tipo::varchar(30), a.via, a.causa::varchar(30),false, a.motivo_da_exclusao ::varchar(30)  
            from migracao.tab06 a 
        """,
    },
    {
        'nome': "Ocorrências",
        'sql': """
            insert into public.arq4_ocorrencias (tipo,subtipo,"data",hora_ini,hora_fim,motivo,"local",bo,id_veiculo,id_dispositivo)
            select tipo::varchar(20),subtipo::varchar(20),TO_DATE("data", 'DD/MM/YYYY')::date,horaini::time,horafim::time,motivo,"local",bo,null,null from migracao.tab04 ON CONFLICT (tipo,subtipo,"data",hora_ini,hora_fim,motivo,"local") DO NOTHING;
            
            insert into public.arq4_ocorrencias (tipo,subtipo , "data", motivo, hora_ini,hora_fim)
            select tipo,'RECLAMAÇÃO', dt::date, motivo ,'08:00:00','08:00:00' from migracao.arq4_1_reclamacoesusuarios ao
            ON CONFLICT (tipo,subtipo,"data",hora_ini,hora_fim,motivo,"local") DO NOTHING;
        """,
    },
    {
        'nome': "Manutenção",
        'sql': """
            INSERT INTO public.registros_manutencao (falha, id_tue, data_abertura, data_fechamento, hora_inicio, hora_fim, origem, destino, km, "local", tipo_manutencao ) 
            select distinct  mn.tipo_falha,    op.tue::int,    op."data"::date,    data_fechamento::date ,    op.hora_inicio::time,    op.hora_fim::time,      op.origem ,
            op.destino , op.km,op.status, mn.tipo_desc 
            FROM   migracao.tab09 AS op inner  JOIN    migracao.tab14 AS mn ON    op.tue = mn.composicao AND
            TO_DATE(op."data" , 'DD/MM/YYYY') = TO_DATE(mn.data_abertura, 'DD/MM/YYYY') and OP.status IN( 'MANUT')   group by mn.tipo_falha,
            op.tue,    op."data",    op.hora_inicio,    op.hora_fim ,    mn.data_fechamento,    op.origem ,    op.destino ,    op.km,    op.status,    mn.tipo_desc;
            
            update public.registros_manutencao set tempo_indisponivel = hora_fim - hora_inicio;
        """,
    },
    {
        'nome': "Energia",
        'sql': """
            insert into public.energia (mes_ref, tipo,consumo ,"local" ,num_instalacao  )
            select (referencia || '/01')::date, tipo , total_kwh::numeric,"local" , num_instalacao::numeric  from migracao.tab12
            ON CONFLICT (mes_ref,tipo,consumo,local,num_instalacao) DO NOTHING;
        """,
    },
    {
        'nome': "Disponibilidade Frota",
        'sql': """
            insert into public.disponibilidade_tue (id_tue, "data", hora_inicio,hora_fim,destino,descricao,status,km)
            select tue::INT, "data"::date, hora_inicio::time,hora_fim::time,destino,descricao,status,kM::int from migracao.tab09 where status != 'MANUT';
            
            update public.disponibilidade_tue set horas_disp = hora_fim - hora_inicio;
            
            insert into public.horas_disponiveis (id_tue, mes,horas_disponiveis,horas_operacao)
            with operacao as (
                select sum(horas_disp) horas_ope, id_tue, date_trunc('month',"data")::date mes   
                from public.disponibilidade_tue dt where status = 'OPE' group by id_tue, mes
            ), disponibilidade as (
                select sum(horas_disp) horas_disp, id_tue, date_trunc('month',"data")::date mes  
                from public.disponibilidade_tue dt where status = 'DISP' group by id_tue, mes 
            )
            select o.id_tue, o.mes, d.horas_disp, o.horas_ope  
            from operacao o 
            inner join disponibilidade d on o.id_tue = d.id_tue and o.mes = d.mes
            ON CONFLICT (id_tue, mes, horas_disponiveis) DO NOTHING;
        """,
    },
    {
        'nome': "KM_Percorrida",
        'sql': """
            insert into public.km_percorrida(id_tue, km_inicial, km_final,km_percorrida, mes)
            select tue::int , min (km) as km_inicial, max(km) as km_final,  max (km)- min(km)   as km_percorrido, min("data")::date as "mes" 
            from migracao.tab09 where  status != 'MANUT' group by tue order by tue
            ON CONFLICT (id_tue,km_inicial,km_final,mes) DO NOTHING;
            
            update public.km_percorrida set mes = DATE_TRUNC('month', mes)::date;
        """,
    },
    {
        'nome': "Indisponibilidade - TUE",
        'sql': """
            insert into public.indisponibilidade_tue(id_tue,horas_indisp,mes)
            select distinct id_tue, sum(tempo_indisponivel), DATE_TRUNC('month',data_abertura)::date as data_manut  
            from public.registros_manutencao group by id_tue, data_manut
            ON CONFLICT (id_tue,mes,tipo_manut,horas_indisp) DO NOTHING;
        """,
    },
    {
        'nome': "Frota Status",
        'sql': """
            insert into public.frota_status (id_trem, mes_ref, prod_km,horas_disponivel, horas_operacao, horas_manutencao)
            select hd.id_tue, hd.mes, kp.km_percorrida  , hd.horas_disponiveis, hd.horas_operacao, it.horas_indisp  
            from public.horas_disponiveis hd  
            inner join public.indisponibilidade_tue it on hd.id_tue = it.id_tue and hd.mes = it.mes 
            inner join public.km_percorrida kp on it.id_tue = kp.id_tue and it.mes = kp.mes
            ON CONFLICT (id_trem,mes_ref,prod_km,horas_operacao,horas_disponivel,horas_manutencao) DO NOTHING;
            
            with falhas as (
                select count(*) qtd, DATE_TRUNC('month', rm.data_abertura)::date AS  MES,  id_tue 
                from registros_manutencao rm where tipo_manutencao like 'CORRETIVA' group by id_tue, mes
            )
            update frota_status fr set falhas = f.qtd from falhas f where fr.id_trem = f.id_tue and fr.mes_ref = f.mes;
            update frota_status set falhas = 0 where falhas is null;
        """,
    },
    {
        'nome': "Deletar tabelas de migração",
        'sql': """  
            delete from migracao.tab01;
            delete from migracao.tab02_temp2;
            delete from migracao.tab02_MARCO;
            delete from migracao.tab02;
            delete from migracao.tab03;
            delete from migracao.tab04;
            delete from migracao.tab05;
            delete from migracao.tab06;
            delete from migracao.tab07;
            delete from migracao.tab08;
            delete from migracao.tab09;
            delete from migracao.tab14;
            delete from migracao.tab12;
            delete from migracao.tab13;
            delete from migracao.arq11_detalhesviagens;
            delete from migracao.arq12_excecoesviagens;
            delete from migracao.arq13_1_incidentes;
            delete from migracao.arq13_2_ocorrenciasseguranca;
            delete from migracao.arq15_tueoperacoes;
            delete from migracao.arq16_contagempassageiros;
            delete from migracao.arq17_bloqueios;
            delete from migracao.arq18_equipamentos;
            delete from migracao.arq1_resumoviagensfrota;
            delete from migracao.arq2_dadosbilhetagem;
            delete from migracao.arq3_dadosviagens;
            delete from migracao.arq4_1_reclamacoesusuarios;
            delete from migracao.arq4_2_manutencao;
            delete from migracao.arq4_3_seguranca;
            delete from migracao.arq5_1_falhasmanutencao;
            delete from migracao.arq5_6_dadosfrota;
            delete from migracao.arq5_8_necessidadedisponibilidade;
            delete from migracao.arq7_estacoes;
            delete from migracao.arq8_statusviagens;
            delete from migracao.arq9_validacaobilhetes;
        """,
    }
]

class PostgreSQLDataLoader:
    def __init__(self, db_config):
        self.db_config = db_config
        self.schema = db_config.get('schema', 'migracao') 
        self.db_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

    @st.cache_resource
    def get_engine(_self):
        return create_engine(_self.db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)

    def test_connection(self):
        try:
            with self.get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
                return True, "Conexão estabelecida com sucesso!"
        except Exception as e:
            return False, str(e)

    def execute_custom_insert(self, sql):
        try:
            with self.get_engine().begin() as conn:
                conn.execute(text(f"SET search_path TO {self.schema}, public"))
                conn.execute(text(sql))
            return True
        except Exception as e:
            st.error(f"Erro SQL: {e}")
            return False

    def load_dataframe(self, df, table_name):
        try:
            df.to_sql(table_name, self.get_engine(), schema=self.schema, if_exists='append', index=False, method='multi', chunksize=1000)
            return True
        except Exception as e:
            st.error(f"Erro Carga: {e}")
            raise e

@st.cache_data(ttl=600, show_spinner=False)
def run_query(_engine, query):
    try:
        with _engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro na execução da Query: {e}") 
        return pd.DataFrame()

def get_date_filter_ui(key_prefix):
    c1, c2 = st.columns(2)
    with c1:
        ano_sel = st.selectbox("Ano", [2026, 2025, 2024], key=f'ano_{key_prefix}')
    with c2:
        meses_map = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        mes_sel = st.selectbox("Mês", list(meses_map.keys()), format_func=lambda x: meses_map[x], index=6, key=f'mes_{key_prefix}')
    
    last_day = calendar.monthrange(ano_sel, mes_sel)[1]
    return {
        'ano': ano_sel,
        'mes': mes_sel,
        'mes_nome': meses_map[mes_sel],
        'dt_start': f"{ano_sel}-{mes_sel:02d}-01",
        'dt_end': f"{ano_sel}-{mes_sel:02d}-{last_day}",
        'dt_start_ts': f"{ano_sel}-{mes_sel:02d}-01 00:00:00",
        'dt_end_ts': f"{ano_sel}-{mes_sel:02d}-{last_day} 23:59:59"
    }

# --- INÍCIO: SISTEMA DE LOGIN E PERMISSÕES DE ACESSO ---
if 'users' not in st.session_state:
    st.session_state['users'] = {
        'admin': {'password': 'admin', 'role': 'admin'},
        'op': {'password': 'op', 'role': 'operador'},
        'vis': {'password': 'vis', 'role': 'visualizador'}
    }

ALL_TABS = [
    "📂 Carga CSV", 
    "💾 SQL Scripts", 
    "📝 Logs", 
    "🎮 Operação & Análise", 
    "📈 Indicadores (CMD)", 
    "🏛️ Metrô em Números",
    "🤖 Inteligência Artificial (ML)",
    "⚙️ Configurações de Acesso"
]

if 'permissions' not in st.session_state:
    st.session_state['permissions'] = {
        'admin': ALL_TABS,
        'operador': ["📂 Carga CSV", "🎮 Operação & Análise", "📈 Indicadores (CMD)", "🤖 Inteligência Artificial (ML)"],
        'visualizador': ["🏛️ Metrô em Números"]
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'current_role' not in st.session_state:
    st.session_state['current_role'] = None

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚇 Login - GESTÃO DE DADOS - METRO BH")
        st.markdown("Bem-vindo! Por favor, faça o login para acessar o sistema.")
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")

            if submit:
                users = st.session_state['users']
                if username in users and users[username]['password'] == password:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = username
                    st.session_state['current_role'] = users[username]['role']
                    st.success("Login efetuado com sucesso! Redirecionando...")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        
    with st.expander("⚙️ Configuração DB", expanded=False):
        
        with st.form("db_connection_form"): 
            db_host = st.text_input("Host", value=DEFAULT_DB_CONFIG.get('host'), key='input_host')
            db_port = st.text_input("Porta", value=DEFAULT_DB_CONFIG.get('port'), key='input_port')
            db_name = st.text_input("DB Name", value=DEFAULT_DB_CONFIG.get('dbname'), key='input_dbname')
            db_user = st.text_input("User", value=DEFAULT_DB_CONFIG.get('user'), key='input_user')
            db_pass = st.text_input("Pass", type="password", value=DEFAULT_DB_CONFIG.get('password'), key='input_pass')
            
            if st.form_submit_button("Reconectar"):
                config = {'host': db_host, 'port': db_port, 'dbname': db_name, 'user': db_user, 'password': db_pass, 'schema': 'migracao'}
                loader = PostgreSQLDataLoader(config)
                success, msg = loader.test_connection()
                if success:
                    st.session_state['db_config'] = config 
                    st.session_state['connected'] = True
                    st.success("Reconectado!")
                    st.rerun()
                else:
                    st.error(f"Falha: {msg}")
    st.stop()
# --- FIM: SISTEMA DE LOGIN E PERMISSÕES DE ACESSO ---

if 'db_config' not in st.session_state:
    temp_loader = PostgreSQLDataLoader(DEFAULT_DB_CONFIG.copy())
    if temp_loader.test_connection()[0]:
        st.session_state['db_config'] = DEFAULT_DB_CONFIG
        st.session_state['connected'] = True
    else:
        st.session_state['connected'] = False

db_loader = PostgreSQLDataLoader(st.session_state['db_config']) if st.session_state.get('connected') else None

col_status, col_titulo = st.columns([1, 8])
with col_status:
    if st.session_state.get('connected'):
        st.markdown('<div class="status-container"><div class="status-indicator status-on">🟢 DB ON</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-container"><div class="status-indicator status-off">🔴 DB OFF</div></div>', unsafe_allow_html=True)

with col_titulo:
    st.title("🚇 GESTÃO DE DADOS OPERACIONAIS - METRO BH")

with st.sidebar:
    st.markdown(f"👤 **Logado como:** `{st.session_state['current_user']}`")
    st.markdown(f"🛡️ **Nível:** `{st.session_state['current_role']}`")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['current_role'] = None
        st.rerun()

    st.markdown("### Navegação")
    
    allowed_tabs = st.session_state['permissions'].get(st.session_state['current_role'], [])
    if not allowed_tabs:
        st.warning("Usuário sem abas liberadas.")
        st.stop()
        
    menu = st.radio("Menu de Navegação", allowed_tabs, label_visibility="collapsed")

    st.divider()
    

if menu == "📂 Carga CSV":
    st.subheader("Importação de CSV")
    uploaded_file = st.file_uploader("Arquivo CSV", type=['csv'])
    tabela_destino = st.selectbox("Tabela Destino", list(TABLES_CONFIG.keys()))
    
    if st.button("Carregar CSV") and uploaded_file and db_loader:
        try:
            delim = detect_delimiter(uploaded_file)
            df = pd.read_csv(uploaded_file, sep=delim, dtype=str)
            expected_cols = TABLES_CONFIG.get(tabela_destino, [])
            if len(df.columns) == len(expected_cols):
                df.columns = expected_cols
                df = convert_data_types(df, tabela_destino)
                with st.spinner('Carregando dados...'):
                    db_loader.load_dataframe(df, tabela_destino)
                st.success(f"Sucesso: {tabela_destino}")
            else:
                st.error(f"Erro colunas: Esperado {len(expected_cols)}, Recebido {len(df.columns)}")
        except Exception as e:
            st.error(f"Erro: {e}")

elif menu == "💾 SQL Scripts":
    st.subheader("Execução de Scripts")
    if len(INSERTS_PREDEFINIDOS) > 0:
        sel_scripts = st.multiselect("Scripts Predefinidos", [i['nome'] for i in INSERTS_PREDEFINIDOS])
        if st.button("Executar Scripts") and db_loader:
            progress_bar = st.progress(0)
            for idx, nome in enumerate(sel_scripts):
                script = next(i for i in INSERTS_PREDEFINIDOS if i['nome'] == nome)
                cmds = script['sql'].split(';')
                for cmd in cmds:
                    if cmd.strip(): db_loader.execute_custom_insert(cmd)
                progress_bar.progress((idx + 1) / len(sel_scripts))
            st.success("Execução concluída!")

    st.divider()
    if st.button("Executar SQL Manual") and db_loader:
        custom_sql = st.text_area("SQL")
        if custom_sql: db_loader.execute_custom_insert(custom_sql)

elif menu == "📝 Logs":
    st.info("Logs do sistema (Área reservada para logging futuro)")

elif menu == "🎮 Operação & Análise":
    # 1. Filtro Principal (Afeta apenas os KPIs superiores)
    filters = get_date_filter_ui("operacao_main")
    st.subheader(f"Painel Integrado de Operação - {filters['mes_nome']}/{filters['ano']}")

    if db_loader:
        engine = db_loader.get_engine()
        
        # --- Configuração do Ano Anterior (Mesmo Mês) Fixo para os KPIs ---
        ano_ant = filters['ano'] - 1
        mes = filters['mes']
        last_day_ant = calendar.monthrange(ano_ant, mes)[1]
        
        dt_start_ts_ant = f"{ano_ant}-{mes:02d}-01 00:00:00"
        dt_end_ts_ant = f"{ano_ant}-{mes:02d}-{last_day_ant} 23:59:59"
        dt_start_ant = f"{ano_ant}-{mes:02d}-01"
        dt_end_ant = f"{ano_ant}-{mes:02d}-{last_day_ant}"

        def calc_delta(atual, anterior):
            if anterior == 0 and atual > 0: return "100% vs Ano Ant."
            elif anterior == 0 and atual == 0: return "0%"
            else: return f"{((atual - anterior) / anterior) * 100:.1f}% vs Ano Ant."
        
        c_kpi1, c_kpi2, c_kpi3, c_kpi4, c_kpi5 = st.columns(5)
        
        # --- 1. Passageiros ---
        df_pax = run_query(engine, f"SELECT COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}'")
        val_pax = df_pax.iloc[0,0] if not df_pax.empty else 0
        val_pax_ant = run_query(engine, f"SELECT COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{dt_start_ts_ant}' AND data_hora <= '{dt_end_ts_ant}'").iloc[0,0] if not df_pax.empty else 0

        with c_kpi1:
            st.metric("Passageiros", f"{val_pax:,.0f}".replace(",", "."), delta=calc_delta(val_pax, val_pax_ant))
            render_download_btn(df_pax, "total_passageiros")

        # --- 2. Receita ---
        df_rev = run_query(engine, f"SELECT SUM(valor) as val FROM public.arq2_bilhetagem WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}'")
        val_rev = df_rev.iloc[0,0] if not df_rev.empty and df_rev.iloc[0,0] else 0
        df_rev_ant = run_query(engine, f"SELECT SUM(valor) as val FROM public.arq2_bilhetagem WHERE data_hora >= '{dt_start_ts_ant}' AND data_hora <= '{dt_end_ts_ant}'")
        val_rev_ant = df_rev_ant.iloc[0,0] if not df_rev_ant.empty and df_rev_ant.iloc[0,0] else 0

        with c_kpi2:
            st.metric("Receita", f"R$ {val_rev:,.2f}".replace(".", ","), delta=calc_delta(val_rev, val_rev_ant))
            render_download_btn(df_rev, "total_receita")

        # --- 3. Viagens (Real) ---
        df_real = run_query(engine, f"SELECT COUNT(*) as qtd FROM public.arq3_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'")
        val_real = df_real.iloc[0,0] if not df_real.empty else 0
        df_real_ant = run_query(engine, f"SELECT COUNT(*) as qtd FROM public.arq3_viagens WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}'")
        val_real_ant = df_real_ant.iloc[0,0] if not df_real_ant.empty else 0

        with c_kpi3:
            st.metric("Viagens (Real)", f"{val_real:,.0f}", delta=calc_delta(val_real, val_real_ant))
            render_download_btn(df_real, "total_viagens_real")

        # --- 4. Tempo Médio (Pico) ---
        q_tempo = f"""SELECT AVG(EXTRACT(EPOCH FROM tempo_real)/60) as tmp FROM public.arq3_viagens v
                      WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tempo_real IS NOT null AND tipo_real = 6 
                      AND dia_semana in (1,2,3,4,5) AND ((v.hora_ini >= '06:00:00' AND v.hora_ini < '08:00:00') OR (v.hora_ini >= '17:00:00' AND v.hora_ini < '19:00:00'))"""
        df_tempo = run_query(engine, q_tempo)
        val_tempo = df_tempo.iloc[0,0] if not df_tempo.empty and df_tempo.iloc[0,0] else 0
        
        q_tempo_ant = f"""SELECT AVG(EXTRACT(EPOCH FROM tempo_real)/60) as tmp FROM public.arq3_viagens v
                      WHERE data >= '{dt_start_ant}' AND data <= '{dt_end_ant}' AND tempo_real IS NOT null AND tipo_real = 6 
                      AND dia_semana in (1,2,3,4,5) AND ((v.hora_ini >= '06:00:00' AND v.hora_ini < '08:00:00') OR (v.hora_ini >= '17:00:00' AND v.hora_ini < '19:00:00'))"""
        df_tempo_ant = run_query(engine, q_tempo_ant)
        val_tempo_ant = df_tempo_ant.iloc[0,0] if not df_tempo_ant.empty and df_tempo_ant.iloc[0,0] else 0

        with c_kpi4:
            st.metric("Tempo Médio (Pico)", f"{val_tempo:.1f} min", delta=calc_delta(val_tempo, val_tempo_ant), delta_color="inverse")
            render_download_btn(df_tempo, "tempo_medio_pico")

        # --- 5. Total KM Percorrida ---
        df_mkbf = run_query(engine, f"SELECT SUM(prod_km) as km FROM public.frota_status WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}'")
        km = df_mkbf.iloc[0]['km'] if not df_mkbf.empty and df_mkbf.iloc[0]['km'] else 0
        df_mkbf_ant = run_query(engine, f"SELECT SUM(prod_km) as km FROM public.frota_status WHERE mes_ref >= '{dt_start_ant}' AND mes_ref <= '{dt_end_ant}'")
        km_ant = df_mkbf_ant.iloc[0]['km'] if not df_mkbf_ant.empty and df_mkbf_ant.iloc[0]['km'] else 0

        with c_kpi5:
            st.metric("Total KM Percorrida", f"{km:,.0f} KM".replace(",", "."), delta=calc_delta(km, km_ant))
            render_download_btn(df_mkbf, "total_km_percorrida")

        st.divider()

        # =======================================================
        # --- SEÇÃO DE GRÁFICOS EVOLUTIVOS (CARREGAMENTO LEVE) ---
        # =======================================================
        st.markdown("### 📈 Análise Evolutiva e Comparativa")
        st.markdown("**selecione qual métrica você deseja analisar** e o sistema carregará o gráfico dinamicamente.")
        
        col_sel1, col_sel2 = st.columns([1, 1])
        
        with col_sel1:
            # Substituí os 5 botões por um Selectbox elegante
            grafico_selecionado = st.selectbox(
                "📊 Qual indicador deseja analisar?", 
                ["Nenhum (Ocultar Gráfico)", "Passageiros", "Receita", "Viagens Realizadas"]
            )
            
        if grafico_selecionado != "Nenhum (Ocultar Gráfico)":
            with col_sel2:
                st.markdown("**Período de Comparação:**")
                # Esse filtro de data só existe e processa quando o usuário quer ver o gráfico!
                filters_comp = get_date_filter_ui("operacao_comp")
                
            nome_atual = f"{filters['mes_nome']}/{filters['ano']}"
            nome_comp = f"{filters_comp['mes_nome']}/{filters_comp['ano']}"
            
            st.markdown(f"#### Comparativo Diário: {nome_atual} vs {nome_comp}")
            
            # --- Renderização Condicional (Roda apenas a query do que foi selecionado) ---
            if grafico_selecionado == 'Passageiros':
                q_evo = f"SELECT EXTRACT(DAY FROM data_hora) as dia, COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1"
                df_evo = run_query(engine, q_evo)
                q_comp = f"SELECT EXTRACT(DAY FROM data_hora) as dia, COUNT(*) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{filters_comp['dt_start_ts']}' AND data_hora <= '{filters_comp['dt_end_ts']}' GROUP BY 1"
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
                    fig.update_xaxes(title="Dia do Mês", dtick=1)
                    st.plotly_chart(fig, use_container_width=True)
                    render_download_btn(df_final, "evolucao_pax_comparativo")

            elif grafico_selecionado == 'Receita':
                q_evo = f"SELECT EXTRACT(DAY FROM data_hora) as dia, SUM(valor) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1"
                df_evo = run_query(engine, q_evo)
                q_comp = f"SELECT EXTRACT(DAY FROM data_hora) as dia, SUM(valor) as qtd FROM public.arq2_bilhetagem WHERE data_hora >= '{filters_comp['dt_start_ts']}' AND data_hora <= '{filters_comp['dt_end_ts']}' GROUP BY 1"
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
                    fig.update_xaxes(title="Dia do Mês", dtick=1)
                    st.plotly_chart(fig, use_container_width=True)
                    render_download_btn(df_final, "evolucao_rev_comparativo")

            elif grafico_selecionado == 'Viagens Realizadas':
                q_evo = f"SELECT EXTRACT(DAY FROM data) as dia, COUNT(*) as qtd FROM public.arq3_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1"
                df_evo = run_query(engine, q_evo)
                q_comp = f"SELECT EXTRACT(DAY FROM data) as dia, COUNT(*) as qtd FROM public.arq3_viagens WHERE data >= '{filters_comp['dt_start']}' AND data <= '{filters_comp['dt_end']}' GROUP BY 1"
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
                    fig.update_xaxes(title="Dia do Mês", dtick=1)
                    st.plotly_chart(fig, use_container_width=True)
                    render_download_btn(df_final, "evolucao_viagens_comparativo")

        st.divider()


# --- MAPA DA LINHA DO TREM ---
        st.markdown("### 🗺️ Mapa da Linha 1 - Metrô BH")
        st.markdown("*Visão geográfica da linha. O tamanho dos círculos representa o volume de entradas na estação no período selecionado.*")
        
        # 1. Coordenadas aproximadas das estações da Linha 1 do Metrô de BH
        map_data = pd.DataFrame([
            {'Estação': 'Eldorado', 'lat': -19.93796, 'lon': -44.02777},
            {'Estação': 'Cidade Industrial', 'lat': -19.94444, 'lon': -44.01322},
            {'Estação': 'Vila Oeste', 'lat': -19.93811, 'lon': -44.00130},
            {'Estação': 'Gameleira', 'lat': -19.92728, 'lon': -43.98730},
            {'Estação': 'Calafate', 'lat': -19.92184, 'lon': -43.96960},
            {'Estação': 'Carlos Prates', 'lat': -19.91700, 'lon': -43.95556},
            {'Estação': 'Lagoinha', 'lat': -19.91251, 'lon': -43.94117},
            {'Estação': 'Central', 'lat': -19.91693, 'lon': -43.93288},
            {'Estação': 'Santa Efigênia', 'lat': -19.91952, 'lon': -43.92211},
            {'Estação': 'Santa Tereza', 'lat': -19.91730, 'lon': -43.91187},
            {'Estação': 'Horto', 'lat': -19.90555, 'lon': -43.91310},
            {'Estação': 'Santa Inês', 'lat': -19.89472, 'lon': -43.90895},
            {'Estação': 'José Cândido', 'lat': -19.88302, 'lon': -43.91330},
            {'Estação': 'Minas Shopping', 'lat': -19.87193, 'lon': -43.92511},
            {'Estação': 'São Gabriel', 'lat': -19.86256, 'lon': -43.92547},
            {'Estação': 'Primeiro de Maio', 'lat': -19.85729, 'lon': -43.93402},
            {'Estação': 'Waldomiro Lobo', 'lat': -19.84781, 'lon': -43.93265},
            {'Estação': 'Floramar', 'lat': -19.83290, 'lon': -43.94025},
            {'Estação': 'Vilarinho', 'lat': -19.81974, 'lon': -43.94783}
        ])

        # 2. Buscar o fluxo de passageiros (volume de bilhetagem) no período filtrado
        q_map_vol = f"""
            SELECT id_estacao, COUNT(*) as volume
            FROM public.arq2_bilhetagem
            WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}'
            GROUP BY 1
        """
        df_map_vol = run_query(engine, q_map_vol)

        # 3. Cruzar as informações de volume com as coordenadas do mapa
        if not df_map_vol.empty:
            # Converter o id para int (caso venha como string) e mapear para o nome da estação
            df_map_vol['id_estacao'] = pd.to_numeric(df_map_vol['id_estacao'], errors='coerce')
            df_map_vol['Estação'] = df_map_vol['id_estacao'].map(STATION_MAP)
            
            # Fazer o merge com os dados do mapa, preenchendo com 0 as estações sem movimento
            map_data = pd.merge(map_data, df_map_vol[['Estação', 'volume']], on='Estação', how='left').fillna(0)
        else:
            map_data['volume'] = 0

        # 4. Calcular o tamanho dinâmico das bolhas (mínimo 8, máximo 40 para não estourar a tela)
        max_vol = map_data['volume'].max()
        if max_vol > 0:
            map_data['marker_size'] = (map_data['volume'] / max_vol * 32) + 8
        else:
            map_data['marker_size'] = 12

        # Formatar os números para o padrão brasileiro (ex: 1.500)
        map_data['volume_fmt'] = map_data['volume'].apply(lambda x: f"{int(x):,}").str.replace(',', '.')

        # 5. Renderizar a Linha Interligando as estações
        fig_map = px.line_mapbox(
            map_data, lat="lat", lon="lon",
            zoom=10.5, height=500, color_discrete_sequence=["#3498db"]
        )
        
        # 6. Renderizar os Pontos (Marcadores dinâmicos) de cada estação
        fig_map.add_trace(go.Scattermapbox(
            lat=map_data['lat'],
            lon=map_data['lon'],
            mode='markers+text',
            # Aplica o array dinâmico no tamanho do marcador
            marker=go.scattermapbox.Marker(
                size=map_data['marker_size'], 
                color='#2ecc71',
                opacity=0.8
            ),
            text=map_data['Estação'],
            textposition="top center",
            customdata=map_data[['Estação', 'volume_fmt']],
            # Formata a janelinha (tooltip) que aparece ao passar o mouse
            hovertemplate="<b>%{customdata[0]}</b><br>Fluxo de Entradas: %{customdata[1]}<extra></extra>"
        ))
        
        # Você pode trocar de "carto-positron" para "open-street-map" ou "carto-darkmatter" se preferir
        fig_map.update_layout(
            mapbox_style="carto-positron", 
            margin={"r":0,"t":0,"l":0,"b":0},
            showlegend=False
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        render_download_btn(map_data, "mapa_estacoes")
        st.divider()
        # -----------------------------

        sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs([
            "📊 Visão Geral & Ocorrências", 
            "🎫 Comercial & Estações", 
            "🚆 Transporte & Viagens", 
            "🛠️ Frota & Manutenção"
        ])

        with sub_t1:
            st.markdown("#### 📊 Balanço de Oferta x Demanda (Hora a Hora) - Por Sentido")
            
            CAPACIDADE_TREM = 1000
            
            q_oferta_ida = f"""
                SELECT EXTRACT(HOUR FROM hora_ini) as hora, COUNT(*) as viagens
                FROM public.arq3_viagens
                WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'
                AND (origem = 'Eldorado' OR origem = 'ELD') 
                GROUP BY 1
            """
            q_oferta_volta = f"""
                SELECT EXTRACT(HOUR FROM hora_ini) as hora, COUNT(*) as viagens
                FROM public.arq3_viagens
                WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}'
                AND (origem = 'Vilarinho' OR origem = 'VRO')
                GROUP BY 1
            """
            
            q_demanda_dir = f"""
                SELECT EXTRACT(HOUR FROM data_hora) as hora, id_estacao, COUNT(*) as qtd
                FROM public.arq2_bilhetagem
                WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}'
                GROUP BY 1, 2
            """
            
            df_ida = run_query(engine, q_oferta_ida)
            df_volta = run_query(engine, q_oferta_volta)
            df_demanda_dir = run_query(engine, q_demanda_dir)
            
            col_ida, col_volta = st.columns(2)
            num_dias = (datetime.strptime(filters['dt_end'], '%Y-%m-%d') - datetime.strptime(filters['dt_start'], '%Y-%m-%d')).days + 1

            if not df_demanda_dir.empty:
                df_demanda_dir['id_estacao'] = pd.to_numeric(df_demanda_dir['id_estacao'], errors='coerce').fillna(10)
                
                df_demanda_dir['peso_ida'] = (19 - df_demanda_dir['id_estacao']) / 18.0
                df_demanda_dir['peso_volta'] = (df_demanda_dir['id_estacao'] - 1) / 18.0
                
                df_demanda_dir['peso_ida'] = df_demanda_dir['peso_ida'].clip(0, 1)
                df_demanda_dir['peso_volta'] = df_demanda_dir['peso_volta'].clip(0, 1)
                
                df_demanda_dir['pax_ida'] = df_demanda_dir['qtd'] * df_demanda_dir['peso_ida']
                df_demanda_dir['pax_volta'] = df_demanda_dir['qtd'] * df_demanda_dir['peso_volta']
                
                df_demanda_agg = df_demanda_dir.groupby('hora')[['pax_ida', 'pax_volta']].sum().reset_index()
            else:
                df_demanda_agg = pd.DataFrame(columns=['hora', 'pax_ida', 'pax_volta'])

            with col_ida:
                st.markdown("##### ➡️ Sentido: Eldorado -> Vilarinho")
                if not df_ida.empty and not df_demanda_agg.empty:
                    df_comb_ida = pd.merge(df_ida, df_demanda_agg, on='hora', how='outer').fillna(0)
                    df_comb_ida['cap_media'] = ((df_comb_ida['viagens'] * CAPACIDADE_TREM) / num_dias).round(0)
                    df_comb_ida['pax_estimado'] = (df_comb_ida['pax_ida'] / num_dias).round(0) 
                    
                    fig_ida = go.Figure()
                    fig_ida.add_trace(go.Bar(x=df_comb_ida['hora'], y=df_comb_ida['cap_media'], name='Oferta (Lugares)', marker_color='rgba(46, 204, 113, 0.4)'))
                    fig_ida.add_trace(go.Scatter(x=df_comb_ida['hora'], y=df_comb_ida['pax_estimado'], name='Demanda Est.', mode='lines+markers', line=dict(color='#e74c3c')))
                    fig_ida.update_layout(title="Ida: Oferta vs Demanda", legend=dict(orientation="h", y=-0.2), margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_ida, use_container_width=True)
                    render_download_btn(df_comb_ida, "oferta_demanda_ida")

            with col_volta:
                st.markdown("##### ⬅️ Sentido: Vilarinho -> Eldorado")
                if not df_volta.empty and not df_demanda_agg.empty:
                    df_comb_volta = pd.merge(df_volta, df_demanda_agg, on='hora', how='outer').fillna(0)
                    df_comb_volta['cap_media'] = ((df_comb_volta['viagens'] * CAPACIDADE_TREM) / num_dias).round(0)
                    df_comb_volta['pax_estimado'] = (df_comb_volta['pax_volta'] / num_dias).round(0)
                    
                    fig_volta = go.Figure()
                    fig_volta.add_trace(go.Bar(x=df_comb_volta['hora'], y=df_comb_volta['cap_media'], name='Oferta (Lugares)', marker_color='rgba(52, 152, 219, 0.4)'))
                    fig_volta.add_trace(go.Scatter(x=df_comb_volta['hora'], y=df_comb_volta['pax_estimado'], name='Demanda Est.', mode='lines+markers', line=dict(color='#e67e22')))
                    fig_volta.update_layout(title="Volta: Oferta vs Demanda", legend=dict(orientation="h", y=-0.2), margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_volta, use_container_width=True)
                    render_download_btn(df_comb_volta, "oferta_demanda_volta")

            st.caption("""
                    **Como a Demanda Estimada é calculada?**
                    Como o sistema de bilhetagem registra apenas a estação de entrada (sem registro de saída), o sentido da viagem é estimado de forma ponderada com base na localização da estação:
                    - Embarques próximos ao **Eldorado** (Estação 1) possuem quase 100% de probabilidade de seguir no sentido **Vilarinho** (Ida).
                    - Embarques próximos a **Vilarinho** (Estação 19) possuem quase 100% de probabilidade de seguir no sentido **Eldorado** (Volta).
                    - Estações na região central dividem o fluxo proporcionalmente entre os dois sentidos, refletindo o movimento pendular diário.
                    """)

            st.divider()
            c_g1, c_g2, c_g3 = st.columns(3)
            
            with c_g1:
                st.markdown("##### ⚠️ Top Locais Incidentes")
                q_inc = f"""SELECT subtipo, COUNT(*) as qtd FROM public.arq4_ocorrencias 
                            WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND subtipo NOT LIKE 'RECLAMAÇÃO'
                            GROUP BY 1 ORDER BY 2 DESC LIMIT 10"""
                df_inc = run_query(engine, q_inc)
                if not df_inc.empty:
                    st.plotly_chart(px.bar(df_inc, x='subtipo', y='qtd', orientation='v', height=300), use_container_width=True)
                    render_download_btn(df_inc, "top_incidentes")

            with c_g2:
                st.markdown("##### 📢 Top Reclamações")
                q_rec = f"""SELECT motivo, COUNT(*) as qtd FROM public.arq4_ocorrencias 
                            WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tipo like 'RECLAMAÇÃO%'
                            GROUP BY 1 ORDER BY 2 DESC LIMIT 10"""
                df_rec = run_query(engine, q_rec)
                if not df_rec.empty:
                    st.plotly_chart(px.bar(df_rec, x='motivo', y='qtd', color_discrete_sequence=['#f1c40f'], height=300), use_container_width=True)
                    render_download_btn(df_rec, "top_reclamacoes")

            with c_g3:
                st.markdown("##### 💳 Mix de Pagamento")
                q_pgto = f"""SELECT forma_pgto, COUNT(*) as qtd FROM public.arq2_bilhetagem 
                             WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1 ORDER BY 2 DESC LIMIT 10"""
                df_pgto = run_query(engine, q_pgto)
                if not df_pgto.empty:
                    st.plotly_chart(px.pie(df_pgto, values='qtd', names='forma_pgto', hole=0.4, height=300), use_container_width=True)
                    render_download_btn(df_pgto, "mix_pagamento")

        with sub_t2:
            c_c1, c_c2 = st.columns([2, 1])
            with c_c1:
                st.markdown("##### 🏆 Ranking de Estações (Volume)")
                q_rank = f"""SELECT id_estacao, COUNT(*) as qtd FROM public.arq2_bilhetagem 
                             WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1 ORDER BY 2 DESC"""
                df_rank = run_query(engine, q_rank)
                if not df_rank.empty:
                    df_rank = map_stations(df_rank, 'id_estacao')
                    st.plotly_chart(px.bar(df_rank, x='qtd', y='id_estacao', orientation='h', color='qtd', color_continuous_scale='Viridis'), use_container_width=True)
                    render_download_btn(df_rank, "ranking_estacoes")
            
            with c_c2:
                st.markdown("##### 🎫 Tipos de Bilhete")
                q_bil = f"""SELECT tipo_bilhetagem, COUNT(*) as qtd FROM public.arq2_bilhetagem 
                            WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1 ORDER BY 2 DESC"""
                df_bil = run_query(engine, q_bil)
                if not df_bil.empty:
                    st.plotly_chart(px.pie(df_bil, values='qtd', names='tipo_bilhetagem', hole=0.4), use_container_width=True)
                    render_download_btn(df_bil, "tipos_bilhete")

            c_c3_1, c_c3_2 = st.columns(2)
            
            with c_c3_1:
                st.markdown("##### ☀️/🌙 Fluxo Manhã vs Tarde")
                q_turno = f"""SELECT id_estacao, CASE WHEN EXTRACT(HOUR FROM data_hora) < 12 THEN 'Manhã' ELSE 'Tarde' END as turno, COUNT(*) as qtd
                              FROM public.arq2_bilhetagem WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1, 2 ORDER BY 1, 2"""
                df_turno = run_query(engine, q_turno)
                if not df_turno.empty:
                    df_turno = map_stations(df_turno, 'id_estacao')
                    st.plotly_chart(px.bar(df_turno, x='id_estacao', y='qtd', color='turno', barmode='group'), use_container_width=True)
                    render_download_btn(df_turno, "fluxo_turnos")

            with c_c3_2:
                st.markdown("##### 💸 Formas de Pagamento (Detalhado)")
                q_pgto_det = f"""SELECT grupo_bilhetagem as forma_pgto, COUNT(*) as qtd FROM public.arq2_bilhetagem 
                             WHERE data_hora >= '{filters['dt_start_ts']}' AND data_hora <= '{filters['dt_end_ts']}' GROUP BY 1 ORDER BY 2 DESC"""
                df_pgto_det = run_query(engine, q_pgto_det)
                if not df_pgto_det.empty:
                    st.plotly_chart(px.bar(df_pgto_det, x='forma_pgto', y='qtd', color='forma_pgto'), use_container_width=True)
                    render_download_btn(df_pgto_det, "pgto_detalhado")

        with sub_t3:
            c_t1, c_t2 = st.columns([2, 1])
            with c_t1:
                st.markdown("##### 🕒 Headway Médio ")
                q_hw = f"""
                    WITH diffs AS (
                        SELECT hora_ini, LAG(hora_ini) OVER (ORDER BY hora_ini) as prev_hora
                        FROM public.arq3_viagens
                        WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' AND tipo_real = 6
                    )
                    SELECT EXTRACT(HOUR FROM hora_ini) as hora, 
                           round(AVG(EXTRACT(EPOCH FROM (hora_ini - prev_hora))/60)::numeric * 100,0) as headway
                    FROM diffs
                    WHERE prev_hora IS NOT NULL
                    GROUP BY 1 ORDER BY 1
                """
                df_hw = run_query(engine, q_hw)
                if not df_hw.empty:
                    fig_hw = px.line(
                        df_hw, 
                        x='hora', 
                        y='headway', 
                        markers=True,
                        text='headway',
                        labels={'hora': 'Hora do Dia', 'headway': 'Intervalo Médio (min)'}
                    )
                    fig_hw.update_traces(textposition="top center")
                    st.plotly_chart(fig_hw, use_container_width=True)
                    render_download_btn(df_hw, "headway_medio")
                    
                    st.caption("""
                    Intervalo de tempo médio (em minutos arredondados) entre as partidas consecutivas de dois trens.
                    - **Tempo menor:** Indica maior oferta e frequência de trens (típico de Horários de Pico).
                    - **Tempo maior:** Indica menor frequência (típico de Horários de Vale).
                    *(Nota: O cálculo considera as diferenças de horário de início de viagens comerciais).*
                    """)

            with c_t2:
                st.markdown("##### 📊 Programado x Realizado")
                q_comp = f"""
                    SELECT 'Programado' as tipo, SUM(viagens) as qtd FROM public.arq1_progplan WHERE mesref >= '{filters['dt_start']}' AND mesref <= '{filters['dt_end']}'
                    UNION ALL
                    SELECT 'Realizado' as tipo, COUNT(*) as qtd FROM public.arq3_viagens WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' and tipo_real = 6;
                """
                df_comp = run_query(engine, q_comp)
                if not df_comp.empty:
                    st.plotly_chart(px.bar(df_comp, x='tipo', y='qtd', color='tipo', text='qtd'), use_container_width=True)
                    render_download_btn(df_comp, "prog_vs_real")

            c_t3, c_t4 = st.columns(2)
            with c_t3:
                st.markdown("##### ⏱️ Distribuição de Atrasos")
                q_atr = f"""
                    SELECT atraso, COUNT(*) as qtd  
                    FROM public.arq3_viagens 
                    WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' 
                    GROUP BY atraso 
                    HAVING COUNT(*) >= 1
                    ORDER BY atraso
                """
                df_atr = run_query(engine, q_atr)
                if not df_atr.empty:
                    fig_atr = px.bar(
                        df_atr, 
                        x='atraso', 
                        y='qtd', 
                        color_discrete_sequence=['#E74C3C'],
                        text='qtd',
                        labels={'atraso': 'Peso/Nível do Atraso', 'qtd': 'Qtd de Viagens'}
                    )
                    fig_atr.update_traces(textposition='outside')
                    fig_atr.update_xaxes(type='category')
                    
                    st.plotly_chart(fig_atr, use_container_width=True)
                    render_download_btn(df_atr, "distribuicao_atrasos")
                    
                    st.caption("""
                    **Critérios de Peso (Atraso):**
                    - **0.5**: Atraso entre 2x e 3x o intervalo programado
                    - **1.0**: Atraso superior a 3x o intervalo programado
                    - **2.0**: Ocorrência de Incidente Leve
                    - **4.0**: Ocorrência de Incidente Grave
                    *(Nota: Atrasos menores que 2x o intervalo recebem peso 0.0)*
                    """)

            with c_t4:
                st.markdown("##### 🚫 Status Detalhado (Com Totais)")
                q_status = f"""SELECT viagem_interrompida as status, COUNT(*) as qtd FROM public.arq3_viagens 
                               WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' GROUP BY 1"""
                df_status = run_query(engine, q_status)
                if not df_status.empty:
                    fig_st = px.bar(df_status, x='status', y='qtd', color='status', text='qtd')
                    fig_st.update_traces(textposition='outside')
                    st.plotly_chart(fig_st, use_container_width=True)
                    render_download_btn(df_status, "status_detalhado")

            st.divider()
            st.markdown("##### 📍 Rotas Realizadas (Origem x Destino)")
            q_rotas = f"""
                SELECT origem, destino, COUNT(*) as qtd 
                FROM public.arq3_viagens 
                WHERE data >= '{filters['dt_start']}' AND data <= '{filters['dt_end']}' 
                AND ordem IS NOT NULL AND destino IS NOT NULL 
                GROUP BY origem, destino 
                HAVING COUNT(*) > 1
                ORDER BY qtd DESC
            """
            df_rotas = run_query(engine, q_rotas)
            if not df_rotas.empty:
                df_rotas['Rota'] = df_rotas['origem'] + " ➔ " + df_rotas['destino']
                
                fig_rotas = px.bar(
                    df_rotas, 
                    x='Rota', 
                    y='qtd', 
                    color='origem',
                    text='qtd',
                    labels={'Rota': 'Origem ➔ Destino', 'qtd': 'Qtd de Viagens', 'origem': 'Origem'}
                )
                fig_rotas.update_traces(textposition='outside')
                
                st.plotly_chart(fig_rotas, use_container_width=True)
                render_download_btn(df_rotas, "rotas_realizadas")

        with sub_t4:
            st.markdown("##### 🛠️ Análise de Frota")
            
            q_frota_km = f"SELECT id_trem, SUM(prod_km) as prod_km FROM public.frota_status WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1"
            df_frota_km = run_query(engine, q_frota_km)
            
            c_f1, c_f2, c_f3 = st.columns(3)
            
            with c_f1:
                st.markdown("###### 🔝 Top Operação (KM)")
                if not df_frota_km.empty:
                    df_top_op = df_frota_km.sort_values('prod_km', ascending=False).head(10)
                    df_top_op['Trem'] = "T" + df_top_op['id_trem'].astype(str)
                    st.plotly_chart(px.bar(df_top_op, x='Trem', y='prod_km', color_discrete_sequence=['#2ecc71']), use_container_width=True)
                    render_download_btn(df_top_op, "top_operacao_km")
            
            with c_f2:
                st.markdown("###### 📉 Top Indisponível (Horas)")
                q_indisp = f"SELECT id_trem, ROUND((EXTRACT(EPOCH FROM SUM(horas_manutencao)) / 3600)::numeric, 0) as horas FROM public.frota_status WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
                df_indisp = run_query(engine, q_indisp)
                if not df_indisp.empty:
                    df_indisp['Trem'] = "T" + df_indisp['id_trem'].astype(str)
                    st.plotly_chart(px.bar(df_indisp, x='Trem', y='horas', color_discrete_sequence=['#e74c3c']), use_container_width=True)
                    render_download_btn(df_indisp, "top_indisponivel_horas")

            with c_f3:
                st.markdown("###### 💤 Top Disponível s/ Uso")
                q_ocioso = f"SELECT id_trem, ROUND((EXTRACT(EPOCH FROM SUM(horas_disponivel)) / 3600)::numeric, 0) as horas_ocioso FROM public.frota_status WHERE mes_ref >= '{filters['dt_start']}' AND mes_ref <= '{filters['dt_end']}' GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
                df_ocioso = run_query(engine, q_ocioso)
                if not df_ocioso.empty:
                    df_ocioso['Trem'] = "T" + df_ocioso['id_trem'].astype(str)
                    st.plotly_chart(px.bar(df_ocioso, x='Trem', y='horas_ocioso', color_discrete_sequence=['#f39c12']), use_container_width=True)
                    render_download_btn(df_ocioso, "top_ocioso_horas")

            st.divider()
            
            c_m1, c_m2, c_m3 = st.columns(3)
            
            with c_m1:
                st.markdown("###### 🔧 Top Preventiva")
                q_prev = f"""SELECT id_tue, COUNT(*) as qtd FROM public.registros_manutencao 
                             WHERE data_abertura >= '{filters['dt_start']}' AND data_abertura <= '{filters['dt_end']}' AND tipo_manutencao = 'PREVENTIVA' 
                             GROUP BY 1 ORDER BY 2 DESC LIMIT 10"""
                df_prev = run_query(engine, q_prev)
                if not df_prev.empty:
                    df_prev['Trem'] = "T" + df_prev['id_tue'].astype(str)
                    st.plotly_chart(px.bar(df_prev, x='Trem', y='qtd', color_discrete_sequence=['#3498db']), use_container_width=True)
                    render_download_btn(df_prev, "top_preventivas")

            with c_m2:
                st.markdown("###### 🚨 Top Corretiva")
                q_corr = f"""SELECT id_tue, COUNT(*) as qtd FROM public.registros_manutencao 
                             WHERE data_abertura >= '{filters['dt_start']}' AND data_abertura <= '{filters['dt_end']}' AND tipo_manutencao = 'CORRETIVA' 
                             GROUP BY 1 ORDER BY 2 DESC LIMIT 10"""
                df_corr = run_query(engine, q_corr)
                if not df_corr.empty:
                    df_corr['Trem'] = "T" + df_corr['id_tue'].astype(str)
                    st.plotly_chart(px.bar(df_corr, x='Trem', y='qtd', color_discrete_sequence=['#9b59b6']), use_container_width=True)
                    render_download_btn(df_corr, "top_corretivas")

            with c_m3:
                st.markdown("###### 📊 Tipos de Manutenção")
                q_tipo_m = f"""SELECT tipo_manutencao, COUNT(*) as qtd FROM public.registros_manutencao 
                               WHERE data_abertura >= '{filters['dt_start']}' AND data_abertura <= '{filters['dt_end']}' GROUP BY 1"""
                df_tipo_m = run_query(engine, q_tipo_m)
                if not df_tipo_m.empty:
                    st.plotly_chart(px.pie(df_tipo_m, values='qtd', names='tipo_manutencao'), use_container_width=True)
                    render_download_btn(df_tipo_m, "tipos_manutencao")

    else:
        st.error("Banco de dados desconectado.")

elif menu == "📈 Indicadores (CMD)":
    filters = get_date_filter_ui("cmd")
    st.subheader(f"Painel de Indicadores (CMD) - {filters['mes_nome']}/{filters['ano']}")
    
    if db_loader:
        ico = 0.985; tmp = 1.010; ial = 0.995; iol = 0.980
        mro = 1.20; dtt = 0.998; est = 0.99; lin = 0.99; irg = 0.95; isp = 0.90

        ido = (0.1 * tmp) + (0.3 * ico) + (0.3 * ial) + (0.3 * iol)
        idm = (0.25 * mro) + (0.25 * dtt) + (0.25 * est) + (0.25 * lin)
        ids = (0.5 * irg) + (0.5 * isp)
        cmd = (0.4 * ido) + (0.4 * idm) + (0.2 * ids)

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
            if st.button("📈 Evolução ", key="btn_isp"): st.session_state['active_cmd_chart'] = 'isp'

        st.divider()

        active_cmd_chart = st.session_state.get('active_cmd_chart')
        if active_cmd_chart:
            metas_cmd = {
                'ico': 0.980, 'tmp': 1.010, 'ial': 0.950, 'iol': 0.950,
                'mro': 1.0, 'dtt': 0.995, 'est': 0.98, 'lin': 0.99,
                'irg': 0.90, 'isp': 0.85, 'cmd': 1.000
            }
            
            base_vals = {
                'ico': ico, 'tmp': tmp, 'ial': ial, 'iol': iol,
                'mro': mro, 'dtt': dtt, 'est': est, 'lin': lin,
                'irg': irg, 'isp': isp, 'cmd': cmd
            }
            
            base_val = base_vals.get(active_cmd_chart, 1.0)
            meta_val = metas_cmd.get(active_cmd_chart, 1.0)
            
            dates = pd.date_range(start=filters['dt_start'], end=filters['dt_end'])
            valores = [base_val * random.uniform(0.97, 1.03) for _ in dates]
            df_cmd_evo = pd.DataFrame({'Data': dates, 'Valor': valores})
            
            fig_cmd = px.line(
                df_cmd_evo, x='Data', y='Valor', 
                title=f"Evolução Diária - Indicador {active_cmd_chart.upper()}",
                markers=True
            )
            
            fig_cmd.add_hline(y=meta_val, line_dash="dash", line_color="red", annotation_text=f"Meta ({meta_val})")
            st.plotly_chart(fig_cmd, use_container_width=True)
            render_download_btn(df_cmd_evo, "evolucao_cmd")

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
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("📈 Ver Evolução Geral do CMD", key="btn_cmd", use_container_width=True): 
                    st.session_state['active_cmd_chart'] = 'cmd'
                    st.rerun()

elif menu == "🏛️ Metrô em Números":
    filters = get_date_filter_ui("numeros")
    st.markdown("### 🏛️ Painel Metrô da RMBH em Números")
    st.markdown("*Visão consolidada de transparência e indicadores estratégicos com comparativo ao Ano Anterior (YoY).*")
    
    if db_loader:
        engine = db_loader.get_engine()
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        # Datas do Ano Atual selecionado
        ano_atual = filters['ano']
        ano_start = f"{ano_atual}-01-01"
        ano_end = f"{ano_atual}-12-31"
        
        # Datas do Ano Anterior
        ano_ant = ano_atual - 1
        ano_ant_start = f"{ano_ant}-01-01"
        ano_ant_end = f"{ano_ant}-12-31"

        # Função auxiliar para calcular a variação percentual
        def calc_delta(atual, anterior):
            if anterior == 0 and atual > 0:
                return "100%"
            elif anterior == 0 and atual == 0:
                return "0%"
            else:
                var = ((atual - anterior) / anterior) * 100
                return f"{var:.1f}% comparado ao Ano Anterior"

        # --- KPI 1: Média Mensal de Passageiros ---
        q_media_mes = f"""
            WITH mensal AS (
                SELECT DATE_TRUNC('month', data_hora) as mes, COUNT(*) as qtd 
                FROM public.arq2_bilhetagem 
                WHERE data_hora >= '{ano_start} 00:00:00' AND data_hora <= '{ano_end} 23:59:59' 
                GROUP BY 1
            )
            SELECT AVG(qtd) FROM mensal
        """
        df_med_mes = run_query(engine, q_media_mes)
        val_med_mes = df_med_mes.iloc[0,0] if not df_med_mes.empty and df_med_mes.iloc[0,0] else 0

        q_media_mes_ant = f"""
            WITH mensal AS (
                SELECT DATE_TRUNC('month', data_hora) as mes, COUNT(*) as qtd 
                FROM public.arq2_bilhetagem 
                WHERE data_hora >= '{ano_ant_start} 00:00:00' AND data_hora <= '{ano_ant_end} 23:59:59' 
                GROUP BY 1
            )
            SELECT AVG(qtd) FROM mensal
        """
        df_med_mes_ant = run_query(engine, q_media_mes_ant)
        val_med_mes_ant = df_med_mes_ant.iloc[0,0] if not df_med_mes_ant.empty and df_med_mes_ant.iloc[0,0] else 0
        
        col_kpi1.metric("Média Passageiros/Mês", f"{val_med_mes:,.0f}".replace(",", "."), delta=calc_delta(val_med_mes, val_med_mes_ant))

        # --- KPI 2: Manutenções Corretivas ---
        q_manut_corr = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_start}' AND data_abertura <= '{ano_end}' AND tipo_manutencao = 'CORRETIVA'"
        val_corr_ano = run_query(engine, q_manut_corr).iloc[0,0] if not run_query(engine, q_manut_corr).empty else 0

        q_manut_corr_ant = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_ant_start}' AND data_abertura <= '{ano_ant_end}' AND tipo_manutencao = 'CORRETIVA'"
        val_corr_ano_ant = run_query(engine, q_manut_corr_ant).iloc[0,0] if not run_query(engine, q_manut_corr_ant).empty else 0
        
        # inverse: Aumento de corretiva é ruim (seta vermelha)
        col_kpi2.metric("Manut. Corretivas (Ano)", f"{val_corr_ano:,.0f}".replace(",", "."), delta=calc_delta(val_corr_ano, val_corr_ano_ant), delta_color="inverse")

        # --- KPI 3: Manutenções Preventivas ---
        q_manut_prev = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_start}' AND data_abertura <= '{ano_end}' AND tipo_manutencao = 'PREVENTIVA'"
        val_prev_ano = run_query(engine, q_manut_prev).iloc[0,0] if not run_query(engine, q_manut_prev).empty else 0

        q_manut_prev_ant = f"SELECT COUNT(*) FROM public.registros_manutencao WHERE data_abertura >= '{ano_ant_start}' AND data_abertura <= '{ano_ant_end}' AND tipo_manutencao = 'PREVENTIVA'"
        val_prev_ano_ant = run_query(engine, q_manut_prev_ant).iloc[0,0] if not run_query(engine, q_manut_prev_ant).empty else 0
        
        col_kpi3.metric("Manut. Preventivas (Ano)", f"{val_prev_ano:,.0f}".replace(",", "."), delta=calc_delta(val_prev_ano, val_prev_ano_ant))

        # --- KPI 4: Viagens Canceladas ---
        q_canc = f"SELECT COUNT(*) FROM public.arq3_viagens WHERE data >= '{ano_start}' AND data <= '{ano_end}' AND tipo_real in (9,10)"
        val_canc = run_query(engine, q_canc).iloc[0,0] if not run_query(engine, q_canc).empty else 0

        q_canc_ant = f"SELECT COUNT(*) FROM public.arq3_viagens WHERE data >= '{ano_ant_start}' AND data <= '{ano_ant_end}' AND tipo_real in (9,10)"
        val_canc_ant = run_query(engine, q_canc_ant).iloc[0,0] if not run_query(engine, q_canc_ant).empty else 0

        # inverse: Aumento de cancelamentos é ruim (seta vermelha)
        col_kpi4.metric("Viagens Canceladas (Ano)", f"{val_canc:,.0f}".replace(",", "."), delta=calc_delta(val_canc, val_canc_ant), delta_color="inverse")

        st.divider()

        c_mn1, c_mn2 = st.columns(2)

        with c_mn1:
            st.markdown(f"##### 💳 Perfil de Bilhetagem ({ano_atual})")
            q_perfil_pgto = f"""SELECT tipo_bilhetagem, COUNT(*) as qtd FROM public.arq2_bilhetagem 
                                WHERE data_hora >= '{ano_start} 00:00:00' AND data_hora <= '{ano_end} 23:59:59' 
                                GROUP BY 1 ORDER BY 2 DESC"""
            df_perfil = run_query(engine, q_perfil_pgto)
            if not df_perfil.empty:
                st.plotly_chart(px.pie(df_perfil, values='qtd', names='tipo_bilhetagem', hole=0.5), use_container_width=True)
                render_download_btn(df_perfil, "perfil_bilhetagem")

        with c_mn2:
            st.markdown(f"##### 🚉 Comparativo: Passageiros Mês/Estação ({ano_ant} vs {ano_atual})")
            # Query ajustada para buscar os dois anos e permitir barras agrupadas
            q_est_media_comp = f"""
                SELECT id_estacao, EXTRACT(YEAR FROM data_hora)::varchar as ano_ref, 
                       ROUND(COALESCE(COUNT(*)::float / NULLIF(COUNT(DISTINCT EXTRACT(MONTH FROM data_hora)), 0), 0)) as media_mensal
                FROM public.arq2_bilhetagem
                WHERE data_hora >= '{ano_ant_start} 00:00:00' AND data_hora <= '{ano_end} 23:59:59'
                GROUP BY 1, 2 ORDER BY 1, 2
            """
            df_est_med_comp = run_query(engine, q_est_media_comp)
            if not df_est_med_comp.empty:
                df_est_med_comp = map_stations(df_est_med_comp, 'id_estacao')
                fig_comp = px.bar(df_est_med_comp, x='id_estacao', y='media_mensal', color='ano_ref', barmode='group',
                                  labels={'id_estacao': 'Estação', 'media_mensal': 'Média Mensal', 'ano_ref': 'Ano'})
                fig_comp.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
                st.plotly_chart(fig_comp, use_container_width=True)
                render_download_btn(df_est_med_comp, "comparativo_estacoes")
                
        st.divider()

        st.markdown(f"##### 🎟️ Consolidado de Bilhetagem por Estação e Tipo de Bilhete ({ano_atual})")
        
        q_tipo_est = f"""
            SELECT ap.nome, ap.id, tipo_bilhetagem, COUNT(*) as qtd  
            FROM public.arq2_bilhetagem ab 
            INNER JOIN public.arq7_paradas ap ON ab.id_estacao = ap.id
            WHERE tipo_bilhetagem IS NOT NULL  
            AND data_hora BETWEEN '{ano_start} 00:00:00' AND '{ano_end} 23:59:59' 
            GROUP BY ap.nome, ap.id, tipo_bilhetagem  
            HAVING COUNT(*) > 1 
            ORDER BY ap.id, qtd DESC
        """
        df_tipo_est = run_query(engine, q_tipo_est)
        
        if not df_tipo_est.empty:
            fig_tipo_est = px.bar(
                df_tipo_est, x='nome', y='qtd', color='tipo_bilhetagem', barmode='stack',
                labels={'nome': '', 'qtd': 'Quantidade de Validações', 'tipo_bilhetagem': 'Tipo de Bilhete'}
            )
            fig_tipo_est.update_xaxes(tickangle=-45)
            fig_tipo_est.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
            st.plotly_chart(fig_tipo_est, use_container_width=True)
            render_download_btn(df_tipo_est, "consolidado_tipo_bilhete")
            
        st.divider()

        st.markdown(f"##### 🎟️ Volume de Bilhetagem por Estação e Grupo de Bilhete ({ano_atual})")
        
        q_grupo_est = f"""
            SELECT ap.nome, ap.id, grupo_bilhetagem, COUNT(*) as qtd  
            FROM public.arq2_bilhetagem ab 
            INNER JOIN public.arq7_paradas ap ON ab.id_estacao = ap.id
            WHERE grupo_bilhetagem IS NOT NULL  
            AND data_hora BETWEEN '{ano_start} 00:00:00' AND '{ano_end} 23:59:59' 
            GROUP BY ap.nome, ap.id, grupo_bilhetagem  
            HAVING COUNT(*) > 1 
            ORDER BY ap.id, qtd DESC
        """
        df_grupo_est = run_query(engine, q_grupo_est)
        
        if not df_grupo_est.empty:
            fig_grupo_est = px.bar(
                df_grupo_est, x='nome', y='qtd', color='grupo_bilhetagem', barmode='stack',
                labels={'nome': '', 'qtd': 'Quantidade de Validações', 'grupo_bilhetagem': 'Grupo de Bilhete'}
            )
            fig_grupo_est.update_xaxes(tickangle=-45)
            fig_grupo_est.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
            st.plotly_chart(fig_grupo_est, use_container_width=True)
            render_download_btn(df_grupo_est, "consolidado_grupo_bilhete")
            
        st.divider()

    else:
        st.error("Conexão com o banco de dados necessária.")

# --- NOVA ABA: INTELIGÊNCIA ARTIFICIAL (ML) ---
elif menu == "🤖 Inteligência Artificial (ML)":
    st.subheader("🤖 Central de Inteligência Artificial (Modelos Preditivos)")
    st.markdown("""
    *Esta área contém modelos avançados de Machine Learning para auxílio à tomada de decisão. 
    Os painéis abaixo estão operando com **dados simulados (mockups)** aguardando a integração com a API final dos modelos treinados.*
    """)
    st.divider()

    # Expandido para acomodar os novos modelos solicitados
    ml_tab1, ml_tab2, ml_tab3, ml_tab4, ml_tab5, ml_tab6, ml_tab7 = st.tabs([
        "📊 1. Previsão de Demanda", 
        "🛠️ 2. Probabilidade de Falha", 
        "⏱️ 3. Previsão de Atrasos", 
        "🚨 4. Detecção Anomalias",
        "⚡ 5. Consumo de Energia",
        "🕵️ 6. Prevenção a Fraudes",
        "⚠️ 7. Risco de Ocorrências"
    ])

    with ml_tab1:
        st.markdown("#### 📈 Previsão de Demanda de Passageiros (Próximos 7 Dias)")
        st.caption("Algoritmo sugerido: **Prophet** ou **XGBoost**. Útil para dimensionamento de equipe nas estações e definição de headway.")
        
        hoje = datetime.now().date()
        datas_historico = [hoje - timedelta(days=i) for i in range(14, 0, -1)]
        datas_futuro = [hoje + timedelta(days=i) for i in range(1, 8)]
        
        def gerar_pax(datas):
            vals = []
            for d in datas:
                base = random.randint(140000, 160000) if d.weekday() < 5 else random.randint(40000, 60000)
                vals.append(base)
            return vals
        
        hist_pax = gerar_pax(datas_historico)
        fut_pax = gerar_pax(datas_futuro)
        
        fut_upper = [int(v * 1.08) for v in fut_pax]
        fut_lower = [int(v * 0.92) for v in fut_pax]

        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=datas_historico, y=hist_pax, mode='lines+markers', name='Demanda Real', line=dict(color='#3498db', width=3)))
        fig_ts.add_trace(go.Scatter(x=datas_futuro, y=fut_pax, mode='lines+markers', name='Previsão (ML)', line=dict(color='#e67e22', width=3, dash='dash')))
        fig_ts.add_trace(go.Scatter(x=datas_futuro, y=fut_upper, mode='lines', line=dict(width=0), showlegend=False))
        fig_ts.add_trace(go.Scatter(x=datas_futuro, y=fut_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(230, 126, 34, 0.2)', name='Intervalo de Confiança'))
        
        fig_ts.update_layout(title="Volume Total de Passageiros Estimado", xaxis_title="Data", yaxis_title="Passageiros / Dia", hovermode="x unified")
        st.plotly_chart(fig_ts, use_container_width=True)

    with ml_tab2:
        st.markdown("#### 🛠️ Previsão de Falha Crítica em TUEs (Próximos 15 dias)")
        st.caption("Algoritmo sugerido: **Random Forest** ou **Análise de Sobrevivência**. Auxilia o CMD (Indicador MRO) puxando trens para manutenção preventiva antes da falha.")
        
        trens_mock = [f"TUE {str(i).zfill(3)}" for i in range(1, 16)]
        riscos = [random.randint(5, 95) for _ in trens_mock]
        df_frota_ml = pd.DataFrame({'Trem': trens_mock, 'Probabilidade_Falha': riscos})
        df_frota_ml = df_frota_ml.sort_values(by='Probabilidade_Falha', ascending=False).reset_index(drop=True)
        
        def color_risk(val):
            if val > 75: return '#e74c3c'
            elif val > 40: return '#f1c40f'
            else: return '#2ecc71'
            
        df_frota_ml['Cor'] = df_frota_ml['Probabilidade_Falha'].apply(color_risk)
        df_frota_ml['Status Recomendado'] = df_frota_ml['Probabilidade_Falha'].apply(lambda x: 'Manutenção Imediata' if x > 75 else ('Atenção' if x > 40 else 'Operação Normal'))
        
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            fig_frota = px.bar(df_frota_ml.head(10), x='Probabilidade_Falha', y='Trem', orientation='h', color='Cor', color_discrete_map='identity', text='Probabilidade_Falha')
            fig_frota.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_frota.update_layout(title="Top 10 Trens com Maior Risco", xaxis_title="Probabilidade de Falha (%)", yaxis_title="")
            st.plotly_chart(fig_frota, use_container_width=True)
            
        with col_f2:
            st.markdown("##### 📋 Ações Sugeridas pelo Modelo")
            for _, row in df_frota_ml.head(4).iterrows():
                cor_box = "rgba(231, 76, 60, 0.2)" if row['Cor'] == '#e74c3c' else ("rgba(241, 196, 15, 0.2)" if row['Cor'] == '#f1c40f' else "rgba(46, 204, 113, 0.2)")
                st.markdown(f"""
                <div style="background-color: {cor_box}; border-left: 5px solid {row['Cor']}; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                    <strong>{row['Trem']}</strong> - Risco: {row['Probabilidade_Falha']}%<br>
                    <span style="font-size: 12px; color: #ccc;">Ação: {row['Status Recomendado']}</span>
                </div>
                """, unsafe_allow_html=True)

    with ml_tab3:
        st.markdown("#### ⏱️ Mapa de Risco de Atrasos e Gargalos (Hoje)")
        st.caption("Algoritmo sugerido: **Regressão Logística** ou **CatBoost**. Prevê a probabilidade de um headway estourar ou viagens atrasarem com base na hora e dia da semana.")
        
        horas = [f"{str(h).zfill(2)}:00" for h in range(5, 24)]
        estacoes = ['Eldorado', 'Calafate', 'Lagoinha', 'Central', 'Minas Shopping', 'Vilarinho']
        
        dados_heatmap = []
        for e in estacoes:
            linha_risco = []
            for h in range(5, 24):
                if h in [7, 8, 17, 18]: base_r = random.uniform(0.6, 0.95)
                elif h in [6, 9, 16, 19]: base_r = random.uniform(0.3, 0.6)
                else: base_r = random.uniform(0.05, 0.2)
                linha_risco.append(base_r)
            dados_heatmap.append(linha_risco)
            
        fig_hm = px.imshow(dados_heatmap, x=horas, y=estacoes, color_continuous_scale='RdYlGn_r', aspect="auto")
        fig_hm.update_layout(title="Probabilidade de Atraso por Estação e Horário", coloraxis_colorbar=dict(title="Risco (0 a 1)"))
        st.plotly_chart(fig_hm, use_container_width=True)

    with ml_tab4:
        st.markdown("#### 🚨 Sistema de Detecção de Anomalias (Tempo Real)")
        st.caption("Algoritmo sugerido: **Isolation Forest**. Identifica picos atípicos de embarque ou validador travado automaticamente, gerando alertas para o CCO.")
        
        horas_dia = [f"{str(h).zfill(2)}:00" for h in range(0, 24)]
        pax_normal = [random.randint(10, 50) if (h < 5 or h > 22) else random.randint(300, 800) for h in range(24)]
        
        hora_anomalia = 14
        pax_normal[hora_anomalia] = 3500 
        
        fig_anom = go.Figure()
        fig_anom.add_trace(go.Scatter(x=horas_dia, y=pax_normal, mode='lines', name='Fluxo Estação (Horto)', line=dict(color='#9b59b6', width=2)))
        
        fig_anom.add_trace(go.Scatter(
            x=[horas_dia[hora_anomalia]], 
            y=[pax_normal[hora_anomalia]], 
            mode='markers+text', 
            marker=dict(color='red', size=15, symbol='star'),
            text=['⚠️ Alerta de Anomalia Disparado'],
            textposition='top center',
            name='Anomalia Detectada'
        ))
        
        fig_anom.update_layout(title="Monitoramento de Fluxo - Estação Horto (Últimas 24h)", xaxis_title="Hora do Dia", yaxis_title="Validações / Hora")
        st.plotly_chart(fig_anom, use_container_width=True)
        
        st.warning("ALERTA DO MODELO: Fluxo atípico detectado às 14:00 na Estação Horto. Variação de +430% em relação à média histórica para este dia e horário. Sugestão: Enviar trem reserva ou reforçar segurança no local.")

    with ml_tab5:
        st.markdown("#### ⚡ Previsão de Consumo de Energia e Eficiência")
        st.caption("Algoritmo sugerido: **LSTM** ou **XGBoost Regressor**. Baseado na Tabela de Energia (Tab 12) e Quadro de Viagens. Otimiza o planejamento energético.")
        
        meses_energia = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
        consumo_real = [random.uniform(1.2, 1.5) * 1000000 for _ in range(3)]
        consumo_previsto = consumo_real + [random.uniform(1.2, 1.5) * 1000000 for _ in range(3)]
        consumo_otimizado = [v * 0.88 for v in consumo_previsto] # Simula economia com IA
        
        fig_energia = go.Figure()
        fig_energia.add_trace(go.Bar(x=meses_energia[:3], y=consumo_real, name='Consumo Real (KWh)', marker_color='#34495e'))
        fig_energia.add_trace(go.Bar(x=meses_energia[3:], y=consumo_previsto[3:], name='Previsão Base (KWh)', marker_color='#7f8c8d', opacity=0.6))
        fig_energia.add_trace(go.Scatter(x=meses_energia, y=consumo_otimizado, mode='lines+markers', name='Meta IA Otimizada (KWh)', line=dict(color='#2ecc71', width=3, dash='dot')))
        
        fig_energia.update_layout(title="Projeção de Consumo Energético vs Otimização sugerida pela IA", yaxis_title="Consumo (KWh)", barmode='group')
        st.plotly_chart(fig_energia, use_container_width=True)
        st.success("💡 Insight do Modelo: Ajustar a aceleração nos trechos Lagoinha-Central pode gerar uma economia projetada de 12% na fatura de energia do próximo mês.")

    with ml_tab6:
        st.markdown("#### 🕵️ Clusterização de Perfis e Prevenção a Fraudes")
        st.caption("Algoritmo sugerido: **K-Means** ou **DBSCAN**. Analisa a Bilhetagem (Arq2) buscando evasão de receita, compartilhamento ilegal de cartões ou falhas de bloqueio.")
        
        # Simulando uma distribuição de scatter plot para anomalias de bilhetes
        n_pontos = 200
        uso_normal_x = np.random.normal(2, 0.5, int(n_pontos*0.85)) # Uso diario medio
        uso_normal_y = np.random.normal(2, 0.5, int(n_pontos*0.85)) # Estacoes distintas medio
        
        uso_fraude_x = np.random.normal(8, 2, int(n_pontos*0.15)) # Muito uso diario
        uso_fraude_y = np.random.normal(1.5, 0.3, int(n_pontos*0.15)) # Mesma estação (ex: vendendo passagem na catraca)
        
        df_clusters = pd.DataFrame({
            'Validações_Diárias': np.concatenate([uso_normal_x, uso_fraude_x]),
            'Estações_Distintas': np.concatenate([uso_normal_y, uso_fraude_y]),
            'Perfil': ['Usuário Padrão']*int(n_pontos*0.85) + ['Comportamento Suspeito (Evasão/Venda)']*int(n_pontos*0.15)
        })
        
        fig_cluster = px.scatter(df_clusters, x='Validações_Diárias', y='Estações_Distintas', color='Perfil', 
                                 color_discrete_map={'Usuário Padrão': '#3498db', 'Comportamento Suspeito (Evasão/Venda)': '#e74c3c'})
        fig_cluster.update_layout(title="Mapeamento de Comportamento de Cartões (Gratuidade/Vale Transporte)")
        st.plotly_chart(fig_cluster, use_container_width=True)

    with ml_tab7:
        st.markdown("#### ⚠️ Mapeamento Preditivo de Risco e Segurança")
        st.caption("Algoritmo sugerido: **Naive Bayes** ou **Redes Neurais (Classificação)**. Analisa histórico de Ocorrências (Arq4) cruzado com dia e hora para focar policiamento.")
        
        col_r1, col_r2 = st.columns([1, 2])
        
        with col_r1:
            estacao_risco = st.selectbox("Selecione a Estação para Análise de Risco Predito:", ["Central", "Vilarinho", "Eldorado", "Lagoinha", "São Gabriel"])
            st.info(f"O modelo calcula a probabilidade do tipo de evento que ocorrerá hoje na estação **{estacao_risco}** baseando-se em eventos passados e fatores externos.")
            
        with col_r2:
            # Simula riscos diferentes baseados na estação selecionada
            if estacao_risco == "Central":
                riscos_cat = [80, 40, 20, 60, 50]
            elif estacao_risco == "Vilarinho":
                riscos_cat = [30, 85, 40, 30, 20]
            else:
                riscos_cat = [random.randint(10, 90) for _ in range(5)]
                
            categorias_risco = ['Furto/Roubo', 'Vandalismo TUE', 'Acesso Indevido à Via', 'Falha Sistêmica (Catraca)', 'Mal Súbito']
            
            df_radar = pd.DataFrame(dict(Risco=riscos_cat, Categoria=categorias_risco))
            fig_radar = px.line_polar(df_radar, r='Risco', theta='Categoria', line_close=True, markers=True, 
                                      color_discrete_sequence=['#e67e22'])
            fig_radar.update_traces(fill='toself')
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Índice Preditivo de Ocorrências (0 a 100)")
            st.plotly_chart(fig_radar, use_container_width=True)


# --- NOVA ABA DE CONFIGURAÇÃO DE PERMISSÕES ---
elif menu == "⚙️ Configurações de Acesso":
    st.subheader("⚙️ Configurações de Permissão (Nível de Usuário)")
    
    if st.session_state['current_role'] != 'admin':
        st.error("Acesso negado. Apenas usuários com nível 'admin' podem acessar esta página.")
    else:
        st.markdown("Selecione quais abas estarão visíveis no menu lateral para cada nível de usuário. Após salvar, as novas regras entram em vigor imediatamente para toda a sessão.")
        
        roles = list(st.session_state['permissions'].keys())
        
        with st.form("permissions_form"):
            new_permissions = {}
            for role in roles:
                st.markdown(f"**Nível:** `{role.upper()}`")
                
                selected_tabs = st.multiselect(
                    f"Abas permitidas para o nível {role}:",
                    ALL_TABS,
                    default=st.session_state['permissions'].get(role, []),
                    key=f"ms_{role}"
                )
                new_permissions[role] = selected_tabs
                st.divider()
                
            submit_btn = st.form_submit_button("💾 Salvar Permissões")
            
            if submit_btn:
                st.session_state['permissions'] = new_permissions
                st.success("Permissões atualizadas com sucesso! A navegação lateral já reflete as novas regras.")
                st.rerun()

# --- FIM: NOVA ABA DE CONFIGURAÇÃO DE PERMISSÕES ---