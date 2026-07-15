import streamlit as st
from components.disclaimer import render_academic_disclaimer, render_causation_disclaimer, render_small_sample_warning

def render_footer(sample_size: int):
    """
    Renders ethical disclaimers, causation warnings, and conditional small sample size alerts in a unified footer.
    """
    st.markdown('<br><br>', unsafe_allow_html=True)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;">', unsafe_allow_html=True)

    # 1. Small Sample Size Warning
    render_small_sample_warning(sample_size)

    # 2. Case Study and Causation Disclaimers
    render_academic_disclaimer()
    render_causation_disclaimer()
