import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics, calculate_group_attrition, calculate_workload_attrition_matrix
from utils.chart_theme import apply_apple_theme, COLOR_RETENTION, COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY
from components.page_header import render_page_header
from components.empty_states import render_empty_state
from components.footer import render_footer

def show_workload_mobility():
    """
    Renders the Workload and Mobility page.
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
        title="Workload and Mobility",
        subtitle="Examine overtime demands, business travel, commute friction, and satisfaction scores",
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

    tab1, tab2, tab3 = st.tabs(["💼 Workload & Demands", "🚗 Commute & Work-Life", "😊 Engagement & Satisfaction"])

    with tab1:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Overtime and Travel Demands</h3>', unsafe_allow_html=True)
        col_wl1, col_wl2 = st.columns(2)

        with col_wl1:
            ot_data = calculate_group_attrition(df, "OvertimeGroup", overall_rate, exited_employees)
            
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
            apply_apple_theme(
                ot_fig, 
                title="Attrition Rate by Overtime Work Status", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                height=280
            )
            st.plotly_chart(ot_fig, use_container_width=True)

        with col_wl2:
            travel_data = calculate_group_attrition(df, "TravelGroup", overall_rate, exited_employees)
            travel_data = travel_data.set_index("Group").reindex(['Non-Travel', 'Travel Rarely', 'Travel Frequently']).dropna(subset=["Headcount"]).reset_index()

            travel_fig = go.Figure(data=[go.Bar(
                x=travel_data["Group"],
                y=travel_data["Attrition Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                width=0.4,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=travel_data[["Headcount"]].values
            )])
            travel_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=2.5, y1=overall_rate,
                line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                travel_fig, 
                title="Attrition Rate by Business Travel Frequency", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                height=280
            )
            st.plotly_chart(travel_fig, use_container_width=True)

        # Workload Attrition Index Matrix (OverTime x BusinessTravel)
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-top: 10px; margin-bottom: 12px;">Workload Interaction Heatmap (Workload Attrition Index)</h3>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 12.5px; color: #6E6E73; margin-bottom: 12px;">
                * <strong>Workload Attrition Index:</strong> Observed Attrition Rate for group ÷ Active Organizational Baseline Rate. 
                Values above 1.00 signify a higher rate than the baseline (e.g. 2.00x is twice the active baseline attrition).
            </div>
            """,
            unsafe_allow_html=True
        )

        wl_matrix = calculate_workload_attrition_matrix(df, overall_rate)
        
        if not wl_matrix.empty:
            # Pivot into a 2x3 grid
            pivot_index = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Workload Attrition Index").fillna(1.0)
            pivot_count = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Headcount").fillna(0)
            pivot_exits = wl_matrix.pivot(index="BusinessTravel", columns="OverTime", values="Exited").fillna(0)
            
            # Align rows
            pivot_index = pivot_index.reindex(['Non-Travel', 'Travel Rarely', 'Travel Frequently'])
            pivot_count = pivot_count.reindex(['Non-Travel', 'Travel Rarely', 'Travel Frequently'])
            pivot_exits = pivot_exits.reindex(['Non-Travel', 'Travel Rarely', 'Travel Frequently'])

            wl_fig = go.Figure(data=go.Heatmap(
                z=pivot_index.values,
                x=pivot_index.columns,
                y=pivot_index.index,
                colorscale="Reds",
                hovertemplate="<b>OT: %{x}</b><br>Travel: %{y}<br>Workload Index: %{z:.2f}x<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=np.dstack((pivot_count.values, pivot_exits.values))
            ))
            apply_apple_theme(
                wl_fig,
                title="Overtime × Business Travel Interaction Matrix (Index)",
                xaxis_title="Overtime Work",
                yaxis_title="Business Travel",
                height=300
            )
            st.plotly_chart(wl_fig, use_container_width=True)

            # Table display
            st.markdown('<p style="font-size: 13px; font-weight: 600; margin-bottom: 6px;">Workload Combination Detailed Metrics</p>', unsafe_allow_html=True)
            st.dataframe(
                wl_matrix.drop(columns=["OverTime", "BusinessTravel"]),
                column_config={
                    "Workload Combination": st.column_config.TextColumn("Workload Combination"),
                    "Headcount": st.column_config.NumberColumn("Total Headcount", format="%d"),
                    "Exited": st.column_config.NumberColumn("Exited Employees", format="%d"),
                    "Retained": st.column_config.NumberColumn("Retained Employees", format="%d"),
                    "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
                    "Workload Attrition Index": st.column_config.NumberColumn("Workload Attrition Index", format="%.2fx"),
                    "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp")
                },
                hide_index=True,
                use_container_width=True
            )

    with tab2:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Commute and Work-Life Balance</h3>', unsafe_allow_html=True)
        col_cm1, col_cm2 = st.columns(2)

        with col_cm1:
            # Distance Band
            dist_data = calculate_group_attrition(df, "DistanceBand", overall_rate, exited_employees)
            dist_data = dist_data.set_index("Group").reindex(['0–5', '6–10', '11–20', '21+']).dropna(subset=["Headcount"]).reset_index()

            dist_fig = go.Figure(data=[go.Bar(
                x=dist_data["Group"],
                y=dist_data["Attrition Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                width=0.4,
                hovertemplate="<b>Distance Group: %{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=dist_data[["Headcount"]].values
            )])
            dist_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(dist_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                dist_fig, 
                title="Attrition Rate by Distance from Home Band", 
                xaxis_title="Distance from Home (Bands)", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(dist_fig, use_container_width=True)

        with col_cm2:
            # Work Life Balance
            wlb_data = calculate_group_attrition(df, "WorkLifeBalanceLabel", overall_rate, exited_employees)
            wlb_data = wlb_data.set_index("Group").reindex(['Poor', 'Fair', 'Good', 'Excellent']).dropna(subset=["Headcount"]).reset_index()

            wlb_fig = go.Figure(data=[go.Bar(
                x=wlb_data["Group"],
                y=wlb_data["Attrition Rate"],
                marker_color=[COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_RETENTION, COLOR_RETENTION],
                width=0.4,
                hovertemplate="<b>Work-Life Balance: %{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=wlb_data[["Headcount"]].values
            )])
            wlb_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(wlb_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
            )
            apply_apple_theme(
                wlb_fig, 
                title="Attrition Rate by Work-Life Balance Rating", 
                xaxis_title="Work-Life Balance Score", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(wlb_fig, use_container_width=True)

        # Dist vs Retained density/box
        st.markdown('<p style="font-size: 14px; font-weight: 600; margin-top: 10px; margin-bottom: 8px;">Commute Distance Distribution by Attrition Status</p>', unsafe_allow_html=True)
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
        apply_apple_theme(
            dist_box,
            title="Commute Distance Distribution Box Plot",
            xaxis_title="Distance from Home",
            yaxis_title="",
            height=200
        )
        st.plotly_chart(dist_box, use_container_width=True)

    with tab3:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Engagement and Satisfaction Ratings</h3>', unsafe_allow_html=True)
        
        satisfaction_metric = st.selectbox(
            "Select Satisfaction Variable",
            options=["EnvironmentSatisfactionLabel", "JobSatisfactionLabel", "RelationshipSatisfactionLabel", "JobInvolvementLabel"],
            format_func=lambda x: x.replace("Label", "").replace("Satisfaction", " Satisfaction").replace("Involvement", " Involvement")
        )

        sat_data = calculate_group_attrition(df, satisfaction_metric, overall_rate, exited_employees)
        sat_data = sat_data.set_index("Group").reindex(['Low', 'Medium', 'High', 'Very High']).dropna(subset=["Headcount"]).reset_index()

        sat_fig = go.Figure(data=[go.Bar(
            x=sat_data["Group"],
            y=sat_data["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
            customdata=sat_data[["Headcount"]].values
        )])
        sat_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(sat_data)-0.5, y1=overall_rate,
            line=dict(color=COLOR_NEUTRAL_GREY, width=1.5, dash="dash"),
        )
        
        display_title = satisfaction_metric.replace("Label", "").replace("Satisfaction", " Satisfaction").replace("Involvement", " Involvement")
        apply_apple_theme(
            sat_fig, 
            title=f"Attrition Rate by {display_title} Rating", 
            xaxis_title=f"{display_title} Level", 
            yaxis_title="Attrition Rate (%)", 
            height=320
        )
        st.plotly_chart(sat_fig, use_container_width=True)

        st.markdown('<p style="font-size: 13px; font-weight: 600; margin-bottom: 6px;">Satisfaction Metric Breakdown Table</p>', unsafe_allow_html=True)
        st.dataframe(
            sat_data.rename(columns={"Group": "Rating Level"}),
            column_config={
                "Rating Level": st.column_config.TextColumn("Rating Level"),
                "Headcount": st.column_config.NumberColumn("Total Headcount", format="%d"),
                "Exited": st.column_config.NumberColumn("Exited Employees", format="%d"),
                "Retained": st.column_config.NumberColumn("Retained Employees", format="%d"),
                "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
                "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp"),
                "Relative Index": st.column_config.NumberColumn("Relative Attrition Index", format="%.2fx"),
                "Exit Contribution": st.column_config.NumberColumn("Exit Contribution Share", format="%.1f%%")
            },
            hide_index=True,
            use_container_width=True
        )

    render_footer(active_count)

if __name__ == "__main__":
    show_workload_mobility()
