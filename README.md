# Healthcare Market Research Report Generator

A healthcare market intelligence platform that transforms healthcare market datasets into competitor analysis reports, market landscape assessments, trend analysis, executive summaries, and actionable business insights.

## Features

| Feature | Description |
|---|---|
| **Competitor Analysis** | Rank and tier pharmaceutical companies by revenue, market share, and pipeline |
| **Market Landscape Assessment** | Segment-wise TAM, CAGR, and market share breakdown |
| **Trend Analysis** | Global market growth, AI investment, biosimilars, digital health trends |
| **Data Validation & QA** | Automated data quality checks with completeness scoring |
| **Executive Summary Generation** | Auto-generated market intelligence executive summaries |
| **Excel & CSV Reporting** | Multi-sheet colour-coded Excel exports with QA dashboard |

## Installation

```bash
pip install openpyxl pandas plotly streamlit
```

## Usage

```bash
# Full report (all sections)
python healthcare_market_research.py --report all

# Competitor analysis only
python healthcare_market_research.py --report competitor

# Filter by therapeutic segment
python healthcare_market_research.py --report competitor --segment Oncology

# Export to Excel
python healthcare_market_research.py --report all --export report.xlsx

# Export to CSV
python healthcare_market_research.py --report competitor --export competitors.csv
```

## Sample Output

```
Healthcare Market Research Report Generator
Data Quality: 100% | Records: 14

COMPETITOR ANALYSIS
#   Company         Segment         Revenue($B)  Share%  Pipeline  Tier
1   Johnson & J     Immunology      85.2         11.9    113       Tier 1 (Leader)
2   Merck           Oncology        60.1         8.4     92        Tier 1 (Leader)
3   Pfizer          Oncology        58.5         8.2     89        Tier 1 (Leader)
...

MARKET LANDSCAPE | TAM: USD 1252B | Fastest Growing: Biosimilars
  Generics           $422B  CAGR:4.1%   Share:33.7%
  Oncology           $248B  CAGR:12.1%  Share:19.8%
  Immunology         $156B  CAGR:9.4%   Share:12.5%
```

## Technologies

- **Python** — Core logic and data processing
- **SQLite** — Market data storage and querying
- **Pandas** — Data analysis and manipulation
- **Plotly** — Interactive data visualizations
- **Streamlit** — Web dashboard interface
- **OpenPyXL** — Excel report generation

## Author

**Prafulla Patil** — B.Pharm | Healthcare Data Analyst | ICH-GCP Certified  
GitHub: [prafullapatil28902-hash](https://github.com/prafullapatil28902-hash)  
LinkedIn: [linkedin.com/in/prafulla-patil-pharmacy](https://linkedin.com/in/prafulla-patil-pharmacy)
