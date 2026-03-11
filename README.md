# GESTÃO DE DADOS OPERACIONAIS - METRO BH

## Configuração do Ambiente
1. Crie o ambiente virtual: `python -m venv venv`
2. Ative o ambiente virtual (Windows: `venv\Scripts\activate` | Mac/Linux: `source venv/bin/activate`)
3. Instale as dependências: `pip install -r requirements.txt`
4. Configure suas credenciais no arquivo `.env`
5. Inicialize o banco de dados (Criação da tabela de usuários): `python database/setup_db.py`
6. Execute a aplicação: `streamlit run app.py`