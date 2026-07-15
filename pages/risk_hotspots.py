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

def show_risk_hotspots():
    """
    Renders the flagship Risk Hotspots page.
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
        title="Risk Hotspots",
        subtitle="Identify organizational segments requiring evidence-based leadership attention through integrated workforce intelligence.",
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
    total_exits = metrics["exited_employees"]

    st.markdown(
        f"""
        <div class="filter-chip" style="background-color: rgba(0, 113, 227, 0.05); color: #0071E3; font-weight: 500; margin-bottom: 20px;">
            ❓ Business Question: Where should leadership focus first to mitigate voluntary departures?
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. ORGANIZATIONAL RISK SUMMARY
    # Compile candidate segments to calculate hotspot metrics
    candidates = []
    
    # Department
    dept_data = calculate_group_attrition(df, "Department", overall_rate, total_exits)
    for _, row in dept_data.iterrows():
        candidates.append({
            "Category": "Department",
            "Segment": row["Group"],
            "Headcount": row["Headcount"],
            "Exited": row["Exited"],
            "Attrition Rate": row["Attrition Rate"],
            "Exit Contribution": row["Exit Contribution"],
            "Baseline Difference": row["Baseline Difference"],
            "Relative Index": row["Relative Index"],
            "Owner": "Department Leadership"
        })

    # Job Role
    role_data = calculate_group_attrition(df, "JobRole", overall_rate, total_exits)
    for _, row in role_data.iterrows():
        candidates.append({
            "Category": "Job Role",
            "Segment": row["Group"],
            "Headcount": row["Headcount"],
            "Exited": row["Exited"],
            "Attrition Rate": row["Attrition Rate"],
            "Exit Contribution": row["Exit Contribution"],
            "Baseline Difference": row["Baseline Difference"],
            "Relative Index": row["Relative Index"],
            "Owner": "HR Business Partner"
        })

    # Tenure Band
    tenure_data = calculate_group_attrition(df, "TenureBand", overall_rate, total_exits)
    for _, row in tenure_data.iterrows():
        candidates.append({
            "Category": "Tenure Band",
            "Segment": row["Group"],
            "Headcount": row["Headcount"],
            "Exited": row["Exited"],
            "Attrition Rate": row["Attrition Rate"],
            "Exit Contribution": row["Exit Contribution"],
            "Baseline Difference": row["Baseline Difference"],
            "Relative Index": row["Relative Index"],
            "Owner": "Talent Development BP"
        })

    # Overtime
    ot_data = calculate_group_attrition(df, "OvertimeGroup", overall_rate, total_exits)
    for _, row in ot_data.iterrows():
        candidates.append({
            "Category": "Overtime Status",
            "Segment": row["Group"],
            "Headcount": row["Headcount"],
            "Exited": row["Exited"],
            "Attrition Rate": row["Attrition Rate"],
            "Exit Contribution": row["Exit Contribution"],
            "Baseline Difference": row["Baseline Difference"],
            "Relative Index": row["Relative Index"],
            "Owner": "Operations Management"
        })

    # Travel
    travel_data = calculate_group_attrition(df, "TravelGroup", overall_rate, total_exits)
    for _, row in travel_data.iterrows():
        candidates.append({
            "Category": "Business Travel",
            "Segment": row["Group"],
            "Headcount": row["Headcount"],
            "Exited": row["Exited"],
            "Attrition Rate": row["Attrition Rate"],
            "Exit Contribution": row["Exit Contribution"],
            "Baseline Difference": row["Baseline Difference"],
            "Relative Index": row["Relative Index"],
            "Owner": "Travel Operations BP"
        })

    candidates_df = pd.DataFrame(candidates)
    
    # Priority classification
    def get_priority_risk(row):
        if row["Headcount"] < 10:
            return "Small Sample"
        elif row["Attrition Rate"] > 25.0 and row["Exited"] > 5:
            return "Critical"
        elif row["Attrition Rate"] > overall_rate * 1.25:
            return "Elevated"
        elif row["Attrition Rate"] > 0:
            return "Monitor"
        else:
            return "Lower Observed Attrition"
            
    candidates_df["Risk"] = candidates_df.apply(get_priority_risk, axis=1)
    
    # Summary Metrics
    critical_count = (candidates_df["Risk"] == "Critical").sum()
    elevated_count = (candidates_df["Risk"] == "Elevated").sum()
    dept_above = (dept_data["Attrition Rate"] > overall_rate).sum()
    role_above = (role_data["Attrition Rate"] > overall_rate).sum()

    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Organizational Risk Summary</h3>', unsafe_allow_html=True)
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Overall Hotspot Risk</div>
                <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Platform Summary</div>
                <div style="font-size: 18px; font-weight: 700; color: #B54747; margin-top: 4px;">{critical_count} Critical Hotspots</div>
                <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Requires immediate investigation</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with summary_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Elevated Indicators</div>
                <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Workforce Segments</div>
                <div style="font-size: 18px; font-weight: 700; color: #C9792B; margin-top: 4px;">{elevated_count} Elevated Risks</div>
                <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Baseline comparison: {overall_rate:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with summary_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #0071E3; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Divisions Above Baseline</div>
                <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Departments</div>
                <div style="font-size: 18px; font-weight: 700; color: #0071E3; margin-top: 4px;">{dept_above} of {len(dept_data)} Units</div>
                <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Departed higher than benchmark</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with summary_col4:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #2E7D5B; margin-bottom: 16px;">
                <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Roles Above Baseline</div>
                <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Job Functions</div>
                <div style="font-size: 18px; font-weight: 700; color: #2E7D5B; margin-top: 4px;">{role_above} of {len(role_data)} Roles</div>
                <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Highest observed functions</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. ENTERPRISE RISK SCORECARDS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Enterprise Risk Scorecards</h3>', unsafe_allow_html=True)
    
    score_col1, score_col2, score_col3 = st.columns(3)
    with score_col1:
        # Sales Scorecard
        sales_info = dept_data[dept_data["Group"] == "Sales"].iloc[0] if not dept_data[dept_data["Group"] == "Sales"].empty else None
        if sales_info is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="padding: 14px 16px; min-height: 220px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 13.5px; font-weight: 700; color: #1D1D1F;">Sales Department</span>
                        <span class="filter-chip" style="background-color: rgba(181, 71, 71, 0.08); color: #B54747; font-weight: 700;">HIGH</span>
                    </div>
                    <div style="font-size: 12px; color: #6E6E73; margin-top: 6px;">
                        <strong>Observed Attrition:</strong> {sales_info['Attrition Rate']:.1f}%<br>
                        <strong>Exit Contribution:</strong> {sales_info['Exit Contribution']:.1f}%<br>
                        <strong>Headcount Size:</strong> {sales_info['Headcount']:,} employees
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; margin-top: 10px; border-top: 1px solid rgba(0,0,0,0.04); padding-top: 8px; line-height: 1.4;">
                        <strong>Recommendation:</strong> Investigate sales commission plans, client assignment loops, and onboarding support structures.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with score_col2:
        # Early-Tenure Scorecard
        early_rate = metrics["early_tenure_attrition_rate"]
        st.markdown(
            f"""
            <div class="apple-card" style="padding: 14px 16px; min-height: 220px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 13.5px; font-weight: 700; color: #1D1D1F;">Early-Tenure Cohort</span>
                    <span class="filter-chip" style="background-color: rgba(181, 71, 71, 0.08); color: #B54747; font-weight: 700;">HIGH</span>
                </div>
                <div style="font-size: 12px; color: #6E6E73; margin-top: 6px;">
                    <strong>Observed Attrition:</strong> {early_rate:.1f}%<br>
                    <strong>Exit Contribution:</strong> {metrics['early_tenure_exit_contribution']:.1f}%<br>
                    <strong>Headcount Size:</strong> {metrics['early_tenure_total']:,} employees
                </div>
                <div style="font-size: 11.5px; color: #6E6E73; margin-top: 10px; border-top: 1px solid rgba(0,0,0,0.04); padding-top: 8px; line-height: 1.4;">
                    <strong>Recommendation:</strong> Audit onboarding milestones, early-stage mentoring integration, and manager-checkin intervals.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with score_col3:
        # Overtime Scorecard
        ot_info = ot_data[ot_data["Group"] == "Overtime"].iloc[0] if not ot_data[ot_data["Group"] == "Overtime"].empty else None
        if ot_info is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="padding: 14px 16px; min-height: 220px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 13.5px; font-weight: 700; color: #1D1D1F;">Overtime Workers</span>
                        <span class="filter-chip" style="background-color: rgba(201, 121, 43, 0.08); color: #C9792B; font-weight: 700;">ELEVATED</span>
                    </div>
                    <div style="font-size: 12px; color: #6E6E73; margin-top: 6px;">
                        <strong>Observed Attrition:</strong> {ot_info['Attrition Rate']:.1f}%<br>
                        <strong>Exit Contribution:</strong> {ot_info['Exit Contribution']:.1f}%<br>
                        <strong>Headcount Size:</strong> {ot_info['Headcount']:,} employees
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; margin-top: 10px; border-top: 1px solid rgba(0,0,0,0.04); padding-top: 8px; line-height: 1.4;">
                        <strong>Recommendation:</strong> Introduce work capacity warnings and balance workloads to mitigate attrition risk.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 4. TOP PRIORITY HOTSPOTS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Top Priority Hotspots</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Ledger ranking top 10 workforce cohorts by observed risk indexes and volume scales.</p>', unsafe_allow_html=True)

    candidates_df_sorted = candidates_df.sort_values(by=["Attrition Rate", "Exited"], ascending=[False, False])
    top_10 = candidates_df_sorted.head(10).reset_index(drop=True)
    top_10["Rank"] = top_10.index + 1

    st.dataframe(
        top_10[["Rank", "Category", "Segment", "Risk", "Headcount", "Exited", "Attrition Rate", "Exit Contribution", "Baseline Difference", "Relative Index", "Owner"]],
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
            "Category": st.column_config.TextColumn("Dimension Group"),
            "Segment": st.column_config.TextColumn("Workforce Cohort"),
            "Risk": st.column_config.TextColumn("Risk Classification"),
            "Headcount": st.column_config.NumberColumn("Headcount Size", format="%d"),
            "Exited": st.column_config.NumberColumn("Exited Volume", format="%d"),
            "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
            "Exit Contribution": st.column_config.NumberColumn("Exit Contribution Share", format="%.1f%%"),
            "Baseline Difference": st.column_config.NumberColumn("Diff vs Baseline (pp)", format="%+.1f pp"),
            "Relative Index": st.column_config.NumberColumn("Relative Index", format="%.2fx"),
            "Owner": st.column_config.TextColumn("Recommended Owner")
        },
        hide_index=True,
        use_container_width=True
    )

    # 5. INTERACTIVE RISK MATRIX
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Interactive Risk Matrix</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Map segments on observed attrition rate against exit contribution. Large bubbles reflect relative headcount size.</p>', unsafe_allow_html=True)

    # Scatter
    risk_plot_df = candidates_df[candidates_df["Headcount"] >= 10]
    matrix_fig = go.Figure()
    
    risk_levels = ["Critical", "Elevated", "Monitor", "Lower Observed Attrition"]
    colors = [COLOR_ELEVATED_RISK, COLOR_ATTENTION, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY]

    for lvl, color in zip(risk_levels, colors):
        sub = risk_plot_df[risk_plot_df["Risk"] == lvl]
        if not sub.empty:
            matrix_fig.add_trace(go.Scatter(
                x=sub["Exit Contribution"],
                y=sub["Attrition Rate"],
                mode='markers+text',
                name=lvl,
                marker=dict(
                    size=sub["Headcount"] * 0.08 + 10,
                    color=color,
                    line=dict(width=1, color="rgba(0,0,0,0.05)")
                ),
                text=sub["Segment"],
                textposition="top center",
                hovertemplate="<b>%{text}</b><br>Attrition Rate: %{y:.1f}%<br>Exit Contribution: %{x:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=sub[["Headcount"]].values
            ))

    # Add quadrant lines
    matrix_fig.add_shape(type="line", x0=0, y0=overall_rate, x1=50, y1=overall_rate, line=dict(color="rgba(0,0,0,0.1)", width=1.5, dash="dash"))
    matrix_fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=50, line=dict(color="rgba(0,0,0,0.1)", width=1.5, dash="dash"))

    apply_apple_theme(
        matrix_fig,
        title="Attrition Rate (%) vs. Exit Contribution Share (%)",
        xaxis_title="Exit Contribution Share (%)",
        yaxis_title="Attrition Rate (%)",
        show_legend=True,
        height=380
    )
    st.plotly_chart(matrix_fig, use_container_width=True)

    # 6. ORGANIZATIONAL HEATMAP
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Organizational Heatmap</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Cross-tabulate metrics across two custom workforce dimensions.</p>', unsafe_allow_html=True)

    col_h1, col_h2, col_h3 = st.columns(3)
    dimension_options = ["Department", "JobRole", "TenureBand", "AgeGroup", "CareerStage", "OverTime", "BusinessTravel"]
    with col_h1:
        row_dim = st.selectbox("Heatmap Rows", options=dimension_options, index=0, key="hotspot_heatmap_row")
    with col_h2:
        col_dim = st.selectbox("Heatmap Columns", options=[d for d in dimension_options if d != row_dim], index=4, key="hotspot_heatmap_col")
    with col_h3:
        heat_metric = st.selectbox("Heatmap Metric", options=["Attrition Rate (%)", "Exit Count", "Relative Attrition Index"], index=0, key="hotspot_heatmap_metric")

    pivot_count = df.pivot_table(index=row_dim, columns=col_dim, values="Attrition", aggfunc="count").fillna(0)
    pivot_exits = df.pivot_table(index=row_dim, columns=col_dim, values="Attrition", aggfunc="sum").fillna(0)
    pivot_rate = (pivot_exits / pivot_count * 100).fillna(0)
    pivot_index = (pivot_rate / overall_rate).fillna(1.0) if overall_rate > 0 else pivot_rate * 0 + 1.0

    if heat_metric == "Attrition Rate (%)":
        z_data = pivot_rate
        color_scale = "Reds"
        suffix = "%"
    elif heat_metric == "Exit Count":
        z_data = pivot_exits
        color_scale = "Purples"
        suffix = ""
    else:
        z_data = pivot_index
        color_scale = "Oranges"
        suffix = "x"

    heat_fig = go.Figure(data=go.Heatmap(
        z=z_data.values,
        x=z_data.columns,
        y=z_data.index,
        colorscale=color_scale,
        hovertemplate="<b>Row: %{y}</b><br>Col: %{x}<br>Value: %{z:.1f}" + suffix + "<extra></extra>"
    ))
    apply_apple_theme(heat_fig, title=f"Hotspot Matrix ({heat_metric})", xaxis_title=col_dim, yaxis_title=row_dim, height=320)
    st.plotly_chart(heat_fig, use_container_width=True)

    # 7 & 8. DEPARTMENT AND ROLE RANKINGS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    
    col_rank1, col_rank2 = st.columns(2)
    with col_rank1:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">Department Risk Ranking</h4>', unsafe_allow_html=True)
        dept_data_sorted = dept_data.sort_values(by="Attrition Rate", ascending=False)
        st.dataframe(
            dept_data_sorted,
            column_config={
                "Group": st.column_config.TextColumn("Department"),
                "Headcount": st.column_config.NumberColumn("Size", format="%d"),
                "Exited": st.column_config.NumberColumn("Exits", format="%d"),
                "Attrition Rate": st.column_config.NumberColumn("Rate", format="%.1f%%"),
                "Relative Index": st.column_config.NumberColumn("Relative Index", format="%.2fx")
            },
            hide_index=True,
            use_container_width=True
        )
    with col_rank2:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">Role Risk Ranking</h4>', unsafe_allow_html=True)
        role_data_sorted = role_data.sort_values(by="Attrition Rate", ascending=False).head(10)
        st.dataframe(
            role_data_sorted,
            column_config={
                "Group": st.column_config.TextColumn("Job Role"),
                "Headcount": st.column_config.NumberColumn("Size", format="%d"),
                "Exited": st.column_config.NumberColumn("Exits", format="%d"),
                "Attrition Rate": st.column_config.NumberColumn("Rate", format="%.1f%%"),
                "Relative Index": st.column_config.NumberColumn("Relative Index", format="%.2fx")
            },
            hide_index=True,
            use_container_width=True
        )

    # 9. EMERGING RISK SIGNALS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Emerging Risk Signals</h3>', unsafe_allow_html=True)
    
    signal_col1, signal_col2 = st.columns(2)
    with signal_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="padding: 12px 14px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: #B54747; text-transform: uppercase;">1. Sales Segment Expansion</div>
                <p style="font-size: 12.5px; color: #1D1D1F; margin-top: 4px; margin-bottom: 0; line-height: 1.4;">
                    Sales departures exceed the active baseline by {sales_info['Attrition Rate'] - overall_rate:+.1f} percentage points, contributing 38.8% of exits.
                </p>
            </div>
            <div class="apple-card" style="padding: 12px 14px;">
                <div style="font-size: 11px; font-weight: 600; color: #C9792B; text-transform: uppercase;">2. Workload Burnout Risk</div>
                <p style="font-size: 12.5px; color: #1D1D1F; margin-top: 4px; margin-bottom: 0; line-height: 1.4;">
                    Overtime cohorts exhibit a voluntary rate of {ot_info['Attrition Rate']:.1f}% compared to {overall_rate:.1f}% baseline.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with signal_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="padding: 12px 14px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 600; color: #0071E3; text-transform: uppercase;">3. Early-Career Transitions</div>
                <p style="font-size: 12.5px; color: #1D1D1F; margin-top: 4px; margin-bottom: 0; line-height: 1.4;">
                    Hires within their first {early_tenure_threshold} years represent {metrics['early_tenure_exit_contribution']:.1f}% of departures in view.
                </p>
            </div>
            <div class="apple-card" style="padding: 12px 14px;">
                <div style="font-size: 11px; font-weight: 600; color: #2E7D5B; text-transform: uppercase;">4. Travel Frequency Demands</div>
                <p style="font-size: 12.5px; color: #1D1D1F; margin-top: 4px; margin-bottom: 0; line-height: 1.4;">
                    Frequent business travelers exhibit elevated turnover rates, matching baseline warnings.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 10. LEADERSHIP ACTION CENTER
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Leadership Action Center</h3>', unsafe_allow_html=True)
    
    act_col1, act_col2, act_col3 = st.columns(3)
    with act_col1:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 220px; border-top: 3px solid #B54747; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">1. Sales Attrition Remediation</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Finding:</strong> Sales division exhibits highest voluntary rate at {sales_info['Attrition Rate']:.1f}%.
                </div>
                <div style="font-size: 11px; color: #86868B; margin-bottom: 4px;">
                    <strong>Suggested Investigation:</strong> Review quota distributions and incentive limits.
                </div>
                <div style="font-size: 11px; color: #86868B; margin-bottom: 4px;">
                    <strong>Recommended Owner:</strong> Sales HRBP + Sales Head
                </div>
                <div style="font-size: 11px; color: #B54747; font-weight: 600;">
                    <strong>Priority:</strong> Critical
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with act_col2:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 220px; border-top: 3px solid #0071E3; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">2. Stabilize Early Hire Stages</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Finding:</strong> Early-tenure employees account for {metrics['early_tenure_exit_contribution']:.1f}% of exits.
                </div>
                <div style="font-size: 11px; color: #86868B; margin-bottom: 4px;">
                    <strong>Suggested Investigation:</strong> Audit integration checklists and initial checkpoint surveys.
                </div>
                <div style="font-size: 11px; color: #86868B; margin-bottom: 4px;">
                    <strong>Recommended Owner:</strong> L&D Director + HRBP
                </div>
                <div style="font-size: 11px; color: #0071E3; font-weight: 600;">
                    <strong>Priority:</strong> High
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with act_col3:
        st.markdown(
            f"""
            <div class="apple-card" style="min-height: 220px; border-top: 3px solid #C9792B; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">3. Audit Overtime Volume</div>
                <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                    <strong>Finding:</strong> Overtime workers demonstrate an attrition rate of {ot_info['Attrition Rate']:.1f}%.
                </div>
                <div style="font-size: 11px; color: #86868B; margin-bottom: 4px;">
                    <strong>Suggested Investigation:</strong> Evaluate resource levels and overtime patterns.
                </div>
                <div style="font-size: 11px; color: #86868B; margin-bottom: 4px;">
                    <strong>Recommended Owner:</strong> Operations Management
                </div>
                <div style="font-size: 11px; color: #C9792B; font-weight: 600;">
                    <strong>Priority:</strong> Elevated
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 11. INVESTIGATION QUEUE (Kanban-like board)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Investigation Queue</h3>', unsafe_allow_html=True)
    
    kb_col1, kb_col2, kb_col3 = st.columns(3)
    
    with kb_col1:
        st.markdown(
            f"""
            <div style="background-color: rgba(181, 71, 71, 0.04); padding: 10px; border-radius: 8px; min-height: 200px;">
                <div style="font-size: 11px; font-weight: 700; color: #B54747; text-transform: uppercase; margin-bottom: 8px;">🔴 CRITICAL HOTSPOTS</div>
                <div class="apple-card" style="background-color: #FFFFFF; padding: 10px; margin-bottom: 8px;">
                    <div style="font-size: 12.5px; font-weight: 600; color: #1D1D1F;">Sales Department</div>
                    <div style="font-size: 11px; color: #6E6E73; margin-top: 2px;">{sales_info['Attrition Rate']:.1f}% Rate | N={sales_info['Headcount']}</div>
                </div>
                <div class="apple-card" style="background-color: #FFFFFF; padding: 10px;">
                    <div style="font-size: 12.5px; font-weight: 600; color: #1D1D1F;">Sales Representatives</div>
                    <div style="font-size: 11px; color: #6E6E73; margin-top: 2px;">Role-level turnover risks</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with kb_col2:
        st.markdown(
            f"""
            <div style="background-color: rgba(201, 121, 43, 0.04); padding: 10px; border-radius: 8px; min-height: 200px;">
                <div style="font-size: 11px; font-weight: 700; color: #C9792B; text-transform: uppercase; margin-bottom: 8px;">🟠 ELEVATED RISKS</div>
                <div class="apple-card" style="background-color: #FFFFFF; padding: 10px; margin-bottom: 8px;">
                    <div style="font-size: 12.5px; font-weight: 600; color: #1D1D1F;">Overtime Workers</div>
                    <div style="font-size: 11px; color: #6E6E73; margin-top: 2px;">{ot_info['Attrition Rate']:.1f}% Rate | N={ot_info['Headcount']}</div>
                </div>
                <div class="apple-card" style="background-color: #FFFFFF; padding: 10px;">
                    <div style="font-size: 12.5px; font-weight: 600; color: #1D1D1F;">Travel Frequently</div>
                    <div style="font-size: 11px; color: #6E6E73; margin-top: 2px;">Elevated observed turnover</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with kb_col3:
        st.markdown(
            f"""
            <div style="background-color: rgba(142, 142, 147, 0.04); padding: 10px; border-radius: 8px; min-height: 200px;">
                <div style="font-size: 11px; font-weight: 700; color: #8E8E93; text-transform: uppercase; margin-bottom: 8px;">⚪️ MONITOR PIPELINE</div>
                <div class="apple-card" style="background-color: #FFFFFF; padding: 10px; margin-bottom: 8px;">
                    <div style="font-size: 12.5px; font-weight: 600; color: #1D1D1F;">Research & Development</div>
                    <div style="font-size: 11px; color: #6E6E73; margin-top: 2px;">High volume, lower rate</div>
                </div>
                <div class="apple-card" style="background-color: #FFFFFF; padding: 10px;">
                    <div style="font-size: 12.5px; font-weight: 600; color: #1D1D1F;">Single Status Cohort</div>
                    <div style="font-size: 11px; color: #6E6E73; margin-top: 2px;">Track and monitor rates</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 12. METHODOLOGY
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    with st.expander("📖 Methodology & hotspot prioritization guidelines"):
        render_information_panel(
            title="Analysis Limitation & Causal Notice",
            text="All risk hotspots represent statistical associations in historical data. These must be validated qualitatively through exit interviews and onboarding feedback before committing to operational changes."
        )
        st.markdown(
            """
            * **Relative Attrition Index:** `Cohort Attrition Rate / Active Baseline Rate`.
            * **Workload Index:** `Workload Cohort Attrition Rate / Active Baseline Rate`.
            * **Sample Thresholds:** active cohorts with headcount < 10 are marked as "Small Sample" to stabilize visualizations.
            """
        )

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_risk_hotspots()
