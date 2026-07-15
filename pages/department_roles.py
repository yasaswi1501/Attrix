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
from components.empty_states import render_empty_state
from components.footer import render_footer
from components.insight_cards import render_insight_card
from components.disclaimer import render_information_panel

def show_departments_roles():
    """
    Renders the premium Departments and Job Roles page.
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
        title="Departments & Roles",
        subtitle="Identify organizational units and job functions with elevated observed attrition and meaningful exit concentration.",
        employee_count=active_count,
        total_count=total_count
    )

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    # Calculate baseline
    metrics = calculate_core_metrics(df, early_tenure_threshold)
    overall_rate = metrics["overall_attrition_rate"]
    exited_employees = metrics["exited_employees"]

    st.markdown(
        f"""
        <div class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 500; margin-bottom: 20px;">
            ❓ Business Question: Where is attrition concentrated across departments and roles?
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. ORGANIZATIONAL STATUS STRIP
    num_depts = df["Department"].nunique()
    num_roles = df["JobRole"].nunique()
    
    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Departments: {num_depts}</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Roles: {num_roles}</span>
            <span class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 500;">Baseline Attrition: {overall_rate:.1f}%</span>
            <span class="filter-chip" style="background-color: rgba(201, 121, 43, 0.06); color: #C9792B;">Min Sample: 10 employees</span>
            <span class="filter-chip" style="background-color: rgba(46, 125, 91, 0.06); color: #2E7D5B;">Filtered Population: {active_count:,}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. DEPARTMENT EXECUTIVE SUMMARY
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Department intelligence</h3>', unsafe_allow_html=True)
    dept_data = calculate_group_attrition(df, "Department", overall_rate, exited_employees)
    
    highest_rate_dept = dept_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not dept_data.empty else None
    largest_vol_dept = dept_data.sort_values(by="Exited", ascending=False).iloc[0] if not dept_data.empty else None
    largest_contrib_dept = dept_data.sort_values(by="Exit Contribution", ascending=False).iloc[0] if not dept_data.empty else None
    most_stable_dept = dept_data.sort_values(by="Attrition Rate", ascending=True).iloc[0] if not dept_data.empty else None

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        if highest_rate_dept is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Attrition Rate</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{highest_rate_dept['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #B54747; margin-top: 4px;">{highest_rate_dept['Attrition Rate']:.1f}%</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">{highest_rate_dept['Exited']} exits (N={highest_rate_dept['Headcount']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col2:
        if largest_vol_dept is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #0071E3; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Largest Exit Volume</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{largest_vol_dept['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #0071E3; margin-top: 4px;">{largest_vol_dept['Exited']} Departures</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Rate of {largest_vol_dept['Attrition Rate']:.1f}% (N={largest_vol_dept['Headcount']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col3:
        if largest_contrib_dept is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Exit Contribution Share</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{largest_contrib_dept['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #C9792B; margin-top: 4px;">{largest_contrib_dept['Exit Contribution']:.1f}% Share</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Contributes major turnover exits</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col4:
        if most_stable_dept is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #2E7D5B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Most Stable Department</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{most_stable_dept['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #2E7D5B; margin-top: 4px;">{most_stable_dept['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">N={most_stable_dept['Headcount']} (Lowest relative risk)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 4. DEPARTMENT RATE-VERSUS-VOLUME ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;">', unsafe_allow_html=True)
    
    col_dept1, col_dept2 = st.columns(2)
    with col_dept1:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 4px;">Which departments have the highest observed attrition rate?</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 12.5px; color: #6E6E73; margin-bottom: 12px;">Comparing attrition rates across divisions against the global baseline.</p>', unsafe_allow_html=True)
        
        dept_sorted_rate = dept_data.sort_values(by="Attrition Rate", ascending=True)
        dept_rate_fig = go.Figure(data=[go.Bar(
            x=dept_sorted_rate["Attrition Rate"],
            y=dept_sorted_rate["Group"],
            orientation='h',
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{y}</b><br>Attrition Rate: %{x:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=dept_sorted_rate[["Exited", "Headcount"]].values
        )])
        dept_rate_fig.add_shape(
            type="line",
            x0=overall_rate, y0=-0.5,
            x1=overall_rate, y1=len(dept_sorted_rate)-0.5,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(dept_rate_fig, title="", xaxis_title="Attrition Rate (%)", yaxis_title="", height=200)
        st.plotly_chart(dept_rate_fig, use_container_width=True)

    with col_dept2:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 4px;">Which departments contribute the most exits?</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 12.5px; color: #6E6E73; margin-bottom: 12px;">Evaluating the volume of voluntary departures and relative headcount contribution.</p>', unsafe_allow_html=True)
        
        dept_sorted_vol = dept_data.sort_values(by="Exited", ascending=True)
        dept_vol_fig = go.Figure(data=[go.Bar(
            x=dept_sorted_vol["Exited"],
            y=dept_sorted_vol["Group"],
            orientation='h',
            marker_color=COLOR_NEUTRAL_GREY,
            width=0.4,
            hovertemplate="<b>%{y}</b><br>Exits count: %{x}<br>Exit Contribution: %{customdata[0]:.1f}%<extra></extra>",
            customdata=dept_sorted_vol[["Exit Contribution"]].values
        )])
        apply_apple_theme(dept_vol_fig, title="", xaxis_title="Exit Count", yaxis_title="", height=200)
        st.plotly_chart(dept_vol_fig, use_container_width=True)

    render_information_panel(
        title="Analytical Distinction: Attrition Rate vs. Exit Volume",
        text="Attrition rate measures the percentage of employees who exited within a group. Exit volume measures the absolute count of exits. "
             "A smaller group (e.g. Sales) can experience a high rate but contribute fewer absolute exits than a large group (e.g. R&D) with a lower rate."
    )

    # 5. ROLE EXECUTIVE SUMMARY
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Role intelligence</h3>', unsafe_allow_html=True)
    
    role_data = calculate_group_attrition(df, "JobRole", overall_rate, exited_employees)
    role_data_filtered = role_data[role_data["Headcount"] >= 10]
    
    highest_rate_role = role_data_filtered.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not role_data_filtered.empty else None
    largest_vol_role = role_data_filtered.sort_values(by="Exited", ascending=False).iloc[0] if not role_data_filtered.empty else None
    largest_contrib_role = role_data_filtered.sort_values(by="Exit Contribution", ascending=False).iloc[0] if not role_data_filtered.empty else None
    largest_pop_role = role_data_filtered.sort_values(by="Headcount", ascending=False).iloc[0] if not role_data_filtered.empty else None

    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1:
        if highest_rate_role is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Role Rate</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_rate_role['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #B54747; margin-top: 4px;">{highest_rate_role['Attrition Rate']:.1f}%</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">N={highest_rate_role['Headcount']} (Min sample >= 10)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with r_col2:
        if largest_vol_role is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #0071E3; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Largest Role Volume</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{largest_vol_role['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #0071E3; margin-top: 4px;">{largest_vol_role['Exited']} Exits</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Rate of {largest_vol_role['Attrition Rate']:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with r_col3:
        if largest_contrib_role is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Role Exit Share</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{largest_contrib_role['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #C9792B; margin-top: 4px;">{largest_contrib_role['Exit Contribution']:.1f}% Share</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Critical exit weight</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col4:
        if largest_pop_role is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #2E7D5B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Largest Role Population</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{largest_pop_role['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #2E7D5B; margin-top: 4px;">N={largest_pop_role['Headcount']} Active</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">{largest_pop_role['Exited']} exits recorded</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 6. ROLE RATE-VERSUS-VOLUME ANALYSIS (Threshold slider & Tabs)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 20px 0;">', unsafe_allow_html=True)
    st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 4px;">Role-Level Metrics Analysis</h4>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12.5px; color: #6E6E73; margin-bottom: 16px;">Adjust the minimum group size to isolate statistical noise from low-headcount cohorts.</p>', unsafe_allow_html=True)

    min_headcount = st.slider(
        "Minimum Group Size Filter (Headcount Threshold)",
        min_value=1,
        max_value=100,
        value=10,
        key="dept_roles_min_headcount",
        help="Filters out small employee populations to stabilize rate visualizations."
    )

    filtered_role_data = role_data[role_data["Headcount"] >= min_headcount]

    if filtered_role_data.empty:
        st.info(f"No job roles meet the headcount threshold of {min_headcount}. Relax the slider to view metrics.")
    else:
        role_tab1, role_tab2, role_tab3 = st.tabs(["📊 Role Attrition Rate", "🔢 Role Exit Volume", "📉 Role Exit Contribution"])
        
        with role_tab1:
            role_sorted_rate = filtered_role_data.sort_values(by="Attrition Rate", ascending=True)
            role_rate_fig = go.Figure(data=[go.Bar(
                x=role_sorted_rate["Attrition Rate"],
                y=role_sorted_rate["Group"],
                orientation='h',
                marker_color=COLOR_ATTENTION,
                width=0.4,
                hovertemplate="<b>%{y}</b><br>Attrition Rate: %{x:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
                customdata=role_sorted_rate[["Exited", "Headcount"]].values
            )])
            role_rate_fig.add_shape(
                type="line",
                x0=overall_rate, y0=-0.5,
                x1=overall_rate, y1=len(role_sorted_rate)-0.5,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )
            apply_apple_theme(role_rate_fig, title="", xaxis_title="Attrition Rate (%)", yaxis_title="", height=280)
            st.plotly_chart(role_rate_fig, use_container_width=True)

        with role_tab2:
            role_sorted_vol = filtered_role_data.sort_values(by="Exited", ascending=True)
            role_vol_fig = go.Figure(data=[go.Bar(
                x=role_sorted_vol["Exited"],
                y=role_sorted_vol["Group"],
                orientation='h',
                marker_color=COLOR_NEUTRAL_GREY,
                width=0.4,
                hovertemplate="<b>%{y}</b><br>Exits: %{x}<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=role_sorted_vol[["Headcount"]].values
            )])
            apply_apple_theme(role_vol_fig, title="", xaxis_title="Exit Count", yaxis_title="", height=280)
            st.plotly_chart(role_vol_fig, use_container_width=True)

        with role_tab3:
            role_sorted_contrib = filtered_role_data.sort_values(by="Exit Contribution", ascending=True)
            role_contrib_fig = go.Figure(data=[go.Bar(
                x=role_sorted_contrib["Exit Contribution"],
                y=role_sorted_contrib["Group"],
                orientation='h',
                marker_color=COLOR_ACCENT_BLUE,
                width=0.4,
                hovertemplate="<b>%{y}</b><br>Exit Share: %{x:.1f}%<extra></extra>"
            )])
            apply_apple_theme(role_contrib_fig, title="", xaxis_title="Exit Contribution Share (%)", yaxis_title="", height=280)
            st.plotly_chart(role_contrib_fig, use_container_width=True)

    # 7. DEPARTMENT × ROLE HOTSPOT MATRIX
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Where are department-role hotspots concentrated?</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Pivot observed metrics across both department and job role axes to pinpoint multi-dimensional retention anomalies.</p>', unsafe_allow_html=True)

    heatmap_metric = st.selectbox(
        "Select Hotspot Matrix Metric",
        options=["Attrition Rate (%)", "Exit Count", "Relative Attrition Index"],
        index=0,
        key="dept_roles_heatmap_metric"
    )

    pivot_count = df.pivot_table(index="JobRole", columns="Department", values="Attrition", aggfunc="count").fillna(0)
    pivot_exits = df.pivot_table(index="JobRole", columns="Department", values="Attrition", aggfunc="sum").fillna(0)
    pivot_rate = (pivot_exits / pivot_count * 100).fillna(0)
    pivot_index = (pivot_rate / overall_rate).fillna(1.0) if overall_rate > 0 else pivot_rate * 0 + 1.0

    if heatmap_metric == "Attrition Rate (%)":
        z_data = pivot_rate
        color_scale = "Reds"
        z_suffix = "%"
    elif heatmap_metric == "Exit Count":
        z_data = pivot_exits
        color_scale = "Purples"
        z_suffix = ""
    else:
        z_data = pivot_index
        color_scale = "Oranges"
        z_suffix = "x"

    heatmap_fig = go.Figure(data=go.Heatmap(
        z=z_data.values,
        x=z_data.columns,
        y=z_data.index,
        colorscale=color_scale,
        hovertemplate="<b>Role: %{y}</b><br>Dept: %{x}<br>Metric: %{z:.1f}" + z_suffix + "<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
        customdata=np.dstack((pivot_count.values, pivot_exits.values))
    ))

    apply_apple_theme(
        heatmap_fig,
        title=f"Department × Job Role Heatmap ({heatmap_metric})",
        xaxis_title="Department",
        yaxis_title="Job Role",
        height=380
    )
    heatmap_fig.update_layout(margin={"t": 45, "b": 35, "l": 150, "r": 20}) 
    st.plotly_chart(heatmap_fig, use_container_width=True)

    # 8. PRIORITY HOTSPOT TABLE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Priority department-role hotspots</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Ledger of functional cohorts ranked by attrition metrics and annotated by priorities.</p>', unsafe_allow_html=True)

    # Compute priorities
    pivot_df = df.groupby(["Department", "JobRole"]).agg(
        Headcount=("Attrition", "count"),
        Exited=("Attrition", "sum")
    ).reset_index()
    pivot_df["Retained"] = pivot_df["Headcount"] - pivot_df["Exited"]
    pivot_df["Attrition Rate"] = (pivot_df["Exited"] / pivot_df["Headcount"] * 100).fillna(0)
    pivot_df["Exit Contribution"] = (pivot_df["Exited"] / exited_employees * 100).fillna(0) if exited_employees > 0 else 0.0
    pivot_df["Baseline Difference"] = pivot_df["Attrition Rate"] - overall_rate
    pivot_df["Relative Index"] = (pivot_df["Attrition Rate"] / overall_rate).fillna(1.0) if overall_rate > 0 else 1.0

    def get_priority(row):
        if row["Headcount"] < 10:
            return "Small Sample"
        elif row["Attrition Rate"] > 25.0 and row["Exited"] > 5:
            return "Critical Attention"
        elif row["Attrition Rate"] > overall_rate:
            return "Elevated"
        elif row["Attrition Rate"] > 0:
            return "Monitor"
        else:
            return "Lower Attrition"

    pivot_df["Priority"] = pivot_df.apply(get_priority, axis=1)
    pivot_df_sorted = pivot_df.sort_values(by="Attrition Rate", ascending=False)

    st.dataframe(
        pivot_df_sorted,
        column_config={
            "Department": st.column_config.TextColumn("Department"),
            "JobRole": st.column_config.TextColumn("Job Role"),
            "Headcount": st.column_config.NumberColumn("Headcount", format="%d"),
            "Exited": st.column_config.NumberColumn("Exited", format="%d"),
            "Retained": st.column_config.NumberColumn("Retained", format="%d"),
            "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
            "Exit Contribution": st.column_config.NumberColumn("Exit Contribution", format="%.1f%%"),
            "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp"),
            "Relative Index": st.column_config.NumberColumn("Relative Index", format="%.2fx"),
            "Priority": st.column_config.TextColumn("Priority Category Status"),
        },
        hide_index=True,
        use_container_width=True
    )

    # 9. LEADERSHIP IMPLICATIONS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">What should leadership investigate next?</h3>', unsafe_allow_html=True)
    
    col_impl1, col_impl2, col_impl3 = st.columns(3)
    with col_impl1:
        if highest_rate_dept is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #B54747; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">1. Sales Attrition Volume</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> The Sales division shows the highest rate at {highest_rate_dept['Attrition Rate']:.1f}%.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Audit sales commission caps, client assignments, and onboarding support.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Sales HRBP + Sales Head
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_impl2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 220px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">2. R&D Absolute Departures</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Finding:</strong> R&D accounts for 56.1% of all voluntary departures in the dataset.
                </div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Action:</strong> Investigate mid-career stagnation points and engineering manager alignment.
                </div>
                <div style="font-size: 10px; color: #86868B;">
                    <strong>Owner:</strong> Engineering leadership
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_impl3:
        if highest_rate_role is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #C9792B; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">3. Role-Level Quota Tension</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> {highest_rate_role['Group']} roles exceed company attrition baseline.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Evaluate onboarding structures and quota thresholds for new hires.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Sales Enablement partner
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 10. METHODOLOGY AND LIMITATIONS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    with st.expander("📖 Methodology & Calculation Formulations"):
        st.markdown(
            """
            * **Attrition Rate Formula:** `(Exited Employees / Total Employees in View) * 100`
            * **Exit Contribution Share:** `(Exits within specific group / Total Exits in View) * 100`
            * **Relative Attrition Index:** `Group Attrition Rate / Baseline Attrition Rate` (1.00x represents exact alignment).
            * **Sample Size Controls:** Active subsets with headcount < 10 are flagged as "Small Sample" to prevent rate misinterpretation.
            * **Causation Notice:** All findings indicate statistical association and must be validated qualitatively before action.
            """
        )

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_departments_roles()
