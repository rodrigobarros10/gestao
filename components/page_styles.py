import streamlit as st


def apply_ultra_compact_css():
    st.markdown(
        """
        <style>
        .block-container { padding: 0.5rem 1rem !important; max-width: 100%; }
        header { visibility: hidden; height: 0px; }

        .kpi-wrapper { display: flex; gap: 8px; justify-content: space-between; margin-bottom: 12px; margin-top: 5px; }
        .kpi-card { flex: 1; background: rgba(20, 20, 25, 0.6); border: 1px solid #333; border-radius: 8px; padding: 10px 5px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); backdrop-filter: blur(5px); transition: transform 0.2s; }
        .kpi-card:hover { transform: translateY(-2px); border-color: #555; }
        .kpi-title { font-family: 'Segoe UI', sans-serif; font-size: 11px; color: #aaa; font-weight: 600; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.5px; }
        .kpi-val { font-family: 'Segoe UI', sans-serif; font-size: 20px; color: #fff; font-weight: 800; margin: 2px 0; }
        .kpi-delta { font-size: 11px; font-weight: 700; }
        .d-pos { color: #2ecc71; }
        .d-neg { color: #e74c3c; }
        .d-neu { color: #f1c40f; }

        .pbi-title { font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; margin-bottom: 0px; color: #1A1A1D !important; }
        .stButton > button, .stDownloadButton > button { padding: 2px 10px !important; font-size: 12px !important; border-radius: 4px; }
        hr { margin: 8px 0px; opacity: 0.2; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_operacao_css():
    st.markdown(
        """
        <style>
        .stDataFrame { margin-top: 5px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_indicadores_css():
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 98%; }
        header { visibility: hidden; height: 0px; }
        .stMetric { margin-bottom: -15px; }
        h3 { font-size: 18px !important; margin-bottom: 0px !important; padding-bottom: 5px !important; }
        hr { margin-top: 10px; margin-bottom: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
