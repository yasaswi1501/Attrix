import streamlit as st

def render_empty_state(message: str = "No employee records match the selected filters.", sub_message: str = "Adjust one or more filters in the sidebar to view workforce insights."):
    """
    Renders an Apple-inspired empty state when data filters return zero rows.
    """
    st.markdown(
        f"""
        <div style="
            background-color: #FFFFFF;
            border-radius: 16px;
            border: 1px dashed rgba(0, 0, 0, 0.15);
            padding: 60px 40px;
            text-align: center;
            margin: 40px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
        ">
            <div style="font-size: 48px; margin-bottom: 20px;">🔍</div>
            <h3 style="font-size: 20px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">{message}</h3>
            <p style="font-size: 14px; color: #6E6E73; max-width: 400px; margin: 0 auto;">{sub_message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
