import calendar
from datetime import datetime

import streamlit as st

def get_date_filter_ui(key_prefix, show_labels=True):
    c1, c2 = st.columns(2)
    
    # Define a visibilidade baseada no parâmetro
    visibilidade = "visible" if show_labels else "collapsed"
    
    with c1:
        current_year = datetime.now().year
        years = [current_year - i for i in range(0, 4)]
        ano_sel = st.selectbox(
            "Ano",
            years,
            key=f"ano_{key_prefix}",
            label_visibility=visibilidade,
        )
    with c2:
        meses_map = {1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'11', 12:'12'}
        mes_sel = st.selectbox(
            "Mês", 
            list(meses_map.keys()), 
            format_func=lambda x: meses_map[x], 
            index=1, 
            key=f'mes_{key_prefix}', 
            label_visibility=visibilidade
        )
    
    last_day = calendar.monthrange(ano_sel, mes_sel)[1]
    return {
        'ano': ano_sel, 'mes': mes_sel, 'mes_nome': meses_map[mes_sel],
        'dt_start': f"{ano_sel}-{mes_sel:02d}-01", 'dt_end': f"{ano_sel}-{mes_sel:02d}-{last_day}",
        'dt_start_ts': f"{ano_sel}-{mes_sel:02d}-01 00:00:00", 'dt_end_ts': f"{ano_sel}-{mes_sel:02d}-{last_day} 23:59:59"
    }
