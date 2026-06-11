# 🏥 Healthcare Market Research Report Generator

A production-ready tool that helps **healthcare market research analysts** turn
raw healthcare market data (companies, drugs/products, therapeutic areas,
revenue, and regional data) into **competitor analysis, market-intelligence
reports, trend analysis, automated insights, and executive summaries** — all
through a clean Streamlit interface with one-click Excel and PDF exports.

Built with **Python · Streamlit · SQLite · Pandas · Plotly · OpenPyXL ·
ReportLab**.

---

## 📌 Problem Statement

Healthcare and pharmaceutical market research analysts spend a large share of
their time on **secondary research plumbing**: cleaning messy market datasets,
reconciling competitor portfolios, computing market shares, spotting growth
trends, and then hand-assembling slide-ready summaries and reports. This is
slow, error-prone, and hard to keep consistent across therapeutic areas.

This tool automates that workflow end-to-end. An analyst uploads a CSV of
healthcare market data and immediately receives validated data, competitor
intelligence, market-landscape analytics, trend signals, analyst-style insights,
and a polished executive summary — exportable to Excel and PDF for clients and
stakeholders.

---

## 🔁 Market Research Workflow Mapping

The application mirrors the real secondary-market-research workflow:

| Analyst workflow stage | Tool capability |
|------------------------|-----------------|
| 1. Gather secondary data | **Data Upload** — CSV ingestion (companies, products, therapeutic areas, revenue, regions) |
| 2. Clean & QA the data | **Data Validation** — missing values, duplicates, invalid entries, inconsistencies, quality score |
| 3. Profile the competition | **Competitor Analysis** — company profiles, portfolios, coverage, market share, top competitors |
| 4. Size & structure the market | **Market Landscape** — totals, therapeutic-area & regional distribution, growth |
| 5. Spot the dynamics | **Trend Analysis** — fastest-growing areas, most active companies, emerging products, white space |
| 6. Interpret the data | **Insight Generator** — leading competitors, gaps, opportunities, risks, strategic observations |
| 7. Communicate findings | **Executive Summary** + **PDF / Excel exports** for stakeholders |
| 8. Slice & investigate | **Search & Filter** by company, therapeutic area, product, region |

---

## ✨ Features

1. **Data Upload** — upload healthcare market CSVs, or load a bundled realistic
   sample (Diabetes, Oncology, Cardiovascular).
2. **Data Validation** — missing-value, duplicate, invalid-number, range, and
   cross-field consistency checks with a 0–100 quality score and a validation
   report.
3. **Competitor Analysis** — company profiles, product portfolios,
   therapeutic-area coverage matrix, market-share comparison, top competitors.
4. **Market Landscape** — total companies/products, therapeutic-area
   distribution, regional distribution, growth trends and heatmap.
5. **Trend Analysis** — fastest-growing therapeutic areas (revenue-weighted),
   most active companies, emerging (recently-approved) products, quantified
   market opportunities.
6. **Insight Generator** — automatic analyst-style narrative: leading
   competitors, market gaps, growth opportunities, risk areas (incl. patent
   cliffs), strategic observations.
7. **Executive Summary Generator** — market overview, competitive landscape,
   key findings, opportunities, and recommendations.
8. **Dashboard** — market KPIs, competitor rankings, product distribution, trend
   charts, and growth indicators.
9. **Export Options** — Excel workbook, full PDF report, executive summary
   (PDF + TXT), and a focused competitor-analysis PDF.
10. **Search & Filter** — filter the entire app by company, therapeutic area,
    product, and region.

---

## 🏗️ Architecture Diagram

```
        ┌────────────────────────────────────────────────────────┐
        │                 Streamlit UI  (app/main.py)             │
        │   Sidebar: data source + search/filter                  │
        │   Tabs: Overview · Validation · Competitors ·           │
        │         Landscape · Trends · Insights · Summary ·       │
        │         Dashboard · Export                              │
        └───────────────┬────────────────────────────────────────┘
                        │
   ┌────────────────────┼───────────────────────────────────────┐
   ▼                    ▼                                       ▼
data_loader        validation                              exporters
(parse/type)     (quality report)                    Excel · PDF · Summary
   │                                                          ▲
   ▼                                                          │
database  ── SQLite (working dataset) ─────────────────────────┘
   │
   ▼  cleaned analytics frame
┌───────────────────────────────────────────────────────────────┐
│ Analytics:  competitor_analysis · market_landscape ·          │
│             trend_analysis · insights · executive_summary     │
└───────────────┬───────────────────────────────────────────────┘
                ▼
          visualizations  (Plotly figures → dashboard + reports)
```

A more detailed breakdown is in [`docs/architecture.md`](docs/architecture.md).

---

## 📁 Project Structure

```
healthcare-market-research/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Streamlit entry point (UI + orchestration)
│   ├── config.py               # Paths, schema, validation ranges, palette
│   ├── sample_data.py          # Realistic sample-data generator
│   ├── data_loader.py          # CSV parsing + type coercion
│   ├── database.py             # SQLite persistence
│   ├── validation.py           # Data-quality checks + report
│   ├── competitor_analysis.py  # Profiles, portfolios, market share
│   ├── market_landscape.py     # Totals, distributions, growth
│   ├── trend_analysis.py       # Trends + market opportunities
│   ├── insights.py             # Rules-based analyst insights
│   ├── executive_summary.py    # Executive-summary assembly
│   ├── visualizations.py       # Plotly charts
│   └── exporters.py            # Excel + PDF exporters
├── data/
│   └── sample_healthcare_market_dataset.csv
├── database/                   # SQLite db (generated at runtime)
├── exports/                    # Generated exports (runtime)
├── reports/                    # Optional saved reports (runtime)
├── docs/
│   ├── architecture.md
│   └── pdf_report_template.md
├── screenshots/
├── requirements.txt
├── run.py                      # Convenience launcher
├── .gitignore
└── README.md
```

