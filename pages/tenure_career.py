import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics, calculate_group_attrition
from utils.chart_theme import apply_apple_theme, COLOR_RETENTION, COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY
from components.page_header import render_page_header
from components.kpi_cards import render_kpi_card
from components.empty_states import render_empty_state
from components.footer import render_footer

def show_tenure_career():
    """
    Renders the Tenure and Career Stage page.
    """
    if "clean_df" not in st.session_state or st.session_state["clean_df"] is None:
        st.warning("Please upload or load the dataset first on the Methodology page.")
        return

    df = st.session_state["filtered_df"]
    raw_df = st.session_state["clean_df"]
    early_tenure_threshold = st.session_state.get("early_tenure_threshold", 2)

    total_count = len(raw_df)
    active_count = len(df)

    render_page_header(
        title="Tenure and Career Stage",
        subtitle="Understand the correlation between organizational tenure, career progression, and attrition",
        employee_count=active_count,
        total_count=total_count
    )

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    metrics = calculate_core_metrics(df, early_tenure_threshold)
    overall_rate = metrics["overall_attrition_rate"]
    exited_employees = metrics["exited_employees"]

    # 1. Early-Tenure Analytical Snapshot
    st.markdown(f'<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Early Tenure Analysis (Threshold: ≤ {early_tenure_threshold} Years)</h3>', unsafe_allow_html=True)
    
    col_early1, col_early2, col_early3 = st.columns(3)
    with col_early1:
        render_kpi_card(
            title=f"Early Tenure Cohort Size",
            value=f"{metrics['early_tenure_total']:,}",
            context=f"Employees ≤ {early_tenure_threshold} years tenure",
            tooltip="The number of active employees whose organizational tenure is at or below the selected threshold."
        )
    with col_early2:
        render_kpi_card(
            title=f"Early Tenure Attrition Rate",
            value=f"{metrics['early_tenure_attrition_rate']:.1f}%",
            context=f"Baseline: {overall_rate:.1f}%",
            trend_type="negative" if metrics['early_tenure_attrition_rate'] > overall_rate * 1.25 else "neutral",
            tooltip="The attrition rate calculated strictly within the early-tenure cohort."
        )
    with col_early3:
        render_kpi_card(
            title=f"Exit Contribution Share",
            value=f"{metrics['early_tenure_exit_contribution']:.1f}%",
            context="of all exits in active view",
            trend_type="warning" if metrics['early_tenure_exit_contribution'] > 40.0 else "neutral",
            tooltip="Exited early-tenure employees divided by all exited employees in the active view, multiplied by 100."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Tenure & Career Stages", "⏰ Role Transitions & Promotions", "🤝 Manager Continuity"])

    with tab1:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Tenure Band & Career Stage Attrition</h3>', unsafe_allow_html=True)
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            # Tenure Band
            tenure_data = calculate_group_attrition(df, "TenureBand", overall_rate, exited_employees)
            tenure_data = tenure_data.set_index("Group").reindex(['Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11–15 years', '16+ years']).dropna(subset=["Headcount"]).reset_index()

            tenure_fig = go.Figure(data=[go.Bar(
                x=tenure_data["Group"],
                y=tenure_data["Attrition Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=tenure_data[["Headcount", "Exited"]].values
            )])
            tenure_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(tenure_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                tenure_fig, 
                title="Attrition Rate by Tenure Band", 
                xaxis_title="Tenure at Company", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(tenure_fig, use_container_width=True)

        with col_t2:
            # Career Stage
            career_data = calculate_group_attrition(df, "CareerStage", overall_rate, exited_employees)
            career_data = career_data.set_index("Group").reindex([
                'Early Career: 0–5 years', 
                'Developing Career: 6–10 years', 
                'Mid-Career: 11–20 years', 
                'Experienced: 21–30 years', 
                'Senior Career: 31+ years'
            ]).dropna(subset=["Headcount"]).reset_index()

            career_fig = go.Figure(data=[go.Bar(
                x=career_data["Group"],
                y=career_data["Attrition Rate"],
                marker_color=COLOR_NEUTRAL_GREY,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=career_data[["Headcount", "Exited"]].values
            )])
            career_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(career_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                career_fig, 
                title="Attrition Rate by Career Stage (Total Experience)", 
                xaxis_title="Career Cohort", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            # Shorten labels for x-axis visual spacing
            short_labels = ['Early (0–5y)', 'Dev (6–10y)', 'Mid (11–20y)', 'Exp (21–30y)', 'Senior (31y+)']
            career_fig.update_xaxes(tickvals=list(range(len(short_labels))), ticktext=short_labels)
            st.plotly_chart(career_fig, use_container_width=True)

        # Exact years line graph
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-top: 10px; margin-bottom: 12px;">Exact Years at Company Trend</h3>', unsafe_allow_html=True)
        
        # Calculate attrition rate for exact years
        years_df = df.groupby("YearsAtCompany").agg(
            Headcount=('Attrition', 'count'),
            Exited=('Attrition', lambda x: (x == 1).sum())
        ).reset_index()
        years_df["Rate"] = (years_df["Exited"] / years_df["Headcount"] * 100).round(2)
        
        # Warn if headcount is small for specific points
        years_df["Label"] = years_df.apply(
            lambda row: f"{row['YearsAtCompany']}y (Rate: {row['Rate']:.1f}%, N={int(row['Headcount'])})", axis=1
        )
        # We filter out extremely long tenures to avoid visual stretching if count is 0
        years_df_filtered = years_df[years_df["YearsAtCompany"] <= 20]
        
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=years_df_filtered["YearsAtCompany"],
            y=years_df_filtered["Rate"],
            mode='lines+markers',
            line=dict(color=COLOR_ACCENT_BLUE, width=2.5),
            marker=dict(size=8, color=COLOR_ACCENT_BLUE),
            text=years_df_filtered["Label"],
            hovertemplate="<b>%{text}</b><extra></extra>"
        ))
        
        line_fig.add_shape(
            type="line",
            x0=0, y0=overall_rate,
            x1=20, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        
        apply_apple_theme(
            line_fig, 
            title="Attrition Rate by Exact Years at Company (0 to 20 Years)", 
            xaxis_title="Years at Company", 
            yaxis_title="Observed Attrition Rate (%)", 
            height=280
        )
        st.plotly_chart(line_fig, use_container_width=True)

    with tab2:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Role Transitions & Promotions Analysis</h3>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            # Current Role Tenure
            role_ten_df = df.groupby("YearsInCurrentRole").agg(
                Headcount=('Attrition', 'count'),
                Exited=('Attrition', lambda x: (x == 1).sum())
            ).reset_index()
            role_ten_df["Rate"] = (role_ten_df["Exited"] / role_ten_df["Headcount"] * 100).round(2)
            role_ten_filtered = role_ten_df[role_ten_df["YearsInCurrentRole"] <= 15]

            rt_fig = go.Figure(data=[go.Bar(
                x=role_ten_filtered["YearsInCurrentRole"],
                y=role_ten_filtered["Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                hovertemplate="<b>%{x} Years in Current Role</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=role_ten_filtered[["Headcount"]].values
            )])
            rt_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=15.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                rt_fig, 
                title="Attrition Rate by Years in Current Role", 
                xaxis_title="Years in Current Role", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(rt_fig, use_container_width=True)

        with col_p2:
            # Promotion Stagnation
            stagnation_data = calculate_group_attrition(df, "PromotionStagnation", overall_rate, exited_employees)
            stagnation_data = stagnation_data.set_index("Group").reindex(['0 years', '1–2 years', '3–5 years', '6–10 years', '11+ years']).dropna(subset=["Headcount"]).reset_index()

            prom_fig = go.Figure(data=[go.Bar(
                x=stagnation_data["Group"],
                y=stagnation_data["Attrition Rate"],
                marker_color=COLOR_NEUTRAL_GREY,
                hovertemplate="<b>%{x} Since Last Promotion</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=stagnation_data[["Headcount", "Exited"]].values
            )])
            prom_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(stagnation_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                prom_fig, 
                title="Attrition Rate by Years Since Last Promotion", 
                xaxis_title="Interval Since Promotion", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(prom_fig, use_container_width=True)

        # Interpretation warning note on Promotions
        st.markdown(
            """
            <div style="font-size: 12px; color: #86868B; line-height: 1.4; margin-top: 10px;">
                * <strong>Promotion Interval Limitation:</strong> An interval of "0 years" represents either newly hired employees or 
                those recently promoted. Conversely, longer promotion intervals (e.g. 11+ years) may represent structural ceilings normal 
                for highly senior leadership levels or specific career pathways. These intervals must be validated against job level before assuming stagnation.
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab3:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Manager Continuity Analysis</h3>', unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            # Group by YearsWithCurrManager
            m_ten_df = df.groupby("YearsWithCurrManager").agg(
                Headcount=('Attrition', 'count'),
                Exited=('Attrition', lambda x: (x == 1).sum())
            ).reset_index()
            m_ten_df["Rate"] = (m_ten_df["Exited"] / m_ten_df["Headcount"] * 100).round(2)
            m_ten_filtered = m_ten_df[m_ten_df["YearsWithCurrManager"] <= 15]

            mgr_fig = go.Figure(data=[go.Bar(
                x=m_ten_filtered["YearsWithCurrManager"],
                y=m_ten_filtered["Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                hovertemplate="<b>%{x} Years with Current Manager</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=m_ten_filtered[["Headcount"]].values
            )])
            mgr_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=15.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                mgr_fig, 
                title="Attrition Rate by Years Working with Current Manager", 
                xaxis_title="Years with Manager", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(mgr_fig, use_container_width=True)

        with col_m2:
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Key Observations on Leadership & Manager Continuity</p>', unsafe_allow_html=True)
            st.markdown(
                """
                <div style="font-size: 13.5px; color: #333333; line-height: 1.5;">
                    <ul>
                        <li style="margin-bottom: 8px;"><strong>Onboarding Transition Period:</strong> Exits often show spikes within the first 
                        year working under a new manager (< 1 year). This can indicate alignment friction or standard reorganization transitions.</li>
                        <li style="margin-bottom: 8px;"><strong>Relational Stability:</strong> Employees with long-standing tenure under the 
                        same manager (e.g. 5+ years) exhibit significantly stabilized attrition rates, suggesting leadership continuity promotes retention.</li>
                        <li style="margin-bottom: 8px;"><strong>Performance Ethics:</strong> This analysis evaluates group-level tenure trends. 
                        It must never be used to grade or profile individual managers or attribute exits to particular leadership personalities.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    render_footer(active_count)

if __name__ == "__main__":
    show_tenure_career()
