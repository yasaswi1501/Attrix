# Workforce Dataset Dictionary - Palo Alto Networks

This dataset contains **1,470 employee records** and **31 columns** mapping demographics, employment status, workload metrics, and organizational satisfaction ratings.

---

## 1. Target and Identity Fields

### Attrition
* **Description:** Indicates whether an employee has left the organization.
* **Type:** Integer / Binary Label
* **Normalized Values:**
  * `0` = Retained (Continuous Employment)
  * `1` = Exited (Voluntary departure)

---

## 2. Demographic Variables

### Age
* **Description:** Employee age in years.
* **Type:** Integer (Range: 18–60 in current dataset)

### Gender
* **Description:** Employee gender.
* **Type:** Categorical
* **Expected Values:** `Male`, `Female`

### MaritalStatus
* **Description:** Marital status.
* **Type:** Categorical
* **Expected Values:** `Single`, `Married`, `Divorced`

### Education
* **Description:** Highest formal education level completed.
* **Type:** Integer (Ordinal scale 1–5)
* **Categories:**
  * `1` = Below College
  * `2` = College
  * `3` = Bachelor
  * `4` = Master
  * `5` = Doctor

### EducationField
* **Description:** Primary field of education study.
* **Type:** Categorical
* **Common Values:** `Life Sciences`, `Medical`, `Marketing`, `Technical Degree`, `Human Resources`, `Other`

---

## 3. Employment and Career Progression Variables

### Department
* **Description:** Employee's business department.
* **Type:** Categorical
* **Expected Values:** `Research & Development`, `Sales`, `Human Resources`

### JobRole
* **Description:** Specific designation or title.
* **Type:** Categorical
* **Common Values:** `Sales Executive`, `Research Scientist`, `Laboratory Technician`, `Manufacturing Director`, `Healthcare Representative`, `Manager`, `Sales Representative`, `Research Director`, `Human Resources`

### JobLevel
* **Description:** Seniority tier.
* **Type:** Integer (1 to 5)
  * `1` = Entry-level or junior role
  * `5` = Highly senior role

### YearsAtCompany
* **Description:** Number of years employed at Palo Alto Networks.
* **Type:** Integer

### YearsInCurrentRole
* **Description:** Number of years in current job design/role.
* **Type:** Integer

### YearsSinceLastPromotion
* **Description:** Number of years since employee's last formal promotion.
* **Type:** Integer

### YearsWithCurrManager
* **Description:** Number of years reporting to the current supervisor/manager.
* **Type:** Integer

### TotalWorkingYears
* **Description:** Cumulative years of professional work experience across all organizations.
* **Type:** Integer

### NumCompaniesWorked
* **Description:** Number of prior companies worked for before joining.
* **Type:** Integer

---

## 4. Workload, Mobility, and Commute

### OverTime
* **Description:** Indicates whether the employee regularly works overtime hours.
* **Type:** Categorical / Binary
* **Expected Values:** `Yes`, `No`

### BusinessTravel
* **Description:** Frequency of business travel required.
* **Type:** Categorical
* **Expected Values:** `Non-Travel`, `Travel Rarely`, `Travel Frequently`

### DistanceFromHome
* **Description:** Distance between the employee’s home address and primary workplace.
* **Type:** Numeric (Unit not explicitly specified; labeled generic "Distance from Home" in axis views)

---

## 5. Compensation and Financial Metrics

### MonthlyIncome
* **Description:** Monthly gross salary in USD.
* **Type:** Numeric

### DailyRate / HourlyRate / MonthlyRate
* **Description:** Hourly, daily, and monthly administrative pay rates used for budgeting.
* **Type:** Numeric

### PercentSalaryHike
* **Description:** Percentage salary increase during most recent performance cycle.
* **Type:** Numeric

### StockOptionLevel
* **Description:** Level of stock options granted (equity tier).
* **Type:** Integer (typically 0 to 3)

---

## 6. Employee Satisfaction, Engagement, and Performance

### EnvironmentSatisfaction
* **Description:** Employee satisfaction with their physical work environment.
* **Type:** Ordinal (Scale 1–4)
* **Labels:** `1` = Low, `2` = Medium, `3` = High, `4` = Very High

### JobSatisfaction
* **Description:** Employee satisfaction with their job duties.
* **Type:** Ordinal (Scale 1–4)
* **Labels:** `1` = Low, `2` = Medium, `3` = High, `4` = Very High

### RelationshipSatisfaction
* **Description:** Satisfaction with interpersonal work relationships.
* **Type:** Ordinal (Scale 1–4)
* **Labels:** `1` = Low, `2` = Medium, `3` = High, `4` = Very High

### JobInvolvement
* **Description:** Level of focus, engagement, and alignment with roles.
* **Type:** Ordinal (Scale 1–4)
* **Labels:** `1` = Low, `2` = Medium, `3` = High, `4` = Very High

### WorkLifeBalance
* **Description:** Satisfaction with personal-professional time split.
* **Type:** Ordinal (Scale 1–4)
* **Labels:** `1` = Poor, `2` = Fair, `3` = Good, `4` = Excellent

### PerformanceRating
* **Description:** Most recent manager performance rating score.
* **Type:** Ordinal / Numeric

### TrainingTimesLastYear
* **Description:** Count of professional training sessions attended in the prior year.
* **Type:** Integer
