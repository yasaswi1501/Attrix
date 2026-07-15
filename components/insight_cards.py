import streamlit as st

def render_insight_card(
    title: str,
    observation: str,
    evidence: str,
    interpretation: str,
    recommendation: str,
    priority: str = "Monitor"
):
    """
    Renders an Apple-inspired premium executive briefing insight card.
    """
    # Map priority badge style
    if priority.lower() == "critical":
        badge_style = "background-color: rgba(181, 71, 71, 0.08); color: #B54747; border: 1px solid rgba(181, 71, 71, 0.15);"
    elif priority.lower() == "elevated":
        badge_style = "background-color: rgba(201, 121, 43, 0.08); color: #C9792B; border: 1px solid rgba(201, 121, 43, 0.15);"
    else:
        badge_style = "background-color: rgba(0, 113, 227, 0.08); color: #0071E3; border: 1px solid rgba(0, 113, 227, 0.15);"

    st.markdown(
        f"""
        <div class="apple-card" style="margin-bottom: 20px; padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(0, 0, 0, 0.04); padding-bottom: 8px;">
                <span style="font-size: 14px; font-weight: 600; color: #1D1D1F;">{title}</span>
                <span class="status-badge" style="{badge_style}">{priority.upper()}</span>
            </div>
            <div style="font-size: 13.5px; line-height: 1.55; color: #1D1D1F;">
                <div style="margin-bottom: 8px;">
                    <span style="color: #6E6E73; font-weight: 500;">🔍 Observation:</span> {observation}
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #6E6E73; font-weight: 500;">📊 Evidence:</span> {evidence}
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #6E6E73; font-weight: 500;">💡 Interpretation:</span> {interpretation}
                </div>
                <div>
                    <span style="color: #6E6E73; font-weight: 500;">🚀 Recommendation:</span> {recommendation}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_dynamic_insight_card(
    title: str,
    finding: str,
    recommendation: str,
    confidence: str,
    owner: str,
    priority: str
):
    """
    Renders a premium reusable card containing dynamic insights, recommendations, and metrics context.
    """
    risk_color = "#B54747" if priority.lower() == "critical" else ("#C9792B" if priority.lower() == "high" else "#0071E3")
    
    st.markdown(
        f"""
        <div class="apple-card" style="border-left: 3px solid {risk_color}; padding: 14px 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 13.5px; font-weight: 700; color: #1D1D1F;">{title}</span>
                <span class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 600; font-size: 10px;">{confidence}</span>
            </div>
            <p style="font-size: 12.5px; color: #1D1D1F; line-height: 1.45; margin-bottom: 8px;">
                <strong>Finding:</strong> {finding}
            </p>
            <p style="font-size: 12px; color: #6E6E73; line-height: 1.4; margin-bottom: 8px; border-top: 1px solid rgba(0,0,0,0.03); padding-top: 6px;">
                <strong>Suggested Action:</strong> {recommendation}
            </p>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #86868B; margin-top: 6px;">
                <span>Owner: {owner}</span>
                <span style="color: {risk_color}; font-weight: 600;">Priority: {priority}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
