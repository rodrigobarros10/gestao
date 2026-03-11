import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

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