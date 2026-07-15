import streamlit as st
from components.header import render_header

def render_page_header(title: str, subtitle: str, employee_count: int, total_count: int):
    """
    Unified page header component matching the enterprise API guidelines.
    """
    completeness_pct = st.session_state.get("completeness_pct", 100.0)
    render_header(
        title=title,
        subtitle=subtitle,
        active_count=employee_count,
        total_count=total_count,
        completeness_pct=completeness_pct
    )
