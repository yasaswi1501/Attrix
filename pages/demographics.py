import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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

def show_demographics():
    """
    Renders the premium Demographic Explorer page.
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
        title="Demographic Explorer",
        subtitle="Explore how observed attrition varies across age, gender, marital status, education level, and education field.",
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
            ❓ Business Question: Which workforce segments show elevated observed attrition and deserve further investigation?
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. DEMOGRAPHIC STATUS STRIP
    min_age = int(df["Age"].min()) if not df.empty else 18
    max_age = int(df["Age"].max()) if not df.empty else 60
    num_genders = df["Gender"].nunique()
    num_marital = df["MaritalStatus"].nunique()
    num_edus = df["Education"].nunique()

    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Age Range: {min_age}–{max_age}</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Gender Groups: {num_genders}</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Marital Statuses: {num_marital}</span>
            <span class="filter-chip" style="background-color: rgba(142, 142, 147, 0.08); color: #1D1D1F;">Education Levels: {num_edus}</span>
            <span class="filter-chip" style="background-color: rgba(46, 125, 91, 0.06); color: #2E7D5B;">Filtered Population: {active_count:,}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Calculate subsegment data structures for cards
    age_data = calculate_group_attrition(df, "AgeGroup", overall_rate, exited_employees)
    # Reindex logically
    age_data_ordered = age_data.set_index("Group").reindex(['Under 18', '18–24', '25–34', '35–44', '45–54', '55+']).dropna(subset=["Headcount"]).reset_index()
    
    gender_data = calculate_group_attrition(df, "Gender", overall_rate, exited_employees)
    marital_data = calculate_group_attrition(df, "MaritalStatus", overall_rate, exited_employees)
    
    edu_data = calculate_group_attrition(df, "EducationLabel", overall_rate, exited_employees)
    edu_data_ordered = edu_data.set_index("Group").reindex(['1 = Below College', '2 = College', '3 = Bachelor', '4 = Master', '5 = Doctor']).dropna(subset=["Headcount"]).reset_index()
    
    field_data = calculate_group_attrition(df, "EducationField", overall_rate, exited_employees)

    # 3. EXECUTIVE DEMOGRAPHIC SUMMARY
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">Demographic intelligence</h3>', unsafe_allow_html=True)
    
    highest_age = age_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not age_data.empty else None
    highest_marital = marital_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not marital_data.empty else None
    highest_field = field_data.sort_values(by="Attrition Rate", ascending=False).iloc[0] if not field_data.empty else None
    
    # Combined list to locate largest contributor
    all_segments = []
    for item in [age_data, marital_data, field_data, edu_data]:
        all_segments.append(item)
    flat_segments = pd.concat(all_segments)
    highest_contrib = flat_segments.sort_values(by="Exit Contribution", ascending=False).iloc[0] if not flat_segments.empty else None

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        if highest_age is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #B54747; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Age Cohort</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">Age {highest_age['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #B54747; margin-top: 4px;">{highest_age['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">{highest_age['Exited']} exits (N={highest_age['Headcount']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col2:
        if highest_marital is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #C9792B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Marital Cohort</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1D1D1F; margin-top: 4px;">{highest_marital['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #C9792B; margin-top: 4px;">{highest_marital['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Difference of {highest_marital['Attrition Rate'] - overall_rate:+.1f} pp</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col3:
        if highest_field is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #0071E3; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Highest Education Field</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_field['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #0071E3; margin-top: 4px;">{highest_field['Attrition Rate']:.1f}% Rate</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">N={highest_field['Headcount']} Active</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with d_col4:
        if highest_contrib is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 120px; padding: 12px 14px; border-top: 3px solid #2E7D5B; margin-bottom: 16px;">
                    <div style="font-size: 10px; font-weight: 600; color: #86868B; text-transform: uppercase;">Top Exit Contribution</div>
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-top: 4px; line-height: 1.2;">{highest_contrib['Group']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #2E7D5B; margin-top: 4px;">{highest_contrib['Exit Contribution']:.1f}% Share</div>
                    <div style="font-size: 11px; color: #86868B; margin-top: 2px;">Largest absolute exit weight</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 4. AGE ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">Age Analysis</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">How does observed attrition vary across age and age groups?</p>', unsafe_allow_html=True)

    col_age1, col_age2 = st.columns(2)
    with col_age1:
        # Age-group attrition bar
        age_fig = go.Figure(data=[go.Bar(
            x=age_data_ordered["Group"],
            y=age_data_ordered["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=age_data_ordered[["Exited", "Headcount"]].values
        )])
        age_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(age_data_ordered)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(age_fig, title="Observed Attrition Rate by Age Group", xaxis_title="Age Band", yaxis_title="Attrition Rate (%)", height=240)
        st.plotly_chart(age_fig, use_container_width=True)

    with col_age2:
        # Exact-age distribution box
        age_box_fig = go.Figure()
        age_box_fig.add_trace(go.Box(
            y=df[df["Attrition"] == 1]["Age"],
            name="Exited",
            marker_color=COLOR_ELEVATED_RISK,
            boxpoints='outliers'
        ))
        age_box_fig.add_trace(go.Box(
            y=df[df["Attrition"] == 0]["Age"],
            name="Retained",
            marker_color=COLOR_RETENTION,
            boxpoints='outliers'
        ))
        apply_apple_theme(age_box_fig, title="Age distribution by attrition status", xaxis_title="", yaxis_title="Age (Years)", height=240)
        st.plotly_chart(age_box_fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size: 11.5px; color: #86868B; margin-top: -8px; margin-bottom: 20px; line-height: 1.4;">
            *Note: Observed departures skew heavily younger, with the 18–24 cohort demonstrating a rate significantly above baseline. 
            This correlates strongly with entry-level job roles and higher early-tenure mobility.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 5. GENDER AND MARITAL-STATUS ANALYSIS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    
    col_gm1, col_gm2 = st.columns(2)
    with col_gm1:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 4px;">Gender comparison</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 12.5px; color: #6E6E73; margin-bottom: 12px;">Workforce distribution and observed attrition rates by gender.</p>', unsafe_allow_html=True)
        
        gender_fig = go.Figure(data=[go.Bar(
            x=gender_data["Group"],
            y=gender_data["Attrition Rate"],
            marker_color=COLOR_NEUTRAL_GREY,
            width=0.35,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=gender_data[["Exited", "Headcount"]].values
        )])
        gender_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(gender_data)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(gender_fig, title="", xaxis_title="", yaxis_title="Attrition Rate (%)", height=180)
        st.plotly_chart(gender_fig, use_container_width=True)

    with col_gm2:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; margin-bottom: 4px;">Marital-status comparison</h4>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 12.5px; color: #6E6E73; margin-bottom: 12px;">Observed voluntary departures and headcounts by marital status.</p>', unsafe_allow_html=True)
        
        marital_fig = go.Figure(data=[go.Bar(
            x=marital_data["Group"],
            y=marital_data["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.35,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<br>Exits: %{customdata[0]}<br>Headcount: %{customdata[1]}<extra></extra>",
            customdata=marital_data[["Exited", "Headcount"]].values
        )])
        marital_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(marital_data)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(marital_fig, title="", xaxis_title="", yaxis_title="Attrition Rate (%)", height=180)
        st.plotly_chart(marital_fig, use_container_width=True)

    # 6. EDUCATION AND EDUCATION-FIELD ANALYSIS (Ordinal sort & Segmented controls)
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Education & Field Analysis</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Review how educational attainment and academic background correspond to voluntary departures.</p>', unsafe_allow_html=True)

    edu_tab1, edu_tab2, edu_tab3, edu_tab4 = st.tabs([
        "🎓 Education Level Attrition", 
        "🔢 Education Level Exits", 
        "📚 Education Field Attrition", 
        "📉 Education Field Contribution"
    ])
    
    with edu_tab1:
        edu_rate_fig = go.Figure(data=[go.Bar(
            x=edu_data_ordered["Group"],
            y=edu_data_ordered["Attrition Rate"],
            marker_color=COLOR_ACCENT_BLUE,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        )])
        edu_rate_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(edu_data_ordered)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(edu_rate_fig, title="", xaxis_title="Education Level", yaxis_title="Attrition Rate (%)", height=240)
        st.plotly_chart(edu_rate_fig, use_container_width=True)

    with edu_tab2:
        edu_vol_fig = go.Figure(data=[go.Bar(
            x=edu_data_ordered["Group"],
            y=edu_data_ordered["Exited"],
            marker_color=COLOR_NEUTRAL_GREY,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Exits: %{y}<extra></extra>"
        )])
        apply_apple_theme(edu_vol_fig, title="", xaxis_title="Education Level", yaxis_title="Exit Count", height=240)
        st.plotly_chart(edu_vol_fig, use_container_width=True)

    with edu_tab3:
        field_rate_fig = go.Figure(data=[go.Bar(
            x=field_data["Group"],
            y=field_data["Attrition Rate"],
            marker_color=COLOR_ATTENTION,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Attrition Rate: %{y:.1f}%<extra></extra>"
        )])
        field_rate_fig.add_shape(
            type="line",
            x0=-0.5, y0=overall_rate,
            x1=len(field_data)-0.5, y1=overall_rate,
            line=dict(color=COLOR_ELEVATED_RISK, width=1.5, dash="dash"),
        )
        apply_apple_theme(field_rate_fig, title="", xaxis_title="Education Field", yaxis_title="Attrition Rate (%)", height=240)
        st.plotly_chart(field_rate_fig, use_container_width=True)

    with edu_tab4:
        field_contrib_fig = go.Figure(data=[go.Bar(
            x=field_data["Group"],
            y=field_data["Exit Contribution"],
            marker_color=COLOR_NEUTRAL_GREY,
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Exit Contribution: %{y:.1f}%<extra></extra>"
        )])
        apply_apple_theme(field_contrib_fig, title="", xaxis_title="Education Field", yaxis_title="Exit Share (%)", height=240)
        st.plotly_chart(field_contrib_fig, use_container_width=True)

    # 7. CROSS-SEGMENT EXPLORER
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Cross-segment explorer</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Intersect demographic classifications with operational attributes to isolate multi-dimensional drivers.</p>', unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        primary_dim = st.selectbox(
            "Primary Demographic Dimension",
            options=["AgeGroup", "Gender", "MaritalStatus", "EducationLabel", "EducationField"],
            index=0,
            key="demo_explorer_primary"
        )
    with col_ctrl2:
        secondary_dim = st.selectbox(
            "Secondary Operational Dimension",
            options=["Department", "JobRole", "OverTime", "BusinessTravel", "JobLevel"],
            index=0,
            key="demo_explorer_secondary"
        )

    # Pivot calculations
    pivot_df = df.groupby([primary_dim, secondary_dim]).agg(
        Headcount=("Attrition", "count"),
        Exited=("Attrition", "sum")
    ).reset_index()
    pivot_df["Rate"] = (pivot_df["Exited"] / pivot_df["Headcount"] * 100).fillna(0)

    # Render as grouped bar chart
    cross_fig = go.Figure()
    categories = sorted(pivot_df[primary_dim].unique())
    subcategories = sorted(pivot_df[secondary_dim].unique())
    
    for subcat in subcategories:
        sub_data = pivot_df[pivot_df[secondary_dim] == subcat]
        # Realign by categories
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

    # 8. DETAILED DEMOGRAPHIC TABLE
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 6px;">Demographic segment details</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 13.5px; color: #6E6E73; margin-bottom: 16px;">Ledger of demographic segments containing detailed records, index rates, and sample size categories.</p>', unsafe_allow_html=True)

    table_rows = []
    for dim, ddf in [("Age Group", age_data), ("Gender", gender_data), ("Marital Status", marital_data), 
                     ("Education Level", edu_data), ("Education Field", field_data)]:
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
            "Segment": st.column_config.TextColumn("Workforce Segment"),
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

    # 9. LEADERSHIP IMPLICATIONS
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 14px;">What should leadership investigate next?</h3>', unsafe_allow_html=True)
    
    col_impl1, col_impl2, col_impl3 = st.columns(3)
    with col_impl1:
        if highest_age is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #B54747; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">1. Early Career Attrition</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> Employees aged {highest_age['Group']} show elevated attrition of {highest_age['Attrition Rate']:.1f}%.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Audit early integration mentors, training ramps, and onboarding checkpoints.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Early Career Programs + HRBP
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_impl2:
        if highest_marital is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #0071E3; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">2. Marital Status Flight Index</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> {highest_marital['Group']} employees show a rate of {highest_marital['Attrition Rate']:.1f}% (baseline difference: {highest_marital['Attrition Rate'] - overall_rate:+.1f} pp).
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Evaluate shifts, relocation demands, and location stability parameters.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> HR Ops + Compensation Specialist
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col_impl3:
        if highest_field is not None:
            st.markdown(
                f"""
                <div class="apple-card" style="min-height: 220px; border-top: 3px solid #C9792B; padding: 14px 16px;">
                    <div style="font-size: 13.5px; font-weight: 700; color: #1D1D1F; margin-bottom: 6px;">3. Background Field Hotspots</div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Finding:</strong> Background in {highest_field['Group']} yields a departure rate of {highest_field['Attrition Rate']:.1f}%.
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73; line-height: 1.45; margin-bottom: 10px;">
                        <strong>Action:</strong> Audit matching parameters during sourcing to align profiles with job descriptions.
                    </div>
                    <div style="font-size: 10px; color: #86868B;">
                        <strong>Owner:</strong> Talent Acquisition Lead
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 10. ETHICAL INTERPRETATION AND METHODOLOGY
    st.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 24px 0;">', unsafe_allow_html=True)
    with st.expander("📖 Ethical Policy & Statistical Methodology Guidelines"):
        render_information_panel(
            title="Ethical Analysis Statement & Causality Warning",
            text="Demographic segment analysis is purely descriptive of historical aggregates. Observed statistical association does not imply individual causation. "
                 "Attributes (such as age, gender, marital status, or educational choices) must not drive hiring, promotion, profiling, or termination decisions."
        )
        st.markdown(
            """
            * **Attrition Rate Calculation:** `(Departed Cohort / Active Cohort) * 100`
            * **Exit Share Share:** `(Cohort exits / Active exits) * 100`
            * **Relative Index:** `Cohort Attrition Rate / Active Baseline`
            * **Sample Limits:** Subsegments with headcount < 15 are flagged as "Small Sample" to prevent volatility and ensure privacy.
            """
        )

    # Footer
    render_footer(active_count)

if __name__ == "__main__":
    show_demographics()
