import streamlit as st
import calendar

def get_date_filter_ui(key_prefix):
    c1, c2 = st.columns(2)
    with c1:
        ano_sel = st.selectbox("Ano", [2026, 2025, 2024,2023], key=f'ano_{key_prefix}')
    with c2:
        meses_map = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        mes_sel = st.selectbox("Mês", list(meses_map.keys()), format_func=lambda x: meses_map[x], index=6, key=f'mes_{key_prefix}')
    
    last_day = calendar.monthrange(ano_sel, mes_sel)[1]
    return {
        'ano': ano_sel, 'mes': mes_sel, 'mes_nome': meses_map[mes_sel],
        'dt_start': f"{ano_sel}-{mes_sel:02d}-01", 'dt_end': f"{ano_sel}-{mes_sel:02d}-{last_day}",
        'dt_start_ts': f"{ano_sel}-{mes_sel:02d}-01 00:00:00", 'dt_end_ts': f"{ano_sel}-{mes_sel:02d}-{last_day} 23:59:59"
    }