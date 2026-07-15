import streamlit as st
import pandas as pd
from utils.data_loader import load_uploaded_data
from utils.data_cleaning import clean_and_validate_data
from utils.feature_engineering import apply_feature_engineering
from utils.filtering import filter_dataframe
from components.page_header import render_page_header
from components.footer import render_footer
from utils.exports import convert_df_to_csv

def show_methodology():
    """
    Renders the Methodology and Data Quality page.
    """
    # Fetch data from session state
    if "clean_df" not in st.session_state or st.session_state["clean_df"] is None:
        st.warning("Data not loaded.")
        return

    raw_df = st.session_state["clean_df"]
    df = st.session_state["filtered_df"]
    dq_report = st.session_state.get("dq_report", {})
    early_tenure_threshold = st.session_state.get("early_tenure_threshold", 2)

    total_count = len(raw_df)
    active_count = len(df)

    render_page_header(
        title="Methodology and Data Quality",
        subtitle="Technical documentation, research formulas, and live data quality dashboards",
        employee_count=active_count,
        total_count=total_count
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Live Data Quality Audit", 
        "📂 Alternative Data Uploader",
        "📖 Formulations & Dictionary", 
        "📄 Academic Disclaimer"
    ])

    with tab1:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Live Data Quality Summary</h3>', unsafe_allow_html=True)
        
        if dq_report:
            # Grid of quality cards
            qcol1, qcol2, qcol3, qcol4 = st.columns(4)
            with qcol1:
                st.metric("Total Records Processed", f"{dq_report.get('raw_record_count', 0):,}")
            with qcol2:
                st.metric("Clean Records (Retained)", f"{dq_report.get('clean_record_count', 0):,}")
            with qcol3:
                st.metric("Duplicate Count (Dropped)", f"{dq_report.get('duplicate_count', 0)}")
            with qcol4:
                st.metric("Completeness Ratio", f"{dq_report.get('data_completeness_pct', 0.0):.2f}%")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Detailed Quality Validations Ledger</p>', unsafe_allow_html=True)
            
            details = dq_report.get("validation_details", [])
            if details:
                details_df = pd.DataFrame(details)
                st.dataframe(
                    details_df,
                    column_config={
                        "check_name": "Validation Check",
                        "affected_records": "Affected Count",
                        "severity": "Severity Level",
                        "resolution": "Applied Resolution",
                        "action": "Remediation Details"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.success("All schema, duplicate, attrition format, and logical range checks passed successfully. No anomalies found.")
        else:
            st.info("No data quality report generated.")

    with tab2:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Upload Custom Workforce CSV</h3>', unsafe_allow_html=True)
        st.markdown(
            """
            Provide a custom CSV matching the schema to update all visualizations and calculations for the current session.
            """
        )
        
        uploaded_file = st.file_uploader("Choose a CSV File", type="csv")
        if uploaded_file is not None:
            uploaded_df = load_uploaded_data(uploaded_file)
            if uploaded_df is not None:
                clean_df_up, dq_report_up = clean_and_validate_data(uploaded_df)
                
                if "error" in dq_report_up:
                    st.error(f"Validation failed: {dq_report_up['error']}")
                else:
                    # Apply changes to session state
                    st.session_state["clean_df"] = clean_df_up
                    st.session_state["dq_report"] = dq_report_up
                    st.session_state["completeness_pct"] = dq_report_up["data_completeness_pct"]
                    
                    # Apply feature engineering
                    engineered_up = apply_feature_engineering(clean_df_up, early_tenure_threshold)
                    st.session_state["engineered_df"] = engineered_up
                    
                    # Re-filter
                    filters = st.session_state.get("sidebar_filters", {})
                    st.session_state["filtered_df"] = filter_dataframe(engineered_up, filters)
                    
                    st.success("Custom workforce dataset uploaded, validated, and applied successfully! Refreshing session...")
                    st.rerun()

    with tab3:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Metric Formulations</h3>', unsafe_allow_html=True)
        
        # LaTeX Formulas
        st.markdown("#### Attrition Rate")
        st.latex(r"Attrition\ Rate = \frac{Exited\ Employees}{Total\ Employees} \times 100")
        
        st.markdown("#### Retention Rate")
        st.latex(r"Retention\ Rate = \frac{Retained\ Employees}{Total\ Employees} \times 100")

        st.markdown("#### Relative Attrition Index")
        st.latex(r"Relative\ Attrition\ Index = \frac{Group\ Attrition\ Rate}{Organizational\ Baseline\ Attrition\ Rate}")
        st.markdown(
            "An index value of `1.00` represents a rate identical to the overall organizational baseline. "
            "Values above `1.00` indicate elevated risk (e.g., `2.00x` is double the baseline)."
        )

        st.markdown("#### Early-Tenure Attrition Rate")
        st.latex(r"Early\ Tenure\ Attrition\ Rate = \frac{Exited\ Employees\ with\ Tenure \leq T}{Total\ Employees\ with\ Tenure \leq T} \times 100")
        st.markdown(f"Where the threshold $T$ is currently configured as **{early_tenure_threshold} years**.")

        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-top: 20px; margin-bottom: 12px;">Data Dictionary Overview</h3>', unsafe_allow_html=True)
        st.markdown(
            """
            * **Attrition**: Binary indicator of whether the employee exited (`1 = Exited`, `0 = Retained`).
            * **BusinessTravel**: Frequency of work travel (`Non-Travel`, `Travel Rarely`, `Travel Frequently`).
            * **JobLevel**: Seniority grade of the employee (typically integers starting at 1).
            * **OverTime**: Workload indicator of whether the employee logs overtime (`Yes`, `No`).
            * **DistanceFromHome**: Commute indicator between home and work site.
            * **Satisfaction & Engagement Ratings**: Standard scales of 1 (Low) to 4 (Very High) for `EnvironmentSatisfaction`, `JobSatisfaction`, `RelationshipSatisfaction`, `JobInvolvement`.
            * **WorkLifeBalance**: Performance/balance ratings mapped from 1 (Poor) to 4 (Excellent).
            """
        )

    with tab4:
        st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Analytical Case Study Scope</h3>', unsafe_allow_html=True)
        from components.disclaimer import render_academic_disclaimer, render_causation_disclaimer, render_data_privacy_notice, render_statistical_limitation
        render_academic_disclaimer()
        render_causation_disclaimer()
        render_data_privacy_notice()
        render_statistical_limitation()

    render_footer(active_count)

if __name__ == "__main__":
    show_methodology()
