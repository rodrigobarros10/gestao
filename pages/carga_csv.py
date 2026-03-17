import streamlit as st

from config.constants import TABLES_CONFIG
from services.etl_service import ETLService
from utils.page import require_access, setup_page

setup_page(layout="wide", page_title="Carga CSV", page_icon="📂")
require_access(page_keys=["carga_csv"], show_error=True)

# 2. BOTÃO DE VOLTAR NA PÁGINA PRINCIPAL
# Usamos colunas para que o botão não ocupe a largura inteira da tela
col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True):
        st.switch_page("app.py")

st.title("📂 Carga CSV")
uploaded_file = st.file_uploader("Arquivo CSV", type=['csv'])
tabela_destino = st.selectbox("Tabela Destino", list(TABLES_CONFIG.keys()))

if st.button("Carregar CSV") and uploaded_file and st.session_state.get('db_loader'):
    etl = ETLService(st.session_state['db_loader'])
    with st.spinner('Carregando dados...'):
        success, msg = etl.process_and_load_csv(uploaded_file, tabela_destino, TABLES_CONFIG[tabela_destino])
    if success: st.success(msg)
    else: st.error(msg)
