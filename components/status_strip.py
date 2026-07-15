import streamlit as st

def render_status_strip(
    active_count: int, 
    total_count: int, 
    completeness_pct: float, 
    early_tenure_threshold: int, 
    has_filters: bool,
    baseline_rate: float = 16.1
):
    """
    Renders a compact horizontal status strip below the hero using dark design tokens.
    """
    coverage_text = f"Coverage: {active_count:,} of {total_count:,} employees"
    filter_text = "Filters: Active Filters Applied" if has_filters else "Filters: All workforce"
    integrity_text = f"Data Integrity: Excellent ({completeness_pct:.1f}%)" if completeness_pct > 95.0 else f"Data Integrity: {completeness_pct:.1f}%"
    tenure_text = f"Early Tenure: First {early_tenure_threshold} years"
    baseline_text = f"Baseline: {baseline_rate:.1f}%"
    
    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;">
            <span class="filter-chip" style="background-color: rgba(59, 130, 246, 0.08); color: #3B82F6; font-weight: 500; border: 1px solid rgba(59, 130, 246, 0.15);">{coverage_text}</span>
            <span class="filter-chip" style="background-color: rgba(255, 255, 255, 0.04); color: #F4F4F5; border: 1px solid rgba(255, 255, 255, 0.08);">{filter_text}</span>
            <span class="filter-chip" style="background-color: rgba(16, 185, 129, 0.08); color: #10B981; font-weight: 500; border: 1px solid rgba(16, 185, 129, 0.15);">{integrity_text}</span>
            <span class="filter-chip" style="background-color: rgba(245, 158, 11, 0.08); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.15);">{tenure_text}</span>
            <span class="filter-chip" style="background-color: rgba(255, 255, 255, 0.04); color: #A1A1AA; border: 1px solid rgba(255, 255, 255, 0.08);">{baseline_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
