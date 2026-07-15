import pandas as pd
import numpy as np
from typing import Dict, Any

def run_chi_square_test(df: pd.DataFrame, feature_col: str, target_col: str = "Attrition") -> Dict[str, Any]:
    """
    Performs a Chi-Square test of independence between the target Attrition and a categorical feature.
    Calculates Cramér's V for association strength and checks for small expected cell counts.
    """
    try:
        from scipy.stats import chi2_contingency
    except ImportError:
        return {"error": "scipy is not installed"}

    if df is None or df.empty or len(df[target_col].unique()) < 2:
        return {"error": "Insufficient data to run test"}

    # Create contingency table
    contingency_table = pd.crosstab(df[feature_col], df[target_col])
    
    # Run test
    try:
        chi2, p_val, dof, expected = chi2_contingency(contingency_table)
    except Exception as e:
        return {"error": f"Statistical calculation error: {str(e)}"}

    n = contingency_table.sum().sum()
    
    # Cramér's V calculation
    # Since Attrition has 2 categories (Retained, Exited), min(r-1, c-1) = 1.
    # Therefore, V = sqrt(chi2 / n)
    cramers_v = np.sqrt(chi2 / n) if n > 0 else 0.0

    # Check for cell count assumption
    cells_below_5 = (expected < 5).sum()
    total_cells = expected.size
    pct_below_5 = (cells_below_5 / total_cells) * 100.0 if total_cells > 0 else 0.0
    violates_assumption = pct_below_5 > 20.0

    # Visual strength interpretations
    if cramers_v < 0.1:
        strength = "Negligible"
    elif cramers_v < 0.3:
        strength = "Weak"
    elif cramers_v < 0.5:
        strength = "Moderate"
    else:
        strength = "Strong"

    # Plain language interpretation
    significant = p_val < 0.05
    if significant:
        narrative = (
            f"There is a statistically significant association (p = {p_val:.4f}) between "
            f"{feature_col} and Attrition, with a {strength.lower()} strength of association "
            f"(Cramér's V = {cramers_v:.3f})."
        )
    else:
        narrative = (
            f"No statistically significant association was observed (p = {p_val:.4f}, "
            f"Cramér's V = {cramers_v:.3f}) between {feature_col} and Attrition."
        )

    return {
        "test_name": "Chi-Square Test of Independence",
        "feature": feature_col,
        "chi2_statistic": float(round(chi2, 4)),
        "p_value": float(p_val),
        "dof": int(dof),
        "sample_size": int(n),
        "cramers_v": float(round(cramers_v, 4)),
        "association_strength": strength,
        "is_significant": bool(significant),
        "violates_assumption": bool(violates_assumption),
        "cells_below_5_pct": float(round(pct_below_5, 2)),
        "narrative": narrative,
        "limitation": "Observed associations do not establish direct causation. Confounding factors may exist."
    }

def run_mann_whitney_u_test(df: pd.DataFrame, numeric_col: str, target_col: str = "Attrition") -> Dict[str, Any]:
    """
    Performs a Mann-Whitney U test comparing the distribution of a numeric column
    between the Retained (0) and Exited (1) groups.
    Calculates effect size (rank-biserial correlation).
    """
    try:
        from scipy.stats import mannwhitneyu
    except ImportError:
        return {"error": "scipy is not installed"}

    if df is None or df.empty or len(df[target_col].unique()) < 2:
        return {"error": "Insufficient data to run test"}

    # Drop NaNs for the numeric column
    clean_data = df[[numeric_col, target_col]].dropna()
    
    group_0 = clean_data[clean_data[target_col] == 0][numeric_col]
    group_1 = clean_data[clean_data[target_col] == 1][numeric_col]

    n0 = len(group_0)
    n1 = len(group_1)

    if n0 < 3 or n1 < 3:
        return {"error": "Sample size in one of the groups is too small to perform test"}

    # Summary Stats
    med0 = float(group_0.median())
    med1 = float(group_1.median())
    iqr0_25 = float(group_0.quantile(0.25))
    iqr0_75 = float(group_0.quantile(0.75))
    iqr1_25 = float(group_1.quantile(0.25))
    iqr1_75 = float(group_1.quantile(0.75))

    try:
        stat, p_val = mannwhitneyu(group_0, group_1, alternative='two-sided')
    except Exception as e:
        return {"error": f"Statistical calculation error: {str(e)}"}

    # Effect Size: Rank-biserial correlation
    # r = 1 - (2 * U) / (n0 * n1)
    # We use the standard U statistic, but since mannwhitneyu returns U of first group, 
    # we compute it carefully.
    denom = n0 * n1
    effect_size = 1 - (2.0 * stat) / denom if denom > 0 else 0.0
    abs_effect = abs(effect_size)

    if abs_effect < 0.1:
        strength = "Negligible"
    elif abs_effect < 0.3:
        strength = "Small"
    elif abs_effect < 0.5:
        strength = "Medium"
    else:
        strength = "Large"

    significant = p_val < 0.05
    if significant:
        direction = "higher" if med1 > med0 else "lower"
        narrative = (
            f"There is a statistically significant difference (p = {p_val:.4f}) in "
            f"{numeric_col} between retained and exited employees. Exited employees show a "
            f"{direction} median value ({med1:.2f}) compared to retained employees ({med0:.2f}), "
            f"with a {strength.lower()} effect size (rank-biserial r = {effect_size:.3f})."
        )
    else:
        narrative = (
            f"No statistically significant difference in {numeric_col} was observed "
            f"between retained and exited groups (p = {p_val:.4f}, rank-biserial r = {effect_size:.3f})."
        )

    return {
        "test_name": "Mann-Whitney U Test",
        "feature": numeric_col,
        "u_statistic": float(stat),
        "p_value": float(p_val),
        "retained_count": int(n0),
        "exited_count": int(n1),
        "retained_median": med0,
        "exited_median": med1,
        "retained_iqr": [iqr0_25, iqr0_75],
        "exited_iqr": [iqr1_25, iqr1_75],
        "effect_size": float(round(effect_size, 4)),
        "difference_strength": strength,
        "is_significant": bool(significant),
        "narrative": narrative,
        "limitation": "The Mann-Whitney U test compares distributions, not just means. A significant result suggests general shift in distribution rather than strict mean differences. Observed difference does not imply causation."
    }
