"""
Healthcare Market Research Report Generator — Streamlit entry point.

Run with:  streamlit run app/main.py

The app is organised as a sidebar (data source + global filters) plus a set of
tabs, each backed by a dedicated analytics module. State (the working dataset) is
persisted in SQLite via :mod:`app.database` and cached in ``st.session_state``.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running via ``streamlit run app/main.py`` from the project root by making
# the project importable as the ``app`` package.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app import competitor_analysis as ca
from app import database as db
from app import data_loader
from app import insights as ins
from app import market_landscape as ml
from app import trend_analysis as ta
from app import visualizations as viz
from app import exporters
from app.config import APP_ICON, APP_TITLE
from app.executive_summary import build_executive_summary
from app.sample_data import generate_sample_dataset
from app.validation import validate

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")


# --------------------------------------------------------------------------- #
# Data access helpers
# --------------------------------------------------------------------------- #
def _store_dataset(df: pd.DataFrame) -> None:
    """Persist a freshly loaded raw dataset and reset cached state."""
    db.save_dataframe(df)
    st.session_state["raw_df"] = df
    st.session_state.pop("filters", None)


def _get_raw() -> pd.DataFrame:
    """Return the raw working dataset (from session or SQLite)."""
    if "raw_df" in st.session_state:
        return st.session_state["raw_df"]
    df = db.load_dataframe()
    if not df.empty:
        st.session_state["raw_df"] = df
    return df


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the sidebar search/filter selections to the analytics frame."""
    filters = st.session_state.get("filters", {})
    out = df
    for col, selected in filters.items():
        if selected and col in out.columns:
            out = out[out[col].isin(selected)]
    return out


# --------------------------------------------------------------------------- #
# Sidebar — data source + filters
# --------------------------------------------------------------------------- #
def render_sidebar() -> None:
    st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
    st.sidebar.caption("Convert raw healthcare market data into competitive intelligence.")

    st.sidebar.header("1 · Data source")
    uploaded = st.sidebar.file_uploader("Upload market data (CSV)", type=["csv"])
    col_a, col_b = st.sidebar.columns(2)

    if col_a.button("Load sample", use_container_width=True):
        try:
            _store_dataset(data_loader.load_sample())
            st.sidebar.success("Sample dataset loaded.")
        except Exception:
            # Fall back to generating one if the bundled CSV is missing.
            _store_dataset(generate_sample_dataset())
            st.sidebar.success("Generated sample dataset.")

    if col_b.button("Clear data", use_container_width=True):
        st.session_state.clear()
        st.sidebar.info("Cleared. Upload or load sample to continue.")

    if uploaded is not None:
        try:
            df = data_loader.load_csv(uploaded)
            _store_dataset(df)
            st.sidebar.success(f"Loaded {len(df):,} rows.")
        except data_loader.DataLoadError as exc:
            st.sidebar.error(str(exc))

    # Global search & filter (only meaningful once data exists).
    raw = _get_raw()
    if not raw.empty:
        st.sidebar.header("2 · Search & filter")
        frame = data_loader.analytics_frame(raw)
        filters = {}
        for label, col in [
            ("Company", "company"),
            ("Therapeutic area", "therapeutic_area"),
            ("Product", "product"),
            ("Region", "region"),
        ]:
            options = sorted(frame[col].dropna().unique().tolist())
            filters[col] = st.sidebar.multiselect(label, options, default=[])
        st.session_state["filters"] = filters

    st.sidebar.markdown("---")
    st.sidebar.caption("Built for healthcare market research analysts.")


# --------------------------------------------------------------------------- #
# Tab renderers
# --------------------------------------------------------------------------- #
def tab_overview(df: pd.DataFrame) -> None:
    st.subheader("Data Overview")
    st.caption("Preview of the active (filtered) dataset.")
    kpis = ml.market_kpis(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies", kpis["total_companies"])
    c2.metric("Products", kpis["total_products"])
    c3.metric("Therapeutic areas", kpis["total_therapeutic_areas"])
    c4.metric("Total revenue", f"${kpis['total_revenue_usd_m']:,.0f}M")
    st.dataframe(df, use_container_width=True, height=420)


def tab_validation(raw: pd.DataFrame) -> None:
    st.subheader("Data Validation")
    st.caption("Quality checks are run against the *raw uploaded* data.")
    report = validate(raw)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", report.total_rows)
    c2.metric("Errors", report.error_count)
    c3.metric("Warnings", report.warning_count)
    c4.metric("Quality score", f"{report.quality_score}/100")

    if report.passed and report.warning_count == 0:
        st.success("✅ No data-quality issues detected. Dataset is clean.")
    elif report.passed:
        st.warning("Dataset usable, but some warnings were found — see below.")
    else:
        st.error("Errors found that may affect analysis — review and re-upload.")

    vdf = report.to_dataframe()
    if not vdf.empty:
        st.dataframe(vdf, use_container_width=True)
    else:
        st.info("Nothing to report.")


def tab_competitors(df: pd.DataFrame) -> None:
    st.subheader("Competitor Analysis")
    st.plotly_chart(viz.competitor_ranking_chart(df), use_container_width=True)

    st.markdown("#### Company profiles")
    st.dataframe(ca.company_profiles(df), use_container_width=True)

    companies = ["(All)"] + sorted(df["company"].unique().tolist())
    chosen = st.selectbox("Inspect a company portfolio", companies)
    company = None if chosen == "(All)" else chosen
    st.markdown("#### Product portfolio")
    st.dataframe(ca.product_portfolio(df, company), use_container_width=True)

    st.markdown("#### Therapeutic-area coverage")
    st.dataframe(ca.therapeutic_coverage(df), use_container_width=True)


def tab_landscape(df: pd.DataFrame) -> None:
    st.subheader("Market Landscape")
    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.therapeutic_distribution_chart(df), use_container_width=True)
    c2.plotly_chart(viz.regional_distribution_chart(df), use_container_width=True)

    st.markdown("#### Therapeutic area distribution")
    st.dataframe(ml.therapeutic_distribution(df), use_container_width=True)
    st.markdown("#### Regional distribution")
    st.dataframe(ml.regional_distribution(df), use_container_width=True)
    st.plotly_chart(viz.growth_heatmap(df), use_container_width=True)


