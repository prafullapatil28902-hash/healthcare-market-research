"""
Market-landscape analysis.

High-level structural view of the market: totals, therapeutic-area and regional
distribution, and growth trends.
"""
from __future__ import annotations

from typing import Dict

import pandas as pd


def market_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Headline KPIs used by the dashboard tiles."""
    if df.empty:
        return {
            "total_companies": 0,
            "total_products": 0,
            "total_therapeutic_areas": 0,
            "total_regions": 0,
            "total_revenue_usd_m": 0.0,
            "avg_growth_pct": 0.0,
        }

    return {
        "total_companies": int(df["company"].nunique()),
        "total_products": int(df["product"].nunique()),
        "total_therapeutic_areas": int(df["therapeutic_area"].nunique()),
        "total_regions": int(df["region"].nunique()),
        "total_revenue_usd_m": float(df["revenue_usd_m"].sum()),
        "avg_growth_pct": round(float(df["growth_rate_pct"].mean()), 2),
    }


def therapeutic_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue, product count, and share by therapeutic area."""
    if df.empty:
        return pd.DataFrame()

    dist = (
        df.groupby("therapeutic_area")
        .agg(
            products=("product", "nunique"),
            companies=("company", "nunique"),
            total_revenue_usd_m=("revenue_usd_m", "sum"),
            avg_growth_pct=("growth_rate_pct", "mean"),
        )
        .reset_index()
    )
    total = dist["total_revenue_usd_m"].sum()
    dist["revenue_share_pct"] = (
        (dist["total_revenue_usd_m"] / total * 100).round(2) if total else 0.0
    )
    dist["avg_growth_pct"] = dist["avg_growth_pct"].round(2)
    return dist.sort_values("total_revenue_usd_m", ascending=False).reset_index(
        drop=True
    )


def regional_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and growth by region."""
    if df.empty:
        return pd.DataFrame()

    dist = (
        df.groupby("region")
        .agg(
            companies=("company", "nunique"),
            products=("product", "nunique"),
            total_revenue_usd_m=("revenue_usd_m", "sum"),
            avg_growth_pct=("growth_rate_pct", "mean"),
        )
        .reset_index()
    )
    total = dist["total_revenue_usd_m"].sum()
    dist["revenue_share_pct"] = (
        (dist["total_revenue_usd_m"] / total * 100).round(2) if total else 0.0
    )
    dist["avg_growth_pct"] = dist["avg_growth_pct"].round(2)
    return dist.sort_values("total_revenue_usd_m", ascending=False).reset_index(
        drop=True
    )


def growth_by_area_region(df: pd.DataFrame) -> pd.DataFrame:
    """Average growth rate per therapeutic area × region (for a heatmap)."""
    if df.empty:
        return pd.DataFrame()
    return pd.pivot_table(
        df,
        index="therapeutic_area",
        columns="region",
        values="growth_rate_pct",
        aggfunc="mean",
    ).round(2)
