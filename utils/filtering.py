import pandas as pd
from typing import Dict, Any

def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies a dict of active filters to the dataframe using intersection logic.
    Each key in the dict represents a column, and the value represents the active filter.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    filtered_df = df.copy()

    # Department
    if "Department" in filters and filters["Department"]:
        filtered_df = filtered_df[filtered_df["Department"].isin(filters["Department"])]

    # JobRole
    if "JobRole" in filters and filters["JobRole"]:
        filtered_df = filtered_df[filtered_df["JobRole"].isin(filters["JobRole"])]

    # Age Range (tuple: min, max)
    if "Age" in filters and filters["Age"]:
        min_age, max_age = filters["Age"]
        filtered_df = filtered_df[(filtered_df["Age"] >= min_age) & (filtered_df["Age"] <= max_age)]

    # YearsAtCompany Range (tuple: min, max)
    if "YearsAtCompany" in filters and filters["YearsAtCompany"]:
        min_tenure, max_tenure = filters["YearsAtCompany"]
        filtered_df = filtered_df[(filtered_df["YearsAtCompany"] >= min_tenure) & (filtered_df["YearsAtCompany"] <= max_tenure)]

    # Gender
    if "Gender" in filters and filters["Gender"]:
        filtered_df = filtered_df[filtered_df["Gender"].isin(filters["Gender"])]

    # MaritalStatus
    if "MaritalStatus" in filters and filters["MaritalStatus"]:
        filtered_df = filtered_df[filtered_df["MaritalStatus"].isin(filters["MaritalStatus"])]

    # Education (numeric ratings)
    if "Education" in filters and filters["Education"]:
        filtered_df = filtered_df[filtered_df["Education"].isin(filters["Education"])]

    # EducationField
    if "EducationField" in filters and filters["EducationField"]:
        filtered_df = filtered_df[filtered_df["EducationField"].isin(filters["EducationField"])]

    # OverTime
    if "OverTime" in filters and filters["OverTime"]:
        filtered_df = filtered_df[filtered_df["OverTime"].isin(filters["OverTime"])]

    # BusinessTravel
    if "BusinessTravel" in filters and filters["BusinessTravel"]:
        filtered_df = filtered_df[filtered_df["BusinessTravel"].isin(filters["BusinessTravel"])]

    # JobLevel
    if "JobLevel" in filters and filters["JobLevel"]:
        filtered_df = filtered_df[filtered_df["JobLevel"].isin(filters["JobLevel"])]

    # Optional DistanceFromHome Range
    if "DistanceFromHome" in filters and filters["DistanceFromHome"]:
        min_dist, max_dist = filters["DistanceFromHome"]
        filtered_df = filtered_df[(filtered_df["DistanceFromHome"] >= min_dist) & (filtered_df["DistanceFromHome"] <= max_dist)]

    # Optional MonthlyIncome Range
    if "MonthlyIncome" in filters and filters["MonthlyIncome"]:
        min_inc, max_inc = filters["MonthlyIncome"]
        filtered_df = filtered_df[(filtered_df["MonthlyIncome"] >= min_inc) & (filtered_df["MonthlyIncome"] <= max_inc)]

    return filtered_df
