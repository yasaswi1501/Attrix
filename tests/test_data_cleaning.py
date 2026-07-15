import unittest
import pandas as pd
import numpy as np
from utils.data_cleaning import clean_and_validate_data, EXPECTED_COLUMNS

class TestDataCleaning(unittest.TestCase):
    def setUp(self):
        # Create a mock raw dataframe matching the 31 columns
        data = {col: [np.nan] * 3 for col in EXPECTED_COLUMNS}
        
        # Populate specific test columns
        data["Age"] = [25, 17, 85]  # 17 & 85 are out-of-range age warnings
        data["Attrition"] = ["Yes", "no", "invalid_label"]  # Tests parsing of Attrition label
        data["BusinessTravel"] = ["Travel_Rarely", "Non-Travel", "Travel_Frequently"]
        data["MonthlyIncome"] = [5000, -100, 15000]  # -100 is negative income violation
        data["YearsAtCompany"] = [2, 5, 10]
        data["TotalWorkingYears"] = [1, 6, 20]  # Row 0: YearsAtCompany (2) > TotalWorkingYears (1) -> logical error
        data["YearsInCurrentRole"] = [1, 2, 3]
        data["YearsSinceLastPromotion"] = [0, 1, 2]
        data["YearsWithCurrManager"] = [1, 2, 3]
        
        # Rest of mandatory columns must be non-null to prevent coercion issues
        for col in EXPECTED_COLUMNS:
            if data[col][0] is np.nan or pd.isna(data[col][0]):
                data[col] = [3] * 3
                
        self.raw_df = pd.DataFrame(data)

    def test_attrition_parsing_and_drop(self):
        # Row 2 has "invalid_label" and should be dropped
        # Row 0 and 1 should remain (parsed to 1 and 0)
        clean_df, summary = clean_and_validate_data(self.raw_df)
        
        self.assertEqual(summary["raw_record_count"], 3)
        # Expected clean count should be 2 because 1 invalid attrition is dropped
        self.assertEqual(len(clean_df), 2)
        self.assertListEqual(list(clean_df["Attrition"].values), [1.0, 0.0])

    def test_negative_value_coercion(self):
        clean_df, summary = clean_and_validate_data(self.raw_df)
        
        # Row 1 has -100 in MonthlyIncome, should be coerced to NaN
        # Row 0 has 5000, should be preserved
        self.assertTrue(pd.isna(clean_df.iloc[1]["MonthlyIncome"]))
        self.assertEqual(clean_df.iloc[0]["MonthlyIncome"], 5000.0)

    def test_duplicate_removal(self):
        # Add duplicate row to raw df
        dup_df = pd.concat([self.raw_df, self.raw_df.iloc[[0]]], ignore_index=True)
        clean_df, summary = clean_and_validate_data(dup_df)
        
        self.assertEqual(summary["duplicate_count"], 1)
        self.assertEqual(len(clean_df), 2)  # 4 rows, 1 duplicate removed -> 3, then 1 invalid attrition dropped -> 2

if __name__ == "__main__":
    unittest.main()
