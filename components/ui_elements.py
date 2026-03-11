import streamlit as st
from utils.helpers import convert_df_to_csv
from datetime import datetime

def load_custom_css(img_base64=""):
    st.markdown(f"""
    <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
            url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;            
            background-position: center;      
            background-repeat: no-repeat;      
            background-attachment: fixed;      
        }}
        .main .block-container {{ padding-top: 1rem; padding-bottom: 2rem; }}
        .kpi-card-container {{
            background-color: #262730;
            border: 1px solid #464b5d;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 15px;
        }}
        .kpi-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
        .kpi-title {{ font-size: 14px; color: #9ca3af; font-weight: 600; text-transform: uppercase; margin: 0; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: #ffffff; margin: 5px 0; }}
        .kpi-subtitle {{ font-size: 12px; color: #9ca3af; }}
        .kpi-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; }}
        .badge-success {{ background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }}
        .badge-danger {{ background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid #e74c3c; }}
    </style>
    """, unsafe_allow_html=True)

def render_download_btn(df, filename_prefix):
    if df is not None and not df.empty:
        with st.expander("📥 Donwload CSV"):
            csv = convert_df_to_csv(df)
            data_atual = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label="Clique para Baixar",
                data=csv,
                file_name=f"{filename_prefix}_{data_atual}.csv",
                mime='text/csv',
                use_container_width=True
            )

def render_kpi_card_modern(title, value, subtitle, target, is_good, footer=""):
    badge_class = "badge-success" if is_good else "badge-danger"
    badge_icon = "✔" if is_good else "✗"
    badge_text = "Na Meta" if is_good else "Abaixo"
    val_fmt = f"{value:.3f}" if isinstance(value, float) else str(value)

    html = f"""
    <div class="kpi-card-container">
        <div class="kpi-header">
            <p class="kpi-title">{title}</p>
            <span class="kpi-badge {badge_class}">{badge_icon} {badge_text}</span>
        </div>
        <div class="kpi-value">{val_fmt}</div>
        <div class="kpi-subtitle">{subtitle}</div>
        <div class="kpi-footer" style="font-size: 11px; margin-top:5px; color:#666;">
            Meta: <b>{target}</b><br>{footer}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)