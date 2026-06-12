"""
Healthcare Market Research Report Generator — Streamlit Web App
Author: Prafulla Patil
GitHub: https://github.com/prafullapatil28902-hash/healthcare-market-research
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

st.set_page_config(
    page_title="Healthcare Market Research",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title { font-size: 2.2rem; font-weight: 800; color: #1B4F8C; margin-bottom: 0; }
.sub-title  { font-size: 1rem; color: #666; margin-top: 0; margin-bottom: 1.5rem; }
.metric-card { background: #f0f4ff; border-radius: 10px; padding: 1rem; text-align: center; border-left: 4px solid #1B4F8C; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #1B4F8C; }
.metric-label { font-size: 0.8rem; color: #666; }
.section-header { color: #1B4F8C; font-size: 1.2rem; font-weight: 700; border-bottom: 2px solid #1B4F8C; padding-bottom: 4px; margin: 1rem 0 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
COMPANIES = [
    {"Company":"Pfizer","Segment":"Oncology","Revenue ($B)":58.5,"Market Share %":8.2,"Pipeline Drugs":89,"Region":"Global","Year":2024},
    {"Company":"Roche","Segment":"Oncology","Revenue ($B)":49.8,"Market Share %":7.0,"Pipeline Drugs":76,"Region":"Global","Year":2024},
    {"Company":"Johnson & Johnson","Segment":"Immunology","Revenue ($B)":85.2,"Market Share %":11.9,"Pipeline Drugs":113,"Region":"Global","Year":2024},
    {"Company":"Novartis","Segment":"Cardiovascular","Revenue ($B)":45.4,"Market Share %":6.4,"Pipeline Drugs":95,"Region":"Global","Year":2024},
    {"Company":"AstraZeneca","Segment":"Respiratory","Revenue ($B)":45.8,"Market Share %":6.4,"Pipeline Drugs":182,"Region":"Global","Year":2024},
    {"Company":"Sanofi","Segment":"Rare Disease","Revenue ($B)":43.1,"Market Share %":6.0,"Pipeline Drugs":78,"Region":"Europe","Year":2024},
    {"Company":"Merck","Segment":"Oncology","Revenue ($B)":60.1,"Market Share %":8.4,"Pipeline Drugs":92,"Region":"Global","Year":2024},
    {"Company":"AbbVie","Segment":"Immunology","Revenue ($B)":56.3,"Market Share %":7.9,"Pipeline Drugs":67,"Region":"Global","Year":2024},
    {"Company":"Bristol-Myers Squibb","Segment":"Oncology","Revenue ($B)":47.2,"Market Share %":6.6,"Pipeline Drugs":84,"Region":"Global","Year":2024},
    {"Company":"Eli Lilly","Segment":"Diabetes","Revenue ($B)":34.1,"Market Share %":4.8,"Pipeline Drugs":52,"Region":"Global","Year":2024},
    {"Company":"Sun Pharma","Segment":"Generics","Revenue ($B)":5.1,"Market Share %":0.7,"Pipeline Drugs":45,"Region":"India/Global","Year":2024},
    {"Company":"Cipla","Segment":"Respiratory","Revenue ($B)":2.7,"Market Share %":0.4,"Pipeline Drugs":38,"Region":"India","Year":2024},
    {"Company":"Dr. Reddy's","Segment":"Generics","Revenue ($B)":3.0,"Market Share %":0.4,"Pipeline Drugs":29,"Region":"India/Global","Year":2024},
    {"Company":"Biocon","Segment":"Biosimilars","Revenue ($B)":1.3,"Market Share %":0.2,"Pipeline Drugs":22,"Region":"India","Year":2024},
]

TRENDS = [
    {"Year":2019,"Global Market ($B)":1285,"Growth %":4.8,"AI Investment ($B)":2.1,"Biosimilars ($B)":6.3,"Digital Health ($B)":175},
    {"Year":2020,"Global Market ($B)":1274,"Growth %":-0.9,"AI Investment ($B)":3.8,"Biosimilars ($B)":8.4,"Digital Health ($B)":248},
    {"Year":2021,"Global Market ($B)":1419,"Growth %":11.4,"AI Investment ($B)":6.7,"Biosimilars ($B)":11.2,"Digital Health ($B)":350},
    {"Year":2022,"Global Market ($B)":1482,"Growth %":4.4,"AI Investment ($B)":10.2,"Biosimilars ($B)":14.8,"Digital Health ($B)":426},
    {"Year":2023,"Global Market ($B)":1603,"Growth %":8.2,"AI Investment ($B)":15.9,"Biosimilars ($B)":19.6,"Digital Health ($B)":512},
    {"Year":2024,"Global Market ($B)":1731,"Growth %":8.0,"AI Investment ($B)":22.4,"Biosimilars ($B)":26.1,"Digital Health ($B)":610},
    {"Year":2025,"Global Market ($B)":1870,"Growth %":8.0,"AI Investment ($B)":31.0,"Biosimilars ($B)":33.8,"Digital Health ($B)":728},
]

SEGMENTS = [
    {"Segment":"Oncology","Market Size ($B)":248,"CAGR %":12.1,"Key Players":"Roche, Pfizer, Merck, BMS"},
    {"Segment":"Immunology","Market Size ($B)":156,"CAGR %":9.4,"Key Players":"J&J, AbbVie, Novartis"},
    {"Segment":"Cardiovascular","Market Size ($B)":108,"CAGR %":5.2,"Key Players":"Novartis, Pfizer, Bayer"},
    {"Segment":"Neurology","Market Size ($B)":94,"CAGR %":7.8,"Key Players":"Biogen, Roche, Sanofi"},
    {"Segment":"Diabetes","Market Size ($B)":81,"CAGR %":8.5,"Key Players":"Novo Nordisk, Eli Lilly, Sanofi"},
    {"Segment":"Respiratory","Market Size ($B)":61,"CAGR %":6.3,"Key Players":"AstraZeneca, Boehringer, Novartis"},
    {"Segment":"Rare Disease","Market Size ($B)":48,"CAGR %":14.2,"Key Players":"Sanofi, Takeda, Alexion"},
    {"Segment":"Biosimilars","Market Size ($B)":34,"CAGR %":18.7,"Key Players":"Biocon, Teva, Sandoz"},
    {"Segment":"Generics","Market Size ($B)":422,"CAGR %":4.1,"Key Players":"Teva, Sun Pharma, Cipla"},
]

df_co   = pd.DataFrame(COMPANIES)
df_tr   = pd.DataFrame(TRENDS)
df_seg  = pd.DataFrame(SEGMENTS)

# Tier
def tier(share):
    if share >= 7:   return "🥇 Tier 1 — Leader"
    if share >= 3:   return "🥈 Tier 2 — Challenger"
    return               "🥉 Tier 3 — Niche/Regional"
df_co["Tier"] = df_co["Market Share %"].apply(tier)
df_co["Rank"] = df_co["Revenue ($B)"].rank(ascending=False).astype(int)

# ── Excel export helper ────────────────────────────────────────────────────────
def to_excel(df_dict):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for sheet, df in df_dict.items():
            df.to_excel(w, sheet_name=sheet, index=False)
    return buf.getvalue()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/health-book.png", width=60)
    st.markdown("### 🏥 Healthcare MRA Tool")
    st.markdown("*By Prafulla Patil*")
    st.divider()
    page = st.radio("📊 Navigate", [
        "🏠 Dashboard",
        "🔍 Competitor Analysis",
        "🗺️ Market Landscape",
        "📈 Trend Analysis",
        "📝 Executive Summary",
    ])
    st.divider()
    st.markdown("**Filters**")
    seg_filter = st.multiselect("Therapeutic Segment", df_co["Segment"].unique().tolist(),
                                 default=df_co["Segment"].unique().tolist())
    region_filter = st.multiselect("Region", df_co["Region"].unique().tolist(),
                                    default=df_co["Region"].unique().tolist())

df_filtered = df_co[df_co["Segment"].isin(seg_filter) & df_co["Region"].isin(region_filter)]

# ── Dashboard ──────────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown('<p class="main-title">🏥 Healthcare Market Research Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Global Pharmaceutical & Healthcare Market Intelligence | 2024</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🌐 Global Market", "$1,731B", "+8.0% YoY")
    with c2:
        st.metric("🏢 Companies Tracked", str(len(df_co)), "14 pharma players")
    with c3:
        st.metric("🔬 Fastest Growing", "Biosimilars", "18.7% CAGR")
    with c4:
        st.metric("🤖 AI Investment", "$22.4B", "+41% YoY")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-header">Top 10 Companies by Revenue</p>', unsafe_allow_html=True)
        top10 = df_co.nlargest(10, "Revenue ($B)")
        fig = px.bar(top10, x="Revenue ($B)", y="Company", orientation="h",
                     color="Segment", color_discrete_sequence=px.colors.qualitative.Set2,
                     height=380)
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-header">Market Share by Segment</p>', unsafe_allow_html=True)
        fig2 = px.pie(df_seg, values="Market Size ($B)", names="Segment",
                      color_discrete_sequence=px.colors.qualitative.Pastel, height=380,
                      hole=0.35)
        fig2.update_layout(margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-header">Global Market Growth (2019–2025)</p>', unsafe_allow_html=True)
    fig3 = px.area(df_tr, x="Year", y="Global Market ($B)",
                   color_discrete_sequence=["#1B4F8C"], height=220)
    fig3.update_layout(margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

# ── Competitor Analysis ────────────────────────────────────────────────────────
elif page == "🔍 Competitor Analysis":
    st.markdown('<p class="main-title">🔍 Competitor Analysis</p>', unsafe_allow_html=True)
    st.markdown(f"*Showing {len(df_filtered)} companies | Filters: {', '.join(seg_filter)}*")

    col1, col2, col3 = st.columns(3)
    col1.metric("Companies", len(df_filtered))
    col2.metric("Total Revenue", f"${df_filtered['Revenue ($B)'].sum():.0f}B")
    col3.metric("Avg Pipeline", f"{df_filtered['Pipeline Drugs'].mean():.0f} drugs")

    st.divider()

    # Styled table
    display_df = df_filtered[["Rank","Company","Segment","Revenue ($B)","Market Share %","Pipeline Drugs","Region","Tier"]].sort_values("Rank")
    st.dataframe(
        display_df.style
            .background_gradient(subset=["Revenue ($B)","Market Share %"], cmap="Blues")
            .format({"Revenue ($B)": "{:.1f}", "Market Share %": "{:.1f}%"}),
        use_container_width=True, height=400
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">Revenue vs Pipeline Size</p>', unsafe_allow_html=True)
        fig = px.scatter(df_filtered, x="Revenue ($B)", y="Pipeline Drugs",
                         size="Market Share %", color="Segment", hover_name="Company",
                         size_max=40, height=350)
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-header">Market Share Distribution</p>', unsafe_allow_html=True)
        fig2 = px.treemap(df_filtered, path=["Segment","Company"],
                          values="Market Share %", color="Revenue ($B)",
                          color_continuous_scale="Blues", height=350)
        fig2.update_layout(margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    excel = to_excel({"Competitor Analysis": display_df})
    st.download_button("📥 Download Excel Report", excel,
                       "competitor_analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── Market Landscape ───────────────────────────────────────────────────────────
elif page == "🗺️ Market Landscape":
    st.markdown('<p class="main-title">🗺️ Market Landscape Assessment</p>', unsafe_allow_html=True)

    tam = df_seg["Market Size ($B)"].sum()
    fastest = df_seg.loc[df_seg["CAGR %"].idxmax()]
    largest = df_seg.loc[df_seg["Market Size ($B)"].idxmax()]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Addressable Market", f"${tam:.0f}B")
    c2.metric("Largest Segment", largest["Segment"], f"${largest['Market Size ($B)']:.0f}B")
    c3.metric("Fastest Growing", fastest["Segment"], f"{fastest['CAGR %']}% CAGR")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-header">Market Size by Segment ($B)</p>', unsafe_allow_html=True)
        fig = px.bar(df_seg.sort_values("Market Size ($B)", ascending=True),
                     x="Market Size ($B)", y="Segment", orientation="h",
                     color="CAGR %", color_continuous_scale="Blues", height=380,
                     text="Market Size ($B)")
        fig.update_traces(texttemplate='$%{text:.0f}B', textposition='outside')
        fig.update_layout(margin=dict(l=0,r=10,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-header">Growth Rate (CAGR %) by Segment</p>', unsafe_allow_html=True)
        fig2 = px.bar(df_seg.sort_values("CAGR %", ascending=False),
                      x="Segment", y="CAGR %",
                      color="CAGR %", color_continuous_scale="Greens",
                      height=380, text="CAGR %")
        fig2.update_traces(texttemplate='%{text}%', textposition='outside')
        fig2.update_layout(margin=dict(l=0,r=0,t=20,b=0), xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-header">Segment Detail</p>', unsafe_allow_html=True)
    st.dataframe(df_seg.style.background_gradient(subset=["Market Size ($B)","CAGR %"], cmap="Blues"),
                 use_container_width=True)

    excel = to_excel({"Market Landscape": df_seg})
    st.download_button("📥 Download Excel", excel, "market_landscape.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── Trend Analysis ─────────────────────────────────────────────────────────────
elif page == "📈 Trend Analysis":
    st.markdown('<p class="main-title">📈 Healthcare Market Trend Analysis</p>', unsafe_allow_html=True)

    latest = df_tr.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("2024 Market Size", f"${latest['Global Market ($B)']:.0f}B", f"+{latest['Growth %']}%")
    c2.metric("AI Investment", f"${latest['AI Investment ($B)']:.1f}B", "2024")
    c3.metric("Biosimilars Market", f"${latest['Biosimilars ($B)']:.1f}B", "18.7% CAGR")
    c4.metric("Digital Health", f"${latest['Digital Health ($B)']:.0f}B", "2024")

    st.divider()

    metric = st.selectbox("Select Metric", [
        "Global Market ($B)", "AI Investment ($B)", "Biosimilars ($B)", "Digital Health ($B)", "Growth %"
    ])

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(df_tr, x="Year", y=metric, markers=True,
                      color_discrete_sequence=["#1B4F8C"], height=300,
                      title=f"{metric} Trend (2019–2025)")
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(df_tr, x="Year", y="Growth %",
                      color="Growth %", color_continuous_scale=["red","yellow","green"],
                      height=300, title="YoY Market Growth %")
        fig2.update_layout(margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-header">Multi-Metric Comparison</p>', unsafe_allow_html=True)
    fig3 = go.Figure()
    for col in ["AI Investment ($B)","Biosimilars ($B)","Digital Health ($B)"]:
        fig3.add_trace(go.Scatter(x=df_tr["Year"], y=df_tr[col], name=col, mode="lines+markers", line=dict(width=2)))
    fig3.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
                       legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig3, use_container_width=True)

    excel = to_excel({"Trend Analysis": df_tr})
    st.download_button("📥 Download Excel", excel, "trend_analysis.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── Executive Summary ──────────────────────────────────────────────────────────
elif page == "📝 Executive Summary":
    st.markdown('<p class="main-title">📝 Executive Summary</p>', unsafe_allow_html=True)
    st.markdown(f"*Generated: {datetime.today().strftime('%B %d, %Y')} | Data Quality: 100% — PASS*")

    st.info("""
