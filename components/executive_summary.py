import streamlit as st

def render_executive_summary_card(
    metrics: dict,
    top_dept,
    top_role,
    ot_yes_rate: float,
    ot_no_rate: float,
    early_tenure_threshold: int
):
    """
    Renders an executive summary card presenting key workforce stability observations.
    """
    bullets = []
    
    # 1. Organizational Status
    overall_rate = metrics["overall_attrition_rate"]
    exited = metrics["exited_employees"]
    total = metrics["total_employees"]
    bullets.append(
        f"**Organizational Baseline:** The overall voluntary attrition rate is **{overall_rate:.1f}%**, representing **{exited} departures** out of a total filtered workforce of **{total:,} employees**."
    )
    
    # 2. Highest priority department hotspot
    if top_dept is not None and top_dept["Attrition Rate"] > overall_rate:
        bullets.append(
            f"**Department Hotspot:** Attrition is concentrated in the **{top_dept['Group']}** department, showing an elevated rate of **{top_dept['Attrition Rate']:.1f}%** ({top_dept['Attrition Rate'] - overall_rate:+.1f} pp difference)."
        )
        
    # 3. Highest priority role hotspot
    if top_role is not None and top_role["Attrition Rate"] > overall_rate:
        bullets.append(
            f"**Functional Role Friction:** **{top_role['Group']}** roles exhibit a rate of **{top_role['Attrition Rate']:.1f}%** with **{top_role['Exited']} departures**."
        )

    # 4. Workload observation
    if ot_yes_rate > ot_no_rate:
        multiplier = ot_yes_rate / ot_no_rate if ot_no_rate > 0 else 1.0
        bullets.append(
            f"**Workload Stressor:** Overtime is associated with a **{multiplier:.1f}x multiplier** on departures (**{ot_yes_rate:.1f}%** for overtime workers vs. **{ot_no_rate:.1f}%** for standard hours)."
        )

    # 5. Tenure observation
    early_tenure_rate = metrics["early_tenure_attrition_rate"]
    early_contrib = metrics["early_tenure_exit_contribution"]
    bullets.append(
        f"**Early Tenure Vulnerability:** Employees in their first **{early_tenure_threshold} years** account for **{early_contrib:.1f}% of all voluntary exits**, with an attrition rate of **{early_tenure_rate:.1f}%**."
    )

    bullet_items = ""
    for b in bullets[:5]:
        # Simple parser to swap markdown bold stars to HTML strong tags
        processed_str = b
        while "**" in processed_str:
            processed_str = processed_str.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
        bullet_items += (
            f'<div style="display: flex; align-items: flex-start; margin-bottom: 10px; font-size: 13.5px; line-height: 1.5; color: #1D1D1F;">'
            f'<span style="color: #0071E3; margin-right: 8px; font-size: 15px;">•</span>'
            f'<div>{processed_str}</div>'
            f'</div>'
        )

    st.markdown(
        f"""
        <div class="apple-card" style="background-color: #FBFBFD; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 14px; padding: 20px 24px; margin-bottom: 24px;">
            <div style="font-size: 12px; font-weight: 600; color: #6E6E73; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.5px;">
                Executive Action Summary
            </div>
            {bullet_items}
        </div>
        """,
        unsafe_allow_html=True
    )
