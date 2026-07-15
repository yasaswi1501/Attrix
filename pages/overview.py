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
from components.insight_cards import render_dynamic_insight_card
from components.status_strip import render_status_strip
from components.disclaimer import (
    render_academic_disclaimer,
    render_causation_disclaimer,
    render_statistical_limitation
)
from components.page_header import render_page_header
from services.insights_engine import ExecutiveInsightsEngine

def show_overview():
    """
    Renders the premium flagship Executive Overview page.
    """
    # Fetch session data
    if "clean_df" not in st.session_state or st.session_state["clean_df"] is None:
        st.warning("Please upload or load the dataset first on the Methodology page.")
        return

    df = st.session_state["filtered_df"]
    raw_df = st.session_state["clean_df"]
    early_tenure_threshold = st.session_state.get("early_tenure_threshold", 2)
    completeness_pct = st.session_state.get("completeness_pct", 100.0)

    total_count = len(raw_df)
    active_count = len(df)

    # 1. PAGE HEADER (Replacing manual hero implementation)
    render_page_header(
        title="Attrix",
        subtitle="Enterprise Workforce Intelligence",
        employee_count=active_count,
        total_count=total_count
    )

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

    # Fetch dynamic insights
    insights = ExecutiveInsightsEngine.generate_overview_insights(df, early_tenure_threshold)

    # Supporting description rendered below the page header
    st.markdown(
        """
        <p style="font-size: 13.5px; color: #A1A1AA; line-height: 1.45; margin-bottom: 20px; margin-top: -16px;">
            Understand attrition patterns, organizational concentration areas, and workforce risk signals through clear, evidence-based analytics.
        </p>
        """,
        unsafe_allow_html=True
    )

    # 2. STATUS STRIP (With dynamic baseline parameters)
    has_filters = len(st.session_state.get("sidebar_filters", {})) > 0
    render_status_strip(
        active_count=active_count,
        total_count=total_count,
        completeness_pct=completeness_pct,
        early_tenure_threshold=early_tenure_threshold,
        has_filters=has_filters,
        baseline_rate=baseline_rate
    )

    # 3. BUSINESS QUESTION BANNER
    st.markdown(
        f"""
        <div class="filter-chip" style="background-color: rgba(59, 130, 246, 0.08); color: #3B82F6; font-weight: 500; margin-bottom: 20px; border: 1px solid rgba(59, 130, 246, 0.15);">
            ❓ Business Question: What workforce patterns require immediate executive attention?
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. CORE WORKFORCE SNAPSHOT CARDS
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Core Workforce Snapshot</h3>', unsafe_allow_html=True)
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
            context="Overall voluntary exits",
            trend_text=trend_text,
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
            context="Tenure <= threshold",
            trend_text=early_trend_text,
            trend_type=early_trend_type,
            tooltip=f"Attrition rate of employees with tenure <= {early_tenure_threshold} years."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. LEADERSHIP ATTENTION CARDS
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Leadership Attention</h3>', unsafe_allow_html=True)
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 140px; border-left: 4px solid #EF4444; padding: 14px; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #EF4444; text-transform: uppercase; margin-bottom: 4px;">Departmental Risk</div>
                <div style="font-size: 16px; font-weight: 700; color: #F4F4F5; margin-bottom: 4px;">{insights['department']['name']}</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.35;">Exceeds baseline by {top_dept['Attrition Rate'] - metrics['overall_attrition_rate']:+.1f} pp in view.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with summary_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 140px; border-left: 4px solid #F59E0B; padding: 14px; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #F59E0B; text-transform: uppercase; margin-bottom: 4px;">Overtime Exposure</div>
                <div style="font-size: 16px; font-weight: 700; color: #F4F4F5; margin-bottom: 4px;">{ot_yes_rate:.1f}% Attrition</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.35;">Overtime acts as a key differentiator on departures.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with summary_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 140px; border-left: 4px solid #3B82F6; padding: 14px; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #3B82F6; text-transform: uppercase; margin-bottom: 4px;">Early-Tenure Exits</div>
                <div style="font-size: 16px; font-weight: 700; color: #F4F4F5; margin-bottom: 4px;">{metrics['early_tenure_exit_contribution']:.1f}% of Exits</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.35;">Concentrated within the first {early_tenure_threshold} years of service.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with summary_col4:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 140px; border-left: 4px solid #EF4444; padding: 14px; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #EF4444; text-transform: uppercase; margin-bottom: 4px;">Role Hotspot Risk</div>
                <div style="font-size: 16px; font-weight: 700; color: #F4F4F5; margin-bottom: 4px;">{insights['role']['name']}</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.35;">Highest observed functional risk concentration.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 6. DEPARTMENT AND ROLE INTELLIGENCE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 24px;">', unsafe_allow_html=True)
    
    col_intel1, col_intel2 = st.columns(2)
    
    with col_intel1:
        st.markdown('<h2 style="font-size: 20px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">Which departments exceed the organizational baseline?</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 13.5px; color: #A1A1AA; margin-bottom: 16px;">Analyze structural voluntary departure patterns and contributions across core functional units.</p>', unsafe_allow_html=True)
        
        # Department chart
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

        if top_dept is not None:
            render_dynamic_insight_card(
                title="Department Retention Diagnostic",
                finding=insights["department"]["finding"],
                recommendation=insights["department"]["recommendation"],
                confidence=insights["department"]["confidence"],
                owner=insights["department"]["owner"],
                priority=insights["department"]["priority"]
            )

    with col_intel2:
        st.markdown('<h2 style="font-size: 20px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">Which job roles show the strongest concentration of exits?</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 13.5px; color: #A1A1AA; margin-bottom: 16px;">Isolate specific job roles experiencing structural retention friction.</p>', unsafe_allow_html=True)
        
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

        if top_role is not None:
            render_dynamic_insight_card(
                title="Job Role Retention Diagnostic",
                finding=insights["role"]["finding"],
                recommendation=insights["role"]["recommendation"],
                confidence=insights["role"]["confidence"],
                owner=insights["role"]["owner"],
                priority=insights["role"]["priority"]
            )

    # 7. TENURE AND WORKLOAD INTELLIGENCE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    
    col_intel3, col_intel4 = st.columns(2)
    
    with col_intel3:
        st.markdown('<h2 style="font-size: 20px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">Are early-career employees leaving more often?</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 13.5px; color: #A1A1AA; margin-bottom: 16px;">Analyze if voluntary departures are concentrated in early-stage hires or long-tenured employees.</p>', unsafe_allow_html=True)
        
        # Tenure chart
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

        render_dynamic_insight_card(
            title="Tenure Retention Diagnostic",
            finding=insights["early_tenure"]["finding"],
            recommendation=insights["early_tenure"]["recommendation"],
            confidence=insights["early_tenure"]["confidence"],
            owner=insights["early_tenure"]["owner"],
            priority=insights["early_tenure"]["priority"]
        )

    with col_intel4:
        st.markdown('<h2 style="font-size: 20px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">Which workload factors deserve further investigation?</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 13.5px; color: #A1A1AA; margin-bottom: 16px;">Examine the correlation between overtime work, business travel demands, and employee turnover.</p>', unsafe_allow_html=True)
        
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

        render_dynamic_insight_card(
            title="Workload Driver Diagnostic",
            finding=insights["overtime"]["finding"],
            recommendation=insights["overtime"]["recommendation"],
            confidence=insights["overtime"]["confidence"],
            owner=insights["overtime"]["owner"],
            priority=insights["overtime"]["priority"]
        )

    # 8. RECOMMENDATIONS PREVIEW
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 20px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">Recommended leadership focus</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #A1A1AA; margin-bottom: 16px;">Primary evidence-linked operational interventions recommended for immediate executive prioritization.</p>', unsafe_allow_html=True)

    rec_col1, rec_col2, rec_col3 = st.columns(3)
    with rec_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 200px; border-top: 3px solid #3B82F6; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">1. Strengthen early-tenure onboarding</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.45; margin-bottom: 10px;">
                    Deploy structured integration checkpoints during the first 180 days to stabilize early hires.
                </div>
                <div style="font-size: 11px; color: #71717A; margin-bottom: 4px;">
                    <strong>Evidence:</strong> {metrics['early_tenure_attrition_rate']:.1f}% early-tenure attrition
                </div>
                <div style="font-size: 11px; color: #71717A; margin-bottom: 4px;">
                    <strong>Owner:</strong> HR Business Partner
                </div>
                <div style="font-size: 11px; color: #3B82F6; font-weight: 600;">
                    <strong>Priority:</strong> High
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rec_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 200px; border-top: 3px solid #3B82F6; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">2. Review overtime concentration</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.45; margin-bottom: 10px;">
                    Establish resource warning systems when overtime requirements cross critical limits.
                </div>
                <div style="font-size: 11px; color: #71717A; margin-bottom: 4px;">
                    <strong>Evidence:</strong> {ot_yes_rate - ot_no_rate:.1f} percentage-point difference
                </div>
                <div style="font-size: 11px; color: #71717A; margin-bottom: 4px;">
                    <strong>Owner:</strong> Department Leadership
                </div>
                <div style="font-size: 11px; color: #3B82F6; font-weight: 600;">
                    <strong>Priority:</strong> High
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rec_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 200px; border-top: 3px solid #EF4444; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #F4F4F5; margin-bottom: 6px;">3. Investigate top role retention</div>
                <div style="font-size: 11.5px; color: #A1A1AA; line-height: 1.45; margin-bottom: 10px;">
                    Revitalize compensation bounds, training ramps, and pathing definitions for highest risk positions.
                </div>
                <div style="font-size: 11px; color: #71717A; margin-bottom: 4px;">
                    <strong>Evidence:</strong> {top_role['Attrition Rate']:.1f}% observed attrition
                </div>
                <div style="font-size: 11px; color: #71717A; margin-bottom: 4px;">
                    <strong>Owner:</strong> HR Director
                </div>
                <div style="font-size: 11px; color: #EF4444; font-weight: 600;">
                    <strong>Priority:</strong> Critical
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 9. METHODOLOGY AND DISCLAIMER AREA
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    with st.expander("📖 Methodology & Analytical Disclaimers"):
        render_academic_disclaimer()
        render_causation_disclaimer()
        render_statistical_limitation()

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_overview()
