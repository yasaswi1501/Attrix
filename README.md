# Attrix

Enterprise Workforce Intelligence & Attrition Risk Analytics Platform

An interactive diagnostic people analytics platform designed to analyze voluntary employee departures, isolate high-risk hotspots, and provide actionable, evidence-linked retention guidelines. Official repository: [https://github.com/yasaswi1501/Attrix](https://github.com/yasaswi1501/Attrix)

---

## 1. Project Structure

```text
unified mentor project - 1/
│
├── app.py                     # Main dashboard router & entry point
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation
├── .gitignore                 # Cache & venv exclusions
│
├── .streamlit/
│   └── config.toml            # Apple-inspired light theme presets
│
├── data/
│   └── raw/
│       └── Palo Alto Networks.csv # Workforce dataset
│
├── components/
│   ├── __init__.py
│   ├── header.py              # Header layouts and active filters chips
│   ├── kpi_cards.py           # Custom styled KPI metric cards
│   ├── empty_states.py        # Empty filter results handler
│   └── footer.py              # Disclaimers and small sample size cautions
│
├── pages/
│   ├── __init__.py
│   ├── overview.py            # Executive Overview & Highlights
│   ├── department_roles.py    # Segmented comparisons & Heatmap
│   ├── demographics.py        # Age distributions, gender & education
│   ├── tenure_career.py       # Career stages, promotions & manager continuity
│   ├── workload_mobility.py   # Overtime, Business Travel index, & commute
│   ├── risk_hotspots.py       # Priority hotspot ledgers & Scatter Quadrant
│   ├── recommendations.py     # Dynamic evidence-linked interventions
│   └── methodology.py         # Technical formulations & Custom file uploader
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # Caching and file buffer handlers
│   ├── data_cleaning.py       # Deduplication & Column/Numeric range quality pipeline
│   ├── feature_engineering.py  # Age/Tenure/Stagnation categorization and binning
│   ├── filtering.py           # Intersection filter engine
│   ├── metrics.py             # Math calculations (Rates, index combos)
│   ├── statistics.py          # Chi-square and Mann-Whitney U test calculations
│   ├── chart_theme.py         # Plotly Apple chart styles & colors
│   └── exports.py             # CSV/Markdown exports
│
├── reports/
│   ├── research_paper.md      # Full workforce research study
│   ├── executive_summary.md   # HR brief executive summary
│   └── data_dictionary.md     # Variables dictionary
│
└── tests/
    ├── __init__.py
    ├── test_data_cleaning.py
    ├── test_metrics.py
    ├── test_filters.py
    └── test_feature_engineering.py
```

---

## 2. Installation & Quickstart

To run this project, make sure Python 3.11+ is installed.

1. **Activate the Virtual Environment:**
   ```bash
   source .venv/bin/activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## 3. Running Unit Tests

Execute the following command inside the project directory:
```bash
pytest
```
Or, if running without pytest command mapping:
```bash
python3 -m unittest discover -s tests
```

---

## Product Specification

Attrix is governed by the Attrix Product Architecture & Engineering Specification (APAES). The complete specification suite is maintained inside the `docs/` directory.
