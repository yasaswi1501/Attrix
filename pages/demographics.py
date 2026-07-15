import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.metrics import calculate_core_metrics, calculate_group_attrition
from utils.chart_theme import apply_apple_theme, COLOR_RETENTION, COLOR_ELEVATED_RISK, COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY, COLOR_ATTENTION
from components.page_header import render_page_header
from components.empty_states import render_empty_state
from components.footer import render_footer

def show_demographics():
    """
    Renders the Demographic Explorer page.
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
        title="Demographic Explorer",
        subtitle="Analyze attrition patterns across workforce cohorts, education fields, and demographics",
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

    # Ethical / Interpretation warning banner
    st.markdown(
        """
        <div class="apple-card" style="background-color: #FBFBFD; border-left: 3px solid #C9792B;">
            <p style="margin: 0; font-size: 13px; color: #6E6E73; line-height: 1.5;">
                <strong>⚠️ Ethical & Analytical Note:</strong> Demographic patterns represent associations observed in historical data. 
                They must never be interpreted as individual predictive indicators or profiling criteria. For example, higher single-employee 
                exits may correspond to earlier career stages and high job mobility rather than marital status itself. 
                Decisions must never be based on personal demographic variables.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Age & Gender", "💍 Marital Status", "🎓 Education Levels & Fields"])

    with tab1:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Age Group Attrition</h3>', unsafe_allow_html=True)
        col_age1, col_age2 = st.columns(2)

        with col_age1:
            # AgeGroup attrition rate
            age_data = calculate_group_attrition(df, "AgeGroup", overall_rate, exited_employees)
            # Reorder logically by index
            age_data = age_data.set_index("Group").reindex(['Under 18', '18–24', '25–34', '35–44', '45–54', '55+']).dropna(subset=["Headcount"]).reset_index()
            
            age_fig = go.Figure(data=[go.Bar(
                x=age_data["Group"],
                y=age_data["Attrition Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=age_data[["Headcount", "Exited"]].values
            )])
            
            age_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(age_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )

            apply_apple_theme(
                age_fig, 
                title="Attrition Rate by Age Group", 
                xaxis_title="Age Band", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(age_fig, use_container_width=True)

        with col_age2:
            # Box plot comparing age distributions by attrition status
            age_box_fig = go.Figure()
            
            # Exited
            age_box_fig.add_trace(go.Box(
                y=df[df["Attrition"] == 1]["Age"],
                name="Exited",
                marker_color=COLOR_ELEVATED_RISK,
                boxpoints='outliers'
            ))
            # Retained
            age_box_fig.add_trace(go.Box(
                y=df[df["Attrition"] == 0]["Age"],
                name="Retained",
                marker_color=COLOR_RETENTION,
                boxpoints='outliers'
            ))

            apply_apple_theme(
                age_box_fig, 
                title="Age Distribution by Attrition Status", 
                xaxis_title="", 
                yaxis_title="Age (Years)", 
                height=320
            )
            st.plotly_chart(age_box_fig, use_container_width=True)

        # Gender comparison table & bar chart
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-top: 10px; margin-bottom: 12px;">Gender Comparison</h3>', unsafe_allow_html=True)
        col_gen1, col_gen2 = st.columns(2)
        
        with col_gen1:
            gender_data = calculate_group_attrition(df, "Gender", overall_rate, exited_employees)
            
            gender_fig = go.Figure(data=[go.Bar(
                x=gender_data["Group"],
                y=gender_data["Attrition Rate"],
                marker_color=[COLOR_ACCENT_BLUE, COLOR_NEUTRAL_GREY],
                width=0.4,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=gender_data[["Headcount", "Exited"]].values
            )])
            
            gender_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=1.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )

            apply_apple_theme(
                gender_fig, 
                title="Attrition Rate by Gender", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                height=260
            )
            st.plotly_chart(gender_fig, use_container_width=True)
            
        with col_gen2:
            st.markdown('<p style="font-size: 13px; font-weight: 600; margin-bottom: 6px;">Gender Cohort Metrics</p>', unsafe_allow_html=True)
            st.dataframe(
                gender_data.rename(columns={"Group": "Gender"}),
                column_config={
                    "Gender": st.column_config.TextColumn("Gender"),
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

    with tab2:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Marital Status Analysis</h3>', unsafe_allow_html=True)
        col_mar1, col_mar2 = st.columns(2)

        with col_mar1:
            # Attrition rate by marital status
            marital_data = calculate_group_attrition(df, "MaritalStatus", overall_rate, exited_employees)
            
            marital_fig = go.Figure(data=[go.Bar(
                x=marital_data["Group"],
                y=marital_data["Attrition Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                width=0.4,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=marital_data[["Headcount", "Exited"]].values
            )])
            
            marital_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=2.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )

            apply_apple_theme(
                marital_fig, 
                title="Attrition Rate by Marital Status", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            st.plotly_chart(marital_fig, use_container_width=True)

        with col_mar2:
            # Overtime context for marital status (Since Overtime is a strong driver, check if marital status interacts with it)
            marital_ot = df.groupby(["MaritalStatus", "OverTime"]).agg(
                Headcount=('Attrition', 'count'),
                Exited=('Attrition', lambda x: (x == 1).sum())
            ).reset_index()
            marital_ot["Rate"] = (marital_ot["Exited"] / marital_ot["Headcount"] * 100).round(2)
            
            # Grouped bar chart
            marital_ot_fig = go.Figure()
            
            # No Overtime
            marital_ot_fig.add_trace(go.Bar(
                x=marital_ot[marital_ot["OverTime"] == "No"]["MaritalStatus"],
                y=marital_ot[marital_ot["OverTime"] == "No"]["Rate"],
                name="No Overtime",
                marker_color=COLOR_RETENTION,
                hovertemplate="<b>%{x} (No Overtime)</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
            ))
            # Overtime
            marital_ot_fig.add_trace(go.Bar(
                x=marital_ot[marital_ot["OverTime"] == "Yes"]["MaritalStatus"],
                y=marital_ot[marital_ot["OverTime"] == "Yes"]["Rate"],
                name="Overtime",
                marker_color=COLOR_ELEVATED_RISK,
                hovertemplate="<b>%{x} (Overtime)</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
            ))
            
            apply_apple_theme(
                marital_ot_fig, 
                title="Marital Status Attrition Segmented by Overtime Work", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                show_legend=True,
                height=320
            )
            st.plotly_chart(marital_ot_fig, use_container_width=True)

        # Table for Marital Status
        st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Marital Cohort Performance Matrix</p>', unsafe_allow_html=True)
        st.dataframe(
            marital_data.rename(columns={"Group": "Marital Status"}),
            column_config={
                "Attrition Rate": st.column_config.NumberColumn(format="%.2f%%"),
                "Baseline Difference": st.column_config.NumberColumn(format="%+.2f pp"),
                "Relative Index": st.column_config.NumberColumn(format="%.2fx"),
                "Exit Contribution": st.column_config.NumberColumn(format="%.2f%%")
            },
            hide_index=True,
            use_container_width=True
        )

    with tab3:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Education Analysis</h3>', unsafe_allow_html=True)
        col_edu1, col_edu2 = st.columns(2)

        with col_edu1:
            # Education level (ordered)
            edu_data = calculate_group_attrition(df, "EducationLabel", overall_rate, exited_employees)
            edu_data = edu_data.set_index("Group").reindex(['1 = Below College', '2 = College', '3 = Bachelor', '4 = Master', '5 = Doctor']).dropna(subset=["Headcount"]).reset_index()

            edu_fig = go.Figure(data=[go.Bar(
                x=edu_data["Group"],
                y=edu_data["Attrition Rate"],
                marker_color=COLOR_ACCENT_BLUE,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=edu_data[["Headcount", "Exited"]].values
            )])
            
            edu_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(edu_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )

            apply_apple_theme(
                edu_fig, 
                title="Attrition Rate by Education Level", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            # Rotate x ticks slightly
            edu_fig.update_xaxes(tickangle=15)
            st.plotly_chart(edu_fig, use_container_width=True)

        with col_edu2:
            # Education Field
            field_data = calculate_group_attrition(df, "EducationField", overall_rate, exited_employees)
            
            field_fig = go.Figure(data=[go.Bar(
                x=field_data["Group"],
                y=field_data["Attrition Rate"],
                marker_color=COLOR_NEUTRAL_GREY,
                hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Headcount: %{customdata[0]}<br>Exits: %{customdata[1]}<extra></extra>",
                customdata=field_data[["Headcount", "Exited"]].values
            )])
            
            field_fig.add_shape(
                type="line",
                x0=-0.5, y0=overall_rate,
                x1=len(field_data)-0.5, y1=overall_rate,
                line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
            )

            apply_apple_theme(
                field_fig, 
                title="Attrition Rate by Education Field", 
                xaxis_title="", 
                yaxis_title="Attrition Rate (%)", 
                height=320
            )
            field_fig.update_xaxes(tickangle=15)
            st.plotly_chart(field_fig, use_container_width=True)

        # Combined Education Table
        st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Education Field Performance Matrix</p>', unsafe_allow_html=True)
        st.dataframe(
            field_data.rename(columns={"Group": "Education Field"}),
            column_config={
                "Education Field": st.column_config.TextColumn("Education Field"),
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
    show_demographics()
