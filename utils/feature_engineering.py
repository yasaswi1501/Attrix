import pandas as pd
import numpy as np

def apply_feature_engineering(df: pd.DataFrame, early_tenure_threshold: int = 2) -> pd.DataFrame:
    """
    Applies derived feature logic to the clean dataframe.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    engineered_df = df.copy()

    # 1. Attrition Labels
    engineered_df['AttritionLabel'] = engineered_df['Attrition'].map({0: 'Retained', 1: 'Exited'})

    # 2. Age Groups
    age_bins = [-np.inf, 17, 24, 34, 44, 54, np.inf]
    age_labels = ['Under 18', '18–24', '25–34', '35–44', '45–54', '55+']
    engineered_df['AgeGroup'] = pd.cut(engineered_df['Age'], bins=age_bins, labels=age_labels)
    # Re-order category to handle any weirdness
    engineered_df['AgeGroup'] = pd.Categorical(engineered_df['AgeGroup'], categories=age_labels, ordered=True)

    # 3. Tenure Bands
    tenure_bins = [-np.inf, 0.9, 2.1, 5.1, 10.1, 15.1, np.inf]
    tenure_labels = ['Less than 1 year', '1–2 years', '3–5 years', '6–10 years', '11–15 years', '16+ years']
    engineered_df['TenureBand'] = pd.cut(engineered_df['YearsAtCompany'], bins=tenure_bins, labels=tenure_labels)
    engineered_df['TenureBand'] = pd.Categorical(engineered_df['TenureBand'], categories=tenure_labels, ordered=True)

    # 4. Career Stage (based on TotalWorkingYears)
    career_bins = [-np.inf, 5.1, 10.1, 20.1, 30.1, np.inf]
    career_labels = ['Early Career: 0–5 years', 'Developing Career: 6–10 years', 'Mid-Career: 11–20 years', 'Experienced: 21–30 years', 'Senior Career: 31+ years']
    engineered_df['CareerStage'] = pd.cut(engineered_df['TotalWorkingYears'], bins=career_bins, labels=career_labels)
    engineered_df['CareerStage'] = pd.Categorical(engineered_df['CareerStage'], categories=career_labels, ordered=True)

    # 5. Promotion Stagnation Bands
    stagnation_bins = [-np.inf, 0.9, 2.1, 5.1, 10.1, np.inf]
    stagnation_labels = ['0 years', '1–2 years', '3–5 years', '6–10 years', '11+ years']
    engineered_df['PromotionStagnation'] = pd.cut(engineered_df['YearsSinceLastPromotion'], bins=stagnation_bins, labels=stagnation_labels)
    engineered_df['PromotionStagnation'] = pd.Categorical(engineered_df['PromotionStagnation'], categories=stagnation_labels, ordered=True)

    # 6. Distance Bands
    dist_bins = [-np.inf, 5, 10, 20, np.inf]
    dist_labels = ['0–5', '6–10', '11–20', '21+']
    engineered_df['DistanceBand'] = pd.cut(engineered_df['DistanceFromHome'], bins=dist_bins, labels=dist_labels)
    engineered_df['DistanceBand'] = pd.Categorical(engineered_df['DistanceBand'], categories=dist_labels, ordered=True)

    # 7. Income Bands (Quartiles, dataset-relative)
    # Using pd.qcut safely
    try:
        engineered_df['IncomeQuartile'] = pd.qcut(
            engineered_df['MonthlyIncome'], 
            q=4, 
            labels=['Lower quartile', 'Lower-middle quartile', 'Upper-middle quartile', 'Upper quartile'],
            duplicates='drop'
        )
    except Exception:
        # Fallback if quantiles can't be computed (e.g. all values same in small groups)
        engineered_df['IncomeQuartile'] = 'Lower quartile'
    
    # Ensure categorical order
    engineered_df['IncomeQuartile'] = pd.Categorical(
        engineered_df['IncomeQuartile'], 
        categories=['Lower quartile', 'Lower-middle quartile', 'Upper-middle quartile', 'Upper quartile'], 
        ordered=True
    )

    # 8. Satisfaction Labels (for 1-4 standard scales)
    standard_map = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very High'}
    wlb_map = {1: 'Poor', 2: 'Fair', 3: 'Good', 4: 'Excellent'}

    engineered_df['EnvironmentSatisfactionLabel'] = engineered_df['EnvironmentSatisfaction'].map(standard_map).fillna('Unknown')
    engineered_df['JobInvolvementLabel'] = engineered_df['JobInvolvement'].map(standard_map).fillna('Unknown')
    engineered_df['JobSatisfactionLabel'] = engineered_df['JobSatisfaction'].map(standard_map).fillna('Unknown')
    engineered_df['RelationshipSatisfactionLabel'] = engineered_df['RelationshipSatisfaction'].map(standard_map).fillna('Unknown')
    engineered_df['WorkLifeBalanceLabel'] = engineered_df['WorkLifeBalance'].map(wlb_map).fillna('Unknown')
    
    # Establish categorical orders
    sat_categories = ['Low', 'Medium', 'High', 'Very High']
    wlb_categories = ['Poor', 'Fair', 'Good', 'Excellent']
    
    engineered_df['EnvironmentSatisfactionLabel'] = pd.Categorical(engineered_df['EnvironmentSatisfactionLabel'], categories=sat_categories, ordered=True)
    engineered_df['JobInvolvementLabel'] = pd.Categorical(engineered_df['JobInvolvementLabel'], categories=sat_categories, ordered=True)
    engineered_df['JobSatisfactionLabel'] = pd.Categorical(engineered_df['JobSatisfactionLabel'], categories=sat_categories, ordered=True)
    engineered_df['RelationshipSatisfactionLabel'] = pd.Categorical(engineered_df['RelationshipSatisfactionLabel'], categories=sat_categories, ordered=True)
    engineered_df['WorkLifeBalanceLabel'] = pd.Categorical(engineered_df['WorkLifeBalanceLabel'], categories=wlb_categories, ordered=True)

    # 9. Workload Groups
    engineered_df['OvertimeGroup'] = engineered_df['OverTime'].map({'Yes': 'Overtime', 'No': 'No Overtime'}).fillna('Unknown')
    
    # Travel group labels (already normalized in cleaning but we make it clear)
    engineered_df['TravelGroup'] = engineered_df['BusinessTravel'].fillna('Unknown')

    # 10. Early-Tenure Indicator
    # selected_threshold comes from user sidebar
    engineered_df['IsEarlyTenure'] = engineered_df['YearsAtCompany'] <= early_tenure_threshold
    engineered_df['EarlyTenureLabel'] = engineered_df['IsEarlyTenure'].map({True: 'Early Tenure', False: 'Tenured'})

    # Education Label derived from Education
    edu_map = {1: '1 = Below College', 2: '2 = College', 3: '3 = Bachelor', 4: '4 = Master', 5: '5 = Doctor'}
    engineered_df['EducationLabel'] = engineered_df['Education'].map(edu_map).fillna('Unknown')
    engineered_df['EducationLabel'] = pd.Categorical(
        engineered_df['EducationLabel'], 
        categories=['1 = Below College', '2 = College', '3 = Bachelor', '4 = Master', '5 = Doctor'], 
        ordered=True
    )

    return engineered_df
