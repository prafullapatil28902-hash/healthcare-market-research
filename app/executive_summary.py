"""
Executive-summary generation.

Assembles a professional, narrative market-research summary from the analytics
and insight modules. Returns a structured object that the UI renders as Markdown
and the exporters render into PDF / Excel.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import List

import pandas as pd

from app import competitor_analysis as ca
from app import insights as ins
from app import market_landscape as ml
from app import trend_analysis as ta


@dataclass
class ExecutiveSummary:
    """Structured executive summary with named sections."""

    title: str
    generated_on: str
    market_overview: str
    competitive_landscape: str
    key_findings: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the summary as Markdown for the Streamlit UI."""
        lines = [
            f"# {self.title}",
            f"*Generated on {self.generated_on}*",
            "",
            "## Market Overview",
            self.market_overview,
            "",
            "## Competitive Landscape",
            self.competitive_landscape,
            "",
            "## Key Findings",
        ]
        lines += [f"- {f}" for f in self.key_findings]
        lines += ["", "## Opportunities"]
        lines += [f"- {o}" for o in self.opportunities]
        lines += ["", "## Recommendations"]
        lines += [f"- {r}" for r in self.recommendations]
        return "\n".join(lines)

    def to_plain_text(self) -> str:
        """Render a plain-text version (used for the .txt export)."""
        md = self.to_markdown()
        return md.replace("# ", "").replace("## ", "").replace("- ", "  - ")


def _fmt_usd_m(value: float) -> str:
    if value >= 1000:
        return f"${value / 1000:,.1f}B"
    return f"${value:,.0f}M"


def build_executive_summary(df: pd.DataFrame) -> ExecutiveSummary:
    """Generate an :class:`ExecutiveSummary` for the supplied dataset."""
    today = _dt.date.today().strftime("%d %B %Y")

    if df.empty:
        return ExecutiveSummary(
            title="Healthcare Market Research — Executive Summary",
            generated_on=today,
            market_overview="No data available.",
            competitive_landscape="No data available.",
        )

    kpis = ml.market_kpis(df)
    areas = ml.therapeutic_distribution(df)
    regions = ml.regional_distribution(df)
    competitors = ca.top_competitors(df, n=5)
    fast = ta.fastest_growing_areas(df, n=3)
    opp = ta.market_opportunities(df)

    # --- Market overview ---------------------------------------------------- #
    lead_area = areas.iloc[0] if not areas.empty else None
    lead_region = regions.iloc[0] if not regions.empty else None
    market_overview = (
        f"The analysed healthcare market comprises {kpis['total_companies']} "
        f"companies marketing {kpis['total_products']} products across "
        f"{kpis['total_therapeutic_areas']} therapeutic areas and "
        f"{kpis['total_regions']} regions, with aggregate revenue of "
        f"{_fmt_usd_m(kpis['total_revenue_usd_m'])} and an average growth rate of "
        f"{kpis['avg_growth_pct']:.1f}%."
    )
    if lead_area is not None:
        market_overview += (
            f" {lead_area['therapeutic_area']} is the largest therapeutic area "
            f"({lead_area['revenue_share_pct']:.0f}% of revenue), while "
            f"{lead_region['region']} leads regionally "
            f"({lead_region['revenue_share_pct']:.0f}% of revenue)."
        )

    # --- Competitive landscape --------------------------------------------- #
    if not competitors.empty:
        leader = competitors.iloc[0]
        names = ", ".join(competitors["company"].head(3).tolist())
        competitive_landscape = (
            f"{leader['company']} is the market leader with "
            f"{_fmt_usd_m(leader['total_revenue_usd_m'])} in revenue "
            f"({leader['market_share_pct']:.1f}% share). The leading cohort "
            f"({names}) sets the competitive benchmark, competing primarily in "
            f"{leader['leading_area']}."
        )
    else:
        competitive_landscape = "Competitive data unavailable."

    # --- Key findings (reuse the insight engine) --------------------------- #
    insight_list = ins.generate_insights(df)
    key_findings = [
        i.text
        for i in insight_list
        if i.category in {"Leading Competitor", "Market Concentration", "Risk Area"}
    ][:5]

    # --- Opportunities ------------------------------------------------------ #
    opportunities: List[str] = []
    if not fast.empty:
        opportunities.append(
            f"Prioritise {fast.iloc[0]['therapeutic_area']} — the fastest-growing "
            f"area at {fast.iloc[0]['weighted_growth_pct']:.1f}% weighted growth."
        )
    for _, row in opp.head(2).iterrows():
        opportunities.append(
            f"{row['therapeutic_area']} in {row['region']}: "
            f"{_fmt_usd_m(row['opportunity_usd_m'])} of addressable white space "
            f"at {row['penetration_pct']:.0f}% penetration."
        )

    # --- Recommendations ---------------------------------------------------- #
    recommendations = _build_recommendations(df, competitors, fast, opp)

    return ExecutiveSummary(
        title="Healthcare Market Research — Executive Summary",
        generated_on=today,
        market_overview=market_overview,
        competitive_landscape=competitive_landscape,
        key_findings=key_findings or ["See detailed analysis tabs."],
        opportunities=opportunities or ["See detailed analysis tabs."],
        recommendations=recommendations,
    )


def _build_recommendations(
    df: pd.DataFrame,
    competitors: pd.DataFrame,
    fast: pd.DataFrame,
    opp: pd.DataFrame,
) -> List[str]:
    """Derive actionable recommendations from the analytics."""
    recs: List[str] = []

    if not fast.empty:
        recs.append(
            f"Allocate R&D and commercial investment toward "
            f"{fast.iloc[0]['therapeutic_area']}, where growth materially "
            f"outpaces the market average."
        )
    if not opp.empty:
        top = opp.iloc[0]
        recs.append(
            f"Pursue geographic expansion into {top['region']} for "
            f"{top['therapeutic_area']}, where penetration is only "
            f"{top['penetration_pct']:.0f}%."
        )
    if not competitors.empty:
        recs.append(
            f"Benchmark portfolio and pricing against {competitors.iloc[0]['company']} "
            f"to defend share in core therapeutic areas."
        )

    # Patent-cliff defence.
    current_year = _dt.date.today().year
    typed = df.copy()
    typed["patent_expiry_year"] = pd.to_numeric(
        typed["patent_expiry_year"], errors="coerce"
    )
    near_cliff = typed[
        (typed["patent_expiry_year"] >= current_year)
        & (typed["patent_expiry_year"] <= current_year + 3)
    ]
    if not near_cliff.empty:
        recs.append(
            "Develop lifecycle-management and next-generation pipeline strategies "
            "to offset upcoming patent expiries and biosimilar competition."
        )

    recs.append(
        "Establish ongoing competitive-intelligence monitoring to track "
        "emerging products and shifts in therapeutic-area growth."
    )
    return recs
