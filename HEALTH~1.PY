"""
Healthcare Market Research Report Generator
============================================
A healthcare market intelligence platform that transforms healthcare market
datasets into competitor analysis reports, market landscape assessments,
trend analysis, executive summaries, and actionable business insights.

Features:
  - Competitor Analysis
  - Market Landscape Assessment
  - Trend Analysis
  - Data Validation & Quality Checks
  - Executive Summary Generation
  - Excel and PDF Reporting
  - Healthcare Industry Insights

Technologies: Python, Streamlit, SQLite, Pandas, Plotly, OpenPyXL

Author : Prafulla Patil
GitHub : https://github.com/prafullapatil28902-hash/healthcare-market-research-tool
"""

import json
import csv
import sqlite3
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    XLSX = True
except ImportError:
    XLSX = False

# ── Sample Healthcare Market Data ─────────────────────────────────────────────
SAMPLE_COMPANIES = [
    {"company": "Pfizer",        "segment": "Oncology",        "revenue_bn": 58.5, "market_share_pct": 8.2,  "pipeline_drugs": 89,  "region": "Global",       "year": 2024},
    {"company": "Roche",         "segment": "Oncology",        "revenue_bn": 49.8, "market_share_pct": 7.0,  "pipeline_drugs": 76,  "region": "Global",       "year": 2024},
    {"company": "Johnson & J",   "segment": "Immunology",      "revenue_bn": 85.2, "market_share_pct": 11.9, "pipeline_drugs": 113, "region": "Global",       "year": 2024},
    {"company": "Novartis",      "segment": "Cardiovascular",  "revenue_bn": 45.4, "market_share_pct": 6.4,  "pipeline_drugs": 95,  "region": "Global",       "year": 2024},
    {"company": "AstraZeneca",   "segment": "Respiratory",     "revenue_bn": 45.8, "market_share_pct": 6.4,  "pipeline_drugs": 182, "region": "Global",       "year": 2024},
    {"company": "Sanofi",        "segment": "Rare Disease",    "revenue_bn": 43.1, "market_share_pct": 6.0,  "pipeline_drugs": 78,  "region": "Europe",       "year": 2024},
    {"company": "Merck",         "segment": "Oncology",        "revenue_bn": 60.1, "market_share_pct": 8.4,  "pipeline_drugs": 92,  "region": "Global",       "year": 2024},
    {"company": "AbbVie",        "segment": "Immunology",      "revenue_bn": 56.3, "market_share_pct": 7.9,  "pipeline_drugs": 67,  "region": "Global",       "year": 2024},
    {"company": "Bristol-Myers", "segment": "Oncology",        "revenue_bn": 47.2, "market_share_pct": 6.6,  "pipeline_drugs": 84,  "region": "Global",       "year": 2024},
    {"company": "Eli Lilly",     "segment": "Diabetes",        "revenue_bn": 34.1, "market_share_pct": 4.8,  "pipeline_drugs": 52,  "region": "Global",       "year": 2024},
    {"company": "Sun Pharma",    "segment": "Generics",        "revenue_bn": 5.1,  "market_share_pct": 0.7,  "pipeline_drugs": 45,  "region": "India/Global", "year": 2024},
    {"company": "Cipla",         "segment": "Respiratory",     "revenue_bn": 2.7,  "market_share_pct": 0.4,  "pipeline_drugs": 38,  "region": "India",        "year": 2024},
    {"company": "Dr. Reddy's",   "segment": "Generics",        "revenue_bn": 3.0,  "market_share_pct": 0.4,  "pipeline_drugs": 29,  "region": "India/Global", "year": 2024},
    {"company": "Biocon",        "segment": "Biosimilars",     "revenue_bn": 1.3,  "market_share_pct": 0.2,  "pipeline_drugs": 22,  "region": "India",        "year": 2024},
]

MARKET_TRENDS = [
    {"year": 2019, "global_market_bn": 1285, "growth_pct": 4.8,  "ai_investment_bn": 2.1,  "biosimilars_bn": 6.3,  "digital_health_bn": 175},
    {"year": 2020, "global_market_bn": 1274, "growth_pct": -0.9, "ai_investment_bn": 3.8,  "biosimilars_bn": 8.4,  "digital_health_bn": 248},
    {"year": 2021, "global_market_bn": 1419, "growth_pct": 11.4, "ai_investment_bn": 6.7,  "biosimilars_bn": 11.2, "digital_health_bn": 350},
    {"year": 2022, "global_market_bn": 1482, "growth_pct": 4.4,  "ai_investment_bn": 10.2, "biosimilars_bn": 14.8, "digital_health_bn": 426},
    {"year": 2023, "global_market_bn": 1603, "growth_pct": 8.2,  "ai_investment_bn": 15.9, "biosimilars_bn": 19.6, "digital_health_bn": 512},
    {"year": 2024, "global_market_bn": 1731, "growth_pct": 8.0,  "ai_investment_bn": 22.4, "biosimilars_bn": 26.1, "digital_health_bn": 610},
    {"year": 2025, "global_market_bn": 1870, "growth_pct": 8.0,  "ai_investment_bn": 31.0, "biosimilars_bn": 33.8, "digital_health_bn": 728},
]

