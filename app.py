import streamlit as st
import plotly.io as pio
from config.settings import DEFAULT_DB_CONFIG
from config.constants import ALL_TABS
from database.connection import PostgreSQLDataLoader
from services.auth_service import AuthService
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

# --- INITIAL SETUP ---
st.set_page_config(page_title="GESTÃO METRO BH", layout="wide", page_icon="🚇")
pio.templates.default = "plotly_dark"
img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

# --- SESSION STATE INITIALIZATION ---
if 'permissions' not in st.session_state:
    st.session_state['permissions'] = {
        'admin': ALL_TABS,
        'operador': ["carga_csv", "operacao", "indicadores", "ia_ml"],
        'visualizador': ["numeros"]
    }
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'current_user' not in st.session_state: st.session_state['current_user'] = None
if 'current_role' not in st.session_state: st.session_state['current_role'] = None

# --- DATABASE CONNECTION ---
if 'db_config' not in st.session_state:
    st.session_state['db_config'] = DEFAULT_DB_CONFIG
    
if 'db_loader' not in st.session_state:
    loader = PostgreSQLDataLoader(st.session_state['db_config'])
    if loader.test_connection()[0]:
        st.session_state['db_loader'] = loader
        st.session_state['connected'] = True
    else:
        st.session_state['connected'] = False



# --- LOGIN SCREEN ---
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Título personalizado em cinza escuro
        st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>🚇 DATA TREM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #FFFFFF;'>Faça login para acessar o sistema</p>", unsafe_allow_html=True)
        
        if not st.session_state.get('connected'):
            st.error("🔴 Banco de dados offline. Verifique as credenciais no .env")
        else:
            with st.form("login_form"):
                username = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar")

                if submit:
                    auth = AuthService(st.session_state['db_loader'])
                    user = auth.authenticate_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['current_user'] = user['username']
                        st.session_state['current_role'] = user['role']
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
    st.stop()

# --- SIDEBAR & LOGOUT (Appears on all pages) ---
with st.sidebar:
    st.markdown(f"👤 **Logado como:** `{st.session_state['current_user']}`")
    st.markdown(f"🛡️ **Nível:** `{st.session_state['current_role']}`")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['current_role'] = None
        st.rerun()
# --- HOMEPAGE / DASHBOARD CARDS (Visão Pós-Login) ---
st.markdown("""
    <h1 style='color: #4F4F4F; margin-bottom: 0px;'>🚇 Data Trem</h1>
    <h4 style='color: #777777; margin-top: 0px; font-weight: normal;'>📍 Painel de Controle Operacional da Concessão Metro BH</h4>
    <hr style='border: 1px solid #E0E0E0;'>
""", unsafe_allow_html=True)

st.markdown("<p style='color: #5A5A5A; font-size: 16px;'>Selecione um dos módulos abaixo para acessar:</p>", unsafe_allow_html=True)


# 1. Recupera as páginas permitidas para o usuário logado
allowed_pages = st.session_state['permissions'].get(st.session_state['current_role'], [])

# 2. Dicionário de Mapeamento: Arquivo -> Ícone de Metrô + Nome Amigável
PAGE_DISPLAY_NAMES = {
    "carga_csv": "🚉 Carga de Dados",
    "configuracoes": "🛠️ Configurações",
    "sql_scripts": "🛤️ Scripts SQL",
    "operacao": "🕹️ Centro de Controle",
    "indicadores": "🚥 Indicadores",
    "numeros": "🎫  Números",
    "ia_ml": "⚙️ Inteligência Operacional",
    "documentacao": "🗺️ Documentação"
}

# 3. Injeção de CSS para Imagem de Fundo e Estilização dos Cards
st.markdown(f"""
<style>
/* Aplicando a imagem de fundo na janela principal do app */
[data-testid="stAppViewContainer"] {{
    background-image: url('data:image/jpeg;base64,{img_base64}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

/* Escurecendo levemente o fundo principal para a imagem não ofuscar o texto (Overlay) */
[data-testid="stAppViewContainer"] > .main {{
    background-color: rgba(14, 17, 23, 0.85); 
}}

/* Transformando os botões padrão do Streamlit em Cards estilizados */
div.stButton > button {{
    height: 140px;
    border-radius: 15px;
    background: rgba(40, 44, 52, 0.7); /* Efeito translúcido / Glassmorphism */
    backdrop-filter: blur(8px);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    transition: all 0.3s ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
}}

/* Efeito ao passar o mouse por cima do Card (Hover) */
div.stButton > button:hover {{
    background: rgba(76, 175, 80, 0.9); /* Verde Metro/Destaque */
    transform: translateY(-8px);
    border: 1px solid #4CAF50;
    box-shadow: 0 10px 20px rgba(76, 175, 80, 0.4);
    color: white;
}}

/* Ajuste da fonte dentro do Card */
div.stButton > button p {{
    font-size: 22px !important;
    font-weight: bold !important;
    margin: 0;
}}
</style>
""", unsafe_allow_html=True)

# 4. Criando o Layout de Grid para os Cards
st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
cols = st.columns(2) # Cria um grid com 2 colunas

# Iterando sobre as páginas permitidas para criar os cards dinamicamente
for index, page in enumerate(allowed_pages):
    
    # Pega o nome amigável com ícone do dicionário. Se não existir, formata o nome do próprio arquivo
    display_name = PAGE_DISPLAY_NAMES.get(page, page.replace('_', ' ').title())
        
    # Distribui os cards pelas colunas
    with cols[index % 2]:
        # O botão age como o Card. Se clicado, navega para a página .py correspondente.
        if st.button(display_name, key=f"card_{page}", use_container_width=True):
            try:
                # O Streamlit vai procurar exatamente pelo nome listado em ALL_TABS (ex: pages/carga_csv.py)
                st.switch_page(f"pages/{page}.py")
            except Exception as e:
                st.error(f"Página não encontrada: pages/{page}.py")