---

## ⚙️ Installation Guide

### Prerequisites
- Python **3.10 – 3.12**
- `pip`

### Steps

```bash
# 1. Clone
git clone <your-repo-url>
cd healthcare-market-research

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage Instructions

```bash
# Option A — convenience launcher
python run.py

# Option B — direct Streamlit command
streamlit run app/main.py
```

Then in the browser (default http://localhost:8501):

1. In the **sidebar**, click **Load sample** (or upload your own CSV).
2. Explore the tabs:
   - **Overview** — KPIs and a data preview.
   - **Validation** — data-quality score and report.
   - **Competitors** — rankings, profiles, portfolios, coverage.
   - **Landscape** — therapeutic-area and regional distribution + growth heatmap.
   - **Trends** — fastest-growing areas, active companies, emerging products,
     opportunities.
   - **Insights** — automatically generated analyst observations.
   - **Summary** — full executive summary.
   - **Dashboard** — consolidated KPI + chart view.
   - **Export** — download Excel / PDF / executive-summary / competitor reports.
3. Use the **Search & filter** controls in the sidebar to narrow the entire app
   by company, therapeutic area, product, or region. Exports respect filters.

### Expected CSV schema

| Column | Description |
|--------|-------------|
| `company` | Company name |
| `company_type` | e.g. Pharma / Biotech |
| `headquarters` | HQ country |
| `product` | Drug / product name |
| `therapeutic_area` | e.g. Diabetes, Oncology, Cardiovascular |
| `indication` | Specific indication |
| `phase` | e.g. Marketed, Phase III |
| `approval_year` | Year of approval |
| `patent_expiry_year` | Patent expiry year |
| `region` | Geographic region |
| `revenue_usd_m` | Product revenue in that region (USD millions) |
| `market_size_usd_m` | Addressable market size (USD millions) |
| `growth_rate_pct` | YoY market growth (%) |

A ready-to-use file is provided at
[`data/sample_healthcare_market_dataset.csv`](data/sample_healthcare_market_dataset.csv).

---

## 🧪 Sample Dataset

The bundled dataset covers three therapeutic areas with real-world-inspired
products across North America, Europe, and Asia-Pacific:

- **Diabetes** — Ozempic, Mounjaro, Trulicity, Jardiance, Farxiga, Lantus, …
- **Oncology** — Keytruda, Opdivo, Tagrisso, Ibrance, Herceptin, Revlimid, …
- **Cardiovascular** — Eliquis, Xarelto, Entresto, Repatha, Praluent

You can also regenerate a comparable dataset:

```bash
python -m app.sample_data
```

---

## 📤 Exports

| Export | Format | Contents |
|--------|--------|----------|
| Excel report | `.xlsx` | Raw data + 7 analysis sheets (profiles, share, areas, regional, growth, opportunities, insights) |
| Full PDF report | `.pdf` | Cover, executive summary, KPIs, competitors, areas, opportunities, insights, validation appendix |
| Executive summary | `.pdf` / `.txt` | Overview, landscape, findings, opportunities, recommendations |
| Competitor analysis | `.pdf` | Profiles, market share, therapeutic-area coverage |

The PDF template is documented in
[`docs/pdf_report_template.md`](docs/pdf_report_template.md).

---

## 🧯 Error Handling

- Friendly, specific errors for unreadable files, empty files, and missing
  required columns.
- Numeric coercion is non-destructive — invalid values are flagged by the
  validator rather than crashing analytics.
- Empty / over-filtered states are handled gracefully with guidance messages.
- Charts and exports degrade safely when a section has no data.

---

## 🧾 Resume Project Description

> **Healthcare Market Research Report Generator** — Built a production-ready
> Python/Streamlit application that converts raw healthcare market data into
> competitor analysis, market-intelligence reports, trend analysis, and
> executive summaries for pharmaceutical market research. Implemented a modular
> analytics engine (Pandas) covering data validation, market-share and
> therapeutic-area analysis, growth-trend detection, and quantified white-space
> opportunity sizing, plus a rules-based insight and executive-summary generator.
> Delivered an interactive Plotly dashboard with search/filter and one-click
> Excel (OpenPyXL) and PDF (ReportLab) report exports, backed by SQLite
> persistence. Demonstrates secondary research, competitive intelligence, data
> validation, business-insight generation, and executive reporting skills for
> healthcare/pharma market research analyst roles.

**Skills demonstrated:** Healthcare market research · Secondary research ·
Competitor analysis · Market intelligence · Data validation & QA · Business
insight generation · Report writing · Executive reporting · Python · Pandas ·
Data visualisation.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Data | Pandas |
| Storage | SQLite (stdlib `sqlite3`) |
| Charts | Plotly |
| Excel export | OpenPyXL |
| PDF export | ReportLab |

---

## 📄 License

Released under the MIT License — see `LICENSE` (add one if publishing publicly).
