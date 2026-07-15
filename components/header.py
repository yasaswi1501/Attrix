import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to style Streamlit elements according to Apple-inspired design principles.
    This overrides default padding, sets SF Pro-compatible font sizes, and styles metrics cards.
    """
    st.markdown(
        """
        <style>
        /* General Layout Adjustments */
        .stApp {
            background-color: #F5F5F7;
            color: #1D1D1F;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
        }
        
        /* Premium Card Style */
        .apple-card {
            background-color: #FFFFFF;
            border-radius: 16px;
            border: 1px solid rgba(0, 0, 0, 0.08);
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .apple-card:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03);
        }
        
        /* Metric Styling */
        .metric-title {
            font-size: 13px;
            color: #6E6E73;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #1D1D1F;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
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
        
        /* Header typography */
        .hero-title {
            font-size: 40px;
            font-weight: 800;
            color: #1D1D1F;
            letter-spacing: -1px;
            margin-bottom: 8px;
            line-height: 1.1;
        }
        .hero-subtitle {
            font-size: 18px;
            color: #6E6E73;
            font-weight: 400;
            margin-bottom: 24px;
            line-height: 1.4;
        }
        
        /* Clean Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 500;
            background-color: rgba(0, 113, 227, 0.08);
            color: #0071E3;
            border: 1px solid rgba(0, 113, 227, 0.15);
        }
        .status-badge-success {
            background-color: rgba(46, 125, 91, 0.08);
            color: #2E7D5B;
            border: 1px solid rgba(46, 125, 91, 0.15);
        }
        
        /* Filter chips */
        .filter-chip-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 24px;
        }
        .filter-chip {
            background-color: #FFFFFF;
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 12px;
            color: #6E6E73;
            display: inline-flex;
            align-items: center;
        }
        
        /* Hide Default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Align streamlit elements */
        div[data-testid="stSidebarCollapseButton"] {
            margin-top: 10px;
        }
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        /* Ensure sidebar navigation labels don't get truncated */
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span {
            white-space: normal !important;
            word-break: break-word !important;
            line-height: 1.2 !important;
            padding-top: 2px;
            padding-bottom: 2px;
        }
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
            st.markdown(f'<div style="text-align: right;"><span class="status-badge">● Data Integrity: {completeness_pct}%</span></div>', unsafe_allow_html=True)
    
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-top: 0; margin-bottom: 24px;">', unsafe_allow_html=True)
