import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics, calculate_group_attrition
from utils.chart_theme import apply_apple_theme, COLOR_RETENTION, COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY
from components.page_header import render_page_header
from components.empty_states import render_empty_state
from components.footer import render_footer

def show_departments_roles():
    """
    Renders the Departments and Job Roles page.
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
        title="Departments and Job Roles",
        subtitle="Drill down into organizational structures to isolate functional hotspots",
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

    # Brief explanation block distinguishing Rate vs Volume
    from components.disclaimer import render_information_panel
    render_information_panel(
        title="Analytical Distinction: Attrition Rate vs. Exit Volume",
        text="A department or role might have a high Attrition Rate but a low Exit Count due to a small overall headcount (rate spike). "
             "Conversely, a large department might have a moderate rate but contribute a massive Exit Volume. "
             "Both views are crucial: rates indicate concentrated culture or workload friction, while volume indicates operational knowledge drain."
    )

    # Tabs for Department and Job Role View
    tab1, tab2, tab3 = st.tabs(["🏢 Department Analysis", "💼 Job Role Analysis", "🗺️ Department × Role Heatmap"])

    with tab1:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Department Rankings</h3>', unsafe_allow_html=True)
        
        # Calculate dept data
        dept_data = calculate_group_attrition(df, "Department", overall_rate, exited_employees)

        # Toggle sorting and metric display
        dept_metric = st.segmented_control(
            "Primary Metric",
            options=["Attrition Rate", "Exited", "Exit Contribution", "Headcount"],
            default="Attrition Rate"
        )
        # Fallback if segmented_control returns None
        if not dept_metric:
            dept_metric = "Attrition Rate"

        # Map display columns
        metric_col_map = {
            "Attrition Rate": ("Attrition Rate", "Attrition Rate (%)"),
            "Exited": ("Exited", "Exit Count"),
            "Exit Contribution": ("Exit Contribution", "Exit Contribution (%)"),
            "Headcount": ("Headcount", "Total Headcount")
        }
        
        df_col, display_label = metric_col_map[dept_metric]
        dept_sorted = dept_data.sort_values(by=df_col, ascending=True)

        dept_fig = go.Figure(data=[go.Bar(
            x=dept_sorted[df_col],
            y=dept_sorted["Group"],
            orientation='h',
            marker_color=COLOR_ACCENT_BLUE,
            hovertemplate="<b>%{y}</b><br>"+display_label+": %{x:.1f if %{x} is float else %{x}}<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
            customdata=dept_sorted[["Headcount", "Exited"]].values
        )])

        # If metric is Attrition Rate, show baseline line
        if dept_metric == "Attrition Rate":
            dept_fig.add_shape(
                type="line",
                x0=overall_rate, y0=-0.5,
                x1=overall_rate, y1=len(dept_sorted)-0.5,
                line=dict(color=COLOR_ELEVATED_RISK, width=2, dash="dash"),
            )

        apply_apple_theme(
            dept_fig, 
            title=f"Department Comparison by {dept_metric}", 
            xaxis_title=display_label, 
            yaxis_title="", 
            height=300
        )
        st.plotly_chart(dept_fig, use_container_width=True)

        # Detailed table
        st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Department Performance Matrix</p>', unsafe_allow_html=True)
        st.dataframe(
            dept_data.rename(columns={"Group": "Department"}),
            column_config={
                "Department": st.column_config.TextColumn("Department"),
                "Headcount": st.column_config.NumberColumn("Total Headcount", format="%d"),
                "Exited": st.column_config.NumberColumn("Exited Employees", format="%d"),
                "Retained": st.column_config.NumberColumn("Retained Employees", format="%d"),
                "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
                "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp"),
                "Relative Index": st.column_config.NumberColumn("Relative Attrition Index", format="%.2fx"),
                "Exit Contribution": st.column_config.NumberColumn("Exit Contribution Share", format="%.1f%%"),
            },
            hide_index=True,
            use_container_width=True
        )

    with tab2:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Job Role Rankings</h3>', unsafe_allow_html=True)
        
        # Headcount threshold input
        min_headcount = st.slider(
            "Minimum Group Size Filter",
            min_value=1,
            max_value=100,
            value=10,
            help="Hides roles with headcounts smaller than this threshold to prevent high rate volatility in tiny samples."
        )

        # Calculate role data
        role_data = calculate_group_attrition(df, "JobRole", overall_rate, exited_employees)
        
        # Filter roles by headcount
        filtered_role_data = role_data[role_data["Headcount"] >= min_headcount]
        
        if filtered_role_data.empty:
            st.info(f"No job roles meet the headcount threshold of {min_headcount}. Relax the threshold to view results.")
        else:
            role_metric = st.segmented_control(
                "Primary Job Role Metric",
                options=["Attrition Rate", "Exited", "Exit Contribution", "Headcount"],
                default="Attrition Rate",
                key="role_metric_toggle"
            )
            if not role_metric:
                role_metric = "Attrition Rate"
                
            r_df_col, r_display_label = metric_col_map[role_metric]
            role_sorted = filtered_role_data.sort_values(by=r_df_col, ascending=True)

            role_fig = go.Figure(data=[go.Bar(
                x=role_sorted[r_df_col],
                y=role_sorted["Group"],
                orientation='h',
                marker_color=COLOR_NEUTRAL_GREY,
                hovertemplate="<b>%{y}</b><br>"+r_display_label+": %{x:.1f}<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=role_sorted[["Headcount", "Exited"]].values
            )])

            if role_metric == "Attrition Rate":
                role_fig.add_shape(
                    type="line",
                    x0=overall_rate, y0=-0.5,
                    x1=overall_rate, y1=len(role_sorted)-0.5,
                    line=dict(color=COLOR_ELEVATED_RISK, width=2, dash="dash"),
                )

            apply_apple_theme(
                role_fig, 
                title=f"Job Role Comparison by {role_metric} (Headcount >= {min_headcount})", 
                xaxis_title=r_display_label, 
                yaxis_title="", 
                height=400
            )
            st.plotly_chart(role_fig, use_container_width=True)

            # Table for roles
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Job Role Performance Matrix</p>', unsafe_allow_html=True)
            st.dataframe(
                filtered_role_data.rename(columns={"Group": "Job Role"}),
                column_config={
                    "Job Role": st.column_config.TextColumn("Job Role"),
                    "Headcount": st.column_config.NumberColumn("Total Headcount", format="%d"),
                    "Exited": st.column_config.NumberColumn("Exited Employees", format="%d"),
                    "Retained": st.column_config.NumberColumn("Retained Employees", format="%d"),
                    "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
                    "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp"),
                    "Relative Index": st.column_config.NumberColumn("Relative Attrition Index", format="%.2fx"),
                    "Exit Contribution": st.column_config.NumberColumn("Exit Contribution Share", format="%.1f%%"),
                },
                hide_index=True,
                use_container_width=True
            )

    with tab3:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Department × Job Role Attrition Matrix</h3>', unsafe_allow_html=True)
        
        heatmap_metric = st.selectbox(
            "Matrix Cell Metric",
            options=["Attrition Rate (%)", "Exit Count", "Relative Attrition Index"],
            index=0
        )

        # Pivot the data
        pivot_count = df.pivot_table(index="JobRole", columns="Department", values="Attrition", aggfunc="count").fillna(0)
        pivot_exits = df.pivot_table(index="JobRole", columns="Department", values="Attrition", aggfunc="sum").fillna(0)
        pivot_rate = (pivot_exits / pivot_count * 100).fillna(0)
        pivot_index = pivot_rate / overall_rate if overall_rate > 0 else pivot_rate * 0 + 1.0

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

        # Plotly heatmap
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
            height=450
        )
        heatmap_fig.update_layout(margin={"t": 60, "b": 50, "l": 150, "r": 30}) # Extra left margin for role labels
        st.plotly_chart(heatmap_fig, use_container_width=True)

    render_footer(active_count)

if __name__ == "__main__":
    show_departments_roles()