THERAPEUTIC_SEGMENTS = [
    {"segment": "Oncology",       "market_size_bn": 248, "cagr_pct": 12.1, "key_players": "Roche, Pfizer, Merck, BMS"},
    {"segment": "Immunology",     "market_size_bn": 156, "cagr_pct": 9.4,  "key_players": "J&J, AbbVie, Novartis"},
    {"segment": "Cardiovascular", "market_size_bn": 108, "cagr_pct": 5.2,  "key_players": "Novartis, Pfizer, Bayer"},
    {"segment": "Neurology",      "market_size_bn": 94,  "cagr_pct": 7.8,  "key_players": "Biogen, Roche, Sanofi"},
    {"segment": "Diabetes",       "market_size_bn": 81,  "cagr_pct": 8.5,  "key_players": "Novo Nordisk, Eli Lilly, Sanofi"},
    {"segment": "Respiratory",    "market_size_bn": 61,  "cagr_pct": 6.3,  "key_players": "AstraZeneca, Boehringer, Novartis"},
    {"segment": "Rare Disease",   "market_size_bn": 48,  "cagr_pct": 14.2, "key_players": "Sanofi, Takeda, Alexion"},
    {"segment": "Biosimilars",    "market_size_bn": 34,  "cagr_pct": 18.7, "key_players": "Biocon, Teva, Sandoz"},
    {"segment": "Generics",       "market_size_bn": 422, "cagr_pct": 4.1,  "key_players": "Teva, Sun Pharma, Cipla"},
]

