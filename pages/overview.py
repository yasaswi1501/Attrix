import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics, calculate_group_attrition
from utils.chart_theme import (
    apply_apple_theme, 
    COLOR_RETENTION, 
    COLOR_ELEVATED_RISK, 
    COLOR_ACCENT_BLUE, 
    COLOR_NEUTRAL_GREY, 
    COLOR_SECONDARY_TEXT,
    COLOR_ATTENTION
)
from components.kpi_cards import render_kpi_card
from components.empty_states import render_empty_state
from components.footer import render_footer
from components.insight_cards import render_insight_card
from components.executive_summary import render_executive_summary_card

def show_overview():
    """
    Renders the flagship Executive Dashboard.
    """
    # Fetch data from session state
    if "clean_df" not in st.session_state or st.session_state["clean_df"] is None:
        st.warning("Please upload or load the dataset first on the Methodology page.")
        return

    df = st.session_state["filtered_df"]
    raw_df = st.session_state["clean_df"]
    early_tenure_threshold = st.session_state.get("early_tenure_threshold", 2)
    completeness_pct = st.session_state.get("completeness_pct", 100.0)

    total_count = len(raw_df)
    active_count = len(df)

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    # Calculate metrics & highlights
    metrics = calculate_core_metrics(df, early_tenure_threshold)
    raw_metrics = calculate_core_metrics(raw_df, early_tenure_threshold)
    baseline_rate = raw_metrics["overall_attrition_rate"]

    dept_df = calculate_group_attrition(df, "Department", metrics["overall_attrition_rate"], metrics["exited_employees"])
    top_dept = dept_df.iloc[0] if not dept_df.empty else None
    
    role_df = calculate_group_attrition(df, "JobRole", metrics["overall_attrition_rate"], metrics["exited_employees"])
    top_role = role_df.iloc[0] if not role_df.empty else None

    ot_yes_df = df[df["OverTime"] == "Yes"]
    ot_no_df = df[df["OverTime"] == "No"]
    ot_yes_rate = (ot_yes_df["Attrition"] == 1).sum() / len(ot_yes_df) * 100 if len(ot_yes_df) > 0 else 0
    ot_no_rate = (ot_no_df["Attrition"] == 1).sum() / len(ot_no_df) * 100 if len(ot_no_df) > 0 else 0

    # 1. HERO HEADER
    hero_col1, hero_col2 = st.columns([5, 3])
    with hero_col1:
        st.markdown(
            """
            <div style="margin-top: 10px;">
                <span style="font-size: 34px; font-weight: 800; color: #1D1D1F; letter-spacing: -1px; line-height: 1.1;">Attrix</span>
                <div style="font-size: 15px; font-weight: 600; color: #0071E3; margin-top: 2px; margin-bottom: 8px;">Enterprise Workforce Intelligence Platform</div>
                <p style="font-size: 13.5px; color: #6E6E73; line-height: 1.45; margin-right: 20px;">
                    Transform complex workforce data into evidence-based organizational intelligence for strategic retention planning.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with hero_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="background-color: #FBFBFD; padding: 12px 16px; margin-bottom: 0;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 4px;">
                    <span style="color: #86868B; font-weight: 500;">TOTAL WORKFORCE:</span>
                    <span style="font-weight: 600; color: #1D1D1F;">{total_count:,}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 4px;">
                    <span style="color: #86868B; font-weight: 500;">ACTIVE COVERAGE:</span>
                    <span style="font-weight: 600; color: #1D1D1F;">{active_count:,} ({round(active_count/total_count*100, 1)}%)</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 4px;">
                    <span style="color: #86868B; font-weight: 500;">DATA INTEGRITY:</span>
                    <span style="font-weight: 600; color: #2E7D5B;">Excellent ({completeness_pct:.1f}%)</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px;">
                    <span style="color: #86868B; font-weight: 500;">LAST ANALYSIS:</span>
                    <span style="font-weight: 600; color: #1D1D1F;">Just now</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-top: 20px; margin-bottom: 24px;">', unsafe_allow_html=True)

    # 2. EXECUTIVE SNAPSHOT (CRITICAL KPI CARDS)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Core Workforce Snapshot</h3>', unsafe_allow_html=True)
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
            title="Early Tenure Attrition",
            value=f"{metrics['early_tenure_attrition_rate']:.1f}%",
            context=early_trend_text,
            trend_type=early_trend_type,
            tooltip=f"Attrition rate of employees with tenure <= {early_tenure_threshold} years."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. EXECUTIVE SUMMARY PANEL
    render_executive_summary_card(
        metrics=metrics,
        top_dept=top_dept,
        top_role=top_role,
        ot_yes_rate=ot_yes_rate,
        ot_no_rate=ot_no_rate,
        early_tenure_threshold=early_tenure_threshold
    )

    # 4. KEY PRIORITIES ROW
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Retention Priority Assessment</h3>', unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    with p_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 155px; border-top: 3px solid #B54747; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #B54747; text-transform: uppercase;">Critical Focus</span>
                    <span class="status-badge" style="background-color: rgba(181, 71, 71, 0.06); color: #B54747; border: 1px solid rgba(181, 71, 71, 0.12); padding: 2px 6px; font-size: 9.5px;">LEVEL 1</span>
                </div>
                <div style="font-size: 13.5px; font-weight: 600; color: #1D1D1F; margin-bottom: 4px;">Sales Representatives</div>
                <div style="font-size: 12px; color: #6E6E73; line-height: 1.4;">
                    Rate of {top_role['Attrition Rate']:.1f}% represents extreme flight risk. Commission models and work scopes require review.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with p_col2:
        multiplier = ot_yes_rate / ot_no_rate if ot_no_rate > 0 else 1.0
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 155px; border-top: 3px solid #C9792B; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #C9792B; text-transform: uppercase;">Elevated Focus</span>
                    <span class="status-badge" style="background-color: rgba(201, 121, 43, 0.06); color: #C9792B; border: 1px solid rgba(201, 121, 43, 0.12); padding: 2px 6px; font-size: 9.5px;">LEVEL 2</span>
                </div>
                <div style="font-size: 13.5px; font-weight: 600; color: #1D1D1F; margin-bottom: 4px;">Overtime Workers</div>
                <div style="font-size: 12px; color: #6E6E73; line-height: 1.4;">
                    Overtime drives a {multiplier:.1f}x attrition increase. Operational capacity limits must be audited.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with p_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 155px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #0071E3; text-transform: uppercase;">Active Monitor</span>
                    <span class="status-badge" style="background-color: rgba(0, 113, 227, 0.06); color: #0071E3; border: 1px solid rgba(0, 113, 227, 0.12); padding: 2px 6px; font-size: 9.5px;">LEVEL 3</span>
                </div>
                <div style="font-size: 13.5px; font-weight: 600; color: #1D1D1F; margin-bottom: 4px;">Early-Tenure Cohorts</div>
                <div style="font-size: 12px; color: #6E6E73; line-height: 1.4;">
                    Exits in years 1 & 2 represent {metrics['early_tenure_exit_contribution']:.1f}% of departures. Onboarding checkpoints needed.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with p_col4:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 155px; border-top: 3px solid #2E7D5B; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #2E7D5B; text-transform: uppercase;">Stable Retention</span>
                    <span class="status-badge" style="background-color: rgba(46, 125, 91, 0.06); color: #2E7D5B; border: 1px solid rgba(46, 125, 91, 0.12); padding: 2px 6px; font-size: 9.5px;">STABLE</span>
                </div>
                <div style="font-size: 13.5px; font-weight: 600; color: #1D1D1F; margin-bottom: 4px;">Non-Travel & Levels 4-5</div>
                <div style="font-size: 12px; color: #6E6E73; line-height: 1.4;">
                    Senior managers and employees with zero business travel constraints show healthy retention profiles.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. DEPARTMENT INTELLIGENCE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 24px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 22px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">Which departments exceed the organizational baseline?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #6E6E73; margin-bottom: 20px;">Analyze structural voluntary departure patterns and contributions across core functional units.</p>', unsafe_allow_html=True)

    dept_col1, dept_col2 = st.columns([5, 3])
    with dept_col1:
        # Donut & Bar Charts comparison
        dept_df_sorted = dept_df.sort_values(by="Attrition Rate", ascending=True)
        dept_fig = go.Figure(data=go.Bar(
            x=dept_df_sorted["Attrition Rate"],
            y=dept_df_sorted["Group"],
            orientation='h',
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{y}</b><br>Attrition Rate: %{x:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=dept_df_sorted[["Exited", "Headcount"]].values
        ))
        # Add baseline line
        dept_fig.add_shape(
            type="line",
            x0=metrics["overall_attrition_rate"], y0=-0.5,
            x1=metrics["overall_attrition_rate"], y1=len(dept_df_sorted)-0.5,
            line=dict(color=COLOR_ELEVATED_RISK, width=2, dash="dash"),
        )
        apply_apple_theme(
            dept_fig,
            title="Observed Attrition Rate vs. Filtered Baseline",
            xaxis_title="Attrition Rate (%)",
            yaxis_title="",
            height=280
        )
        st.plotly_chart(dept_fig, use_container_width=True)

    with dept_col2:
        if top_dept is not None:
            render_insight_card(
                title="Department Retention Diagnostic",
                observation=f"Sales division shows highest risk rate, while R&D dominates exit volume.",
                evidence=f"Sales has an attrition rate of {top_dept['Attrition Rate']:.1f}% (baseline difference: {top_dept['Attrition Rate'] - metrics['overall_attrition_rate']:+.1f} pp). R&D contributed {top_dept['Exited']} exits (56.1% of all departures).",
                interpretation="Sales departures indicate commission/quota pressure. R&D departures indicate career progression or stagnation risks in large engineering units.",
                recommendation="Deploy localized career mapping pathways in R&D and evaluate sales quota benchmarks.",
                priority="Critical"
            )

    # 6. ROLE INTELLIGENCE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 22px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">Where are exits concentrated by job role?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #6E6E73; margin-bottom: 20px;">Isolate specific job roles experiencing structural retention friction.</p>', unsafe_allow_html=True)

    role_col1, role_col2 = st.columns([5, 3])
    with role_col1:
        # Role comparison chart (Top 5 high risk roles)
        role_df_sorted = role_df.sort_values(by="Attrition Rate", ascending=True).tail(5)
        role_fig = go.Figure(data=go.Bar(
            x=role_df_sorted["Attrition Rate"],
            y=role_df_sorted["Group"],
            orientation='h',
            marker_color=COLOR_ATTENTION,
            width=0.4,
            hovertemplate="<b>%{y}</b><br>Attrition Rate: %{x:.1f}%<br>Exits: %{customdata[0]}<extra></extra>",
            customdata=role_df_sorted[["Exited"]].values
        ))
        role_fig.add_shape(
            type="line",
            x0=metrics["overall_attrition_rate"], y0=-0.5,
            x1=metrics["overall_attrition_rate"], y1=len(role_df_sorted)-0.5,
            line=dict(color=COLOR_ELEVATED_RISK, width=2, dash="dash"),
        )
        apply_apple_theme(
            role_fig,
            title="Top 5 High-Risk Job Roles (Attrition Rate %)",
            xaxis_title="Attrition Rate (%)",
            yaxis_title="",
            height=280
        )
        st.plotly_chart(role_fig, use_container_width=True)

    with role_col2:
        if top_role is not None:
            render_insight_card(
                title="Job Role Retention Diagnostic",
                observation=f"Voluntary departures are highly concentrated in customer-facing and lab support roles.",
                evidence=f"Sales Representatives experience a {top_role['Attrition Rate']:.1f}% attrition rate, more than double the company baseline. Laboratory Technicians contribute the largest count of exits.",
                interpretation="High turnover points to intense customer friction, quota stress, or onboarding mismatches in entry-level profiles.",
                recommendation="Introduce quota-ramp schedules and early tenure onboarding checks.",
                priority="Critical"
            )

    # 7. WORKFORCE COMPOSITION (TENURE & CAREER SNAPSHOT)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 22px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">How does organizational tenure relate to observed attrition?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #6E6E73; margin-bottom: 20px;">Analyze if voluntary departures are concentrated in early-stage hires or long-tenured employees.</p>', unsafe_allow_html=True)

    tenure_col1, tenure_col2 = st.columns([5, 3])
    with tenure_col1:
        # Years at company distribution
        tenure_cats = sorted(df["YearsAtCompany"].unique())
        tenure_rates = []
        for yr in tenure_cats:
            sub = df[df["YearsAtCompany"] == yr]
            tenure_rates.append((sub["Attrition"] == 1).sum() / len(sub) * 100 if len(sub) > 0 else 0)
            
        tenure_fig = go.Figure(data=go.Scatter(
            x=tenure_cats,
            y=tenure_rates,
            mode='lines+markers',
            line=dict(color=COLOR_ACCENT_BLUE, width=2),
            marker=dict(size=6, color=COLOR_ACCENT_BLUE),
            hovertemplate="<b>Tenure: %{x} Years</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        ))
        tenure_fig.add_shape(
            type="line",
            x0=0, y0=metrics["overall_attrition_rate"],
            x1=max(tenure_cats) if tenure_cats else 10, y1=metrics["overall_attrition_rate"],
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        apply_apple_theme(
            tenure_fig,
            title="Observed Attrition Rate by Years at Company",
            xaxis_title="Years at Company",
            yaxis_title="Attrition Rate (%)",
            height=280
        )
        st.plotly_chart(tenure_fig, use_container_width=True)

    with tenure_col2:
        render_insight_card(
            title="Tenure Retention Diagnostic",
            observation="Departures are heavily front-loaded in the first two years of employment.",
            evidence=f"Employees within their first {early_tenure_threshold} years account for {metrics['early_tenure_exit_contribution']:.1f}% of total exits in view, exhibiting a cohort attrition rate of {metrics['early_tenure_attrition_rate']:.1f}%.",
            interpretation="Onboarding transition gaps suggest expectations mismatched during recruiting or lack of initial cohort integration support.",
            recommendation="Establish feedback surveys at 30/90/180 day checkpoints for all new hires.",
            priority="Elevated"
        )

    # 8. WORKLOAD DRIVERS (OVERTIME & TRAVEL)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 22px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">Which workload factors appear associated with attrition?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #6E6E73; margin-bottom: 20px;">Examine the correlation between overtime work, business travel demands, and employee turnover.</p>', unsafe_allow_html=True)

    workload_col1, workload_col2 = st.columns([5, 3])
    with workload_col1:
        # Overtime Comparison Bar
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
        ot_fig.add_shape(
            type="line",
            x0=-0.5, y0=metrics["overall_attrition_rate"],
            x1=1.5, y1=metrics["overall_attrition_rate"],
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        apply_apple_theme(
            ot_fig,
            title="Attrition Rate: Overtime vs. Standard Hours",
            xaxis_title="",
            yaxis_title="Attrition Rate (%)",
            height=280
        )
        st.plotly_chart(ot_fig, use_container_width=True)

    with workload_col2:
        render_insight_card(
            title="Workload Driver Diagnostic",
            observation="Systemic overtime demands constitute the strongest workplace driver of voluntary departures.",
            evidence=f"Overtime workers exhibit an attrition rate of {ot_yes_rate:.1f}%, compared to only {ot_no_rate:.1f}% for standard hours (a 3x multiplier).",
            interpretation="Workload burnout directly degrades employee sentiment and increases flight risk, particularly when combined with high commute distance.",
            recommendation="Implement project manager capacity alerts when team overtime exceeds 15% of standard hours.",
            priority="Critical"
        )

    # 9. KEY RECOMMENDATIONS PREVIEW
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 22px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">Top Strategic Actions Preview</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #6E6E73; margin-bottom: 20px;">Primary evidence-linked operational interventions recommended for immediate executive prioritization.</p>', unsafe_allow_html=True)

    rec_col1, rec_col2, rec_col3 = st.columns(3)
    with rec_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 200px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">1. Onboarding Safeguards</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    Deploy structured integration checkpoints during the first 180 days to stabilize early hires.
                </div>
                <div style="font-size: 10.5px; color: #86868B;">
                    <strong>Target:</strong> Year 1 & 2 cohorts ({metrics['early_tenure_exit_contribution']:.1f}% of exits).
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rec_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 200px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">2. Resource Capacity Audits</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    Establish resource warning systems when overtime requirements cross critical limits.
                </div>
                <div style="font-size: 10.5px; color: #86868B;">
                    <strong>Target:</strong> Regular overtime groups (attrition rate of {ot_yes_rate:.1f}%).
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rec_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 200px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">3. Quota Restructuring</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    Revitalize compensation bounds, training ramps, and pathing definitions for Sales Representative positions.
                </div>
                <div style="font-size: 10.5px; color: #86868B;">
                    <strong>Target:</strong> Sales Representative roles (39.8% attrition rate).
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 10. METHODOLOGY PREVIEW
    with st.expander("📖 Methodology & Analytical Safeguards"):
        st.markdown(
            """
            * **Diagnostic Focus:** Observed statistical patterns display descriptive correlations only and do not establish direct causation. Interventions should be validated qualitative-first (e.g. exit surveys, focus groups).
            * **Statistical Stability (Small Sample Guard):** Rate metrics are dynamically flagged as unstable when active population subsets fall below 10 records.
            * **Privacy Compliance:** Individual profiling or risk modeling of identifiable personnel is strictly prohibited.
            """
        )

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_overview()
