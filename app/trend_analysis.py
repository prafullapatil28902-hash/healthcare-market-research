"""
Trend analysis.

Surfaces dynamics in the market: fastest-growing therapeutic areas, most active
companies, recently-launched (emerging) products, and quantified market
opportunities (white space).
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd

# Products approved within this many years are treated as "emerging".
_EMERGING_WINDOW_YEARS = 7


def fastest_growing_areas(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Therapeutic areas ranked by revenue-weighted average growth rate."""
    if df.empty:
        return pd.DataFrame()

    def _weighted(group: pd.DataFrame) -> float:
        weights = group["revenue_usd_m"]
        if weights.sum() == 0:
            return float(group["growth_rate_pct"].mean())
        return float((group["growth_rate_pct"] * weights).sum() / weights.sum())

    rows = []
    for area, group in df.groupby("therapeutic_area"):
        rows.append(
            {
                "therapeutic_area": area,
                "weighted_growth_pct": round(_weighted(group), 2),
                "total_revenue_usd_m": float(group["revenue_usd_m"].sum()),
            }
        )
    out = pd.DataFrame(rows).sort_values("weighted_growth_pct", ascending=False)
    return out.head(n).reset_index(drop=True)


def most_active_companies(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Companies ranked by breadth of activity (products × areas × regions)."""
    if df.empty:
        return pd.DataFrame()

    activity = (
        df.groupby("company")
        .agg(
            products=("product", "nunique"),
            therapeutic_areas=("therapeutic_area", "nunique"),
            regions=("region", "nunique"),
            total_revenue_usd_m=("revenue_usd_m", "sum"),
        )
        .reset_index()
    )
    # A simple composite "activity index".
    activity["activity_index"] = (
        activity["products"] * 2
        + activity["therapeutic_areas"] * 3
        + activity["regions"]
    )
    return (
        activity.sort_values("activity_index", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def emerging_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Recently-approved products, newest first."""
    if df.empty:
        return pd.DataFrame()

    current_year = _dt.date.today().year
    cutoff = current_year - _EMERGING_WINDOW_YEARS

    products = (
        df.groupby(["product", "company", "therapeutic_area"])
        .agg(
            approval_year=("approval_year", "first"),
            total_revenue_usd_m=("revenue_usd_m", "sum"),
        )
        .reset_index()
    )
    emerging = products[products["approval_year"] >= cutoff]
    return (
        emerging.sort_values("approval_year", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def market_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    """Quantify white space: addressable market not yet captured by revenue.

    For each therapeutic-area × region cell we compare total captured revenue to
    the addressable market size, and rank by the unpenetrated, fast-growing gap.
    """
    if df.empty:
        return pd.DataFrame()

    cell = (
        df.groupby(["therapeutic_area", "region"])
        .agg(
            captured_revenue_usd_m=("revenue_usd_m", "sum"),
            market_size_usd_m=("market_size_usd_m", "max"),
            growth_pct=("growth_rate_pct", "mean"),
            companies=("company", "nunique"),
        )
        .reset_index()
    )
    cell["opportunity_usd_m"] = (
        cell["market_size_usd_m"] - cell["captured_revenue_usd_m"]
    ).clip(lower=0)
    cell["penetration_pct"] = (
        (cell["captured_revenue_usd_m"] / cell["market_size_usd_m"] * 100)
        .where(cell["market_size_usd_m"] > 0, 0)
        .round(1)
    )
    # Opportunity score favours large, fast-growing, under-penetrated cells.
    cell["opportunity_score"] = (
        cell["opportunity_usd_m"] * (1 + cell["growth_pct"] / 100)
    ).round(0)
    cell["growth_pct"] = cell["growth_pct"].round(2)

    return cell.sort_values("opportunity_score", ascending=False).reset_index(
        drop=True
    )
