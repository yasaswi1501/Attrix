import streamlit as st

def render_academic_disclaimer():
    """
    Renders the Academic and Case Study disclaimer.
    """
    st.markdown(
        """
        <div class="apple-card" style="background-color: #FBFBFD; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 14px; padding: 18px 20px; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">
                Required Ethical & Data Disclaimer
            </div>
            <div style="font-size: 12.5px; color: #6E6E73; line-height: 1.5;">
                This dashboard is an academic and analytical case study created from the provided workforce dataset. 
                It should not be interpreted as an official disclosure of Palo Alto Networks' internal workforce data, 
                employee practices, or organizational performance. The findings represent patterns observed only within the supplied dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_causation_disclaimer():
    """
    Renders the Causation disclaimer.
    """
    st.markdown(
        """
        <div class="apple-card" style="background-color: #FBFBFD; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 14px; padding: 18px 20px; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">
                Causation Disclaimer
            </div>
            <div style="font-size: 12.5px; color: #6E6E73; line-height: 1.5;">
                The dashboard provides descriptive and diagnostic insights. Observed relationships (e.g., correlations with overtime, 
                travel, or age) do not establish direct causation and should be validated with qualitative research, employee feedback, 
                organizational context, and additional workforce data before policy or operational decisions are made.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_small_sample_warning(sample_size: int):
    """
    Renders a caution warning for small filtered groups (N < 10).
    """
    if sample_size > 0 and sample_size < 10:
        st.markdown(
            f"""
            <div class="apple-card" style="background-color: rgba(201, 121, 43, 0.06); border: 1px solid rgba(201, 121, 43, 0.15); border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;">
                <div style="font-size: 13px; font-weight: 600; color: #C9792B; margin-bottom: 6px;">
                    ⚠️ Small Sample Warning (N = {sample_size})
                </div>
                <div style="font-size: 12.5px; color: #6E6E73; line-height: 1.5;">
                    The active filter selection represents fewer than 10 employees. Observed ratios or rates may be 
                    statistically unstable or highly sensitive to single changes. Exercise caution when interpreting these results.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_data_privacy_notice():
    """
    Renders a data privacy notice.
    """
    st.markdown(
        """
        <div class="apple-card" style="background-color: #FBFBFD; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">
                Data Privacy & Aggregation
            </div>
            <div style="font-size: 12.5px; color: #6E6E73; line-height: 1.5;">
                All reporting remains strictly aggregated. To preserve employee anonymity and data privacy, individual-level profiling 
                and predictive tracking of named employees are not supported.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_statistical_limitation():
    """
    Renders a statistical limitation explanation.
    """
    st.markdown(
        """
        <div class="apple-card" style="background-color: #FBFBFD; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">
                Statistical Confidence
            </div>
            <div style="font-size: 12.5px; color: #6E6E73; line-height: 1.5;">
                Statistical significance (p-values) indicates whether an association is likely to occur by chance. 
                It does not measure business importance or practical impact. Large groups may show high significance for minor effects.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
