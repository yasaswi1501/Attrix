import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.metrics import calculate_core_metrics
from utils.chart_theme import apply_apple_theme, COLOR_RETENTION, COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY, COLOR_ATTENTION
from components.page_header import render_page_header
from components.empty_states import render_empty_state
from components.footer import render_footer
from utils.exports import convert_df_to_csv

def show_risk_hotspots():
    """
    Renders the Risk Hotspots page.
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
        title="Risk Hotspots Analysis",
        subtitle="Combine multi-dimensional workforce factors to isolate and prioritize elevated observed attrition",
        employee_count=active_count,
        total_count=total_count
    )

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    metrics = calculate_core_metrics(df, early_tenure_threshold)
    overall_rate = metrics["overall_attrition_rate"]
    total_exits = metrics["exited_employees"]

    # 1. Hotspot Control Panel
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Hotspot Multi-Dimensional Configuration</h3>', unsafe_allow_html=True)
    
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    
    dimension_options = [
        "Department", "JobRole", "TenureBand", "AgeGroup", 
        "CareerStage", "OverTime", "BusinessTravel", "JobLevel", "MaritalStatus"
    ]
    
    with col_sel1:
        dim_a = st.selectbox("Primary Dimension (Y-Axis)", options=dimension_options, index=0)
    with col_sel2:
        dim_b = st.selectbox("Secondary Dimension (X-Axis)", options=[d for d in dimension_options if d != dim_a], index=4) # Default OverTime or Travel
    with col_sel3:
        min_size = st.slider("Min Group Headcount Threshold", min_value=2, max_value=50, value=10)

    # Calculate combinations
    agg_df = df.groupby([dim_a, dim_b]).agg(
        Headcount=('Attrition', 'count'),
        Exits=('Attrition', lambda x: (x == 1).sum()),
        Retained=('Attrition', lambda x: (x == 0).sum())
    ).reset_index()

    # Drop groups with 0 headcount
    agg_df = agg_df[agg_df["Headcount"] > 0]

    if agg_df.empty:
        st.info("No combinations found. Try adjusting filter criteria.")
        render_footer(active_count)
        return

    # Calculate metrics
    agg_df["Attrition Rate"] = (agg_df["Exits"] / agg_df["Headcount"] * 100).round(2)
    agg_df["Baseline Difference"] = (agg_df["Attrition Rate"] - overall_rate).round(2)
    agg_df["Relative Index"] = (agg_df["Attrition Rate"] / overall_rate).round(2) if overall_rate > 0 else 1.0
    agg_df["Exit Contribution"] = (agg_df["Exits"] / total_exits * 100).round(2) if total_exits > 0 else 0.0
    
    # Priority Logic
    def classify_priority(row):
        size = row["Headcount"]
        rate = row["Attrition Rate"]
        contrib = row["Exit Contribution"]
        
        if size < min_size:
            return "Small Sample"
        elif rate >= 1.5 * overall_rate and contrib >= 5.0:
            return "Critical Attention"
        elif rate >= 1.25 * overall_rate:
            return "Elevated Attention"
        elif rate >= 0.75 * overall_rate or contrib >= 10.0:
            return "Monitor"
        else:
            return "Lower Observed Attrition"

    agg_df["Priority"] = agg_df.apply(classify_priority, axis=1)
    agg_df["Group Label"] = agg_df[dim_a].astype(str) + " / " + agg_df[dim_b].astype(str)

    # Sort descending by rate
    agg_df_sorted = agg_df.sort_values(by="Attrition Rate", ascending=False)

    # Split into visual sections
    tab_vis, tab_tbl = st.tabs(["📊 Hotspot Scatter Quadrants & Matrix", "📋 Prioritization Ledger & Exports"])

    with tab_vis:
        col_quad, col_mat = st.columns([3, 2])
        
        with col_quad:
            # 2. Risk-versus-Volume Scatter Quadrant Chart
            # X-axis: Attrition Rate
            # Y-axis: Exit Count
            # Bubble size: Group size
            quad_fig = go.Figure()
            
            # Map colors for priority
            color_map = {
                "Critical Attention": COLOR_ELEVATED_RISK,
                "Elevated Attention": COLOR_ATTENTION,
                "Monitor": COLOR_ACCENT_BLUE,
                "Lower Observed Attrition": COLOR_RETENTION,
                "Small Sample": COLOR_NEUTRAL_GREY
            }
            
            for prio, color in color_map.items():
                prio_df = agg_df[agg_df["Priority"] == prio]
                if not prio_df.empty:
                    quad_fig.add_trace(go.Scatter(
                        x=prio_df["Attrition Rate"],
                        y=prio_df["Exits"],
                        mode='markers+text',
                        name=prio,
                        marker=dict(
                            size=prio_df["Headcount"],
                            sizemode='diameter',
                            sizeref=2.*max(agg_df["Headcount"])/(50.**2),
                            sizemin=6,
                            color=color,
                            line=dict(width=1, color='rgba(255,255,255,0.7)')
                        ),
                        text=prio_df["Group Label"].apply(lambda s: s.split(" / ")[0][:10] + "..."), # Short label
                        textposition="top center",
                        hovertemplate="<b>Group: %{customdata[0]}</b><br>Attrition Rate: %{x:.1f}%<br>Exits: %{y}<br>Headcount: %{customdata[1]}<br>Exit Contribution: %{customdata[2]}%<extra></extra>",
                        customdata=prio_df[["Group Label", "Headcount", "Exit Contribution"]].values
                    ))
            
            # Add quadrant lines
            quad_fig.add_shape(
                type="line",
                x0=overall_rate, y0=0,
                x1=overall_rate, y1=max(agg_df["Exits"]) * 1.1 + 1,
                line=dict(color=COLOR_NEUTRAL_GREY, width=1, dash="dash"),
            )
            # Y-axis divider (median exits or exits baseline)
            median_exits = agg_df["Exits"].median()
            quad_fig.add_shape(
                type="line",
                x0=0, y0=median_exits,
                x1=max(agg_df["Attrition Rate"]) * 1.1 + 1, y1=median_exits,
                line=dict(color=COLOR_NEUTRAL_GREY, width=1, dash="dash"),
            )

            # Add quadrant text labels
            max_r = max(agg_df["Attrition Rate"]) * 1.05 + 1
            max_e = max(agg_df["Exits"]) * 1.05 + 1
            
            # Top Right: High Rate / High Volume
            quad_fig.add_annotation(x=overall_rate + (max_r - overall_rate)/2, y=median_exits + (max_e - median_exits)/2, text="High Rate / High Volume", showarrow=False, font=dict(color=COLOR_ELEVATED_RISK, size=9))
            # Top Left: Low Rate / High Volume
            quad_fig.add_annotation(x=overall_rate / 2, y=median_exits + (max_e - median_exits)/2, text="Lower Rate / High Volume", showarrow=False, font=dict(color=COLOR_NEUTRAL_GREY, size=9))
            # Bottom Right: High Rate / Low Volume
            quad_fig.add_annotation(x=overall_rate + (max_r - overall_rate)/2, y=median_exits / 2, text="High Rate / Lower Volume", showarrow=False, font=dict(color=COLOR_ATTENTION, size=9))
            # Bottom Left: Low Rate / Low Volume
            quad_fig.add_annotation(x=overall_rate / 2, y=median_exits / 2, text="Lower Risk / Lower Vol", showarrow=False, font=dict(color=COLOR_RETENTION, size=9))

            apply_apple_theme(
                quad_fig, 
                title="Attrition Rate vs. Exit Volume (Quadrant)", 
                xaxis_title="Observed Attrition Rate (%)", 
                yaxis_title="Exit Count (Volumetric)", 
                show_legend=True,
                height=420
            )
            st.plotly_chart(quad_fig, use_container_width=True)
            
        with col_mat:
            # 3. Simple cross matrix heatmap
            pivot_m = agg_df.pivot(index=dim_a, columns=dim_b, values="Attrition Rate").fillna(0)
            pivot_c = agg_df.pivot(index=dim_a, columns=dim_b, values="Headcount").fillna(0)
            
            mat_fig = go.Figure(data=go.Heatmap(
                z=pivot_m.values,
                x=pivot_m.columns,
                y=pivot_m.index,
                colorscale="Reds",
                hovertemplate="<b>" + dim_a + ": %{y}</b><br>" + dim_b + ": %{x}<br>Attrition Rate: %{z:.1f}%<br>Headcount: %{customdata[0]}<extra></extra>",
                customdata=np.dstack((pivot_c.values, pivot_c.values))
            ))
            apply_apple_theme(
                mat_fig,
                title=f"{dim_a} × {dim_b} Rate Grid",
                xaxis_title=dim_b,
                yaxis_title=dim_a,
                height=420
            )
            st.plotly_chart(mat_fig, use_container_width=True)

    with tab_tbl:
        # Prioritization table list
        st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Risk Hotspots ledger & Priority Tiers</p>', unsafe_allow_html=True)
        
        # Add visual styling color tagging for priority column in dataframe
        def highlight_priority(val):
            if val == "Critical Attention":
                return "background-color: rgba(181, 71, 71, 0.15); color: #B54747; font-weight: bold;"
            elif val == "Elevated Attention":
                return "background-color: rgba(201, 121, 43, 0.15); color: #C9792B; font-weight: bold;"
            elif val == "Monitor":
                return "background-color: rgba(0, 113, 227, 0.1); color: #0071E3;"
            elif val == "Lower Observed Attrition":
                return "background-color: rgba(46, 125, 91, 0.1); color: #2E7D5B;"
            else:
                return "color: #86868B; font-style: italic;"

        display_df = agg_df_sorted[[
            "Group Label", "Headcount", "Exited", "Retained", 
            "Attrition Rate", "Baseline Difference", "Relative Index", 
            "Exit Contribution", "Priority"
        ]].reset_index(drop=True)

        st.dataframe(
            display_df.style.applymap(highlight_priority, subset=["Priority"]),
            column_config={
                "Group Label": st.column_config.TextColumn("Risk Hotspot Segment"),
                "Headcount": st.column_config.NumberColumn("Total Headcount", format="%d"),
                "Exited": st.column_config.NumberColumn("Exited Employees", format="%d"),
                "Retained": st.column_config.NumberColumn("Retained Employees", format="%d"),
                "Attrition Rate": st.column_config.NumberColumn("Attrition Rate", format="%.1f%%"),
                "Baseline Difference": st.column_config.NumberColumn("Difference from Baseline (pp)", format="%+.1f pp"),
                "Relative Index": st.column_config.NumberColumn("Relative Attrition Index", format="%.2fx"),
                "Exit Contribution": st.column_config.NumberColumn("Exit Contribution Share", format="%.1f%%"),
                "Priority": st.column_config.TextColumn("Action Priority Tier")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Download ledger
        csv_bytes = convert_df_to_csv(display_df)
        st.download_button(
            label="📥 Export Hotspot Priority Ledger (CSV)",
            data=csv_bytes,
            file_name="attrix_risk_hotspots.csv",
            mime="text/csv"
        )

    render_footer(active_count)

if __name__ == "__main__":
    show_risk_hotspots()
