"""
Automated insight generation.

Turns the quantitative outputs of the analytics modules into analyst-style
narrative bullet points: leading competitors, market gaps, growth opportunities,
risk areas, and strategic observations. The logic is rules-based and fully
transparent — no external LLM call — so it runs offline and is reproducible.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import List

import pandas as pd

from app import competitor_analysis as ca
from app import market_landscape as ml
from app import trend_analysis as ta


@dataclass
class Insight:
    """A single analyst observation."""

    category: str
    text: str


def _fmt_usd_m(value: float) -> str:
    """Format a USD-millions figure compactly (e.g. 12,500 -> $12.5B)."""
    if value >= 1000:
        return f"${value / 1000:,.1f}B"
    return f"${value:,.0f}M"


def generate_insights(df: pd.DataFrame) -> List[Insight]:
    """Produce a prioritised list of insights for the current dataset."""
    if df.empty:
        return [Insight("Data", "No data available to analyse.")]

    insights: List[Insight] = []
    kpis = ml.market_kpis(df)

    # --- Leading competitors ------------------------------------------------ #
    competitors = ca.top_competitors(df, n=3)
    if not competitors.empty:
        leader = competitors.iloc[0]
        insights.append(
            Insight(
                "Leading Competitor",
                f"{leader['company']} leads the analysed market with "
                f"{_fmt_usd_m(leader['total_revenue_usd_m'])} in revenue "
                f"({leader['market_share_pct']:.1f}% share), anchored in "
                f"{leader['leading_area']}.",
            )
        )
        if len(competitors) >= 3:
            top3_share = competitors["market_share_pct"].sum()
            insights.append(
                Insight(
                    "Market Concentration",
                    f"The top 3 players control {top3_share:.1f}% of revenue, "
                    f"indicating a "
                    f"{'highly consolidated' if top3_share > 60 else 'moderately competitive'}"
                    f" market.",
                )
            )

    # --- Growth opportunities ---------------------------------------------- #
    fast = ta.fastest_growing_areas(df, n=3)
    if not fast.empty:
        top_area = fast.iloc[0]
        insights.append(
            Insight(
                "Growth Opportunity",
                f"{top_area['therapeutic_area']} is the fastest-growing area at "
                f"{top_area['weighted_growth_pct']:.1f}% weighted growth — the "
                f"strongest near-term expansion vector.",
            )
        )

    opp = ta.market_opportunities(df)
    if not opp.empty:
        top_opp = opp.iloc[0]
        insights.append(
            Insight(
                "Market Gap",
                f"{top_opp['therapeutic_area']} in {top_opp['region']} shows the "
                f"largest white space: {_fmt_usd_m(top_opp['opportunity_usd_m'])} "
                f"unpenetrated at only {top_opp['penetration_pct']:.0f}% market "
                f"penetration.",
            )
        )

    # --- Risk areas --------------------------------------------------------- #
    current_year = _dt.date.today().year
    typed = df.copy()
    typed["patent_expiry_year"] = pd.to_numeric(
        typed["patent_expiry_year"], errors="coerce"
    )
    at_risk = typed[
        (typed["patent_expiry_year"] >= current_year)
        & (typed["patent_expiry_year"] <= current_year + 3)
    ]
    if not at_risk.empty:
        rev_at_risk = at_risk["revenue_usd_m"].sum()
        n_products = at_risk["product"].nunique()
        insights.append(
            Insight(
                "Risk Area",
                f"{n_products} product(s) representing "
                f"{_fmt_usd_m(rev_at_risk)} face patent expiry within 3 years, "
                f"exposing that revenue to generic / biosimilar erosion.",
            )
        )

    # Single-company dominance in any area is a structural risk for challengers.
    coverage = ca.therapeutic_coverage(df)
    if not coverage.empty:
        for area in [c for c in coverage.columns if c != "Total"]:
            col = coverage[area]
            if col.sum() > 0:
                top_share = col.max() / col.sum() * 100
                if top_share > 50:
                    leader_name = col.idxmax()
                    insights.append(
                        Insight(
                            "Risk Area",
                            f"{leader_name} dominates {area} with "
                            f"{top_share:.0f}% of area revenue — a high barrier "
                            f"to entry for challengers.",
                        )
                    )
                    break

    # --- Strategic observations -------------------------------------------- #
    regions = ml.regional_distribution(df)
    if not regions.empty:
        lead_region = regions.iloc[0]
        insights.append(
            Insight(
                "Strategic Observation",
                f"{lead_region['region']} is the largest regional market "
                f"({lead_region['revenue_share_pct']:.0f}% of revenue) with "
                f"{lead_region['avg_growth_pct']:.1f}% average growth.",
            )
        )

    insights.append(
        Insight(
            "Strategic Observation",
            f"The analysed universe spans {kpis['total_companies']} companies and "
            f"{kpis['total_products']} products across "
            f"{kpis['total_therapeutic_areas']} therapeutic areas, with overall "
            f"average growth of {kpis['avg_growth_pct']:.1f}%.",
        )
    )

    return insights


def insights_to_dataframe(insights: List[Insight]) -> pd.DataFrame:
    """Tabular view of insights for display / export."""
    return pd.DataFrame(
        [{"Category": i.category, "Insight": i.text} for i in insights]
    )
