import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

def calculate_core_metrics(df: pd.DataFrame, early_tenure_threshold: int = 2) -> Dict[str, Any]:
    """
    Computes key performance indicators for the active filtered dataset.
    """
    total = len(df)
    if total == 0:
        return {
            "total_employees": 0,
            "exited_employees": 0,
            "retained_employees": 0,
            "overall_attrition_rate": 0.0,
            "retention_rate": 0.0,
            "early_tenure_total": 0,
            "early_tenure_exits": 0,
            "early_tenure_attrition_rate": 0.0,
            "early_tenure_exit_contribution": 0.0
        }

    exited = int((df["Attrition"] == 1).sum())
    retained = int((df["Attrition"] == 0).sum())
    
    attrition_rate = (exited / total) * 100.0
    retention_rate = (retained / total) * 100.0

    # Early tenure calculations (using threshold)
    early_tenure_df = df[df["YearsAtCompany"] <= early_tenure_threshold]
    early_total = len(early_tenure_df)
    early_exits = int((early_tenure_df["Attrition"] == 1).sum()) if early_total > 0 else 0
    
    early_attrition_rate = (early_exits / early_total) * 100.0 if early_total > 0 else 0.0
    early_exit_contribution = (early_exits / exited) * 100.0 if exited > 0 else 0.0

    return {
        "total_employees": total,
        "exited_employees": exited,
        "retained_employees": retained,
        "overall_attrition_rate": float(round(attrition_rate, 2)),
        "retention_rate": float(round(retention_rate, 2)),
        "early_tenure_total": early_total,
        "early_tenure_exits": early_exits,
        "early_tenure_attrition_rate": float(round(early_attrition_rate, 2)),
        "early_tenure_exit_contribution": float(round(early_exit_contribution, 2))
    }

def calculate_group_attrition(df: pd.DataFrame, group_col: str, overall_rate: float, total_exits_org: int) -> pd.DataFrame:
    """
    Computes attrition metrics segmented by a categorical variable.
    Returns:
        DataFrame with columns: Group, Headcount, Exited, Retained, Attrition Rate, Baseline Difference, Relative Index, Exit Contribution
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["Group", "Headcount", "Exited", "Retained", "Attrition Rate", "Baseline Difference", "Relative Index", "Exit Contribution"])

    # Aggregate
    agg = df.groupby(group_col).agg(
        Headcount=('Attrition', 'count'),
        Exited=('Attrition', lambda x: (x == 1).sum()),
        Retained=('Attrition', lambda x: (x == 0).sum())
    ).reset_index()

    agg = agg.rename(columns={group_col: "Group"})

    # Safe division metrics
    agg["Attrition Rate"] = (agg["Exited"] / agg["Headcount"]) * 100.0
    agg["Baseline Difference"] = agg["Attrition Rate"] - overall_rate
    agg["Relative Index"] = agg["Attrition Rate"] / overall_rate if overall_rate > 0 else 1.0
    agg["Exit Contribution"] = (agg["Exited"] / total_exits_org) * 100.0 if total_exits_org > 0 else 0.0

    # Rounding
    agg["Attrition Rate"] = agg["Attrition Rate"].round(2)
    agg["Baseline Difference"] = agg["Baseline Difference"].round(2)
    agg["Relative Index"] = agg["Relative Index"].round(2)
    agg["Exit Contribution"] = agg["Exit Contribution"].round(2)

    return agg.sort_values(by="Attrition Rate", ascending=False)

def calculate_workload_attrition_matrix(df: pd.DataFrame, overall_rate: float) -> pd.DataFrame:
    """
    Computes the Workload Attrition Index for combinations of OverTime and BusinessTravel.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    agg = df.groupby(["OverTime", "BusinessTravel"]).agg(
        Headcount=('Attrition', 'count'),
        Exited=('Attrition', lambda x: (x == 1).sum()),
        Retained=('Attrition', lambda x: (x == 0).sum())
    ).reset_index()

    # Calculate metrics
    agg["Attrition Rate"] = (agg["Exited"] / agg["Headcount"]) * 100.0
    agg["Workload Attrition Index"] = agg["Attrition Rate"] / overall_rate if overall_rate > 0 else 1.0
    agg["Baseline Difference"] = agg["Attrition Rate"] - overall_rate

    # Rounding
    agg["Attrition Rate"] = agg["Attrition Rate"].round(2)
    agg["Workload Attrition Index"] = agg["Workload Attrition Index"].round(2)
    agg["Baseline Difference"] = agg["Baseline Difference"].round(2)

    # Format combo label
    agg["Workload Combination"] = agg["OverTime"].astype(str) + " + " + agg["BusinessTravel"].astype(str)
    
    # Re-order columns
    columns_order = [
        "Workload Combination", "OverTime", "BusinessTravel", 
        "Headcount", "Exited", "Retained", 
        "Attrition Rate", "Workload Attrition Index", "Baseline Difference"
    ]
    return agg[columns_order].sort_values(by="Workload Attrition Index", ascending=False)
