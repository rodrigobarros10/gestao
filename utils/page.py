import streamlit as st

from components.ui_elements import load_custom_css
from utils.helpers import get_base64_of_bin_file


def setup_page(*, layout="wide", page_title=None, page_icon=None, img_path="fundo_metro.jpeg"):
    st.set_page_config(layout=layout, page_title=page_title, page_icon=page_icon)
    img_base64 = get_base64_of_bin_file(img_path)
    load_custom_css(img_base64)
    return img_base64


def require_login(*, redirect_page="app.py"):
    if not st.session_state.get("logged_in", False):
        st.switch_page(redirect_page)


def require_access(*, page_keys, redirect_page="app.py", show_error=False, error_message="Acesso Negado."):
    require_login(redirect_page=redirect_page)
    role = st.session_state.get("current_role")
    permissions = st.session_state.get("permissions", {})
    allowed = permissions.get(role, [])
    if not any(key in allowed for key in page_keys):
        if show_error:
            st.error(error_message)
        st.stop()


def require_admin(*, redirect_page="app.py", error_message="Acesso restrito a Administradores."):
    require_login(redirect_page=redirect_page)
    if st.session_state.get("current_role") != "admin":
        st.error(error_message)
        st.stop()
