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
    COLOR_ATTENTION
)
from components.page_header import render_page_header
from components.kpi_cards import render_kpi_card
from components.empty_states import render_empty_state
from components.footer import render_footer
from components.insight_cards import render_insight_card
from components.disclaimer import render_information_panel

def show_tenure_career():
    """
    Renders the premium Tenure and Career Stage page.
    """
    if "clean_df" not in st.session_state or st.session_state["clean_df"] is None:
        st.warning("Please upload or load the dataset first on the Methodology page.")
        return

    df = st.session_state["filtered_df"]
    raw_df = st.session_state["clean_df"]
    early_tenure_threshold = st.session_state.get("early_tenure_threshold", 2)

    total_count = len(raw_df)
    active_count = len(df)

    # 1. PAGE HEADER
    render_page_header(
        title="Tenure & Career",
        subtitle="Understand how organizational tenure, career stage, role duration, promotion intervals, and manager continuity relate to observed attrition.",
        employee_count=active_count,
        total_count=total_count
    )

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    # Base calculations
    metrics = calculate_core_metrics(df, early_tenure_threshold)
    overall_rate = metrics["overall_attrition_rate"]
    exited_employees = metrics["exited_employees"]

    st.markdown(
        f"""
        <div class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 500; margin-bottom: 20px;">
            ❓ Business Question: At which career and tenure stages is workforce attrition most concentrated?
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. CAREER AND TENURE STATUS STRIP
    min_tenure = int(df["YearsAtCompany"].min()) if not df.empty else 0
    max_tenure = int(df["YearsAtCompany"].max()) if not df.empty else 40
    median_tenure = df["YearsAtCompany"].median() if not df.empty else 0.0
    num_stages = df["CareerStage"].nunique()

    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Tenure Range: {min_tenure}–{max_tenure} years</span>
            <span class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 500;">Early Tenure Threshold: {early_tenure_threshold} years</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Career Stages: {num_stages}</span>
            <span class="filter-chip" style="background-color: rgba(201, 121, 43, 0.06); color: #C9792B;">Median Tenure: {median_tenure:.1f} years</span>
            <span class="filter-chip" style="background-color: rgba(46, 125, 91, 0.06); color: #2E7D5B;">Filtered Population: {active_count:,}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Pre-calculate role-band structures dynamically
    role_bins = [-np.inf, 0.9, 2.1, 5.1, 10.1, np.inf]
    role_labels = ['Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11+ years']
    
    df_copy = df.copy()
    df_copy['RoleTenureBand'] = pd.cut(df_copy['YearsInCurrentRole'], bins=role_bins, labels=role_labels)
    df_copy['RoleTenureBand'] = pd.Categorical(df_copy['RoleTenureBand'], categories=role_labels, ordered=True)

    df_copy['ManagerContinuityBand'] = pd.cut(df_copy['YearsWithCurrManager'], bins=role_bins, labels=role_labels)
    df_copy['ManagerContinuityBand'] = pd.Categorical(df_copy['ManagerContinuityBand'], categories=role_labels, ordered=True)

    # 3. EXECUTIVE TENURE SUMMARY
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Tenure intelligence</h3>', unsafe_allow_html=True)
    
    tenure_data = calculate_group_attrition(df, "TenureBand", overall_rate, exited_employees)
    highest_tenure_band = tenure_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not tenure_data.empty else None
    
    career_data = calculate_group_attrition(df, "CareerStage", overall_rate, exited_employees)
    highest_career_stage = career_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not career_data.empty else None
    
    stagnation_data = calculate_group_attrition(df, "PromotionStagnation", overall_rate, exited_employees)
    highest_promo = stagnation_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not stagnation_data.empty else None

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        if highest_tenure_band is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Tenure Risk</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_tenure_band['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #B54747; margin-top: 4px;">{highest_tenure_band['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">{highest_tenure_band['Exited']} exits (N={highest_tenure_band['Headcount']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with t_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #0071E3; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Early Tenure Attrition</div>
                <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Cohort Risk (≤ {early_tenure_threshold}y)</div>
                <div style="font-size: 18px; font-weight: 700; color: #0071E3; margin-top: 4px;">{metrics['early_tenure_attrition_rate']:.1f}% Rate</div>
                <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Baseline: {overall_rate:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Early Exit Share</div>
                <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Total Exit Weight</div>
                <div style="font-size: 18px; font-weight: 700; color: #C9792B; margin-top: 4px;">{metrics['early_tenure_exit_contribution']:.1f}% Share</div>
                <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Departed within early tenure</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t_col4:
        if highest_career_stage is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #2E7D5B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Career Stage Attrition</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_career_stage['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #2E7D5B; margin-top: 4px;">{highest_career_stage['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">N={highest_career_stage['Headcount']} (Total working years)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 4. ORGANIZATIONAL TENURE ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Organizational Tenure Analysis</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">How does observed attrition vary across organizational tenure?</p>', unsafe_allow_html=True)

    col_org1, col_org2 = st.columns(2)
    with col_org1:
        # Attrition by tenure band
        tenure_data_ordered = tenure_data.set_index("Group").reindex(['Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11–15 years', '16+ years']).dropna(subset=["Headcount"]).reset_index()
        
        tenure_fig = go.Figure(data=[go.Bar(
            x=tenure_data_ordered["Group"],
            y=tenure_data_ordered["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=tenure_data_ordered[["Exited", "Headcount"]].values
        )])
        tenure_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(tenure_data_ordered)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(tenure_fig, title="Attrition Rate by Tenure Band", xaxis_title="Tenure at Company", yaxis_title="Attrition Rate (%)", height=240)
        st.plotly_chart(tenure_fig, use_container_width=True)

    with col_org2:
        # Exact YearsAtCompany distribution
        years_df = df.groupby("YearsAtCompany").agg(
            Headcount=('Attrition', 'count'),
            Exited=('Attrition', lambda x: (x == 1).sum())
        ).reset_index()
        years_df["Rate"] = (years_df["Exited"] / years_df["Headcount"] * 100).round(2)
        years_df_filtered = years_df[years_df["YearsAtCompany"] <= 20]
        
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=years_df_filtered["YearsAtCompany"],
            y=years_df_filtered["Rate"],
            mode='lines+markers',
            line=dict(color=COLOR_ACCENT_BLUE, width=2.5),
            marker=dict(size=6, color=COLOR_ACCENT_BLUE),
            hovertemplate="<b>Years at Company: %{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        ))
        line_fig.add_shape(
            type="line",
            x0=0, y0=overall_rate,
            x1=20, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(line_fig, title="Observed attrition by years at company", xaxis_title="Years at Company", yaxis_title="Observed Attrition Rate (%)", height=240)
        st.plotly_chart(line_fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #86868B; margin-top: -8px; margin-bottom: 20px; line-height: 1.4;">
            *Note: Observed voluntary departures are heavily front-loaded in the first two years, stabilizing significantly as employees accumulate years at the company.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 5. EARLY-TENURE ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Early-tenure workforce</h3>', unsafe_allow_html=True)

    col_ea1, col_ea2 = st.columns(2)
    with col_ea1:
        st.markdown(f'<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">Early-tenure vs established-tenure comparison</h4>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="apple-card" style="background-color: #FBFBFD; padding: 14px 16px; margin-bottom: 12px;">
                <div style="font-size: 11px; color: #86868B; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">Early Tenure Rates (≤ {early_tenure_threshold} Years)</div>
                <div style="font-size: 20px; font-weight: 700; color: #1D1D1F;">{metrics['early_tenure_attrition_rate']:.1f}% Attrition</div>
                <div style="font-size: 12px; color: #6E6E73; margin-top: 4px;">Size: {metrics['early_tenure_total']:,} employees | Exits: {metrics['early_tenure_exits']:,}</div>
            </div>
            <div class="apple-card" style="background-color: #FBFBFD; padding: 14px 16px;">
                <div style="font-size: 11px; color: #86868B; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">Established Tenure Rates ({early_tenure_threshold}+ Years)</div>
                <div style="font-size: 20px; font-weight: 700; color: #2E7D5B;">{(metrics['exited_employees'] - metrics['early_tenure_exits']) / max(1, metrics['total_employees'] - metrics['early_tenure_total']) * 100:.1f}% Attrition</div>
                <div style="font-size: 12px; color: #6E6E73; margin-top: 4px;">Percentage point difference: {metrics['early_tenure_attrition_rate'] - ((metrics['exited_employees'] - metrics['early_tenure_exits']) / max(1, metrics['total_employees'] - metrics['early_tenure_total']) * 100):+.1f} pp</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ea2:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">Where are early-tenure exits concentrated?</h4>', unsafe_allow_html=True)
        
        early_data_sel = st.segmented_control(
            "Filter Concentration By",
            options=["Department", "Job Role"],
            default="Department",
            key="early_tenure_concentration_sel"
        )
        if not early_data_sel:
            early_data_sel = "Department"

        early_sub_df = df[df["YearsAtCompany"] <= early_tenure_threshold]
        
        if early_sub_df.empty:
            st.info("No early-tenure employees meet current criteria.")
        else:
            group_col = "Department" if early_data_sel == "Department" else "JobRole"
            early_group = early_sub_df.groupby(group_col).agg(
                Headcount=("Attrition", "count"),
                Exits=("Attrition", "sum")
            ).reset_index()
            early_group["Rate"] = (early_group["Exits"] / early_group["Headcount"] * 100).fillna(0)
            early_group = early_group.sort_values(by="Exits", ascending=True)

            early_conc_fig = go.Figure(data=[go.Bar(
                x=early_group["Exits"],
                y=early_group[group_col],
                orientation='h',
                marker_color=COLOR_NEUTRAL_GREY,
                width=0.4,
                hovertemplate="<b>%{y}</b><br>Early Exits: %{x}<br>Early Cohort Rate: %{customdata[0]:.1f}%<extra></extra>",
                customdata=early_group[["Rate"]].values
            )])
            apply_apple_theme(early_conc_fig, title="", xaxis_title="Early Exit Count", yaxis_title="", height=200)
            st.plotly_chart(early_conc_fig, use_container_width=True)

    # 6. CAREER-STAGE ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Career-stage intelligence</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Evaluate how overall career stages correspond to voluntary departures.</p>', unsafe_allow_html=True)

    career_data_ordered = career_data.set_index("Group").reindex([
        'Early Career: 0–5 years', 
        'Developing Career: 6–10 years', 
        'Mid-Career: 11–20 years', 
        'Experienced: 21–30 years', 
        'Senior Career: 31+ years'
    ]).dropna(subset=["Headcount"]).reset_index()

    career_fig = go.Figure(data=[go.Bar(
        x=career_data_ordered["Group"],
        y=career_data_ordered["Attrition Rate"],
        marker_color=COLOR_ACCENT_BLUE,
        width=0.4,
        hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
        customdata=career_data_ordered[["Exited", "Headcount"]].values
    )])
    career_fig.add_shape(
        type="line",
        x0=-0.5, y0=overall_rate,
        x1=len(career_data_ordered)-0.5, y1=overall_rate,
        line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
    )
    apply_apple_theme(career_fig, title="Observed Attrition by Professional Career Stage", xaxis_title="", yaxis_title="Attrition Rate (%)", height=240)
    st.plotly_chart(career_fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #86868B; margin-top: -8px; margin-bottom: 20px; line-height: 1.4;">
            *Career stage is derived from total professional experience and is distinct from organizational tenure. Early-career cohorts experience elevated rates.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 7. CURRENT-ROLE AND PROMOTION ANALYSIS (Tabs and ordered bands)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Role Transitions & Promotions Analysis</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Examine the correlation between time in current role and interval since last promotion.</p>', unsafe_allow_html=True)

    prog_tab1, prog_tab2 = st.tabs(["⏰ Years in current role", "⏳ Time since last promotion"])
    
    with prog_tab1:
        # Years in current role
        role_ten_data = calculate_group_attrition(df_copy, "RoleTenureBand", overall_rate, exited_employees)
        role_ten_data = role_ten_data.set_index("Group").reindex(['Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11+ years']).dropna(subset=["Headcount"]).reset_index()

        rt_fig = go.Figure(data=[go.Bar(
            x=role_ten_data["Group"],
            y=role_ten_data["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        )])
        rt_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(role_ten_data)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(rt_fig, title="", xaxis_title="Years in Current Role", yaxis_title="Attrition Rate (%)", height=240)
        st.plotly_chart(rt_fig, use_container_width=True)

    with prog_tab2:
        # Time since last promotion
        prom_fig = go.Figure(data=[go.Bar(
            x=stagnation_data["Group"],
            y=stagnation_data["Attrition Rate"],
            marker_color=COLOR_NEUTRAL_GREY,
            width=0.4,
            hovertemplate="<b>%{x} since last promotion</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        )])
        prom_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(stagnation_data)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(prom_fig, title="", xaxis_title="Time Since Last Promotion", yaxis_title="Attrition Rate (%)", height=240)
        st.plotly_chart(prom_fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #86868B; margin-top: -8px; margin-bottom: 20px; line-height: 1.4;">
            *Longer promotion intervals may be normal for certain senior roles and should be interpreted alongside job level, tenure, and organizational context.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 8. MANAGER-CONTINUITY ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Manager continuity</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">❓ Business Question: How does time with the current manager relate to observed attrition?</p>', unsafe_allow_html=True)

    mgr_ten_data = calculate_group_attrition(df_copy, "ManagerContinuityBand", overall_rate, exited_employees)
    mgr_ten_data = mgr_ten_data.set_index("Group").reindex(['Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11+ years']).dropna(subset=["Headcount"]).reset_index()

    mgr_fig = go.Figure(data=[go.Bar(
        x=mgr_ten_data["Group"],
        y=mgr_ten_data["Attrition Rate"],
        marker_color=COLOR_ACCENT_BLUE,
        width=0.4,
        hovertemplate="<b>%{x} with manager</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
    )])
    mgr_fig.add_shape(
        type="line",
        x0=-0.5, y0=overall_rate,
        x1=len(mgr_ten_data)-0.5, y1=overall_rate,
        line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
    )
    apply_apple_theme(mgr_fig, title="", xaxis_title="Years with Manager", yaxis_title="Attrition Rate (%)", height=240)
    st.plotly_chart(mgr_fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #86868B; margin-top: -8px; margin-bottom: 20px; line-height: 1.4;">
            *This analysis reflects manager-tenure duration only and does not assess individual manager performance.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 9. TENURE HOTSPOT EXPLORER
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Where are tenure-related hotspots concentrated?</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Cross-tabulate career progression attributes with operational attributes to isolate focus areas.</p>', unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        primary_dim = st.selectbox(
            "Primary Tenure Dimension",
            options=["TenureBand", "CareerStage", "RoleTenureBand", "PromotionStagnation", "ManagerContinuityBand"],
            index=0,
            key="tenure_explorer_primary"
        )
    with col_ctrl2:
        secondary_dim = st.selectbox(
            "Secondary Operational Dimension",
            options=["Department", "JobRole", "JobLevel", "OverTime", "BusinessTravel"],
            index=0,
            key="tenure_explorer_secondary"
        )

    # Pivot calculations
    pivot_df = df_copy.groupby([primary_dim, secondary_dim]).agg(
        Headcount=("Attrition", "count"),
        Exited=("Attrition", "sum")
    ).reset_index()
    pivot_df["Rate"] = (pivot_df["Exited"] / pivot_df["Headcount"] * 100).fillna(0)

    # Grouped bar chart
    cross_fig = go.Figure()
    categories = sorted(pivot_df[primary_dim].unique())
    subcategories = sorted(pivot_df[secondary_dim].unique())
    
    for subcat in subcategories:
        sub_data = pivot_df[pivot_df[secondary_dim] == subcat]
        sub_data = sub_data.set_index(primary_dim).reindex(categories).fillna(0).reset_index()
        
        cross_fig.add_trace(go.Bar(
            x=sub_data[primary_dim],
            y=sub_data["Rate"],
            name=str(subcat),
            hovertemplate="<b>%{x} (" + str(subcat) + ")</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=sub_data[["Exited", "Headcount"]].values
        ))

    apply_apple_theme(
        cross_fig,
        title=f"Observed Attrition: {primary_dim} Segmented by {secondary_dim}",
        xaxis_title=primary_dim,
        yaxis_title="Attrition Rate (%)",
        show_legend=True,
        height=320
    )
    st.plotly_chart(cross_fig, use_container_width=True)

    # 10. DETAILED TENURE TABLE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Tenure and career segment details</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Ledger of career progression bands sorted by attrition metrics.</p>', unsafe_allow_html=True)

    table_rows = []
    for dim, ddf in [("Tenure Band", tenure_data), ("Career Stage", career_data), 
                     ("Promotion Interval", stagnation_data), 
                     ("Years In Current Role", role_ten_data), ("Years With Manager", mgr_ten_data)]:
        ddf = ddf.copy()
        ddf["Dimension"] = dim
        ddf = ddf.rename(columns={"Group": "Segment"})
        table_rows.append(ddf)
        
    table_df = pd.concat(table_rows)[["Dimension", "Segment", "Headcount", "Exited", "Retained", "Attrition Rate", "Exit Contribution", "Baseline Difference", "Relative Index"]]
    table_df["Sample Size Status"] = table_df["Headcount"].apply(lambda hc: "Small Sample" if hc < 15 else "Sufficient")
    table_df = table_df.sort_values(by="Attrition Rate", ascending=False)

    st.dataframe(
        table_df,
        column_config={
            "Dimension": st.column_config.TextColumn("Dimension Group"),
            "Segment": st.column_config.TextColumn("Tenure & Progression Band"),
            "Headcount": st.column_config.NumberColumn("Headcount", format="%d"),
            "Exited": st.column_config.NumberColumn("Exited", format="%d"),
            "Retained": st.column_config.NumberColumn("Retained", format="%d"),
            "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
            "Exit Contribution": st.column_config.NumberColumn("Exit Contribution Share", format="%.1f%%"),
            "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp"),
            "Relative Index": st.column_config.NumberColumn("Relative Index", format="%.2fx"),
            "Sample Size Status": st.column_config.TextColumn("Sample size status")
        },
        hide_index=True,
        use_container_width=True
    )

    # 11. LEADERSHIP IMPLICATIONS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">What should leadership investigate next?</h3>', unsafe_allow_html=True)
    
    col_impl1, col_impl2, col_impl3 = st.columns(3)
    with col_impl1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 220px; border-top: 3px solid #B54747; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">1. Early Tenure Transitions</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Finding:</strong> Employees with ≤ {early_tenure_threshold} years tenure show elevated attrition of {metrics['early_tenure_attrition_rate']:.1f}%.
                </div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Action:</strong> Audit early onboarding consistency, mentoring loops, and manager alignment checkpoints.
                </div>
                <div style="font-size: 10px; color: #86868B;">
                    <strong>Owner:</strong> Talent Management BP
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_impl2:
        if highest_career_stage is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">2. Professional Career Stages</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> The {highest_career_stage['Group']} segment exhibits higher observed rates.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Review career progression tracks and paths for high-mobility cohorts.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Learning & Development Partner
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_impl3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 220px; border-top: 3px solid #C9792B; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">3. Time Since Last Promotion</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Finding:</strong> Stagnation intervals correlate with role durations.
                </div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Action:</strong> Audit transition paths alongside senior job structures to prevent bottlenecks.
                </div>
                <div style="font-size: 10px; color: #86868B;">
                    <strong>Owner:</strong> Compensation Specialist
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 12. METHODOLOGY AND LIMITATIONS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    with st.expander("📖 Methodology & progression limits explanation"):
        render_information_panel(
            title="Analysis Limitation & Causal Notice",
            text="Career progression and tenure indicators reflect statistical associations within historical records. "
                 "Longer promotion intervals may represent normal ceilings in senior leadership roles and must be validated contextually before drawing conclusions."
        )
        st.markdown(
            """
            * **Tenure Band Groups:** Categorized into standard bands ('Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11–15 years', '16+ years').
            * **Career Stages:** Derived from `TotalWorkingYears` to reflect overall industry experience.
            * **Early-Tenure Rate:** Calculated within the `≤ Threshold` subset.
            """
        )

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_tenure_career()
