import unittest
import pandas as pd
from utils.metrics import calculate_core_metrics, calculate_group_attrition, calculate_workload_attrition_matrix

class TestMetrics(unittest.TestCase):
    def setUp(self):
        # Create a mock clean and engineered dataframe
        self.df = pd.DataFrame({
            "Attrition": [1, 0, 1, 0, 0],
            "YearsAtCompany": [1, 3, 2, 8, 12],
            "Department": ["Sales", "R&D", "Sales", "R&D", "HR"],
            "OverTime": ["Yes", "No", "Yes", "No", "Yes"],
            "BusinessTravel": ["Travel Rarely", "Non-Travel", "Travel Rarely", "Non-Travel", "Travel Frequently"]
        })

    def test_core_metrics(self):
        metrics = calculate_core_metrics(self.df, early_tenure_threshold=2)
        
        self.assertEqual(metrics["total_employees"], 5)
        self.assertEqual(metrics["exited_employees"], 2)
        self.assertEqual(metrics["retained_employees"], 3)
        self.assertEqual(metrics["overall_attrition_rate"], 40.0)
        self.assertEqual(metrics["retention_rate"], 60.0)
        
        # Early tenure (<= 2 years): tenure values [1, 2] -> 2 employees (rows 0 and 2)
        # Exited early tenure: 2 employees (both have Attrition=1)
        self.assertEqual(metrics["early_tenure_total"], 2)
        self.assertEqual(metrics["early_tenure_exits"], 2)
        self.assertEqual(metrics["early_tenure_attrition_rate"], 100.0)
        self.assertEqual(metrics["early_tenure_exit_contribution"], 100.0)

    def test_group_attrition(self):
        overall_rate = 40.0
        total_exits = 2
        
        dept_attrition = calculate_group_attrition(self.df, "Department", overall_rate, total_exits)
        
        # Sales has 2 employees, 2 exits -> 100% rate
        sales_row = dept_attrition[dept_attrition["Group"] == "Sales"].iloc[0]
        self.assertEqual(sales_row["Headcount"], 2)
        self.assertEqual(sales_row["Exited"], 2)
        self.assertEqual(sales_row["Attrition Rate"], 100.0)
        self.assertEqual(sales_row["Relative Index"], 2.5)  # 100 / 40 = 2.5
        self.assertEqual(sales_row["Exit Contribution"], 100.0)  # 2 / 2 * 100 = 100.0

        # R&D has 2 employees, 0 exits -> 0% rate
        rd_row = dept_attrition[dept_attrition["Group"] == "R&D"].iloc[0]
        self.assertEqual(rd_row["Headcount"], 2)
        self.assertEqual(rd_row["Exited"], 0)
        self.assertEqual(rd_row["Attrition Rate"], 0.0)
        self.assertEqual(rd_row["Relative Index"], 0.0)

    def test_workload_matrix(self):
        overall_rate = 40.0
        matrix = calculate_workload_attrition_matrix(self.df, overall_rate)
        
        # Check that combinations are returned
        self.assertFalse(matrix.empty)
        self.assertIn("Workload Combination", matrix.columns)
        self.assertIn("Workload Attrition Index", matrix.columns)

if __name__ == "__main__":
    unittest.main()
