import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to style Streamlit elements according to Attrix design tokens.
    Overrides paddings, defines font sizing, styles metrics cards, and customizes input fields.
    """
    st.markdown(
        """
        <style>
        /* General Layout Adjustments & Fonts */
        .stApp {
            background-color: #F5F5F7;
            color: #1D1D1F;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
        }
        
        /* Max-width Container override to create balanced editorial visual frame */
        div[data-testid="stAppViewBlockContainer"], .stMainBlockContainer {
            max-width: 1400px !important;
            padding-left: 40px !important;
            padding-right: 40px !important;
            padding-top: 36px !important;
            padding-bottom: 64px !important;
            margin: 0 auto !important;
        }
        
        /* Premium Card Style (Stripe & Notion Inspired) */
        .apple-card {
            background-color: #FFFFFF;
            border-radius: 14px;
            border: 1px solid rgba(0, 0, 0, 0.06);
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: border-color 150ms ease, box-shadow 150ms ease;
        }
        .apple-card:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
            border-color: rgba(0, 0, 0, 0.12);
        }
        
        /* Metric Card Text Styles */
        .metric-title {
            font-size: 11px;
            color: #6E6E73;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #1D1D1F;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
            line-height: 1.15;
        }
        .metric-context {
            font-size: 12px;
            color: #86868B;
        }
        .metric-indicator-positive {
            color: #2E7D5B;
            font-weight: 600;
        }
        .metric-indicator-negative {
            color: #B54747;
            font-weight: 600;
        }
        .metric-indicator-warning {
            color: #C9792B;
            font-weight: 600;
        }
        
        /* Premium Page Header Sizing */
        .hero-title {
            font-size: 32px;
            font-weight: 700;
            color: #1D1D1F;
            letter-spacing: -0.75px;
            margin-bottom: 6px;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 15px;
            color: #6E6E73;
            font-weight: 400;
            margin-bottom: 20px;
            line-height: 1.45;
        }
        
        /* Status Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 11.5px;
            font-weight: 600;
            background-color: rgba(0, 113, 227, 0.08);
            color: #0071E3;
            border: 1px solid rgba(0, 113, 227, 0.15);
        }
        .status-badge-success {
            background-color: rgba(46, 125, 91, 0.08);
            color: #2E7D5B;
            border: 1px solid rgba(46, 125, 91, 0.15);
        }
        
        /* Dynamic filter chips layout */
        .filter-chip-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        .filter-chip {
            background-color: #FFFFFF;
            border: 1px solid rgba(0, 0, 0, 0.06);
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 11.5px;
            color: #6E6E73;
            display: inline-flex;
            align-items: center;
        }
        
        /* Sidebar Styling (Linear Inspired) */
        div[data-testid="stSidebarCollapseButton"] {
            margin-top: 10px;
        }
        section[data-testid="stSidebar"] {
            background-color: #FBFBFD !important;
            border-right: 1px solid rgba(0, 0, 0, 0.06);
        }
        section[data-testid="stSidebar"] .stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            background-color: #FFFFFF !important;
            color: #1D1D1F !important;
            font-size: 13px !important;
            transition: background-color 150ms ease, border-color 150ms ease;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #F5F5F7 !important;
            border-color: rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Wrap long navigation menu items cleanly */
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span {
            white-space: normal !important;
            word-break: break-word !important;
            line-height: 1.25 !important;
            padding-top: 2px;
            padding-bottom: 2px;
        }
        
        /* Streamlit Input Overrides (Quiet & Minimal) */
        div[data-baseweb="select"] {
            border-radius: 8px !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            background-color: #FFFFFF !important;
        }
        div[data-baseweb="select"] > div {
            border: none !important;
            background: transparent !important;
        }
        span[data-baseweb="tag"] {
            background-color: rgba(0, 113, 227, 0.06) !important;
            color: #0071E3 !important;
            border: 1px solid rgba(0, 113, 227, 0.12) !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        div[data-testid="stSlider"] > div {
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
        
        /* Standard Action Buttons (Vercel Style) */
        .stButton > button {
            border-radius: 8px !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
            padding: 5px 12px !important;
            background-color: #0071E3 !important;
            color: #FFFFFF !important;
            border: 1px solid #0071E3 !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
            transition: background-color 150ms ease, border-color 150ms ease, opacity 150ms ease !important;
        }
        .stButton > button:hover {
            background-color: #0077ED !important;
            border-color: #0077ED !important;
            color: #FFFFFF !important;
        }
        .stButton > button:active {
            background-color: #0062C4 !important;
            border-color: #0062C4 !important;
        }
        
        /* Clean Dataframe Container */
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(0, 0, 0, 0.06) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }
        
        /* Hide Default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header(title: str, subtitle: str, active_count: int, total_count: int, completeness_pct: float = 100.0):
    """
    Renders the unified main header, including dataset coverage status and quality badges.
    """
    inject_custom_css()
    
    st.markdown(f'<h1 class="hero-title">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            f'<div class="filter-chip-container">'
            f'<span class="filter-chip">📊 Coverage: <strong>{active_count}</strong> of <strong>{total_count}</strong> employees ({round((active_count/total_count)*100, 1)}%)</span>'
            f'<span class="filter-chip">🔍 Active Filters Applied</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col2:
        if completeness_pct > 95.0:
            st.markdown('<div style="text-align: right;"><span class="status-badge status-badge-success">● Data Integrity: Excellent</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align: right;"><span class="status-badge">● Data Integrity: {completeness_pct:.1f}%</span></div>', unsafe_allow_html=True)
    
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-top: 0; margin-bottom: 24px;">', unsafe_allow_html=True)
