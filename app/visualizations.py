"""
Plotly chart builders.

Each function returns a configured ``plotly.graph_objects.Figure`` so the same
charts can be embedded in the Streamlit dashboard and (as static images) in the
exported reports.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app import competitor_analysis as ca
from app import market_landscape as ml
from app import trend_analysis as ta
from app.config import COLOR_SEQUENCE, PRIMARY_COLOR

_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=COLOR_SEQUENCE,
    font=dict(family="Segoe UI, Arial, sans-serif", size=13),
)


def _empty(message: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=16))
    fig.update_layout(**_LAYOUT)
    return fig


def competitor_ranking_chart(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Horizontal bar chart of top companies by revenue."""
    profiles = ca.company_profiles(df).head(n)
    if profiles.empty:
        return _empty()
    profiles = profiles.sort_values("total_revenue_usd_m")
    fig = px.bar(
        profiles,
        x="total_revenue_usd_m",
        y="company",
        orientation="h",
        text="market_share_pct",
        labels={"total_revenue_usd_m": "Revenue (USD M)", "company": ""},
        title="Top Competitors by Revenue",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                      marker_color=PRIMARY_COLOR)
    fig.update_layout(**_LAYOUT)
    return fig


def therapeutic_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart of revenue share by therapeutic area."""
    dist = ml.therapeutic_distribution(df)
    if dist.empty:
        return _empty()
    fig = px.pie(
        dist,
        names="therapeutic_area",
        values="total_revenue_usd_m",
        hole=0.45,
        title="Revenue by Therapeutic Area",
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(**_LAYOUT)
    return fig


def regional_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of revenue by region."""
    dist = ml.regional_distribution(df)
    if dist.empty:
        return _empty()
    fig = px.bar(
        dist,
        x="region",
        y="total_revenue_usd_m",
        color="region",
        text="revenue_share_pct",
        labels={"total_revenue_usd_m": "Revenue (USD M)", "region": "Region"},
        title="Revenue by Region",
    )
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig.update_layout(showlegend=False, **_LAYOUT)
    return fig


def growth_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of weighted growth by therapeutic area."""
    fast = ta.fastest_growing_areas(df, n=10)
    if fast.empty:
        return _empty()
    fig = px.bar(
        fast.sort_values("weighted_growth_pct"),
        x="weighted_growth_pct",
        y="therapeutic_area",
        orientation="h",
        labels={"weighted_growth_pct": "Weighted growth (%)",
                "therapeutic_area": ""},
        title="Fastest-Growing Therapeutic Areas",
    )
    fig.update_traces(marker_color=COLOR_SEQUENCE[1])
    fig.update_layout(**_LAYOUT)
    return fig


def product_distribution_chart(df: pd.DataFrame, n: int = 12) -> go.Figure:
    """Treemap of revenue by product, grouped by therapeutic area."""
    if df.empty:
        return _empty()
    prod = (
        df.groupby(["therapeutic_area", "product"])["revenue_usd_m"]
        .sum()
        .reset_index()
        .sort_values("revenue_usd_m", ascending=False)
        .head(n)
    )
    fig = px.treemap(
        prod,
        path=["therapeutic_area", "product"],
        values="revenue_usd_m",
        title="Product Revenue Distribution",
        color="revenue_usd_m",
        color_continuous_scale="Blues",
    )
    fig.update_layout(**_LAYOUT)
    return fig


def growth_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap of average growth by therapeutic area × region."""
    grid = ml.growth_by_area_region(df)
    if grid.empty:
        return _empty()
    fig = px.imshow(
        grid,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="RdYlGn",
        labels=dict(color="Growth %"),
        title="Growth Rate Heatmap (Area × Region)",
    )
    fig.update_layout(**_LAYOUT)
    return fig


def opportunity_chart(df: pd.DataFrame, n: int = 8) -> go.Figure:
    """Bar chart of the largest market opportunities (white space)."""
    opp = ta.market_opportunities(df).head(n)
    if opp.empty:
        return _empty()
    opp = opp.copy()
    opp["label"] = opp["therapeutic_area"] + " — " + opp["region"]
    fig = px.bar(
        opp.sort_values("opportunity_usd_m"),
        x="opportunity_usd_m",
        y="label",
        orientation="h",
        color="penetration_pct",
        color_continuous_scale="Oranges_r",
        labels={"opportunity_usd_m": "White space (USD M)", "label": "",
                "penetration_pct": "Penetration %"},
        title="Top Market Opportunities",
    )
    fig.update_layout(**_LAYOUT)
    return fig
