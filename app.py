import streamlit as st
import plotly.io as pio
from config.settings import DEFAULT_DB_CONFIG
from config.constants import ALL_TABS
from database.connection import PostgreSQLDataLoader
from services.auth_service import AuthService
from utils.helpers import get_base64_of_bin_file
from components.ui_elements import load_custom_css

# --- INITIAL SETUP ---
st.set_page_config(page_title="DATA TREM | Metro BH", layout="wide", page_icon="🚇")
pio.templates.default = "plotly_dark" # Padrão escuro das outras páginas
img_base64 = get_base64_of_bin_file('fundo_metro.jpeg') 
load_custom_css(img_base64)

# --- INJEÇÃO DE CSS GLOBAL & DARK GLASSMORPHISM ---
st.markdown(f"""
<style>
/* Fundo da aplicação com a imagem e Overlay Escuro Transparente */
[data-testid="stAppViewContainer"] {{
    background-image: url('data:image/jpeg;base64,{img_base64}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
[data-testid="stAppViewContainer"] > .main {{
    background-color: rgba(14, 17, 23, 0.80); /* Overlay escuro e transparente */
}}

/* Escondendo cabeçalho padrão para um visual mais limpo */
header {{ visibility: hidden; height: 0px; }}
.block-container {{ padding-top: 3rem !important; max-width: 98%; }}

/* Estilização Geral de Textos */
h1, h2, h3, h4, p {{ font-family: 'Segoe UI', sans-serif; color: #FFFFFF; }}

/* --- ESTILIZAÇÃO DO LOGIN --- */
/* Formulário de Login flutuante (Dark Glassmorphism) */
[data-testid="stForm"] {{
    background: rgba(20, 20, 25, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid #333 !important;
    border-radius: 15px !important;
    padding: 30px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
}}

/* Inputs do Login */
.stTextInput > div > div > input {{
    background-color: rgba(0, 0, 0, 0.5) !important;
    color: #FFFFFF !important;
    border: 1px solid #444 !important;
    border-radius: 8px !important;
    padding: 10px 15px !important;
    transition: all 0.3s ease;
}}
.stTextInput > div > div > input:focus {{
    border-color: #00F2FE !important;
    box-shadow: 0 0 8px rgba(0, 242, 254, 0.3) !important;
}}

/* --- ESTILIZAÇÃO DOS CARDS (BOTÕES) DO DASHBOARD --- */
div.stButton > button {{
    height: 130px;
    border-radius: 12px;
    background: rgba(20, 20, 25, 0.6);
    backdrop-filter: blur(5px);
    color: #FFFFFF;
    border: 1px solid #333;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}}

/* Efeito Hover nos Cards */
div.stButton > button:hover {{
    transform: translateY(-4px);
    background: rgba(30, 30, 35, 0.8);
    border: 1px solid #00F2FE; /* Borda Neon Azul/Ciano */
    box-shadow: 0 8px 20px rgba(0, 242, 254, 0.15);
    color: #00F2FE;
}}

/* Texto interno do Card */
div.stButton > button p {{
    font-size: 18px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    margin: 0;
}}
</style>
""", unsafe_allow_html=True)

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


# ==========================================================
# --- TELA DE LOGIN ---
# ==========================================================
if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True) 
    col_l1, col_l2, col_l3 = st.columns([1.5, 2, 1.5])
    
    with col_l2:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
                <h1 style='color: #1A1A1D; font-size: 42px; font-weight: 800; letter-spacing: 2px; margin-bottom: 0px;'>🚉 DATA TREM</h1>
                <p style='color: #1A1A1D; font-size: 16px; font-weight: 600;'>Portal de Inteligência Operacional • Metro BH</p>
            </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.get('connected'):
            st.error("🔴 Serviço de banco de dados indisponível. Contate a engenharia.")
        else:
            with st.form("login_form"):
                st.markdown("<p style='color: #FFFFFF; font-weight: 600; margin-bottom: 5px;'>Acesso Restrito</p>", unsafe_allow_html=True)
                username = st.text_input("Usuário", placeholder="Insira sua credencial")
                password = st.text_input("Senha", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Autenticar ➔")

                if submit:
                    auth = AuthService(st.session_state['db_loader'])
                    user = auth.authenticate_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['current_user'] = user['username']
                        st.session_state['current_role'] = user['role']
                        st.rerun()
                    else:
                        st.error("⚠️ Credenciais inválidas. Tente novamente.")
    st.stop()


# ==========================================================
# --- SIDEBAR & LOGOUT ---
# ==========================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: #00F2FE; font-weight: 800; letter-spacing: 1px; margin-bottom: 0;'>DATA TREM</h2>
            <hr style='border-color: rgba(255,255,255,0.1); margin-top: 5px;'>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"👤 **Operador:** <span style='color: #aaa;'>{st.session_state['current_user']}</span>", unsafe_allow_html=True)
    st.markdown(f"🛡️ **Acesso:** <span style='color: #aaa;'>{st.session_state['current_role'].upper()}</span>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("🚪 Encerrar Sessão", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['current_role'] = None
        st.rerun()


# ==========================================================
# --- HOMEPAGE / DASHBOARD (Visão Pós-Login) ---
# ==========================================================
st.markdown("""
    <div>
        <h1 style='color: #1A1A1D; font-weight: 800; font-size: 36px; margin-bottom: 0px;'>Painel de Módulos</h1>
        <h4 style='color: #1A1A1D; margin-top: 5px; font-weight: 600; font-size: 18px;'>Selecione um ambiente para iniciar a operação</h4>
    </div>
    <hr style='border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 15px; margin-bottom: 30px;'>
""", unsafe_allow_html=True)

# Mapeamento: Arquivo -> Ícone + Nome Amigável
PAGE_DISPLAY_NAMES = {
    "operacao": "🕹️ Centro de Controle",
    "indicadores": "🚥 Indicadores Operacionais",
    "numeros": "📊 Metrô em Números",
    "ia_ml": "🧠 Inteligência Artificial (IA)",
    "carga_csv": "📤 Carga de Dados (CSV)",
    "sql_scripts": "🛤️ Terminal SQL",
    "configuracoes": "⚙️ Configurações",
    "documentacao": "🗺️ Documentação"
}

allowed_pages = st.session_state['permissions'].get(st.session_state['current_role'], [])

# Ordenar páginas para colocar as principais (operações) no topo, se existirem na permissão
priority_order = ["operacao", "indicadores", "numeros", "ia_ml", "carga_csv", "sql_scripts", "configuracoes", "documentacao"]
sorted_pages = [p for p in priority_order if p in allowed_pages] + [p for p in allowed_pages if p not in priority_order]

# Renderização da grade de botões (3 colunas)
cols = st.columns(3) 
for index, page in enumerate(sorted_pages):
    display_name = PAGE_DISPLAY_NAMES.get(page, page.replace('_', ' ').title())
        
    with cols[index % 3]:
        if st.button(display_name, key=f"card_{page}", use_container_width=True):
            try:
                st.switch_page(f"pages/{page}.py")
            except Exception:
                st.error(f"⚠️ Página não encontrada: pages/{page}.py")