"""
Competitor analysis.

Builds company profiles, product portfolios, therapeutic-area coverage, and
market-share comparisons from the cleaned market dataset.
"""
from __future__ import annotations

import pandas as pd


def company_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """One row per company with portfolio and revenue summary statistics."""
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby("company")
    profile = grouped.agg(
        company_type=("company_type", "first"),
        headquarters=("headquarters", "first"),
        products=("product", "nunique"),
        therapeutic_areas=("therapeutic_area", "nunique"),
        regions=("region", "nunique"),
        total_revenue_usd_m=("revenue_usd_m", "sum"),
    ).reset_index()

    total = profile["total_revenue_usd_m"].sum()
    profile["market_share_pct"] = (
        (profile["total_revenue_usd_m"] / total * 100).round(2) if total else 0.0
    )
    return profile.sort_values("total_revenue_usd_m", ascending=False).reset_index(
        drop=True
    )


def product_portfolio(df: pd.DataFrame, company: str | None = None) -> pd.DataFrame:
    """Product-level revenue, optionally filtered to a single company."""
    if df.empty:
        return pd.DataFrame()

    data = df if company is None else df[df["company"] == company]
    portfolio = (
        data.groupby(["company", "product", "therapeutic_area"])
        .agg(
            indication=("indication", "first"),
            approval_year=("approval_year", "first"),
            patent_expiry_year=("patent_expiry_year", "first"),
            regions=("region", "nunique"),
            total_revenue_usd_m=("revenue_usd_m", "sum"),
        )
        .reset_index()
        .sort_values("total_revenue_usd_m", ascending=False)
        .reset_index(drop=True)
    )
    return portfolio


def therapeutic_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Matrix of revenue by company (rows) × therapeutic area (columns)."""
    if df.empty:
        return pd.DataFrame()

    pivot = pd.pivot_table(
        df,
        index="company",
        columns="therapeutic_area",
        values="revenue_usd_m",
        aggfunc="sum",
        fill_value=0,
    )
    pivot["Total"] = pivot.sum(axis=1)
    return pivot.sort_values("Total", ascending=False)


def market_share(df: pd.DataFrame) -> pd.DataFrame:
    """Company-level market share by total revenue."""
    profiles = company_profiles(df)
    if profiles.empty:
        return profiles
    return profiles[["company", "total_revenue_usd_m", "market_share_pct"]].copy()


def top_competitors(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """The ``n`` highest-revenue competitors with their leading therapeutic area."""
    profiles = company_profiles(df)
    if profiles.empty:
        return profiles

    # Identify each company's strongest therapeutic area.
    lead_area = (
        df.groupby(["company", "therapeutic_area"])["revenue_usd_m"]
        .sum()
        .reset_index()
        .sort_values("revenue_usd_m", ascending=False)
        .drop_duplicates("company")
        .set_index("company")["therapeutic_area"]
    )
    top = profiles.head(n).copy()
    top["leading_area"] = top["company"].map(lead_area)
    return top.reset_index(drop=True)
