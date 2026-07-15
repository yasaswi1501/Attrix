import unittest
import pandas as pd
from utils.feature_engineering import apply_feature_engineering

class TestFeatureEngineering(unittest.TestCase):
    def setUp(self):
        # Create a mock clean dataframe for binning checks
        self.df = pd.DataFrame({
            "Attrition": [1, 0, 1, 0, 0],
            "Age": [20, 26, 36, 46, 56],
            "YearsAtCompany": [0, 1, 4, 8, 17],
            "TotalWorkingYears": [2, 7, 15, 25, 35],
            "YearsSinceLastPromotion": [0, 1, 4, 8, 12],
            "DistanceFromHome": [3, 8, 15, 25, 4],
            "MonthlyIncome": [2000, 4000, 6000, 8000, 10000],
            "Education": [1, 2, 3, 4, 5],
            "OverTime": ["Yes", "No", "Yes", "No", "No"],
            "BusinessTravel": ["Non-Travel", "Travel Rarely", "Travel Frequently", "Non-Travel", "Non-Travel"],
            "EnvironmentSatisfaction": [1, 2, 3, 4, 2],
            "JobInvolvement": [1, 2, 3, 4, 1],
            "JobSatisfaction": [4, 3, 2, 1, 3],
            "RelationshipSatisfaction": [2, 3, 4, 1, 2],
            "WorkLifeBalance": [1, 2, 3, 4, 3]
        })

    def test_age_grouping(self):
        eng = apply_feature_engineering(self.df, early_tenure_threshold=2)
        
        # Age mapping: 20 -> '18–24', 26 -> '25–34', 36 -> '35–44', 46 -> '45–54', 56 -> '55+'
        self.assertEqual(eng.iloc[0]["AgeGroup"], "18–24")
        self.assertEqual(eng.iloc[1]["AgeGroup"], "25–34")
        self.assertEqual(eng.iloc[2]["AgeGroup"], "35–44")
        self.assertEqual(eng.iloc[3]["AgeGroup"], "45–54")
        self.assertEqual(eng.iloc[4]["AgeGroup"], "55+")

    def test_tenure_bands(self):
        eng = apply_feature_engineering(self.df, early_tenure_threshold=2)
        
        # Tenure mapping: 0 -> 'Less than 1 year', 1 -> '1–2 years', 4 -> '3–5 years', 8 -> '6–10 years', 17 -> '16+ years'
        self.assertEqual(eng.iloc[0]["TenureBand"], "Less than 1 year")
        self.assertEqual(eng.iloc[1]["TenureBand"], "1–2 years")
        self.assertEqual(eng.iloc[2]["TenureBand"], "3–5 years")
        self.assertEqual(eng.iloc[3]["TenureBand"], "6–10 years")
        self.assertEqual(eng.iloc[4]["TenureBand"], "16+ years")

    def test_career_stages(self):
        eng = apply_feature_engineering(self.df, early_tenure_threshold=2)
        
        # Career mapping: 2 -> 'Early Career', 7 -> 'Developing', 15 -> 'Mid-Career', 25 -> 'Experienced', 35 -> 'Senior'
        self.assertEqual(eng.iloc[0]["CareerStage"], "Early Career: 0–5 years")
        self.assertEqual(eng.iloc[1]["CareerStage"], "Developing Career: 6–10 years")
        self.assertEqual(eng.iloc[2]["CareerStage"], "Mid-Career: 11–20 years")
        self.assertEqual(eng.iloc[3]["CareerStage"], "Experienced: 21–30 years")
        self.assertEqual(eng.iloc[4]["CareerStage"], "Senior Career: 31+ years")

    def test_early_tenure_threshold(self):
        # Test default threshold = 2
        eng2 = apply_feature_engineering(self.df, early_tenure_threshold=2)
        self.assertTrue(eng2.iloc[0]["IsEarlyTenure"]) # 0 yrs
        self.assertTrue(eng2.iloc[1]["IsEarlyTenure"]) # 1 yr
        self.assertFalse(eng2.iloc[2]["IsEarlyTenure"]) # 4 yrs

        # Test threshold = 4
        eng4 = apply_feature_engineering(self.df, early_tenure_threshold=4)
        self.assertTrue(eng4.iloc[0]["IsEarlyTenure"])
        self.assertTrue(eng4.iloc[1]["IsEarlyTenure"])
        self.assertTrue(eng4.iloc[2]["IsEarlyTenure"]) # 4 yrs (now True)
        self.assertFalse(eng4.iloc[3]["IsEarlyTenure"]) # 8 yrs

    def test_satisfaction_mapping(self):
        eng = apply_feature_engineering(self.df, early_tenure_threshold=2)
        
        # EnvironmentSatisfaction [1, 2, 3, 4, 2] -> ['Low', 'Medium', 'High', 'Very High', 'Medium']
        self.assertEqual(eng.iloc[0]["EnvironmentSatisfactionLabel"], "Low")
        self.assertEqual(eng.iloc[3]["EnvironmentSatisfactionLabel"], "Very High")
        
        # WorkLifeBalance [1, 2, 3, 4, 3] -> ['Poor', 'Fair', 'Good', 'Excellent', 'Good']
        self.assertEqual(eng.iloc[0]["WorkLifeBalanceLabel"], "Poor")
        self.assertEqual(eng.iloc[3]["WorkLifeBalanceLabel"], "Excellent")

if __name__ == "__main__":
    unittest.main()
