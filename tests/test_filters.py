import unittest
import pandas as pd
from utils.filtering import filter_dataframe

class TestFilters(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "Age": [20, 30, 40],
            "Department": ["Sales", "R&D", "Sales"],
            "Gender": ["Male", "Female", "Male"],
            "YearsAtCompany": [1, 5, 10],
            "MaritalStatus": ["Single", "Married", "Divorced"],
            "Education": [3, 4, 2],
            "EducationField": ["Life Sciences", "Medical", "Technical Degree"],
            "OverTime": ["Yes", "No", "Yes"],
            "BusinessTravel": ["Travel Rarely", "Non-Travel", "Travel Frequently"],
            "JobLevel": [1, 2, 3]
        })

    def test_single_filter(self):
        filters = {"Department": ["Sales"]}
        filtered = filter_dataframe(self.df, filters)
        self.assertEqual(len(filtered), 2)
        self.assertListEqual(list(filtered["Age"].values), [20, 40])

    def test_intersection_filters(self):
        # Department = Sales AND Gender = Male -> 2 rows
        # Department = Sales AND OverTime = Yes -> 2 rows
        # Department = Sales AND JobLevel = 1 -> 1 row (Age 20)
        filters = {
            "Department": ["Sales"],
            "JobLevel": [1]
        }
        filtered = filter_dataframe(self.df, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["Age"], 20)

    def test_numeric_ranges(self):
        # Age range: 25 to 35 -> row 1 (Age 30)
        filters = {
            "Age": (25, 35)
        }
        filtered = filter_dataframe(self.df, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["Age"], 30)

        # Tenure range: 2 to 12 -> row 1 and 2 (5, 10)
        filters = {
            "YearsAtCompany": (2, 12)
        }
        filtered = filter_dataframe(self.df, filters)
        self.assertEqual(len(filtered), 2)
        self.assertListEqual(list(filtered["YearsAtCompany"].values), [5, 10])

    def test_empty_filters(self):
        # Empty filters dict -> returns full copy
        filtered = filter_dataframe(self.df, {})
        self.assertEqual(len(filtered), 3)

if __name__ == "__main__":
    unittest.main()
