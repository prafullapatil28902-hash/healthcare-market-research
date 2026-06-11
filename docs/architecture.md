# Architecture

The Healthcare Market Research Report Generator is a modular Streamlit
application. Each capability lives in its own module so it can be tested and
reused independently of the UI.

## High-level flow

```
                ┌──────────────────────────────────────────────┐
                │              Streamlit UI (app/main.py)       │
                │   Sidebar: data source + search & filter      │
                │   Tabs: Overview · Validation · Competitors · │
                │         Landscape · Trends · Insights ·       │
                │         Summary · Dashboard · Export          │
                └───────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼─────────────────────────────────┐
        │                       │                                 │
        ▼                       ▼                                 ▼
┌───────────────┐      ┌──────────────────┐             ┌──────────────────┐
│  data_loader  │      │   validation     │             │   exporters      │
│  (parse/type) │      │ (quality report) │             │ Excel / PDF /    │
└───────┬───────┘      └──────────────────┘             │ summary / comp.  │
        │                                                └────────┬─────────┘
        ▼                                                         │
┌───────────────┐                                                 │
│   database    │  SQLite (database/market_research.db)           │
│  (persist)    │◄────────────── working dataset ─────────────────┘
└───────┬───────┘
        │
        ▼  cleaned analytics frame
┌──────────────────────────────────────────────────────────────────────┐
│  Analytics layer                                                       │
│   competitor_analysis · market_landscape · trend_analysis             │
│   insights · executive_summary                                        │
└───────────────┬──────────────────────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ visualizations│  Plotly figures (dashboard + exports)
        └───────────────┘
```

## Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `config.py` | Paths, schema, validation ranges, palette |
| `sample_data.py` | Deterministic realistic sample-data generator |
| `data_loader.py` | CSV parsing, column normalisation, type coercion |
| `database.py` | SQLite persistence of the working dataset |
| `validation.py` | Missing / duplicate / invalid / inconsistency checks → report |
| `competitor_analysis.py` | Company profiles, portfolios, coverage, market share |
| `market_landscape.py` | Totals, area/region distribution, growth grids |
| `trend_analysis.py` | Fastest-growing areas, active companies, emerging products, opportunities |
| `insights.py` | Rules-based analyst-style narrative insights |
| `executive_summary.py` | Structured executive summary assembly |
| `visualizations.py` | Plotly chart builders |
| `exporters.py` | Excel (OpenPyXL) + PDF (ReportLab) report generation |
| `main.py` | Streamlit orchestration and UI |

## Design choices

- **Single denormalised table.** The workload is analytical and read-mostly, so
  one wide table (one row per company × product × region) keeps the analytics
  simple and fast. No joins are required.
- **Rules-based insights.** The insight and summary engines are fully
  deterministic and run offline — no external LLM dependency — which keeps the
  tool reproducible and suitable for confidential market data.
- **Pure functions, UI-free analytics.** Every analytics module takes a
  DataFrame and returns a DataFrame / dataclass, so the same code powers the
  dashboard and the exported reports.
- **In-memory exports.** Reports are built in `BytesIO` and streamed to the
  browser via Streamlit download buttons; nothing needs to be written to disk.