def init_db(db_path="healthcare_market.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT, segment TEXT,
        revenue_bn REAL, market_share_pct REAL, pipeline_drugs INTEGER, region TEXT, year INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS trends (
        year INTEGER PRIMARY KEY, global_market_bn REAL, growth_pct REAL,
        ai_investment_bn REAL, biosimilars_bn REAL, digital_health_bn REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS segments (
        segment TEXT PRIMARY KEY, market_size_bn REAL, cagr_pct REAL, key_players TEXT)""")
    conn.commit()
    if not c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]:
        c.executemany("INSERT INTO companies (company,segment,revenue_bn,market_share_pct,pipeline_drugs,region,year) VALUES (:company,:segment,:revenue_bn,:market_share_pct,:pipeline_drugs,:region,:year)", SAMPLE_COMPANIES)
    if not c.execute("SELECT COUNT(*) FROM trends").fetchone()[0]:
        c.executemany("INSERT OR IGNORE INTO trends VALUES (:year,:global_market_bn,:growth_pct,:ai_investment_bn,:biosimilars_bn,:digital_health_bn)", MARKET_TRENDS)
    if not c.execute("SELECT COUNT(*) FROM segments").fetchone()[0]:
        c.executemany("INSERT OR IGNORE INTO segments VALUES (:segment,:market_size_bn,:cagr_pct,:key_players)", THERAPEUTIC_SEGMENTS)
    conn.commit()
    return conn

def validate_data(conn):
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    nulls = c.execute("SELECT COUNT(*) FROM companies WHERE company IS NULL OR revenue_bn IS NULL").fetchone()[0]
    neg   = c.execute("SELECT COUNT(*) FROM companies WHERE revenue_bn < 0").fetchone()[0]
    score = max(100 - int((nulls + neg) / max(total, 1) * 100), 0)
    return {"total_records": total, "null_fields": nulls, "negative_values": neg,
            "quality_score": f"{score}%", "status": "PASS" if score >= 90 else "REVIEW REQUIRED"}

def competitor_analysis(conn, segment=None):
    c = conn.cursor()
    rows = c.execute("SELECT * FROM companies WHERE segment=? ORDER BY revenue_bn DESC" if segment
                     else "SELECT * FROM companies ORDER BY revenue_bn DESC",
                     (segment,) if segment else ()).fetchall()
    cols = ["id","company","segment","revenue_bn","market_share_pct","pipeline_drugs","region","year"]
    companies = [dict(zip(cols, r)) for r in rows]
    for i, co in enumerate(companies):
        co["rank"] = i + 1
        co["tier"] = ("Tier 1 (Leader)" if co["market_share_pct"] >= 7 else
                      "Tier 2 (Challenger)" if co["market_share_pct"] >= 3 else "Tier 3 (Niche/Regional)")
    return companies

def market_landscape(conn):
    c = conn.cursor()
    rows = c.execute("SELECT * FROM segments ORDER BY market_size_bn DESC").fetchall()
    cols = ["segment","market_size_bn","cagr_pct","key_players"]
    segs = [dict(zip(cols, r)) for r in rows]
    total = sum(s["market_size_bn"] for s in segs)
    for s in segs: s["share_pct"] = round(s["market_size_bn"] / total * 100, 1)
    return {"total_addressable_market_bn": total,
            "fastest_growing": max(segs, key=lambda x: x["cagr_pct"])["segment"],
            "largest_segment": segs[0]["segment"], "segments": segs}

def trend_analysis(conn):
    c = conn.cursor()
    rows = c.execute("SELECT * FROM trends ORDER BY year").fetchall()
    cols = ["year","global_market_bn","growth_pct","ai_investment_bn","biosimilars_bn","digital_health_bn"]
    trends = [dict(zip(cols, r)) for r in rows]
    latest = trends[-1]
    return {"current_market_size_bn": latest["global_market_bn"],
            "yoy_growth_pct": latest["growth_pct"],
            "ai_investment_growth_bn": latest["ai_investment_bn"],
            "biosimilar_market_bn": latest["biosimilars_bn"],
            "digital_health_bn": latest["digital_health_bn"],
            "key_trend": "AI-driven drug discovery + biosimilar expansion driving market growth",
            "data": trends}

def generate_executive_summary(landscape, trends, validation):
    today = datetime.today().strftime("%B %Y")
    return f"""EXECUTIVE SUMMARY — Global Healthcare Market Intelligence Report
Generated: {today} | Data Quality: {validation['quality_score']} ({validation['status']})

MARKET OVERVIEW
The global pharmaceutical and healthcare market reached USD {trends['current_market_size_bn']:.0f}B in 2024,
growing at {trends['yoy_growth_pct']:.1f}% YoY. Total addressable market: USD {landscape['total_addressable_market_bn']:.0f}B.

KEY FINDINGS
1. {landscape['largest_segment']} is the largest segment driven by major global players.
2. {landscape['fastest_growing']} is the fastest-growing segment (highest CAGR).
3. AI investment in healthcare reached USD {trends['ai_investment_growth_bn']:.1f}B — accelerating drug discovery.
4. Biosimilars market at USD {trends['biosimilar_market_bn']:.1f}B growing at 18.7% CAGR.
5. Indian pharma (Sun Pharma, Cipla, Dr. Reddy's, Biocon) expanding in generics/biosimilars globally.

STRATEGIC IMPLICATIONS
- Prioritize oncology and rare disease pipelines for premium positioning
- Biosimilar development offers high-growth entry points for emerging market players
- AI and digital health investments are becoming table-stakes for competitiveness
- Indian pharma firms are well-positioned for global generics market leadership

Analysis based on {validation['total_records']} company records. Data quality: {validation['quality_score']}."""

def export_excel(companies, landscape, trends, validation, out_path):
    if not XLSX: print("pip install openpyxl"); return
    wb = openpyxl.Workbook()
    NAVY = "1B4F8C"
    hfont = Font(bold=True, color="FFFFFF", size=10)
    hfill = PatternFill("solid", fgColor=NAVY)

    ws1 = wb.active; ws1.title = "Executive Summary"
    ws1["A1"] = "HEALTHCARE MARKET INTELLIGENCE — EXECUTIVE SUMMARY"
    ws1["A1"].font = Font(bold=True, size=13, color=NAVY)
    ws1["A2"] = generate_executive_summary(landscape, trends, validation)
    ws1["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws1.column_dimensions["A"].width = 90; ws1.row_dimensions[2].height = 250

    ws2 = wb.create_sheet("Competitor Analysis")
    ws2.append(["Rank","Company","Segment","Revenue ($B)","Market Share %","Pipeline","Region","Year","Tier"])
    for cell in ws2[1]: cell.font = hfont; cell.fill = hfill
    for co in companies:
        ws2.append([co["rank"],co["company"],co["segment"],co["revenue_bn"],
                    co["market_share_pct"],co["pipeline_drugs"],co["region"],co["year"],co["tier"]])
    for col in ws2.columns:
        ws2.column_dimensions[col[0].column_letter].width = min(max(len(str(c.value or "")) for c in col)+3,28)

    ws3 = wb.create_sheet("Market Landscape")
    ws3.append(["Segment","Market Size ($B)","CAGR %","Market Share %","Key Players"])
    for cell in ws3[1]: cell.font = hfont; cell.fill = hfill
    for s in landscape["segments"]:
        ws3.append([s["segment"],s["market_size_bn"],s["cagr_pct"],s["share_pct"],s["key_players"]])
    for col in ws3.columns: ws3.column_dimensions[col[0].column_letter].width = 22

    ws4 = wb.create_sheet("Trend Analysis")
    ws4.append(["Year","Global Market ($B)","Growth %","AI Investment ($B)","Biosimilars ($B)","Digital Health ($B)"])
    for cell in ws4[1]: cell.font = hfont; cell.fill = hfill
    for t in trends["data"]:
        ws4.append([t["year"],t["global_market_bn"],t["growth_pct"],
                    t["ai_investment_bn"],t["biosimilars_bn"],t["digital_health_bn"]])
    for col in ws4.columns: ws4.column_dimensions[col[0].column_letter].width = 20

    ws5 = wb.create_sheet("Data Quality")
    ws5.append(["Metric","Value"])
    for cell in ws5[1]: cell.font = hfont; cell.fill = hfill
    for k,v in validation.items(): ws5.append([k.replace("_"," ").title(), str(v)])
    ws5.column_dimensions["A"].width = 24; ws5.column_dimensions["B"].width = 16

    wb.save(out_path)
    print(f"Excel report saved: {out_path}")

def export_csv(companies, out_path):
    fields = ["rank","company","segment","revenue_bn","market_share_pct","pipeline_drugs","region","year","tier"]
    with open(out_path,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(companies)
    print(f"CSV saved: {out_path}")

def main():
    parser = argparse.ArgumentParser(
        prog="healthcare-market-research",
        description="Healthcare Market Research Report Generator",
        epilog="Examples:\n  python healthcare_market_research.py --report all\n  python healthcare_market_research.py --report competitor --segment Oncology\n  python healthcare_market_research.py --report all --export report.xlsx"
    )
    parser.add_argument("--report",  "-r", choices=["competitor","landscape","trend","summary","all"], default="all")
    parser.add_argument("--segment", "-s", help="Filter by segment (e.g. Oncology)")
    parser.add_argument("--export",  "-e", help="Export to .xlsx or .csv")
    parser.add_argument("--db",      "-d", default="healthcare_market.db")
    args = parser.parse_args()

    print("\nHealthcare Market Research Report Generator")
    conn = init_db(args.db)
    validation = validate_data(conn)
    companies  = competitor_analysis(conn, args.segment)
    landscape  = market_landscape(conn)
    trends     = trend_analysis(conn)

    print(f"Data Quality: {validation['quality_score']} | Records: {validation['total_records']}")

    if args.report in ("competitor","all"):
        print("\nCOMPETITOR ANALYSIS")
        print(f"{'#':<4}{'Company':<16}{'Segment':<16}{'Revenue($B)':<13}{'Share%':<8}{'Pipeline':<10}{'Tier'}")
        for co in companies[:10]:
            print(f"{co['rank']:<4}{co['company']:<16}{co['segment']:<16}{co['revenue_bn']:<13.1f}{co['market_share_pct']:<8.1f}{co['pipeline_drugs']:<10}{co['tier']}")

    if args.report in ("landscape","all"):
        print(f"\nMARKET LANDSCAPE | TAM: USD {landscape['total_addressable_market_bn']:.0f}B | Fastest Growing: {landscape['fastest_growing']}")
        for s in landscape["segments"]:
            print(f"  {s['segment']:<18} ${s['market_size_bn']:.0f}B  CAGR:{s['cagr_pct']}%  Share:{s['share_pct']}%")

    if args.report in ("trend","all"):
        print(f"\nTREND ANALYSIS | Market: ${trends['current_market_size_bn']:.0f}B | Growth: {trends['yoy_growth_pct']}% | AI: ${trends['ai_investment_growth_bn']:.1f}B")
        for t in trends["data"]:
            print(f"  {t['year']}  Market:${t['global_market_bn']:.0f}B  Growth:{t['growth_pct']}%  AI:${t['ai_investment_bn']:.1f}B")

    if args.report in ("summary","all"):
        print("\n" + generate_executive_summary(landscape, trends, validation))

    if args.export:
        ext = Path(args.export).suffix.lower()
        if ext == ".xlsx": export_excel(companies, landscape, trends, validation, args.export)
        elif ext == ".csv": export_csv(companies, args.export)

    conn.close()

if __name__ == "__main__":
    main()