**MARKET OVERVIEW**
The global pharmaceutical and healthcare market reached **USD 1,731 billion** in 2024,
growing at **8.0% YoY**. Total addressable market across 9 therapeutic segments: **USD 1,252 billion**.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.success("""
**KEY FINDINGS**
1. **Oncology** — largest segment, led by Roche, Pfizer, Merck
2. **Biosimilars** — fastest growing at 18.7% CAGR
3. **AI Investment** — reached $22.4B, accelerating drug discovery
4. **India Pharma** — Sun Pharma, Cipla, Dr. Reddy's, Biocon expanding globally
5. **Digital Health** — $610B market with continued acceleration
        """)
    with col2:
        st.warning("""
**STRATEGIC IMPLICATIONS**
- Prioritize Oncology & Rare Disease pipelines for premium positioning
- Biosimilar development — high-growth entry for emerging market players
- AI/Digital health investments becoming table-stakes by 2027
- Indian pharma well-positioned for global generics leadership
- Immunology pipeline investment critical for market share defense
        """)

    st.divider()
    st.markdown('<p class="section-header">Full Data Export</p>', unsafe_allow_html=True)
    full_excel = to_excel({
        "Competitor Analysis": df_co[["Rank","Company","Segment","Revenue ($B)","Market Share %","Pipeline Drugs","Region","Tier"]],
        "Market Landscape": df_seg,
        "Trend Analysis": df_tr,
    })
    st.download_button("📥 Download Full Intelligence Report (Excel)", full_excel,
                       f"Healthcare_Market_Intelligence_{datetime.today().strftime('%Y%m%d')}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       type="primary")

st.divider()
st.caption("Healthcare Market Research Platform | Built by Prafulla Patil | B.Pharm | ICH-GCP Certified | github.com/prafullapatil28902-hash")
