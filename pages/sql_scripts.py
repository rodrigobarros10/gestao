import streamlit as st
from config.constants import INSERTS_PREDEFINIDOS
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

if not st.session_state.get('logged_in', False):
    st.switch_page("app.py") # ⚠️ Substitua "app.py" pelo nome exato do seu arquivo inicial

# 2. BOTÃO DE VOLTAR NA PÁGINA PRINCIPAL
# Usamos colunas para que o botão não ocupe a largura inteira da tela
col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True):
        st.switch_page("app.py")

if not st.session_state.get('logged_in') or "sql_scripts" not in st.session_state['permissions'].get(st.session_state['current_role'], []):
    st.error("Acesso Negado.")
    st.stop()

st.title("💾 Execução de Scripts")
db_loader = st.session_state['db_loader']

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
custom_sql = st.text_area("SQL Manual")
if st.button("Executar SQL Manual") and db_loader and custom_sql:
    db_loader.execute_custom_insert(custom_sql)
    st.success("Comando enviado!")