import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics, calculate_group_attrition, calculate_workload_attrition_matrix
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

def show_workload_mobility():
    """
    Renders the premium Workload and Mobility page.
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
        title="Workload & Mobility",
        subtitle="Examine how overtime, business travel, commute distance, work-life balance, satisfaction, and involvement relate to observed attrition.",
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
            ❓ Business Question: Which workload and mobility patterns deserve leadership attention?
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. WORKLOAD STATUS STRIP
    num_ot = df["OverTime"].nunique()
    num_travel = df["BusinessTravel"].nunique()
    min_dist = int(df["DistanceFromHome"].min()) if not df.empty else 1
    max_dist = int(df["DistanceFromHome"].max()) if not df.empty else 29
    num_wlb = df["WorkLifeBalanceLabel"].nunique()

    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Overtime: {num_ot} groups</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Travel: {num_travel} groups</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Distance: {min_dist}–{max_dist}</span>
            <span class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 500;">Work-Life Balance: {num_wlb} levels</span>
            <span class="filter-chip" style="background-color: rgba(46, 125, 91, 0.06); color: #2E7D5B;">Filtered Population: {active_count:,}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Precalculate datasets
    ot_data = calculate_group_attrition(df, "OvertimeGroup", overall_rate, exited_employees)
    travel_data = calculate_group_attrition(df, "TravelGroup", overall_rate, exited_employees)
    travel_data_ordered = travel_data.set_index("Group").reindex(['Non-Travel', 'Travel Rarely', 'Travel Frequently']).dropna(subset=["Headcount"]).reset_index()
    
    dist_data = calculate_group_attrition(df, "DistanceBand", overall_rate, exited_employees)
    wlb_data = calculate_group_attrition(df, "WorkLifeBalanceLabel", overall_rate, exited_employees)
    wlb_data_ordered = wlb_data.set_index("Group").reindex(['Poor', 'Fair', 'Good', 'Excellent']).dropna(subset=["Headcount"]).reset_index()

    # 3. EXECUTIVE WORKLOAD SUMMARY
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Workload intelligence</h3>', unsafe_allow_html=True)
    
    highest_ot = ot_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not ot_data.empty else None
    lowest_ot = ot_data.sort_values(by="Attrition Rate", ascending=True).iloc[0] if not ot_data.empty else None
    highest_travel = travel_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not travel_data.empty else None
    highest_wlb = wlb_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not wlb_data.empty else None
    highest_dist = dist_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not dist_data.empty else None

    wl_col1, wl_col2, wl_col3, wl_col4 = st.columns(4)
    with wl_col1:
        if highest_ot is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Overtime Attrition</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{highest_ot['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #B54747; margin-top: 4px;">{highest_ot['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">{highest_ot['Exited']} exits (N={highest_ot['Headcount']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with wl_col2:
        if lowest_ot is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #2E7D5B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">No-Overtime Attrition</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{lowest_ot['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #2E7D5B; margin-top: 4px;">{lowest_ot['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Baseline comparison: {lowest_ot['Attrition Rate'] - overall_rate:+.1f} pp</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with wl_col3:
        if highest_travel is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Risk Travel</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_travel['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #C9792B; margin-top: 4px;">{highest_travel['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">N={highest_travel['Headcount']} Active</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with wl_col4:
        if highest_wlb is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #0071E3; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest WLB Risk</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_wlb['Group']} Balance</div>
                    <div style="font-size: 18px; font-weight: 700; color: #0071E3; margin-top: 4px;">{highest_wlb['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Relative index: {highest_wlb['Relative Index']:.2f}x</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 4. OVERTIME ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Overtime Analysis</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">How does overtime relate to observed attrition?</p>', unsafe_allow_html=True)

    col_ot1, col_ot2 = st.columns(2)
    with col_ot1:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">Overtime attrition comparison</h4>', unsafe_allow_html=True)
        ot_fig = go.Figure(data=[go.Bar(
            x=ot_data["Group"],
            y=ot_data["Attrition Rate"],
            marker_color=[COLOR_RETENTION, COLOR_ELEVATED_RISK],
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
            customdata=ot_data[["Headcount"]].values
        )])
        ot_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=1.5, y1=overall_rate,
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        apply_apple_theme(ot_fig, title="", xaxis_title="", yaxis_title="Attrition Rate (%)", height=200)
        st.plotly_chart(ot_fig, use_container_width=True)

    with col_ot2:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">Where is overtime-related attrition concentrated?</h4>', unsafe_allow_html=True)
        
        ot_sub_sel = st.segmented_control(
            "Filter Concentration By",
            options=["Department", "Job Role", "Job Level"],
            default="Department",
            key="overtime_concentration_sel"
        )
        if not ot_sub_sel:
            ot_sub_sel = "Department"

        ot_sub_df = df[df["OverTime"] == "Yes"]
        
        if ot_sub_df.empty:
            st.info("No overtime employees meet current criteria.")
        else:
            ot_group = ot_sub_df.groupby(ot_sub_sel).agg(
                Headcount=("Attrition", "count"),
                Exited=("Attrition", "sum")
            ).reset_index()
            ot_group["Rate"] = (ot_group["Exits"] / ot_group["Headcount"] * 100).fillna(0)
            ot_group = ot_group.sort_values(by="Exits", ascending=True)

            ot_conc_fig = go.Figure(data=[go.Bar(
                x=ot_group["Exits"],
                y=ot_group[ot_sub_sel],
                orientation='h',
                marker_color=COLOR_NEUTRAL_GREY,
                width=0.4,
                hovertemplate="<b>%{y}</b><br>Exits: %{x}<br>Rate: %{customdata[0]:.1f}%<extra></extra>",
                customdata=ot_group[["Rate"]].values
            )])
            apply_apple_theme(ot_conc_fig, title="", xaxis_title="Exit Count", yaxis_title="", height=200)
            st.plotly_chart(ot_conc_fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #86868B; margin-top: -8px; margin-bottom: 20px; line-height: 1.4;">
            *Note: Sustained overtime requirements remain the single largest behavioral differentiator of departures in historical views.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 5. BUSINESS-TRAVEL ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Business travel intelligence</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Examine how travel requirements correspond to voluntary departures.</p>', unsafe_allow_html=True)

    travel_fig = go.Figure(data=[go.Bar(
        x=travel_data_ordered["Group"],
        y=travel_data_ordered["Attrition Rate"],
        marker_color=COLOR_ACCENT_BLUE,
        width=0.4,
        hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
        customdata=travel_data_ordered[["Headcount"]].values
    )])
    travel_fig.add_shape(
        type="line",
        x0=-0.5, y0=overall_rate,
        x1=len(travel_data_ordered)-0.5, y1=overall_rate,
        line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
    )
    apply_apple_theme(travel_fig, title="", xaxis_title="", yaxis_title="Attrition Rate (%)", height=220)
    st.plotly_chart(travel_fig, use_container_width=True)

    # 6. OVERTIME × TRAVEL WORKLOAD MATRIX
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Which overtime and travel combinations show elevated observed attrition?</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Cross-tabulate overtime demands and travel frequencies to identify high-pressure combinations.</p>', unsafe_allow_html=True)

    matrix_metric = st.selectbox(
        "Select Matrix Metric",
        options=["Attrition Rate (%)", "Exit Count", "Workload Attrition Index"],
        index=0,
        key="workload_mobility_matrix_metric"
    )

    wl_matrix = calculate_workload_attrition_matrix(df, overall_rate)
    
    if not wl_matrix.empty:
        pivot_index = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Workload Attrition Index").fillna(1.0)
        pivot_count = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Headcount").fillna(0)
        pivot_exits = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Exited").fillna(0)
        pivot_rate = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Attrition Rate").fillna(0)

        # Align rows
        row_align = ['Non-Travel', 'Travel Rarely', 'Travel Frequently']
        pivot_index = pivot_index.reindex(row_align)
        pivot_count = pivot_count.reindex(row_align)
        pivot_exits = pivot_exits.reindex(row_align)
        pivot_rate = pivot_rate.reindex(row_align)

        if matrix_metric == "Attrition Rate (%)":
            z_data = pivot_rate
            color_scale = "Reds"
            z_suffix = "%"
        elif matrix_metric == "Exit Count":
            z_data = pivot_exits
            color_scale = "Purples"
            z_suffix = ""
        else:
            z_data = pivot_index
            color_scale = "Oranges"
            z_suffix = "x"

        wl_fig = go.Figure(data=go.Heatmap(
            z=z_data.values,
            x=z_data.columns,
            y=z_data.index,
            colorscale=color_scale,
            hovertemplate="<b>OT: %{x}</b><br>Travel: %{y}<br>Metric: %{z:.2f}" + z_suffix + "<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
            customdata=np.dstack((pivot_count.values, pivot_exits.values))
        ))
        apply_apple_theme(wl_fig, title="", xaxis_title="Overtime Work", yaxis_title="Business Travel", height=240)
        st.plotly_chart(wl_fig, use_container_width=True)

    # 7. DISTANCE-FROM-HOME ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Commute-distance intelligence</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">❓ Business Question: How does observed attrition vary with distance from home?</p>', unsafe_allow_html=True)

    col_dist1, col_dist2 = st.columns(2)
    with col_dist1:
        # Distance bands ordered bar
        dist_data_ordered = dist_data.set_index("Group").reindex(['0–5', '6–10', '11–20', '21+']).dropna(subset=["Headcount"]).reset_index()
        
        dist_fig = go.Figure(data=[go.Bar(
            x=dist_data_ordered["Group"],
            y=dist_data_ordered["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>Distance Group: %{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        )])
        dist_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(dist_data_ordered)-0.5, y1=overall_rate,
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        apply_apple_theme(dist_fig, title="Observed Attrition by Distance Band", xaxis_title="Commute Distance", yaxis_title="Attrition Rate (%)", height=220)
        st.plotly_chart(dist_fig, use_container_width=True)

    with col_dist2:
        # Distance distribution box
        dist_box = go.Figure()
        dist_box.add_trace(go.Box(
            x=df[df["Attrition"] == 1]["DistanceFromHome"],
            name="Exited",
            marker_color=COLOR_ELEVATED_RISK,
            orientation='h'
        ))
        dist_box.add_trace(go.Box(
            x=df[df["Attrition"] == 0]["DistanceFromHome"],
            name="Retained",
            marker_color=COLOR_RETENTION,
            orientation='h'
        ))
        apply_apple_theme(dist_box, title="Distance Distribution Box Plot", xaxis_title="Commute Distance Units", yaxis_title="", height=220)
        st.plotly_chart(dist_box, use_container_width=True)

    # 8. WORK-LIFE-BALANCE ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Work-life balance</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Examine how work-life balance ratings align with voluntary departures.</p>', unsafe_allow_html=True)

    wlb_fig = go.Figure(data=[go.Bar(
        x=wlb_data_ordered["Group"],
        y=wlb_data_ordered["Attrition Rate"],
        marker_color=[COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_RETENTION, COLOR_RETENTION],
        width=0.4,
        hovertemplate="<b>Work-Life Balance: %{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
    )])
    wlb_fig.add_shape(
        type="line",
        x0=-0.5, y0=overall_rate,
        x1=len(wlb_data_ordered)-0.5, y1=overall_rate,
        line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
    )
    apply_apple_theme(wlb_fig, title="", xaxis_title="Work-Life Balance Score", yaxis_title="Attrition Rate (%)", height=220)
    st.plotly_chart(wlb_fig, use_container_width=True)

    # 9. SATISFACTION AND INVOLVEMENT EXPLORER
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Employee experience indicators</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Switch between environment satisfaction, job satisfaction, relationship satisfaction, or involvement scores.</p>', unsafe_allow_html=True)

    satisfaction_metric = st.selectbox(
        "Select Satisfaction Variable",
        options=["EnvironmentSatisfactionLabel", "JobSatisfactionLabel", "RelationshipSatisfactionLabel", "JobInvolvementLabel"],
        format_func=lambda x: x.replace("Label", "").replace("Satisfaction", " Satisfaction").replace("Involvement", " Involvement"),
        key="workload_mobility_satisfaction_metric"
    )

    sat_data = calculate_group_attrition(df, satisfaction_metric, overall_rate, exited_employees)
    sat_data_ordered = sat_data.set_index("Group").reindex(['Low', 'Medium', 'High', 'Very High']).dropna(subset=["Headcount"]).reset_index()

    sat_fig = go.Figure(data=[go.Bar(
        x=sat_data_ordered["Group"],
        y=sat_data_ordered["Attrition Rate"],
        marker_color=COLOR_ACCENT_BLUE,
        width=0.4,
        hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
    )])
    sat_fig.add_shape(
        type="line",
        x0=-0.5, y0=overall_rate,
        x1=len(sat_data_ordered)-0.5, y1=overall_rate,
        line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
    )
    
    display_title = satisfaction_metric.replace("Label", "").replace("Satisfaction", " Satisfaction").replace("Involvement", " Involvement")
    apply_apple_theme(sat_fig, title=f"Attrition Rate by {display_title} Rating", xaxis_title=f"{display_title} Level", yaxis_title="Attrition Rate (%)", height=240)
    st.plotly_chart(sat_fig, use_container_width=True)

    # 10. WORKLOAD HOTSPOT EXPLORER
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Where are workload-related hotspots concentrated?</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Cross-tabulate workload vectors with organizational variables.</p>', unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        primary_dim = st.selectbox(
            "Primary Workload Dimension",
            options=["OvertimeGroup", "TravelGroup", "DistanceBand", "WorkLifeBalanceLabel", "EnvironmentSatisfactionLabel", "JobSatisfactionLabel", "RelationshipSatisfactionLabel", "JobInvolvementLabel"],
            index=0,
            key="workload_explorer_primary"
        )
    with col_ctrl2:
        secondary_dim = st.selectbox(
            "Secondary Operational Dimension",
            options=["Department", "JobRole", "TenureBand", "CareerStage", "JobLevel"],
            index=0,
            key="workload_explorer_secondary"
        )

    # Pivot calculations
    pivot_df = df.groupby([primary_dim, secondary_dim]).agg(
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

    # 11. DETAILED WORKLOAD TABLE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Workload and mobility segment details</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Ledger of workload and satisfaction segments sorted by observed attrition rates.</p>', unsafe_allow_html=True)

    table_rows = []
    for dim, ddf in [("Overtime Group", ot_data), ("Travel Group", travel_data), 
                     ("Distance Band", dist_data), ("Work-Life Balance", wlb_data), 
                     ("Environment Satisfaction", sat_data_ordered)]:
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
            "Segment": st.column_config.TextColumn("Workload & Experience Cohort"),
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

    # 12. LEADERSHIP IMPLICATIONS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">What should leadership investigate next?</h3>', unsafe_allow_html=True)
    
    col_impl1, col_impl2, col_impl3 = st.columns(3)
    with col_impl1:
        if highest_ot is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #B54747; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">1. Overtime Burnout Limits</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> Overtime workers show elevated attrition of {highest_ot['Attrition Rate']:.1f}%.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Establish project manager warning rules when overtime demands exceed thresholds.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Operations Head + HRBP
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_impl2:
        if highest_travel is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">2. Travel Frequency Strains</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> Frequent business travel yields a voluntary rate of {highest_travel['Attrition Rate']:.1f}%.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Audit regional travel guidelines and evaluate virtual client options.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Travel Ops Lead + HRBP
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_impl3:
        if highest_wlb is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #C9792B; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">3. Work-Life Balance Interventions</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> Low work-life balance scores yield a rate of {highest_wlb['Attrition Rate']:.1f}%.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Review division workload volumes and promote flexible/remote structures.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Department Management
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 13. METHODOLOGY AND CAUSATION LIMITS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    with st.expander("📖 Methodology & causation caution details"):
        render_information_panel(
            title="Analysis Notice & Causal Warning",
            text="All workload metrics are associations observed within historical data. Commute distance and overtime must not be interpreted as direct "
                 "causes of voluntary departures without corroborating exit feedback records."
        )
        st.markdown(
            """
            * **Overtime Rate:** `(Exited overtime cohort / Total overtime cohort) * 100`
            * **Workload Attrition Index:** `Workload Attrition Rate / Active Baseline`
            * **Distance Bands:** Standard groupings: `0–5`, `6–10`, `11–20`, `21+` distance units.
            """
        )

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_workload_mobility()
