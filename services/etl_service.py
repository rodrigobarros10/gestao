import pandas as pd
from utils.helpers import detect_delimiter, convert_data_types

class ETLService:
    def __init__(self, db_loader):
        self.db = db_loader

    def process_and_load_csv(self, uploaded_file, tabela_destino, expected_cols):
        try:
            delim = detect_delimiter(uploaded_file)
            df = pd.read_csv(uploaded_file, sep=delim, dtype=str)
            
            if len(df.columns) == len(expected_cols):
                df.columns = expected_cols
                df = convert_data_types(df, tabela_destino)
                self.db.load_dataframe(df, tabela_destino)
                return True, f"Sucesso: {tabela_destino} carregada."
            else:
                return False, f"Erro: Esperado {len(expected_cols)} colunas, Recebido {len(df.columns)}"
        except Exception as e:
            return False, f"Erro crítico: {e}"