import streamlit as st
from pathlib import Path
import pandas as pd

# 1. SET PAGE CONFIG (MUST BE FIRST)
st.set_page_config(
    page_title="Attrix",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.data_loader import load_default_data
from utils.data_cleaning import clean_and_validate_data
from utils.feature_engineering import apply_feature_engineering
from utils.filtering import filter_dataframe

# Page imports
from pages.overview import show_overview
from pages.department_roles import show_departments_roles
from pages.demographics import show_demographics
from pages.tenure_career import show_tenure_career
from pages.workload_mobility import show_workload_mobility
from pages.risk_hotspots import show_risk_hotspots
from pages.recommendations import show_recommendations
from pages.methodology import show_methodology

# Initialize session state variables
if "clean_df" not in st.session_state:
    st.session_state["clean_df"] = None
if "dq_report" not in st.session_state:
    st.session_state["dq_report"] = None
if "engineered_df" not in st.session_state:
    st.session_state["engineered_df"] = None
if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None

from config.settings import RAW_DATA_PATH

# Cross-platform relative path lookup from config settings
DATA_PATH = RAW_DATA_PATH

def main():
    # 2. DATA LOADING PIPELINE (Run once per session)
    if st.session_state["clean_df"] is None:
        if DATA_PATH.exists():
            raw_df = load_default_data(str(DATA_PATH))
            if raw_df is not None:
                clean_df, dq_report = clean_and_validate_data(raw_df)
                if "error" not in dq_report:
                    st.session_state["clean_df"] = clean_df
                    st.session_state["dq_report"] = dq_report
                    st.session_state["completeness_pct"] = dq_report["data_completeness_pct"]
                else:
                    st.error(f"Failed to clean dataset: {dq_report['error']}")
                    return
            else:
                return
        else:
            st.error(f"Workforce CSV dataset not found at expected location: {DATA_PATH}. Please upload a dataset in the Methodology page.")
            st.session_state["clean_df"] = pd.DataFrame() # Fallback empty
            st.session_state["dq_report"] = {}

    clean_df = st.session_state["clean_df"]
    dq_report = st.session_state["dq_report"]

    # 3. GLOBAL SIDEBAR FILTERS
    st.sidebar.markdown(
        '<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">'
        '<span style="font-size: 22px; font-weight: 800; color: #1D1D1F; letter-spacing: -0.5px;">Attrix</span>'
        '<div style="font-size: 11.5px; color: #6E6E73; margin-top: 2px;">Workforce Intelligence Platform</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # Active Coverage and Data Quality Indicator
    if "filtered_df" in st.session_state and st.session_state["filtered_df"] is not None:
        active_count = len(st.session_state["filtered_df"])
    else:
        active_count = len(clean_df) if clean_df is not None else 0
    total_count = len(clean_df) if clean_df is not None else 0
    completeness_pct = st.session_state.get("completeness_pct", 100.0)

    st.sidebar.markdown(
        f"""
        <div style="background-color: #FBFBFD; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; padding: 12px 14px; margin-bottom: 16px; text-align: center;">
            <div style="font-size: 11px; color: #6E6E73; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;">Active Coverage</div>
            <div style="font-size: 18px; font-weight: 700; color: #1D1D1F;">{active_count:,} <span style="font-size: 13px; font-weight: 400; color: #86868B;">of {total_count:,}</span></div>
            <div style="font-size: 11px; color: #2E7D5B; margin-top: 4px; font-weight: 500;">● Data Integrity: {completeness_pct:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Filter Reset Button
    if st.sidebar.button("Reset All Filters", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("filter_") or key == "early_tenure_threshold":
                del st.session_state[key]
        st.rerun()

    st.sidebar.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 12px 0;">', unsafe_allow_html=True)
    st.sidebar.markdown('<p style="font-size: 11px; color: #86868B; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;">Parameters</p>', unsafe_allow_html=True)

    # Early tenure threshold slider
    early_tenure_threshold = st.sidebar.slider(
        "Early Tenure Threshold (Years)",
        min_value=1,
        max_value=5,
        value=st.session_state.get("early_tenure_threshold", 2),
        key="early_tenure_threshold"
    )

    # Re-apply feature engineering when threshold changes
    if clean_df is not None and not clean_df.empty:
        engineered_df = apply_feature_engineering(clean_df, early_tenure_threshold)
        st.session_state["engineered_df"] = engineered_df
    else:
        engineered_df = pd.DataFrame()

    st.sidebar.markdown('<hr style="border: none; border-top: 1px solid rgba(0, 0, 0, 0.08); margin: 12px 0;">', unsafe_allow_html=True)
    st.sidebar.markdown('<p style="font-size: 11px; color: #86868B; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;">Active Segment Filters</p>', unsafe_allow_html=True)

    # Define filter selections
    active_filters = {}

    if engineered_df is not None and not engineered_df.empty:
        # Department multiselect
        dept_options = sorted(engineered_df["Department"].unique())
        selected_depts = st.sidebar.multiselect(
            "Departments",
            options=dept_options,
            key="filter_dept"
        )
        if selected_depts:
            active_filters["Department"] = selected_depts

        # Job role multiselect (restricted by selected departments)
        if selected_depts:
            role_options = sorted(engineered_df[engineered_df["Department"].isin(selected_depts)]["JobRole"].unique())
        else:
            role_options = sorted(engineered_df["JobRole"].unique())
            
        selected_roles = st.sidebar.multiselect(
            "Job Roles",
            options=role_options,
            key="filter_role"
        )
        if selected_roles:
            active_filters["JobRole"] = selected_roles

        # Job level multiselect
        level_options = sorted(engineered_df["JobLevel"].unique())
        selected_levels = st.sidebar.multiselect(
            "Job Levels",
            options=level_options,
            key="filter_level"
        )
        if selected_levels:
            active_filters["JobLevel"] = selected_levels

        # Overtime selector
        selected_ot = st.sidebar.multiselect(
            "Overtime Work",
            options=["Yes", "No"],
            key="filter_ot"
        )
        if selected_ot:
            active_filters["OverTime"] = selected_ot

        # Business Travel selector
        travel_options = ["Non-Travel", "Travel Rarely", "Travel Frequently"]
        selected_travel = st.sidebar.multiselect(
            "Business Travel",
            options=travel_options,
            key="filter_travel"
        )
        if selected_travel:
            active_filters["BusinessTravel"] = selected_travel

        # Age Range Slider
        min_age, max_age = int(engineered_df["Age"].min()), int(engineered_df["Age"].max())
        selected_age = st.sidebar.slider(
            "Age Range",
            min_value=min_age,
            max_value=max_age,
            value=(st.session_state.get("filter_age", (min_age, max_age))),
            key="filter_age"
        )
        active_filters["Age"] = selected_age

        # Tenure Range Slider
        min_tenure, max_tenure = int(engineered_df["YearsAtCompany"].min()), int(engineered_df["YearsAtCompany"].max())
        selected_tenure = st.sidebar.slider(
            "Tenure at Company",
            min_value=min_tenure,
            max_value=max_tenure,
            value=(st.session_state.get("filter_tenure", (min_tenure, max_tenure))),
            key="filter_tenure"
        )
        active_filters["YearsAtCompany"] = selected_tenure

        # Gender multiselect
        selected_gender = st.sidebar.multiselect(
            "Gender",
            options=sorted(engineered_df["Gender"].unique()),
            key="filter_gender"
        )
        if selected_gender:
            active_filters["Gender"] = selected_gender

        # Marital Status multiselect
        selected_marital = st.sidebar.multiselect(
            "Marital Status",
            options=sorted(engineered_df["MaritalStatus"].unique()),
            key="filter_marital"
        )
        if selected_marital:
            active_filters["MaritalStatus"] = selected_marital

        # Education Level multiselect
        edu_options = [1, 2, 3, 4, 5]
        edu_mapping = {1: "1 = Below College", 2: "2 = College", 3: "3 = Bachelor", 4: "4 = Master", 5: "5 = Doctor"}
        selected_edu = st.sidebar.multiselect(
            "Education Levels",
            options=edu_options,
            format_func=lambda x: edu_mapping[x],
            key="filter_education"
        )
        if selected_edu:
            active_filters["Education"] = selected_edu

        # Education Field multiselect
        selected_field = st.sidebar.multiselect(
            "Education Fields",
            options=sorted(engineered_df["EducationField"].unique()),
            key="filter_field"
        )
        if selected_field:
            active_filters["EducationField"] = selected_field

    # 4. FILTER EXECUTION & SHARED STATE PROPAGATION
    st.session_state["sidebar_filters"] = active_filters
    if engineered_df is not None and not engineered_df.empty:
        st.session_state["filtered_df"] = filter_dataframe(engineered_df, active_filters)
    else:
        st.session_state["filtered_df"] = pd.DataFrame()

    # 5. STREAMLIT NAVIGATION ROUTER
    pg = st.navigation([
        st.Page(show_overview, title="Executive Overview", icon="📊"),
        st.Page(show_departments_roles, title="Departments & Roles", icon="🏢"),
        st.Page(show_demographics, title="Demographic Explorer", icon="👥"),
        st.Page(show_tenure_career, title="Tenure & Career", icon="📈"),
        st.Page(show_workload_mobility, title="Workload & Mobility", icon="💼"),
        st.Page(show_risk_hotspots, title="Risk Hotspots", icon="⚠️"),
        st.Page(show_recommendations, title="Insights & Recommendations", icon="💡"),
        st.Page(show_methodology, title="Methodology & Data Quality", icon="📖")
    ])
    pg.run()

if __name__ == "__main__":
    main()
