import streamlit as st

def render_kpi_card(title: str, value: str, context: str, trend_text: str = "", trend_type: str = "neutral", tooltip: str = ""):
    """
    Renders a custom HTML metric card with Apple-inspired styling and micro-indicators.
    
    Args:
        title: The label of the metric.
        value: The main metric value (e.g. "14.2%").
        context: Context description (e.g., "voluntary departures").
        trend_text: Optional comparison text (e.g. "+2.3 pp vs baseline").
        trend_type: 'neutral' (grey), 'positive' (green - indicating healthy retention/retention rate),
                    'negative' (red - indicating high risk/attrition), or 'warning' (orange).
        tooltip: Optional info tooltip string.
    """
    # Map trend class
    if trend_type == "positive":
        trend_class = "metric-indicator-positive"
    elif trend_type == "negative":
        trend_class = "metric-indicator-negative"
    elif trend_type == "warning":
        trend_class = "metric-indicator-warning"
    else:
        trend_class = "metric-context"

    trend_html = f'<span class="{trend_class}">{trend_text}</span>' if trend_text else ""
    tooltip_attr = f'title="{tooltip}"' if tooltip else ""

    st.markdown(
        f"""
        <div class="apple-card" {tooltip_attr}>
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-context">{context} {trend_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
