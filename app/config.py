"""
Central configuration for the Healthcare Market Research Report Generator.

Keeping paths, schema definitions, and presentation constants in one place keeps
the rest of the codebase free of magic strings and makes the project easy to
relocate or repurpose for a different dataset.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Project paths
# --------------------------------------------------------------------------- #
# config.py lives in app/, so the project root is one directory up.
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent

DATA_DIR = ROOT_DIR / "data"
DATABASE_DIR = ROOT_DIR / "database"
EXPORTS_DIR = ROOT_DIR / "exports"
REPORTS_DIR = ROOT_DIR / "reports"
DOCS_DIR = ROOT_DIR / "docs"

DATABASE_PATH = DATABASE_DIR / "market_research.db"
SAMPLE_DATASET_PATH = DATA_DIR / "sample_healthcare_market_dataset.csv"

# Make sure the writable directories exist at import time so the app never
# crashes on a fresh checkout.
for _directory in (DATA_DIR, DATABASE_DIR, EXPORTS_DIR, REPORTS_DIR):
    _directory.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Dataset schema
# --------------------------------------------------------------------------- #
# The canonical (denormalised) market-data schema. Each row represents the
# revenue of one product, sold by one company, in one therapeutic area, in one
# geographic region.
REQUIRED_COLUMNS = [
    "company",
    "company_type",
    "headquarters",
    "product",
    "therapeutic_area",
    "indication",
    "phase",
    "approval_year",
    "patent_expiry_year",
    "region",
    "revenue_usd_m",
    "market_size_usd_m",
    "growth_rate_pct",
]

# Columns that must be numeric for the analytics to work.
NUMERIC_COLUMNS = [
    "approval_year",
    "patent_expiry_year",
    "revenue_usd_m",
    "market_size_usd_m",
    "growth_rate_pct",
]

# Columns that must never be empty for a row to be considered usable.
NON_NULL_COLUMNS = [
    "company",
    "product",
    "therapeutic_area",
    "region",
    "revenue_usd_m",
]

# Sensible validation ranges. Values outside these are flagged (not dropped).
VALIDATION_RANGES = {
    "approval_year": (1950, 2035),
    "patent_expiry_year": (1990, 2060),
    "revenue_usd_m": (0, 1_000_000),
    "market_size_usd_m": (0, 5_000_000),
    "growth_rate_pct": (-50, 100),
}

# --------------------------------------------------------------------------- #
# Presentation
# --------------------------------------------------------------------------- #
APP_TITLE = "Healthcare Market Research Report Generator"
APP_ICON = "🏥"

# A colour-blind-friendly qualitative palette used across all Plotly charts so
# the dashboard, exports, and PDF look consistent.
COLOR_SEQUENCE = [
    "#1f77b4",  # blue
    "#2ca02c",  # green
    "#ff7f0e",  # orange
    "#9467bd",  # purple
    "#d62728",  # red
    "#17becf",  # teal
    "#bcbd22",  # olive
    "#e377c2",  # pink
]

PRIMARY_COLOR = "#1f77b4"
ACCENT_COLOR = "#2ca02c"
