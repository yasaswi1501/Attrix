import streamlit as st
import pandas as pd
from utils.metrics import calculate_core_metrics, calculate_group_attrition
from components.page_header import render_page_header
from components.empty_states import render_empty_state
from components.footer import render_footer

def show_recommendations():
    """
    Renders the Insights and Recommendations page.
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
        title="Evidence-Based Recommendations",
        subtitle="Operational and strategic action plans linked directly to observed workforce data patterns",
        employee_count=active_count,
        total_count=total_count
    )

    if active_count == 0:
        render_empty_state()
        render_footer(active_count)
        return

    # Calculate metrics for dynamic evidence insertion
    metrics = calculate_core_metrics(df, early_tenure_threshold)
    overall_rate = metrics["overall_attrition_rate"]
    exited_employees = metrics["exited_employees"]

    # Compute comparison groups
    # 1. Overtime
    ot_yes_df = df[df["OverTime"] == "Yes"]
    ot_no_df = df[df["OverTime"] == "No"]
    ot_yes_rate = (ot_yes_df["Attrition"] == 1).sum() / len(ot_yes_df) * 100 if len(ot_yes_df) > 0 else 0.0
    ot_no_rate = (ot_no_df["Attrition"] == 1).sum() / len(ot_no_df) * 100 if len(ot_no_df) > 0 else 0.0
    
    # 2. Travel
    travel_freq_df = df[df["BusinessTravel"] == "Travel Frequently"]
    travel_freq_rate = (travel_freq_df["Attrition"] == 1).sum() / len(travel_freq_df) * 100 if len(travel_freq_df) > 0 else 0.0

    # 3. Department
    dept_data = calculate_group_attrition(df, "Department", overall_rate, exited_employees)
    top_dept = dept_data.iloc[0] if not dept_data.empty else None

    # 4. Role
    role_data = calculate_group_attrition(df, "JobRole", overall_rate, exited_employees)
    top_role = role_data.iloc[0] if not role_data.empty else None

    # Render recommendations dynamically
    recommendations_shown = 0

    st.markdown('<h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Targeted Strategic Action Cards</h3>', unsafe_allow_html=True)

    # Reusable recommendation card renderer
    def render_rec_card(title: str, evidence: str, action: str, owner: str, timeline: str, metrics: str, caution: str):
        st.markdown(
            f"""
            <div class="apple-card" style="margin-bottom: 24px; border-left: 4px solid #0071E3;">
                <h4 style="font-size: 16px; font-weight: 700; color: #1D1D1F; margin-top: 0; margin-bottom: 12px;">{title}</h4>
                <div style="font-size: 13.5px; line-height: 1.6; color: #333333;">
                    <p><strong>📊 Observed Data Evidence:</strong><br>{evidence}</p>
                    <p><strong>💡 Recommended Action Plan:</strong><br>{action}</p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 10px; font-size: 12.5px;">
                        <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
                            <td style="padding: 6px 0; font-weight: 600; color: #6E6E73; width: 25%;">Suggested Owner:</td>
                            <td style="padding: 6px 0; color: #1D1D1F;">{owner}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
                            <td style="padding: 6px 0; font-weight: 600; color: #6E6E73;">Suggested Timeline:</td>
                            <td style="padding: 6px 0; color: #1D1D1F;">{timeline}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
                            <td style="padding: 6px 0; font-weight: 600; color: #6E6E73;">Success Metrics:</td>
                            <td style="padding: 6px 0; color: #1D1D1F;">{metrics}</td>
                        </tr>
                    </table>
                    <p style="font-size: 12px; color: #86868B; margin-top: 8px;"><em>⚠️ Risk Caution:</em> {caution}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 1: Early Tenure Onboarding & Mentorship
    if metrics["early_tenure_attrition_rate"] > overall_rate:
        recommendations_shown += 1
        render_rec_card(
            title="Pillar 1: Structured Early-Tenure Integration & Onboarding Checkpoints",
            evidence=(
                f"Employees with ≤ {early_tenure_threshold} years tenure exhibit an elevated observed attrition rate of "
                f"<strong>{metrics['early_tenure_attrition_rate']:.1f}%</strong>, compared to the overall average of "
                f"{overall_rate:.1f}% (a {metrics['early_tenure_attrition_rate'] - overall_rate:.1f} percentage point spike). "
                f"This cohort represents <strong>{metrics['early_tenure_exit_contribution']:.1f}% of all voluntary exits</strong> in the current view."
            ),
            action=(
                "Establish structured check-ins at 30, 60, and 90 days with hiring managers to review role clarity, resource access, and cultural integration. "
                "Pair new hires with a peer mentor outside their immediate reporting structure to facilitate safe onboarding feedback channels. "
                "Audit the recruitment expectations vs. job realities in departments with high early tenure exits."
            ),
            owner="People & Culture Team (HRBPs) + Hiring Managers",
            timeline="Pilot within 60 days, roll out globally in 120 days",
            metrics="First-year voluntary retention rates, 90-day onboarding satisfaction scores, Stay Interview completion rates",
            caution="Avoid over-burdening managers with paperwork; ensure check-in meetings focus on open dialog rather than bureaucratic reporting."
        )

    # Card 2: Overtime Governance & Capacity Planning
    if ot_yes_rate > overall_rate:
        recommendations_shown += 1
        render_rec_card(
            title="Pillar 2: Overtime Governance & Resource Capacity Calibration",
            evidence=(
                f"Employees working overtime exhibit a heightened attrition rate of <strong>{ot_yes_rate:.1f}%</strong>, "
                f"compared to <strong>{ot_no_rate:.1f}%</strong> for those not working overtime (a difference of "
                f"{ot_yes_rate - ot_no_rate:.1f} percentage points). This is a strong workload indicator of attrition correlation."
            ),
            action=(
                "Implement strict manager approval gates for chronic overtime work. "
                "Conduct quarterly resource capacity audits in teams showing consistent overtime logs (e.g. Technical/Engineering roles). "
                "Establish cross-training pathways to balance spikes in workloads. Integrate work-life balance satisfaction indicators into monthly team syncs."
            ),
            owner="Operations Directors + Department Leaders + Workforce Planning",
            timeline="Immediate (within 30 days) guidelines issued, quarterly reviews thereafter",
            metrics="Average monthly overtime hours logged, Work-Life Balance scores (from employee pulse surveys), department retention",
            caution="Do not penalize employees who rely on overtime pay; ensure any adjustments do not negatively affect compensation without communication."
        )

    # Card 3: Business Travel Audits & Virtual Collaboration
    if travel_freq_rate > overall_rate * 1.2:
        recommendations_shown += 1
        render_rec_card(
            title="Pillar 3: Travel Optimization & Virtual Collaboration Guidelines",
            evidence=(
                f"Frequent business travelers show an attrition rate of <strong>{travel_freq_rate:.1f}%</strong>, "
                f"which is {travel_freq_rate - overall_rate:.1f} percentage points higher than the baseline rate of {overall_rate:.1f}%."
            ),
            action=(
                "Audit role-specific travel expectations to establish a 'Virtual First' policy for internal checkpoints. "
                "Ensure frequent travelers receive structured recovery windows (e.g. work-from-home days immediately following multi-day travel). "
                "Re-evaluate travel budgets and customer-facing alignment strategies to reduce absolute travel days per employee."
            ),
            owner="Global Travel Operations + HR Business Partners + Account Management leadership",
            timeline="Within 60–90 days",
            metrics="Total business travel days, travel-related expense ratios, Travel satisfaction scores",
            caution="Ensure customer satisfaction metrics are monitored during any travel reduction pilots to avoid impacting client-facing deliverables."
        )

    # Card 4: Department-Specific Retention Reviews (sales or R&D)
    if top_dept is not None and top_dept["Attrition Rate"] > overall_rate * 1.2:
        recommendations_shown += 1
        render_rec_card(
            title=f"Pillar 4: Target Retention Review - {top_dept['Group']} Department",
            evidence=(
                f"The <strong>{top_dept['Group']}</strong> department experiences the highest attrition rate at "
                f"<strong>{top_dept['Attrition Rate']:.1f}%</strong>, accounting for <strong>{top_dept['Exited']} exits</strong> "
                f"({top_dept['Exit Contribution']:.1f}% of total exits in view)."
            ),
            action=(
                f"Commission an immediate qualitative listening tour in the {top_dept['Group']} department to capture workload, culture, and career path feedback. "
                "Review management and leadership structures for micro-cultures. Bench-mark compensation packages (salary and stock options) against industry norms."
            ),
            owner=f"Department Head of {top_dept['Group']} + People Analytics Manager",
            timeline="Initiate listening tour within 45 days, execute findings in 90 days",
            metrics=f"Department-level quarterly attrition rates, employee Net Promoter Scores (eNPS) in {top_dept['Group']}",
            caution="Ensure all qualitative feedback is aggregated and fully anonymized to encourage candid participation without fear of retaliation."
        )

    # Foundational: Compensation & Stay Interviews (standard fallback if data has low variance, or as a general executive pillar)
    if recommendations_shown < 3:
        # Show stay interview & career path recommendations as standard
        render_rec_card(
            title="Pillar 5: Institutionalize Stay Interviews & Transparency in Career Progression",
            evidence=(
                f"The general organizational attrition baseline is at <strong>{overall_rate:.1f}%</strong>. "
                f"Preventative retention efforts must focus on career progression and leadership continuity."
            ),
            action=(
                "Implement proactive 'Stay Interviews' for high-performing employees who have completed 2-3 years at the company. "
                "Launch transparent internal mobility pathways, allowing employees to rotate projects or teams without manager veto. "
                "Create a clear, documented framework linking Job Level and experience directly to promotion timelines."
            ),
            owner="People & Culture Team + Department Heads",
            timeline="Roll out templates in 60 days",
            metrics="Internal mobility rates, promotion satisfaction scores, voluntary attrition baseline",
            caution="Ensure career mapping matches real business vacancies to prevent employee frustration if promotion wait times do not improve."
        )

    render_footer(active_count)

if __name__ == "__main__":
    show_recommendations()
