import base64
from functools import lru_cache

import pandas as pd

def convert_df_to_csv(df):
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

def detect_delimiter(file):
    try:
        sample = file.read(2048).decode('utf-8', errors='ignore')
        file.seek(0)
        delimiters = [';', ',', '\t', '|']
        counts = {d: sample.count(d) for d in delimiters}
        return max(counts, key=counts.get) if max(counts.values()) > 0 else ';'
    except: return ';'

def convert_data_types(df, table_name):
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_object_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].str.strip()
            df_copy[col].replace(['', 'nan', 'NaN', 'None', 'NULL'], None, inplace=True)
    return df_copy

def map_stations(df, col_name, station_map):
    if df is not None and not df.empty and col_name in df.columns:
        df[col_name] = df[col_name].map(station_map).fillna(df[col_name])
    return df

@lru_cache(maxsize=8)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""
