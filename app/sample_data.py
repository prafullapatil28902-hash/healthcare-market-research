"""
Synthetic but realistic healthcare-market sample-data generator.

The committed CSV (``data/sample_healthcare_market_dataset.csv``) is one concrete
instance of this generator's output. ``generate_sample_dataset`` lets the app
recreate a comparable dataset on demand (deterministically, via a fixed seed) so
users can experiment without supplying their own file.
"""
from __future__ import annotations

import random
from typing import List

import pandas as pd

# --------------------------------------------------------------------------- #
# Reference catalogue: real-world-inspired products grouped by therapeutic area
# --------------------------------------------------------------------------- #
# Each tuple: (company, company_type, headquarters, product, indication,
#              approval_year, patent_expiry_year, global_revenue_usd_m)
_CATALOGUE = {
    "Diabetes": [
        ("Novo Nordisk", "Pharma", "Denmark", "Ozempic", "Type 2 Diabetes", 2017, 2031, 13500),
        ("Novo Nordisk", "Pharma", "Denmark", "Rybelsus", "Type 2 Diabetes", 2019, 2031, 1800),
        ("Novo Nordisk", "Pharma", "Denmark", "Victoza", "Type 2 Diabetes", 2010, 2023, 1250),
        ("Novo Nordisk", "Pharma", "Denmark", "Tresiba", "Type 2 Diabetes", 2015, 2029, 1300),
        ("Eli Lilly", "Pharma", "USA", "Trulicity", "Type 2 Diabetes", 2014, 2027, 7000),
        ("Eli Lilly", "Pharma", "USA", "Mounjaro", "Type 2 Diabetes", 2022, 2036, 4800),
        ("Eli Lilly", "Pharma", "USA", "Humalog", "Type 1 Diabetes", 1996, 2013, 1500),
        ("Sanofi", "Pharma", "France", "Lantus", "Type 1 Diabetes", 2000, 2015, 2300),
        ("Sanofi", "Pharma", "France", "Toujeo", "Type 1 Diabetes", 2015, 2031, 600),
        ("AstraZeneca", "Pharma", "UK", "Farxiga", "Type 2 Diabetes", 2014, 2025, 4400),
        ("Boehringer Ingelheim", "Pharma", "Germany", "Jardiance", "Type 2 Diabetes", 2014, 2025, 6000),
    ],
    "Oncology": [
        ("Merck", "Pharma", "USA", "Keytruda", "Non-Small Cell Lung Cancer", 2014, 2028, 25000),
        ("Bristol Myers Squibb", "Pharma", "USA", "Opdivo", "Melanoma", 2014, 2028, 9000),
        ("Bristol Myers Squibb", "Pharma", "USA", "Revlimid", "Multiple Myeloma", 2005, 2022, 8200),
        ("Roche", "Pharma", "Switzerland", "Avastin", "Colorectal Cancer", 2004, 2019, 3500),
        ("Roche", "Pharma", "Switzerland", "Herceptin", "Breast Cancer", 1998, 2019, 2800),
        ("Roche", "Pharma", "Switzerland", "Tecentriq", "Non-Small Cell Lung Cancer", 2016, 2030, 3100),
        ("AstraZeneca", "Pharma", "UK", "Tagrisso", "Non-Small Cell Lung Cancer", 2015, 2032, 4300),
        ("AstraZeneca", "Pharma", "UK", "Lynparza", "Ovarian Cancer", 2014, 2028, 2200),
        ("AstraZeneca", "Pharma", "UK", "Imfinzi", "Non-Small Cell Lung Cancer", 2017, 2031, 3100),
        ("Pfizer", "Pharma", "USA", "Ibrance", "Breast Cancer", 2015, 2027, 4200),
        ("Novartis", "Pharma", "Switzerland", "Kisqali", "Breast Cancer", 2017, 2031, 1400),
    ],
    "Cardiovascular": [
        ("Bristol Myers Squibb", "Pharma", "USA", "Eliquis", "Anticoagulation", 2012, 2026, 18000),
        ("Bayer", "Pharma", "Germany", "Xarelto", "Anticoagulation", 2011, 2024, 6500),
        ("Novartis", "Pharma", "Switzerland", "Entresto", "Heart Failure", 2015, 2027, 6000),
        ("Amgen", "Biotech", "USA", "Repatha", "Hypercholesterolemia", 2015, 2028, 2000),
        ("Sanofi", "Pharma", "France", "Praluent", "Hypercholesterolemia", 2015, 2029, 500),
    ],
}

# Per-region market size (USD millions) and YoY growth (%) by therapeutic area.
_REGION_PROFILE = {
    "Diabetes": {
        "North America": (95000, 9.5, 0.58),
        "Europe": (48000, 7.2, 0.24),
        "Asia-Pacific": (42000, 12.4, 0.18),
    },
    "Oncology": {
        "North America": (110000, 11.8, 0.55),
        "Europe": (62000, 9.4, 0.25),
        "Asia-Pacific": (55000, 14.2, 0.20),
    },
    "Cardiovascular": {
        "North America": (60000, 6.4, 0.55),
        "Europe": (38000, 5.1, 0.27),
        "Asia-Pacific": (40000, 8.9, 0.18),
    },
}


def generate_sample_dataset(seed: int = 42) -> pd.DataFrame:
    """Return a realistic healthcare-market DataFrame.

    Global product revenue is split across regions using each region's share of
    the therapeutic-area market, with a small deterministic jitter so the data
    looks organic rather than perfectly proportional.
    """
    rng = random.Random(seed)
    rows: List[dict] = []

    for area, products in _CATALOGUE.items():
        region_profile = _REGION_PROFILE[area]
        for (company, ctype, hq, product, indication,
             approval, patent, global_rev) in products:
            for region, (mkt_size, growth, share) in region_profile.items():
                jitter = 1 + rng.uniform(-0.12, 0.12)
                revenue = round(global_rev * share * jitter)
                if revenue <= 0:
                    continue
                rows.append(
                    {
                        "company": company,
                        "company_type": ctype,
                        "headquarters": hq,
                        "product": product,
                        "therapeutic_area": area,
                        "indication": indication,
                        "phase": "Marketed",
                        "approval_year": approval,
                        "patent_expiry_year": patent,
                        "region": region,
                        "revenue_usd_m": revenue,
                        "market_size_usd_m": mkt_size,
                        "growth_rate_pct": growth,
                    }
                )

    return pd.DataFrame(rows)


if __name__ == "__main__":  # pragma: no cover - manual regeneration helper
    from app.config import SAMPLE_DATASET_PATH

    df = generate_sample_dataset()
    df.to_csv(SAMPLE_DATASET_PATH, index=False)
    print(f"Wrote {len(df)} rows to {SAMPLE_DATASET_PATH}")
