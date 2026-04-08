from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
KNOWLEDGE_DIR = DATA_DIR / "knowledge_base"

for d in [RAW_DIR, PROCESSED_DIR, KNOWLEDGE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def build_company_profiles():
    companies = [
        ("cmp_001", "Nordic Steel Manufacturing", "Manufacturing", "Sweden", 4200, 980.0, 12500, 28, 62, 71, 74, 2030, 2),
        ("cmp_002", "BlueGrid Logistics", "Transport", "Germany", 2600, 620.0, 8900, 18, 56, 68, 70, 2035, 3),
        ("cmp_003", "HelioFoods", "Consumer Goods", "France", 3100, 540.0, 6100, 41, 75, 73, 76, 2030, 1),
        ("cmp_004", "TerraBuild Cement", "Construction Materials", "Spain", 1900, 450.0, 10200, 12, 48, 60, 64, 2040, 4),
        ("cmp_005", "AquaPharm Labs", "Healthcare", "Netherlands", 1600, 710.0, 4500, 53, 79, 77, 81, 2030, 1),
        ("cmp_006", "CloudMesh Data Centers", "Technology", "Ireland", 1200, 860.0, 7600, 34, 67, 72, 78, 2032, 2),
        ("cmp_007", "Orbit Textile Group", "Textiles", "Portugal", 5200, 390.0, 6800, 22, 54, 65, 61, 2038, 3),
        ("cmp_008", "VoltWave Energy Systems", "Energy", "Denmark", 1450, 1190.0, 14100, 61, 81, 69, 83, 2029, 1),
    ]
    df = pd.DataFrame(companies, columns=[
        "company_id", "company_name", "sector", "country", "employees", "revenue_musd",
        "energy_consumption_mwh", "renewable_share_pct", "environmental_score",
        "social_score", "governance_score", "climate_target_year", "controversies_count",
    ])
    df["esg_score"] = (0.45 * df["environmental_score"] + 0.25 * df["social_score"] + 0.30 * df["governance_score"]).round(1)
    return df

def build_monthly_emissions(companies):
    dates = pd.date_range("2023-01-01", "2025-12-01", freq="MS")
    rng = np.random.default_rng(42)
    sector_base = {
        "Manufacturing": 820, "Transport": 690, "Consumer Goods": 450, "Construction Materials": 920,
        "Healthcare": 310, "Technology": 520, "Textiles": 610, "Energy": 1040,
    }
    rows = []
    latest = []
    for _, row in companies.iterrows():
        baseline = sector_base[row["sector"]]
        renewable_factor = 1 - row["renewable_share_pct"] / 180
        governance_factor = 1 + (75 - row["governance_score"]) / 300
        controversy_factor = 1 + row["controversies_count"] * 0.03
        vals = []
        for i, date in enumerate(dates):
            season = 1 + 0.06 * np.sin(i / 2.5)
            trend = 1 - (row["environmental_score"] - 55) * 0.0015 * (i / len(dates))
            noise = rng.normal(0, 18)
            emissions = baseline * renewable_factor * governance_factor * controversy_factor * season * trend + noise
            emissions = max(emissions, 90)
            vals.append(round(float(emissions), 2))
            rows.append({"company_id": row["company_id"], "date": date, "emissions_tco2e": round(float(emissions), 2)})
        latest.append(vals[-1])
    companies["latest_emissions_tco2e"] = latest
    return pd.DataFrame(rows), companies

def write_kb():
    docs = {
        "esg_reporting_notes.md": """# ESG Reporting Notes

Strong sustainability reporting usually includes:
- quantified KPIs
- baseline years
- target years
- clear scope boundaries
- governance ownership
- evidence of progress, not only ambition

Weak reporting usually contains:
- vague phrases like 'we aim' without metrics
- carbon neutrality claims without scope definitions
- no board or audit oversight
- no time-bound decarbonization roadmap
""",
        "greenwashing_patterns.md": """# Greenwashing Patterns

Possible greenwashing indicators:
- broad climate claims without baseline data
- repeated sustainability branding with no measurable evidence
- no clear target pathway
- lack of governance ownership

Counter-signals:
- disclosed baselines
- year-over-year trend data
- board accountability
- quantified emissions reductions
""",
        "esrs_summary.md": """# ESRS-style Summary

A strong workflow covers:
- environmental topics: emissions, energy, water, waste
- social topics: employee safety, diversity, training
- governance topics: oversight, ethics, controls, anti-corruption

AI can support document parsing, KPI extraction, risk scoring, and memo generation.
Human validation is still necessary.
""",
    }
    for name, content in docs.items():
        (KNOWLEDGE_DIR / name).write_text(content.strip() + "\n", encoding="utf-8")

if __name__ == "__main__":
    companies = build_company_profiles()
    emissions, companies = build_monthly_emissions(companies)
    companies.to_csv(PROCESSED_DIR / "company_profiles.csv", index=False)
    emissions.to_csv(PROCESSED_DIR / "company_monthly_emissions.csv", index=False)
    write_kb()
    print("Sample data generated.")
