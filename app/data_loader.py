"""
Data loading and normalisation.

Responsible for turning a raw uploaded CSV (or the bundled sample) into a clean,
correctly-typed DataFrame that the rest of the analytics can rely on.
"""
from __future__ import annotations

from typing import IO, Union

import pandas as pd

from app.config import NUMERIC_COLUMNS, REQUIRED_COLUMNS, SAMPLE_DATASET_PATH


class DataLoadError(Exception):
    """Raised when an uploaded file cannot be parsed into the expected schema."""


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case, strip, and underscore column names for robust matching."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[\s\-]+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df


def load_csv(source: Union[str, IO, "pd.io.common.IOBase"]) -> pd.DataFrame:
    """Read a CSV from a path or file-like object into a normalised DataFrame.

    The data is returned *as parsed* (strings preserved) so the validation step
    can report on raw quality issues before any coercion happens.
    """
    try:
        df = pd.read_csv(source)
    except Exception as exc:  # pragma: no cover - surfaced to the UI
        raise DataLoadError(f"Could not read CSV: {exc}") from exc

    if df.empty:
        raise DataLoadError("The uploaded file contains no rows.")

    df = _normalise_columns(df)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataLoadError(
            "The file is missing required columns: " + ", ".join(missing)
        )

    # Trim whitespace from all string cells — a common real-world data issue.
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    return df[REQUIRED_COLUMNS].copy()


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with numeric columns coerced to numbers.

    Invalid numbers become NaN rather than raising, so downstream analytics can
    decide how to handle them (and validation can count them).
    """
    out = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def load_sample() -> pd.DataFrame:
    """Load the bundled sample dataset from disk."""
    return load_csv(SAMPLE_DATASET_PATH)


def analytics_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a numerically-typed frame with usable rows for analytics.

    Drops rows that are missing the essentials (company/product/revenue) so the
    KPIs and charts are computed on trustworthy data.
    """
    out = coerce_types(df)
    out = out.dropna(subset=["revenue_usd_m"])
    out = out[out["company"].astype(str).str.len() > 0]
    out = out[out["product"].astype(str).str.len() > 0]
    return out.reset_index(drop=True)
