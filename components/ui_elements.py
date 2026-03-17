import streamlit as st
from utils.helpers import convert_df_to_csv
from datetime import datetime

def load_custom_css(img_base64=""):
    st.markdown(f"""
    <style>
        :root {{
            --bg-0: rgba(10, 12, 18, 0.86);
            --bg-1: rgba(20, 20, 25, 0.6);
            --bg-2: rgba(32, 34, 45, 0.7);
            --border-0: rgba(255, 255, 255, 0.08);
            --border-1: rgba(255, 255, 255, 0.14);
            --text-0: #F5F7FA;
            --text-1: #C9D1D9;
            --title-0: #1A1A1D;
            --accent-0: #00F2FE;
            --accent-1: #FA709A;
            --shadow-0: 0 10px 30px rgba(0,0,0,0.35);
        }}
        .stApp {{
            background-image: linear-gradient(var(--bg-0), var(--bg-0)), 
            url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;            
            background-position: center;      
            background-repeat: no-repeat;      
            background-attachment: fixed;      
        }}
        .main .block-container {{ padding-top: 1rem; padding-bottom: 2rem; }}
        html, body, [class*="css"] {{
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            color: var(--text-0);
        }}
        h1, h2, h3, h4, h5, h6 {{ color: var(--title-0); letter-spacing: 0.2px; }}
        p, span, label {{ color: var(--text-1); }}

        /* Panels and containers */
        [data-testid="stExpander"] > div {{ 
            border: 1px solid var(--border-0);
            background: var(--bg-1);
            border-radius: 12px;
            box-shadow: var(--shadow-0);
        }}
        [data-testid="stMetricValue"] {{ color: var(--text-0); }}
        [data-testid="stMetricLabel"] {{ color: var(--text-1); }}

        /* Buttons */
        .stButton > button, .stDownloadButton > button {{
            background: var(--bg-2);
            border: 1px solid var(--border-0);
            color: var(--text-0);
            border-radius: 10px;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-0);
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-1px);
            border-color: var(--accent-0);
            color: var(--accent-0);
        }}

        /* Tabs */
        [data-baseweb="tab-list"] {{
            gap: 6px;
        }}
        [data-baseweb="tab"] {{
            background: var(--bg-1);
            border: 1px solid var(--border-0);
            border-radius: 10px;
            padding: 6px 12px;
            color: var(--text-1);
        }}
        [data-baseweb="tab"][aria-selected="true"] {{
            color: var(--text-0);
            border-color: var(--accent-1);
            background: rgba(250, 112, 154, 0.15);
        }}

        .kpi-card-container {{
            background-color: rgba(26, 28, 36, 0.8);
            border: 1px solid var(--border-1);
            border-radius: 10px;
            padding: 15px;
            box-shadow: var(--shadow-0);
            margin-bottom: 15px;
        }}
        .kpi-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
        .kpi-title {{ font-size: 12px; color: var(--text-1); font-weight: 600; text-transform: uppercase; margin: 0; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: var(--text-0); margin: 5px 0; }}
        .kpi-subtitle {{ font-size: 12px; color: var(--text-1); }}
        .kpi-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; }}
        .badge-success {{ background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }}
        .badge-danger {{ background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid #e74c3c; }}
    </style>
    """, unsafe_allow_html=True)

def apply_modern_layout(fig, h=180, show_x=False, show_legend=False):
    fig.update_layout(
        height=h,
        margin=dict(t=8, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="", visible=show_x),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title="", zeroline=False),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1) if show_legend else None,
        font=dict(color="#FFF", family="Segoe UI"),
    )
    return fig

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

def render_chart_footer(df, file_name, fig, title, key, state_prefix="expanded_chart"):
    c1, c2 = st.columns([8, 2])
    with c1:
        render_download_btn(df, file_name)
    with c2:
        if st.button("⛶", key=key, help="Ampliar Gráfico", use_container_width=True):
            st.session_state[f"show_{state_prefix}"] = True
            st.session_state[f"{state_prefix}"] = fig
            st.session_state[f"{state_prefix}_title"] = title
            st.rerun()

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
