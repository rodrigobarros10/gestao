import streamlit as st
import pandas as pd

from config.constants import ALL_TABS
from services.auth_service import AuthService
from utils.page import require_admin, setup_page

setup_page(layout="wide", page_title="Configurações", page_icon="⚙️")
require_admin()

# 2. BOTÃO DE VOLTAR NA PÁGINA PRINCIPAL
# Usamos colunas para que o botão não ocupe a largura inteira da tela
col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    if st.button("⬅️ Voltar ao Início", use_container_width=True):
        st.switch_page("app.py")

st.title("⚙️ Configurações de Sistema")

tab_perm, tab_users = st.tabs(["🛡️ Permissões", "👥 Gestão de Usuários"])

with tab_perm:
    st.subheader("Configurações de Permissão (Nível de Usuário)")
    with st.form("permissions_form"):
        new_permissions = {}
        for role in list(st.session_state['permissions'].keys()):
            st.markdown(f"**Nível:** `{role.upper()}`")
            selected_tabs = st.multiselect(
                f"Abas permitidas para {role}:", ALL_TABS,
                default=st.session_state['permissions'].get(role, []), key=f"ms_{role}"
            )
            new_permissions[role] = selected_tabs
            st.divider()
        if st.form_submit_button("💾 Salvar Permissões"):
            st.session_state['permissions'] = new_permissions
            st.success("Permissões atualizadas!")
            st.rerun()

with tab_users:
    st.subheader("Criação de Novos Usuários")
    auth_service = AuthService(st.session_state['db_loader'])
    
    with st.form("form_create_user"):
        c1, c2 = st.columns(2)
        with c1:
            new_user = st.text_input("Username")
            new_pass = st.text_input("Senha", type="password")
        with c2:
            new_role = st.selectbox("Nível", ["admin", "operador", "visualizador"])
            conf_pass = st.text_input("Confirme a Senha", type="password")
            
        if st.form_submit_button("Criar Usuário"):
            if new_pass != conf_pass: st.error("Senhas não coincidem.")
            elif not new_user: st.error("Preencha o usuário.")
            else:
                success, msg = auth_service.create_user(new_user, new_pass, new_role)
                if success: st.success(msg)
                else: st.error(msg)
                
    st.divider()
    st.subheader("Usuários Cadastrados")
    try:
        df_users = pd.read_sql("SELECT id, username, role, created_at FROM public.usuarios", st.session_state['db_loader'].get_engine())
        st.dataframe(df_users, hide_index=True, use_container_width=True)
    except Exception as e:
        st.warning("Tabela de usuários vazia ou não criada. Rode database/setup_db.py")
