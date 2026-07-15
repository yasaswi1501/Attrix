import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List

EXPECTED_COLUMNS = [
    'Age', 'Attrition', 'BusinessTravel', 'DailyRate', 'Department',
    'DistanceFromHome', 'Education', 'EducationField', 'EnvironmentSatisfaction',
    'Gender', 'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobRole',
    'JobSatisfaction', 'MaritalStatus', 'MonthlyIncome', 'MonthlyRate',
    'NumCompaniesWorked', 'OverTime', 'PercentSalaryHike', 'PerformanceRating',
    'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
    'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
    'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager'
]

NUMERIC_COLUMNS = [
    'Age', 'DailyRate', 'DistanceFromHome', 'Education', 'EnvironmentSatisfaction',
    'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobSatisfaction',
    'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked', 'PercentSalaryHike',
    'PerformanceRating', 'RelationshipSatisfaction', 'StockOptionLevel',
    'TotalWorkingYears', 'TrainingTimesLastYear', 'WorkLifeBalance',
    'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
    'YearsWithCurrManager'
]

CATEGORICAL_COLUMNS = [
    'BusinessTravel', 'Department', 'EducationField', 'Gender', 'JobRole',
    'MaritalStatus', 'OverTime'
]

def clean_and_validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Data quality and cleaning pipeline for Workforce Attrition.
    Returns:
        Tuple[clean_df, data_quality_summary_dict]
    """
    if df is None or df.empty:
        return pd.DataFrame(), {
            "error": "Dataset is empty or None",
            "raw_record_count": 0,
            "clean_record_count": 0,
            "data_completeness_pct": 0.0
        }

    raw_df = df.copy()
    validation_details = []
    
    # 1. Standardize and check columns
    raw_columns = list(raw_df.columns)
    raw_df.columns = [col.strip() for col in raw_df.columns]
    
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in raw_df.columns]
    if missing_cols:
        return raw_df, {
            "error": f"Missing required columns: {', '.join(missing_cols)}",
            "missing_required_columns": missing_cols,
            "expected_schema": EXPECTED_COLUMNS,
            "raw_record_count": len(raw_df),
            "clean_record_count": 0
        }

    # 2. Check and remove duplicate records
    duplicate_mask = raw_df.duplicated()
    duplicate_count = duplicate_mask.sum()
    if duplicate_count > 0:
        validation_details.append({
            "check_name": "Duplicate Records Check",
            "affected_records": int(duplicate_count),
            "severity": "Low",
            "resolution": "Duplicate records removed",
            "action": f"Dropped {duplicate_count} identical row(s)"
        })
        clean_df = raw_df.drop_duplicates()
    else:
        clean_df = raw_df.copy()

    # 3. Validate and clean Attrition Target
    # We accept: 0/1, Yes/No, Retained/Exited, True/False
    valid_attrition_count = 0
    invalid_attrition_count = 0
    missing_attrition_count = 0
    
    def normalize_attrition(val) -> int:
        nonlocal valid_attrition_count, invalid_attrition_count, missing_attrition_count
        if pd.isna(val) or str(val).strip() == "":
            missing_attrition_count += 1
            return -1
        
        val_str = str(val).strip().lower()
        if val_str in ['0', '0.0', 'no', 'retained', 'false', 'f']:
            valid_attrition_count += 1
            return 0
        elif val_str in ['1', '1.0', 'yes', 'exited', 'true', 't']:
            valid_attrition_count += 1
            return 1
        else:
            invalid_attrition_count += 1
            return -1

    clean_df['Attrition_Raw'] = clean_df['Attrition']
    clean_df['Attrition'] = clean_df['Attrition_Raw'].apply(normalize_attrition)
    
    if missing_attrition_count > 0:
        validation_details.append({
            "check_name": "Missing Attrition Labels",
            "affected_records": missing_attrition_count,
            "severity": "Critical",
            "resolution": "Records excluded",
            "action": f"Dropped {missing_attrition_count} record(s) with missing Attrition labels"
        })
    if invalid_attrition_count > 0:
        validation_details.append({
            "check_name": "Invalid Attrition Labels",
            "affected_records": invalid_attrition_count,
            "severity": "Critical",
            "resolution": "Records excluded",
            "action": f"Dropped {invalid_attrition_count} record(s) with unparseable Attrition values"
        })

    # Drop rows with invalid Attrition (-1)
    rows_before = len(clean_df)
    clean_df = clean_df[clean_df['Attrition'] != -1]
    rows_excluded_attrition = rows_before - len(clean_df)

    # 4. Clean Categorical columns
    for col in CATEGORICAL_COLUMNS:
        # Save raw missingness
        missing_in_col = clean_df[col].isna().sum()
        if missing_in_col > 0:
            validation_details.append({
                "check_name": f"Missing values in {col}",
                "affected_records": int(missing_in_col),
                "severity": "Medium",
                "resolution": "Imputed as 'Unknown' for visual aggregation",
                "action": f"Converted {missing_in_col} nulls to 'Unknown'"
            })
        
        # Clean whitespaces and underscores
        clean_df[col] = clean_df[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        # Normalize BusinessTravel underscores
        if col == "BusinessTravel":
            clean_df[col] = clean_df[col].str.replace('Travel_Rarely', 'Travel Rarely')\
                                         .str.replace('Travel_Frequently', 'Travel Frequently')\
                                         .str.replace('Non-Travel', 'Non-Travel')
        
        # Map back empty strings to 'Unknown'
        clean_df[col] = clean_df[col].replace({'nan': 'Unknown', '': 'Unknown'})

    # 5. Clean Numeric columns
    invalid_numeric_count = 0
    for col in NUMERIC_COLUMNS:
        original_col_vals = clean_df[col].copy()
        converted_col = pd.to_numeric(clean_df[col], errors='coerce')
        coerced_count = (original_col_vals.notna() & converted_col.isna()).sum()
        if coerced_count > 0:
            invalid_numeric_count += coerced_count
            validation_details.append({
                "check_name": f"Numeric Conversion Failure in {col}",
                "affected_records": int(coerced_count),
                "severity": "High",
                "resolution": "Coerced to NaN",
                "action": f"Forced {coerced_count} non-numeric value(s) to NaN"
            })
        clean_df[col] = converted_col

    # 6. Check for Impossible or Suspicious values
    impossible_records_count = 0
    
    # Age < 18 or > 80
    age_err = ((clean_df['Age'] < 18) | (clean_df['Age'] > 80)).sum()
    if age_err > 0:
        impossible_records_count += age_err
        validation_details.append({
            "check_name": "Out of Range Age",
            "affected_records": int(age_err),
            "severity": "Medium",
            "resolution": "Rows retained, flagged in diagnostics",
            "action": f"Observed {age_err} record(s) outside 18-80 age range"
        })
        
    # Negative values in key numeric columns
    neg_check_cols = ['MonthlyIncome', 'DistanceFromHome', 'YearsAtCompany', 'TotalWorkingYears', 'NumCompaniesWorked']
    for col in neg_check_cols:
        neg_err = (clean_df[col] < 0).sum()
        if neg_err > 0:
            impossible_records_count += neg_err
            validation_details.append({
                "check_name": f"Negative value in {col}",
                "affected_records": int(neg_err),
                "severity": "High",
                "resolution": "Replaced negative with NaN",
                "action": f"Found {neg_err} negative values in {col}"
            })
            clean_df.loc[clean_df[col] < 0, col] = np.nan

    # Logical checks for tenure variables
    tenure_checks = [
        ('YearsAtCompany', 'TotalWorkingYears'),
        ('YearsInCurrentRole', 'YearsAtCompany'),
        ('YearsWithCurrManager', 'YearsAtCompany'),
        ('YearsSinceLastPromotion', 'YearsAtCompany')
    ]
    for child, parent in tenure_checks:
        tenure_err = (clean_df[child] > clean_df[parent]).sum()
        if tenure_err > 0:
            impossible_records_count += tenure_err
            validation_details.append({
                "check_name": f"Inconsistent Tenure: {child} > {parent}",
                "affected_records": int(tenure_err),
                "severity": "High",
                "resolution": "Rows retained, detailed flags set to warning status",
                "action": f"Detected {tenure_err} violation(s)"
            })
            
    # Education outside 1-5
    edu_err = ((clean_df['Education'] < 1) | (clean_df['Education'] > 5)).sum()
    if edu_err > 0:
        impossible_records_count += edu_err
        validation_details.append({
            "check_name": "Education rating out of range",
            "affected_records": int(edu_err),
            "severity": "Medium",
            "resolution": "Coerced to NaN or clamped",
            "action": f"Observed {edu_err} values outside 1-5 range"
        })
        
    # Satisfaction ratings outside 1-4
    sat_cols = ['EnvironmentSatisfaction', 'JobInvolvement', 'JobSatisfaction', 'RelationshipSatisfaction', 'WorkLifeBalance']
    for col in sat_cols:
        sat_err = ((clean_df[col] < 1) | (clean_df[col] > 4)).sum()
        if sat_err > 0:
            impossible_records_count += sat_err
            validation_details.append({
                "check_name": f"Satisfaction Rating Out of Range: {col}",
                "affected_records": int(sat_err),
                "severity": "Medium",
                "resolution": "Retained raw but flagged",
                "action": f"Observed {sat_err} values outside 1-4 range"
            })

    # Calculate global completeness percentage
    total_cells = clean_df.size
    missing_cells = clean_df.isna().sum().sum()
    completeness_pct = ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 0.0

    # Summary dictionary
    summary = {
        "raw_record_count": len(raw_df),
        "clean_record_count": len(clean_df),
        "num_columns": len(clean_df.columns),
        "missing_value_count": int(missing_cells),
        "duplicate_count": int(duplicate_count),
        "invalid_value_count": int(invalid_attrition_count + invalid_numeric_count + impossible_records_count),
        "rows_excluded": int(duplicate_count + rows_excluded_attrition),
        "data_completeness_pct": float(round(completeness_pct, 2)),
        "validation_details": validation_details
    }

    return clean_df, summary
