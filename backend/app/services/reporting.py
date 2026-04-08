from __future__ import annotations

import pandas as pd
from jinja2 import Template

from ..config import PROCESSED_DIR, REPORTS_DIR
from .analyzer import analyze_text
from .forecasting import forecast_company

COMPANIES_PATH = PROCESSED_DIR / "company_profiles.csv"

TEMPLATE = Template("""
# {{ title }}

## Executive Summary
{{ company_name }} is a {{ sector }} company operating in {{ country }}. The current ESG profile indicates an overall score of **{{ esg_score }}/100**.

## Emissions Overview
- Latest estimated emissions: **{{ latest_emissions_tco2e }} tCO2e/month**
- Forecast average over next 12 months: **{{ forecast_avg }} tCO2e/month**
- Reduction potential: **{{ reduction_potential_pct }}%**
- Risk level: **{{ risk_level|upper }}**

## ESG Signal Analysis
- Environment score: **{{ env_score }}**
- Social score: **{{ soc_score }}**
- Governance score: **{{ gov_score }}**
- Greenwashing risk: **{{ greenwashing_risk }}**

## Key Commitments
{% for item in commitments %}
- {{ item }}
{% endfor %}

## Material Risks
{% if red_flags %}
{% for item in red_flags %}
- {{ item }}
{% endfor %}
{% else %}
- No major red flags detected in the supplied text excerpt.
{% endif %}

## Recommended Actions
1. Increase measurable climate KPIs.
2. Publish annual progress against targets.
3. Improve board-level ESG oversight.
4. Extend supplier and Scope 3 tracking.
5. Reduce vague narrative language in reports.

## Reporting Readiness
This is a product-style AI memo, not a legal compliance opinion.
""")


def generate_report(company_id: str, analysis_text: str | None = None):
    companies = pd.read_csv(COMPANIES_PATH)
    row = companies.loc[companies["company_id"] == company_id]
    if row.empty:
        raise ValueError("Unknown company_id")

    company = row.iloc[0].to_dict()
    forecast = forecast_company(company_id, months=12)
    forecast_avg = round(sum(x["value"] for x in forecast["forecast"]) / len(forecast["forecast"]), 2)

    if analysis_text and len(analysis_text.strip()) > 40:
        analysis = analyze_text(analysis_text)
    else:
        default_text = (
            f"{company['company_name']} commits to reduce emissions by 30% by {company['climate_target_year']}. "
            f"The board reviews sustainability performance quarterly. "
            f"Renewable electricity share reached {company['renewable_share_pct']}%."
        )
        analysis = analyze_text(default_text)

    title = f"{company['company_name']} — AI ESG Intelligence Memo"
    markdown = TEMPLATE.render(
        title=title,
        company_name=company["company_name"],
        sector=company["sector"],
        country=company["country"],
        esg_score=company["esg_score"],
        latest_emissions_tco2e=company["latest_emissions_tco2e"],
        forecast_avg=forecast_avg,
        reduction_potential_pct=forecast["reduction_potential_pct"],
        risk_level=forecast["risk_level"],
        env_score=analysis["environment_score"],
        soc_score=analysis["social_score"],
        gov_score=analysis["governance_score"],
        greenwashing_risk=analysis["greenwashing_risk"],
        commitments=analysis["commitments"][:5],
        red_flags=analysis["red_flags"][:5],
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / f"{company_id}_report.md").write_text(markdown, encoding="utf-8")
    return {"company_id": company_id, "company_name": company["company_name"], "title": title, "report_markdown": markdown}
