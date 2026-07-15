import streamlit as st

def render_empty_state(
    message: str = "No workforce records match the selected filters.",
    sub_message: str = "Adjust one or more active filters in the sidebar or reset them to restore coverage."
):
    """
    Renders an Apple-inspired premium empty state with a Reset Filters action.
    """
    st.markdown(
        f"""
        <div style="
            background-color: #FFFFFF;
            border-radius: 14px;
            border: 1px dashed rgba(0, 0, 0, 0.12);
            padding: 48px 32px;
            text-align: center;
            margin: 24px 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.01);
        ">
            <div style="font-size: 40px; margin-bottom: 16px;">🔍</div>
            <h3 style="font-size: 18px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">{message}</h3>
            <p style="font-size: 13.5px; color: #6E6E73; max-width: 440px; margin: 0 auto 20px auto; line-height: 1.45;">{sub_message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render a centered Reset button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Reset Filters", key="empty_state_reset_btn", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("filter_") or key == "early_tenure_threshold":
                    del st.session_state[key]
            st.rerun()
