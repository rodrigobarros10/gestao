import pandas as pd

from database.connection import run_query


def get_scalar(engine, query, default=0.0):
    df = run_query(engine, query)
    if not df.empty and pd.notnull(df.iloc[0, 0]):
        return float(df.iloc[0, 0])
    return default


def calc_delta(current, previous, inv=False):
    if previous == 0 and current > 0:
        val = 100.0
    elif previous == 0 and current == 0:
        val = 0.0
    else:
        val = ((current - previous) / previous) * 100

    if val > 0:
        return f"+{val:.1f}%", "d-neg" if inv else "d-pos"
    if val < 0:
        return f"{val:.1f}%", "d-pos" if inv else "d-neg"
    return "0.0%", "d-neu"
