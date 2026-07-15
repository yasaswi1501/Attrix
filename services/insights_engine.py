import pandas as pd
from typing import Dict, Any
from utils.metrics import calculate_core_metrics, calculate_group_attrition

class ExecutiveInsightsEngine:
    """
    Centralized insights engine to generate dynamic, evidence-linked findings,
    recommendations, and confidence tags based on currently filtered workforce datasets.
    """
    @staticmethod
    def generate_overview_insights(df: pd.DataFrame, early_tenure_threshold: int = 2) -> Dict[str, Any]:
        if df is None or df.empty:
            return {}

        metrics = calculate_core_metrics(df, early_tenure_threshold)
        overall_rate = metrics["overall_attrition_rate"]
        exited_count = metrics["exited_employees"]

        # 1. Department Risk
        dept_data = calculate_group_attrition(df, "Department", overall_rate, exited_count)
        if not dept_data.empty:
            top_dept = dept_data.sort_values(by="Attrition Rate", ascending=False).iloc[0]
            dept_finding = f"The {top_dept['Group']} department exhibits the highest observed attrition rate at {top_dept['Attrition Rate']:.1f}%, exceeding the filtered organizational baseline of {overall_rate:.1f}% by {top_dept['Attrition Rate'] - overall_rate:+.1f} percentage points."
            dept_recommendation = f"Review workload capacity, leadership alignment, and role progression pathing within {top_dept['Group']}."
            dept_confidence = "High Confidence" if top_dept["Headcount"] >= 30 else "Moderate Confidence"
            dept_priority = "Critical" if top_dept["Attrition Rate"] > 25.0 else "High"
            dept_name = top_dept["Group"]
        else:
            dept_finding = "No department-level data available."
            dept_recommendation = ""
            dept_confidence = "Low Confidence"
            dept_priority = "Medium"
            dept_name = "N/A"

        # 2. Role Risk
        role_data = calculate_group_attrition(df, "JobRole", overall_rate, exited_count)
        role_data_filtered = role_data[role_data["Headcount"] >= 10]
        if not role_data_filtered.empty:
            top_role = role_data_filtered.sort_values(by="Attrition Rate", ascending=False).iloc[0]
            role_finding = f"Within the filtered population, {top_role['Group']} roles show the highest rate of voluntary departures at {top_role['Attrition Rate']:.1f}%."
            role_recommendation = f"Audit career mapping tracks and quota settings for the {top_role['Group']} profile."
            role_confidence = "High Confidence" if top_role["Headcount"] >= 20 else "Moderate Confidence"
            role_priority = "Critical" if top_role["Attrition Rate"] > 30.0 else "High"
            role_name = top_role["Group"]
        else:
            role_finding = "No role-level metrics meet minimum sample thresholds."
            role_recommendation = ""
            role_confidence = "Low Confidence"
            role_priority = "Medium"
            role_name = "N/A"

        # 3. Overtime Workload
        ot_yes_df = df[df["OverTime"] == "Yes"]
        ot_no_df = df[df["OverTime"] == "No"]
        ot_yes_rate = (ot_yes_df["Attrition"] == 1).sum() / len(ot_yes_df) * 100 if len(ot_yes_df) > 0 else 0
        ot_no_rate = (ot_no_df["Attrition"] == 1).sum() / len(ot_no_df) * 100 if len(ot_no_df) > 0 else 0
        ot_diff = ot_yes_rate - ot_no_rate

        ot_finding = f"Employees working overtime exhibit an observed attrition rate of {ot_yes_rate:.1f}%, compared to only {ot_no_rate:.1f}% for standard hours (a difference of {ot_diff:+.1f} percentage points)."
        ot_recommendation = "Establish manager balance checks when overtime requirements cross standard limits."
        ot_confidence = "High Confidence" if len(ot_yes_df) >= 25 else "Moderate Confidence"
        ot_priority = "High" if ot_diff > 10.0 else "Medium"

        # 4. Early-Tenure
        early_finding = f"Hires within their first {early_tenure_threshold} years account for {metrics['early_tenure_exit_contribution']:.1f}% of total exits, exhibiting a cohort attrition rate of {metrics['early_tenure_attrition_rate']:.1f}%."
        early_recommendation = "Optimize feedback checkpoints at 30/90/180 days to stabilize early transitions."
        early_confidence = "High Confidence" if metrics['early_tenure_total'] >= 30 else "Moderate Confidence"
        early_priority = "High" if metrics['early_tenure_attrition_rate'] > overall_rate * 1.25 else "Medium"

        return {
            "department": {
                "name": dept_name,
                "finding": dept_finding,
                "recommendation": dept_recommendation,
                "confidence": dept_confidence,
                "owner": "Department Leadership",
                "priority": dept_priority
            },
            "role": {
                "name": role_name,
                "finding": role_finding,
                "recommendation": role_recommendation,
                "confidence": role_confidence,
                "owner": "HR Business Partner",
                "priority": role_priority
            },
            "overtime": {
                "finding": ot_finding,
                "recommendation": ot_recommendation,
                "confidence": ot_confidence,
                "owner": "Operations Management",
                "priority": ot_priority
            },
            "early_tenure": {
                "finding": early_finding,
                "recommendation": early_recommendation,
                "confidence": early_confidence,
                "owner": "Talent Management Lead",
                "priority": early_priority
            }
        }
