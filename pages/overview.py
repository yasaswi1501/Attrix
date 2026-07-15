import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics, calculate_group_attrition
from utils.chart_theme import apply_apple_theme, COLOR_RETENTION, COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY, COLOR_SECONDARY_TEXT
from components.page_header import render_page_header
from components.kpi_cards import render_kpi_card
from components.empty_states import render_empty_state
from components.footer import render_footer

def show_overview():
    """
    Renders the Executive Overview page.
    """
    # Fetch data from session state
    if "clean_df" not in st.session_state or st.session_state["clean_df"] is None:
        st.warning("Please upload or load the dataset first on the Methodology page.")
        return

    df = st.session_state["filtered_df"]
    raw_df = st.session_state["clean_df"]
    early_tenure_threshold = st.session_state.get("early_tenure_threshold", 2)

    total_count = len(raw_df)
    active_count = len(df)
    
    # Render unified Apple-inspired Header
    render_page_header(
        title="Workforce Attrition Intelligence",
        subtitle="Operational patterns, concentration areas, and organizational risk hotspots",
        employee_count=active_count,
        total_count=total_count
    )

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    # Calculate KPIs
    metrics = calculate_core_metrics(df, early_tenure_threshold)

    # 1. Primary KPI Row
    st.markdown('<h3 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">Core Workforce Metrics</h3>', unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        render_kpi_card(
            title="Total Headcount",
            value=f"{metrics['total_employees']:,}",
            context="Active employees in view",
            tooltip="The number of employee records matching active filter selections."
        )
    with kpi_col2:
        render_kpi_card(
            title="Exited Employees",
            value=f"{metrics['exited_employees']:,}",
            context="Voluntary departures",
            tooltip="The count of employees in the selected subset who have left the organization."
        )
    with kpi_col3:
        # Attrition rate compared to raw dataset baseline
        raw_metrics = calculate_core_metrics(raw_df, early_tenure_threshold)
        baseline_rate = raw_metrics["overall_attrition_rate"]
        diff_pp = metrics["overall_attrition_rate"] - baseline_rate
        trend_text = f"{'+' if diff_pp >= 0 else ''}{diff_pp:.1f} pp vs baseline"
        trend_type = "negative" if diff_pp > 1.0 else ("positive" if diff_pp < -1.0 else "neutral")
        
        render_kpi_card(
            title="Attrition Rate",
            value=f"{metrics['overall_attrition_rate']:.1f}%",
            context=trend_text,
            trend_type=trend_type,
            tooltip="Exited employees divided by total employees in active view, multiplied by 100."
        )
    with kpi_col4:
        render_kpi_card(
            title="Retention Rate",
            value=f"{metrics['retention_rate']:.1f}%",
            context="Continuous employment",
            trend_type="positive" if metrics['retention_rate'] > 85.0 else "neutral",
            tooltip="Retained employees divided by total employees in active view, multiplied by 100."
        )
    with kpi_col5:
        early_diff = metrics['early_tenure_attrition_rate'] - metrics['overall_attrition_rate']
        early_trend_text = f"{'+' if early_diff >= 0 else ''}{early_diff:.1f} pp vs active rate"
        early_trend_type = "negative" if early_diff > 2.0 else "neutral"

        render_kpi_card(
            title=f"Early Tenure Attrition",
            value=f"{metrics['early_tenure_attrition_rate']:.1f}%",
            context=early_trend_text,
            trend_type=early_trend_type,
            tooltip=f"Attrition rate of employees with tenure <= {early_tenure_threshold} years."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Focus Narrative & What Deserves Attention
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.markdown('<h4 style="font-size: 16px; font-weight: 600; margin-top: 0; margin-bottom: 12px; color: #1D1D1F;">🔎 Workforce Patterns Deserving Executive Attention</h4>', unsafe_allow_html=True)
    
    # Calculate highlights
    dept_df = calculate_group_attrition(df, "Department", metrics["overall_attrition_rate"], metrics["exited_employees"])
    top_dept = dept_df.iloc[0] if not dept_df.empty else None
    
    role_df = calculate_group_attrition(df, "JobRole", metrics["overall_attrition_rate"], metrics["exited_employees"])
    top_role = role_df.iloc[0] if not role_df.empty else None

    # Overtime metrics
    ot_yes_df = df[df["OverTime"] == "Yes"]
    ot_no_df = df[df["OverTime"] == "No"]
    ot_yes_rate = (ot_yes_df["Attrition"] == 1).sum() / len(ot_yes_df) * 100 if len(ot_yes_df) > 0 else 0
    ot_no_rate = (ot_no_df["Attrition"] == 1).sum() / len(ot_no_df) * 100 if len(ot_no_df) > 0 else 0

    highlights = []
    
    if top_dept is not None and top_dept["Attrition Rate"] > metrics["overall_attrition_rate"] * 1.25:
        highlights.append(
            f"The <strong>{top_dept['Group']}</strong> department shows a heightened attrition rate of "
            f"<strong>{top_dept['Attrition Rate']:.1f}%</strong> (compared to the baseline of {metrics['overall_attrition_rate']:.1f}%), "
            f"representing {top_dept['Exited']} exits (contributing {top_dept['Exit Contribution']:.1f}% of total exits in view)."
        )
    
    if top_role is not None and top_role["Attrition Rate"] > metrics["overall_attrition_rate"] * 1.5:
        highlights.append(
            f"The <strong>{top_role['Group']}</strong> role experiences elevated attrition at "
            f"<strong>{top_role['Attrition Rate']:.1f}%</strong>. This role contributed <strong>{top_role['Exited']} exits</strong>."
        )

    if ot_yes_rate > ot_no_rate * 1.5:
        highlights.append(
            f"Employees working overtime exhibit a significantly higher observed attrition rate of "
            f"<strong>{ot_yes_rate:.1f}%</strong>, compared to just <strong>{ot_no_rate:.1f}%</strong> for those not working overtime "
            f"(a difference of {ot_yes_rate - ot_no_rate:.1f} percentage points)."
        )

    if metrics["early_tenure_attrition_rate"] > metrics["overall_attrition_rate"] * 1.3:
        highlights.append(
            f"Attrition is concentrated in early-tenure talent: employees within their first <strong>{early_tenure_threshold} years</strong> "
            f"have an attrition rate of <strong>{metrics['early_tenure_attrition_rate']:.1f}%</strong>, accounting for "
            f"<strong>{metrics['early_tenure_exit_contribution']:.1f}% of all exits</strong> in view."
        )

    if not highlights:
        highlights.append("Observed workforce patterns are aligned with baseline rates. No extreme departmental or demographic anomalies were detected in the active view.")

    # Render bullets
    bullets_html = "".join([f'<li style="font-size: 14px; margin-bottom: 8px; color: #333333;">{h}</li>' for h in highlights])
    st.markdown(f'<ul style="margin: 0; padding-left: 20px;">{bullets_html}</ul>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Main Analytical Visualizations
    st.markdown('<h3 style="font-size: 20px; font-weight: 600; margin-top: 10px; margin-bottom: 16px;">Visual Diagnostics</h3>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Donut Chart - Attrition Distribution
        labels = ['Retained', 'Exited']
        values = [metrics["retained_employees"], metrics["exited_employees"]]
        
        donut_fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.6,
            marker_colors=[COLOR_RETENTION, COLOR_ELEVATED_RISK],
            textinfo='percent+value',
            textposition='outside',
            outsidetextfont=dict(color=COLOR_SECONDARY_TEXT, size=11),
            hoverinfo='label+value+percent'
        )])
        donut_fig.update_layout(showlegend=True)
        apply_apple_theme(
            donut_fig, 
            title="Workforce Distribution by Attrition Status", 
            show_legend=True, 
            height=340
        )
        st.plotly_chart(donut_fig, use_container_width=True)

    with col_chart2:
        # Department Attrition Rates
        if not dept_df.empty:
            dept_df_sorted = dept_df.sort_values(by="Attrition Rate", ascending=True)
            
            dept_fig = go.Figure()
            # Bar Chart
            dept_fig.add_trace(go.Bar(
                x=dept_df_sorted["Attrition Rate"],
                y=dept_df_sorted["Group"],
                orientation='h',
                marker_color=COLOR_ACCENT_BLUE,
                hovertemplate="<b>%{y}</b><br>Attrition Rate: %{x:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
                customdata=dept_df_sorted[["Exited", "Headcount"]].values
            ))
            
            # Baseline Reference line
            dept_fig.add_shape(
                type="line",
                x0=metrics["overall_attrition_rate"], y0=-0.5,
                x1=metrics["overall_attrition_rate"], y1=len(dept_df_sorted)-0.5,
                line=dict(color=COLOR_ELEVATED_RISK, width=2, dash="dash"),
            )
            
            # Label baseline
            dept_fig.add_annotation(
                x=metrics["overall_attrition_rate"], y=len(dept_df_sorted)-0.5,
                text=f"Baseline ({metrics['overall_attrition_rate']:.1f}%)",
                showarrow=True,
                arrowhead=1,
                ax=40, ay=-30,
                font=dict(color=COLOR_ELEVATED_RISK, size=10)
            )

            apply_apple_theme(
                dept_fig, 
                title="Attrition Rate by Department", 
                xaxis_title="Observed Attrition Rate (%)", 
                yaxis_title="", 
                height=340
            )
            st.plotly_chart(dept_fig, use_container_width=True)

    # Next Chart Row
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        # Overtime Attrition Rate Comparison
        ot_data = pd.DataFrame({
            "Category": ["No Overtime", "Overtime"],
            "Rate": [ot_no_rate, ot_yes_rate],
            "Headcount": [len(ot_no_df), len(ot_yes_df)],
            "Exits": [(ot_no_df["Attrition"] == 1).sum(), (ot_yes_df["Attrition"] == 1).sum()]
        })
        
        ot_fig = go.Figure(data=[go.Bar(
            x=ot_data["Category"],
            y=ot_data["Rate"],
            marker_color=[COLOR_RETENTION, COLOR_ELEVATED_RISK],
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=ot_data[["Exits", "Headcount"]].values
        )])
        
        # Add organizational baseline reference line
        ot_fig.add_shape(
            type="line",
            x0=-0.5, y0=metrics["overall_attrition_rate"],
            x1=1.5, y1=metrics["overall_attrition_rate"],
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        
        apply_apple_theme(
            ot_fig, 
            title="Attrition Rate: Overtime vs. No Overtime", 
            xaxis_title="", 
            yaxis_title="Attrition Rate (%)", 
            height=340
        )
        st.plotly_chart(ot_fig, use_container_width=True)

    with col_chart4:
        # Business Travel Attrition Rate
        travel_cats = ["Non-Travel", "Travel Rarely", "Travel Frequently"]
        rates = []
        counts = []
        exits = []
        
        for cat in travel_cats:
            sub = df[df["BusinessTravel"] == cat]
            rates.append((sub["Attrition"] == 1).sum() / len(sub) * 100 if len(sub) > 0 else 0)
            counts.append(len(sub))
            exits.append((sub["Attrition"] == 1).sum())
            
        travel_data = pd.DataFrame({
            "Category": travel_cats,
            "Rate": rates,
            "Headcount": counts,
            "Exits": exits
        })
        
        travel_fig = go.Figure(data=[go.Bar(
            x=travel_data["Category"],
            y=travel_data["Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.5,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=travel_data[["Exits", "Headcount"]].values
        )])
        
        travel_fig.add_shape(
            type="line",
            x0=-0.5, y0=metrics["overall_attrition_rate"],
            x1=2.5, y1=metrics["overall_attrition_rate"],
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        
        apply_apple_theme(
            travel_fig, 
            title="Attrition Rate by Business Travel Frequency", 
            xaxis_title="", 
            yaxis_title="Attrition Rate (%)", 
            height=340
        )
        st.plotly_chart(travel_fig, use_container_width=True)

    # Render ethical and data disclaimer footer
    render_footer(active_count)

if __name__ == "__main__":
    show_overview()
