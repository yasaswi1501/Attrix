import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to style Streamlit elements according to Attrix theme tokens.
    Uses native Streamlit CSS variables to react to user settings (Light/Dark/System).
    """
    st.markdown(
        """
        <style>
        /* General Layout Adjustments & Fonts */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
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
            background-color: var(--secondary-background-color);
            border-radius: 14px;
            border: 1px solid rgba(128, 128, 128, 0.15);
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: border-color 150ms ease, background-color 150ms ease;
        }
        .apple-card:hover {
            border-color: rgba(128, 128, 128, 0.3);
        }
        
        /* Metric Card Text Styles */
        .metric-title {
            font-size: 11px;
            color: var(--text-color);
            opacity: 0.6;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-color);
            letter-spacing: -0.5px;
            margin-bottom: 4px;
            line-height: 1.15;
        }
        .metric-context {
            font-size: 12px;
            color: var(--text-color);
            opacity: 0.5;
        }
        .metric-indicator-positive {
            color: #10B981;
            font-weight: 600;
        }
        .metric-indicator-negative {
            color: #EF4444;
            font-weight: 600;
        }
        .metric-indicator-warning {
            color: #F59E0B;
            font-weight: 600;
        }
        
        /* Premium Page Header Sizing */
        .hero-title {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-color);
            letter-spacing: -0.75px;
            margin-bottom: 6px;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 15px;
            color: var(--text-color);
            opacity: 0.6;
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
            background-color: rgba(59, 130, 246, 0.08);
            color: var(--primary-color);
            border: 1px solid rgba(59, 130, 246, 0.15);
        }
        .status-badge-success {
            background-color: rgba(16, 185, 129, 0.08);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.15);
        }
        
        /* Dynamic filter chips layout */
        .filter-chip-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        .filter-chip {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.15);
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 11.5px;
            color: var(--text-color);
            opacity: 0.8;
            display: inline-flex;
            align-items: center;
        }
        
        /* Sidebar Styling (Linear Inspired) */
        div[data-testid="stSidebarCollapseButton"] {
            margin-top: 10px;
        }
        section[data-testid="stSidebar"] {
            background-color: var(--background-color) !important;
            border-right: 1px solid rgba(128, 128, 128, 0.15);
        }
        section[data-testid="stSidebar"] .stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            border: 1px solid rgba(128, 128, 128, 0.15) !important;
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            font-size: 13px !important;
            transition: background-color 150ms ease, border-color 150ms ease;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(128, 128, 128, 0.3) !important;
        }
        
        /* Wrap long navigation menu items cleanly */
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span {
            white-space: normal !important;
            word-break: break-word !important;
            line-height: 1.25 !important;
            padding-top: 2px;
            padding-bottom: 2px;
            color: var(--text-color) !important;
            opacity: 0.7;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] span {
            opacity: 1.0;
            font-weight: 600 !important;
        }
        
        /* Streamlit Input Overrides (Quiet & Minimal) */
        div[data-baseweb="select"] {
            border-radius: 8px !important;
            border: 1px solid rgba(128, 128, 128, 0.15) !important;
            background-color: var(--secondary-background-color) !important;
        }
        div[data-baseweb="select"] > div {
            border: none !important;
            background: transparent !important;
            color: var(--text-color) !important;
        }
        span[data-baseweb="tag"] {
            background-color: rgba(59, 130, 246, 0.06) !important;
            color: var(--primary-color) !important;
            border: 1px solid rgba(59, 130, 246, 0.12) !important;
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
            background-color: var(--primary-color) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--primary-color) !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
            transition: opacity 150ms ease !important;
        }
        .stButton > button:hover {
            opacity: 0.9 !important;
            color: #FFFFFF !important;
        }
        
        /* Clean Dataframe Container */
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.15) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }
        
        /* Minimal Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--background-color);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(128, 128, 128, 0.2);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(128, 128, 128, 0.4);
        }
        
        /* Style Streamlit Header & Sidebar Collapse/Reopen for dark mode */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            color: var(--text-color) !important;
        }
        div[data-testid="collapsedControl"] {
            background-color: var(--secondary-background-color) !important;
            border-bottom-right-radius: 8px !important;
            border-right: 1px solid rgba(128, 128, 128, 0.15) !important;
            border-bottom: 1px solid rgba(128, 128, 128, 0.15) !important;
            color: var(--text-color) !important;
        }
        button[data-testid="stSidebarCollapseButton"] {
            color: var(--text-color) !important;
        }
        
        /* Hide Default elements */
        footer {visibility: hidden;}
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
    
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(128, 128, 128, 0.15); margin-top: 0; margin-bottom: 24px;">', unsafe_allow_html=True)
