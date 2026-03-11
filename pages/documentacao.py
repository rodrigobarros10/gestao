# Arquivo: pages/07_📘_Documentacao.py
import streamlit as st

# --- 1. PROTEÇÃO DE ROTA E CONFIGURAÇÃO ---
st.set_page_config(page_title="Documentação - Metrô BH", page_icon="📘", layout="wide")

# Garante que o usuário não acesse sem estar logado
if not st.session_state.get('logged_in', False):
    # Se não estiver logado, redireciona para a tela principal de login
    # ATENÇÃO: Substitua "app.py" pelo nome exato do seu arquivo principal se for diferente.
    st.switch_page("app.py") 

# --- 2. BOTÃO DE VOLTAR (Na página principal) ---
# Usamos colunas para o botão ficar discreto no canto esquerdo
col_btn, col_vazia = st.columns([1.5, 8.5]) 
with col_btn:
    # Botão com estilo visual mais limpo
    if st.button("⬅️ Painel Principal", use_container_width=True, type="secondary"):
        # Redireciona de volta para o dashboard
        st.switch_page("app.py") 

st.markdown("---")

# --- 3. CONTEÚDO DA DOCUMENTAÇÃO ---
st.title("📘 Documentação do Sistema")

# Exemplo de estrutura de documentação usando abas ou expanders
tab1, tab2, tab3 = st.tabs(["📌 Visão Geral", "🛠️ Módulos", "❓ FAQ"])

with tab1:
    st.header("Visão Geral do Sistema GESTÃO METRO BH")
    st.write("""
    Bem-vindo à documentação oficial. Este sistema foi desenvolvido para centralizar
    a gestão de dados operacionais, indicadores de performance e análises avançadas do Metrô BH.
    
    Utilize o menu lateral (se visível) ou os cards no Painel Principal para navegar entre os módulos.
    """)
    st.info("💡 **Dica:** Mantenha suas credenciais seguras e faça logout ao terminar sua sessão.")

with tab2:
    st.header("Guia dos Módulos")
    
    with st.expander("📂 Carga CSV"):
        st.write("Utilize este módulo para realizar o upload de arquivos de dados brutos...")
        # Adicione prints ou gifs aqui se quiser: st.image("assets/print_carga.png")
        
    with st.expander("🎮 Operação"):
        st.write("Painel em tempo real para acompanhamento da operação metroviária...")

    with st.expander("🤖 IA & ML"):
        st.write("Modelos preditivos de demanda e manutenção...")

with tab3:
    st.header("Perguntas Frequentes")
    st.markdown("""
    **P: Não consigo acessar um módulo, o que fazer?**
    R: Verifique seu nível de permissão no menu lateral. Se achar que está incorreto, contate o administrador.
    
    **P: Onde os dados são salvos?**
    R: Todos os dados são processados e armazenados com segurança no banco PostgreSQL institucional.
    """)