def tab_trends(df: pd.DataFrame) -> None:
    st.subheader("Trend Analysis")
    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.growth_chart(df), use_container_width=True)
    c2.plotly_chart(viz.opportunity_chart(df), use_container_width=True)

    st.markdown("#### Fastest-growing therapeutic areas")
    st.dataframe(ta.fastest_growing_areas(df, n=10), use_container_width=True)
    st.markdown("#### Most active companies")
    st.dataframe(ta.most_active_companies(df, n=10), use_container_width=True)
    st.markdown("#### Emerging products")
    st.dataframe(ta.emerging_products(df), use_container_width=True)
    st.markdown("#### Market opportunities (white space)")
    st.dataframe(ta.market_opportunities(df), use_container_width=True)


def tab_insights(df: pd.DataFrame) -> None:
    st.subheader("Analyst Insights")
    st.caption("Automatically generated, rules-based observations.")
    for insight in ins.generate_insights(df):
        st.markdown(f"**{insight.category}** — {insight.text}")


def tab_summary(df: pd.DataFrame) -> None:
    st.subheader("Executive Summary")
    summary = build_executive_summary(df)
    st.markdown(summary.to_markdown())


def tab_dashboard(df: pd.DataFrame) -> None:
    st.subheader("Market Dashboard")
    kpis = ml.market_kpis(df)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Companies", kpis["total_companies"])
    c2.metric("Products", kpis["total_products"])
    c3.metric("Areas", kpis["total_therapeutic_areas"])
    c4.metric("Revenue", f"${kpis['total_revenue_usd_m']:,.0f}M")
    c5.metric("Avg growth", f"{kpis['avg_growth_pct']:.1f}%")

    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.competitor_ranking_chart(df), use_container_width=True)
    c2.plotly_chart(viz.therapeutic_distribution_chart(df), use_container_width=True)
    c1.plotly_chart(viz.product_distribution_chart(df), use_container_width=True)
    c2.plotly_chart(viz.growth_chart(df), use_container_width=True)
    st.plotly_chart(viz.growth_heatmap(df), use_container_width=True)


def tab_export(df: pd.DataFrame, raw: pd.DataFrame) -> None:
    st.subheader("Export Reports")
    st.caption("All exports reflect the current filters.")
    report = validate(raw)
    ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 📊 Excel workbook")
        st.download_button(
            "Download Excel report",
            data=exporters.build_excel_report(df),
            file_name=f"market_research_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        st.markdown("##### 📄 Full PDF report")
        st.download_button(
            "Download PDF report",
            data=exporters.build_pdf_report(df, report),
            file_name=f"market_research_{ts}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with c2:
        st.markdown("##### 📝 Executive summary")
        st.download_button(
            "Download executive summary (PDF)",
            data=exporters.build_executive_summary_pdf(df),
            file_name=f"executive_summary_{ts}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.download_button(
            "Download executive summary (TXT)",
            data=exporters.build_executive_summary_text(df),
            file_name=f"executive_summary_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.markdown("##### 🏢 Competitor analysis")
        st.download_button(
            "Download competitor report (PDF)",
            data=exporters.build_competitor_pdf(df),
            file_name=f"competitor_analysis_{ts}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    render_sidebar()
    raw = _get_raw()

    if raw.empty:
        st.title(f"{APP_ICON} {APP_TITLE}")
        st.info(
            "👋 Get started by uploading a CSV in the sidebar, or click "
            "**Load sample** to explore with realistic diabetes, oncology, and "
            "cardiovascular market data."
        )
        with st.expander("Expected CSV columns"):
            from app.config import REQUIRED_COLUMNS

            st.write(REQUIRED_COLUMNS)
        return

    # Analytics-ready, filtered frame.
    analytics = data_loader.analytics_frame(raw)
    filtered = _apply_filters(analytics)

    if filtered.empty:
        st.warning("No rows match the current filters. Adjust them in the sidebar.")
        return

    tabs = st.tabs(
        [
            "📋 Overview",
            "✅ Validation",
            "🏢 Competitors",
            "🌍 Landscape",
            "📈 Trends",
            "💡 Insights",
            "📝 Summary",
            "📊 Dashboard",
            "⬇️ Export",
        ]
    )
    with tabs[0]:
        tab_overview(filtered)
    with tabs[1]:
        tab_validation(raw)
    with tabs[2]:
        tab_competitors(filtered)
    with tabs[3]:
        tab_landscape(filtered)
    with tabs[4]:
        tab_trends(filtered)
    with tabs[5]:
        tab_insights(filtered)
    with tabs[6]:
        tab_summary(filtered)
    with tabs[7]:
        tab_dashboard(filtered)
    with tabs[8]:
        tab_export(filtered, raw)


if __name__ == "__main__":
    main()
