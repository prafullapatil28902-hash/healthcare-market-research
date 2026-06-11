# PDF Report Template

The PDF reports are generated programmatically with **ReportLab** in
[`app/exporters.py`](../app/exporters.py). This document describes the template
structure so it can be customised (branding, sections, ordering).

## Full Market Research Report — `build_pdf_report()`

| Page(s) | Content |
|---------|---------|
| 1 — Cover | Title, sub-title ("Competitor Analysis & Market Intelligence"), generation date |
| 2 — Executive Summary | Market overview, competitive landscape, key findings, opportunities, recommendations |
| 3 — Market Snapshot | KPI table (companies, products, areas, regions, revenue, growth) + Top Competitors + Therapeutic Area Landscape |
| 4 — Opportunities & Insights | Market-opportunity table + analyst insight bullets |
| 5 — Appendix | Data-validation report (quality score + issue table) |

Every page carries a footer: `Healthcare Market Research Report — Confidential`
on the left and `Page N` on the right.

## Styling tokens (edit in `_styles()` / module constants)

| Token | Default | Used for |
|-------|---------|----------|
| `_BRAND` | `#1f4e79` | Headings, table headers, title |
| `ReportTitle` | 22 pt | Cover and section titles |
| `SectionHeading` | 14 pt, brand colour | Section headers |
| `Body` | 10 pt, 15 leading | Paragraph text |
| Table header | brand fill, white bold | All data tables |
| Table rows | alternating white / `#eef3f8` | Zebra striping |

## Other PDF builders

- `build_executive_summary_pdf()` — standalone executive summary only.
- `build_competitor_pdf()` — company profiles, market share, therapeutic-area
  coverage.

## Customisation tips

- **Logo / letterhead:** add an `Image` flowable at the top of the cover in
  `build_pdf_report()`.
- **Brand colour:** change `_BRAND` (and `PRIMARY_COLOR` in `config.py` to keep
  charts consistent).
- **Section order:** the report body is a simple list of flowables — reorder or
  remove blocks as needed.
