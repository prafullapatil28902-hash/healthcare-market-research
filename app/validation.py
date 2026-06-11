"""
Data-quality validation.

Produces a structured validation report covering missing values, duplicates,
invalid / out-of-range entries, and cross-field inconsistencies. The report is
consumed both by the Streamlit UI and by the export modules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

from app.config import (
    NON_NULL_COLUMNS,
    NUMERIC_COLUMNS,
    VALIDATION_RANGES,
)


@dataclass
class ValidationIssue:
    """A single category of data-quality finding."""

    category: str
    severity: str  # "error" | "warning" | "info"
    count: int
    message: str
    examples: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Aggregated result of running all validation checks."""

    total_rows: int
    total_columns: int
    issues: List[ValidationIssue]

    @property
    def error_count(self) -> int:
        return sum(i.count for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(i.count for i in self.issues if i.severity == "warning")

    @property
    def passed(self) -> bool:
        """True when no error-severity issues were found."""
        return self.error_count == 0

    @property
    def quality_score(self) -> float:
        """A 0-100 heuristic score: clean data scores 100."""
        if self.total_rows == 0:
            return 0.0
        penalty = self.error_count * 1.0 + self.warning_count * 0.4
        score = max(0.0, 100.0 - (penalty / self.total_rows) * 100.0)
        return round(score, 1)

    def to_dataframe(self) -> pd.DataFrame:
        """Tabular view of the issues for display / export."""
        return pd.DataFrame(
            [
                {
                    "Category": i.category,
                    "Severity": i.severity.title(),
                    "Count": i.count,
                    "Detail": i.message,
                }
                for i in self.issues
            ]
        )


def _check_missing(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for col in NON_NULL_COLUMNS:
        if col not in df.columns:
            continue
        blank = df[col].isna() | (df[col].astype(str).str.strip() == "")
        n = int(blank.sum())
        if n:
            issues.append(
                ValidationIssue(
                    category=f"Missing values: {col}",
                    severity="error",
                    count=n,
                    message=f"{n} row(s) have an empty '{col}' value.",
                    examples=[str(r) for r in df.index[blank][:5].tolist()],
                )
            )
    return issues


def _check_duplicates(df: pd.DataFrame) -> List[ValidationIssue]:
    key = [c for c in ("company", "product", "region") if c in df.columns]
    if not key:
        return []
    dup_mask = df.duplicated(subset=key, keep="first")
    n = int(dup_mask.sum())
    if not n:
        return []
    sample = (
        df.loc[dup_mask, key]
        .astype(str)
        .agg(" | ".join, axis=1)
        .head(5)
        .tolist()
    )
    return [
        ValidationIssue(
            category="Duplicate records",
            severity="warning",
            count=n,
            message=f"{n} duplicate company/product/region combination(s).",
            examples=sample,
        )
    ]


def _check_numeric(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        # Non-numeric where a value was present.
        bad = coerced.isna() & df[col].notna() & (df[col].astype(str).str.strip() != "")
        n = int(bad.sum())
        if n:
            issues.append(
                ValidationIssue(
                    category=f"Invalid number: {col}",
                    severity="error",
                    count=n,
                    message=f"{n} non-numeric value(s) in '{col}'.",
                    examples=df.loc[bad, col].astype(str).head(5).tolist(),
                )
            )
    return issues


def _check_ranges(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for col, (lo, hi) in VALIDATION_RANGES.items():
        if col not in df.columns:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        out_of_range = coerced.notna() & ((coerced < lo) | (coerced > hi))
        n = int(out_of_range.sum())
        if n:
            issues.append(
                ValidationIssue(
                    category=f"Out of range: {col}",
                    severity="warning",
                    count=n,
                    message=f"{n} value(s) in '{col}' outside [{lo}, {hi}].",
                    examples=df.loc[out_of_range, col].astype(str).head(5).tolist(),
                )
            )
    return issues


def _check_consistency(df: pd.DataFrame) -> List[ValidationIssue]:
    """Cross-field sanity checks specific to market data."""
    issues: List[ValidationIssue] = []

    # Patent expiry should not predate approval.
    if {"approval_year", "patent_expiry_year"}.issubset(df.columns):
        appr = pd.to_numeric(df["approval_year"], errors="coerce")
        pat = pd.to_numeric(df["patent_expiry_year"], errors="coerce")
        bad = appr.notna() & pat.notna() & (pat < appr)
        n = int(bad.sum())
        if n:
            issues.append(
                ValidationIssue(
                    category="Inconsistent dates",
                    severity="warning",
                    count=n,
                    message=f"{n} row(s) where patent expiry precedes approval year.",
                )
            )

    # Product revenue should not exceed the addressable market it sits in.
    if {"revenue_usd_m", "market_size_usd_m"}.issubset(df.columns):
        rev = pd.to_numeric(df["revenue_usd_m"], errors="coerce")
        mkt = pd.to_numeric(df["market_size_usd_m"], errors="coerce")
        bad = rev.notna() & mkt.notna() & (mkt > 0) & (rev > mkt)
        n = int(bad.sum())
        if n:
            issues.append(
                ValidationIssue(
                    category="Inconsistent revenue",
                    severity="warning",
                    count=n,
                    message=f"{n} row(s) where product revenue exceeds market size.",
                )
            )

    return issues


def validate(df: pd.DataFrame) -> ValidationReport:
    """Run all checks and return a consolidated :class:`ValidationReport`."""
    issues: List[ValidationIssue] = []
    issues += _check_missing(df)
    issues += _check_duplicates(df)
    issues += _check_numeric(df)
    issues += _check_ranges(df)
    issues += _check_consistency(df)

    return ValidationReport(
        total_rows=len(df),
        total_columns=df.shape[1],
        issues=issues,
    )


def summary_counts(report: ValidationReport) -> Dict[str, int]:
    """Headline counts for KPI tiles."""
    return {
        "rows": report.total_rows,
        "errors": report.error_count,
        "warnings": report.warning_count,
        "score": report.quality_score,
    }
