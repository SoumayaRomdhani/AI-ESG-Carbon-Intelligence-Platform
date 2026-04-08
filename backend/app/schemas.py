from pydantic import BaseModel, Field
from typing import List, Optional


class CompanySummary(BaseModel):
    company_id: str
    company_name: str
    sector: str
    country: str
    esg_score: float
    latest_emissions_tco2e: float
    renewable_share_pct: float
    governance_score: float


class CompanyDetail(CompanySummary):
    employees: int
    revenue_musd: float
    climate_target_year: int
    social_score: float
    environmental_score: float
    controversies_count: int


class ForecastPoint(BaseModel):
    period: str
    value: float
    kind: str


class ForecastResponse(BaseModel):
    company_id: str
    company_name: str
    months: int
    history: List[ForecastPoint]
    forecast: List[ForecastPoint]
    mape_proxy_pct: float
    reduction_potential_pct: float
    risk_level: str
    commentary: str


class ESGEvidence(BaseModel):
    sentence: str
    label: str
    score: float


class ReportAnalysisRequest(BaseModel):
    company_id: Optional[str] = None
    report_text: str = Field(..., min_length=30)


class ReportAnalysisResponse(BaseModel):
    overall_score: float
    environment_score: float
    social_score: float
    governance_score: float
    greenwashing_risk: float
    commitments: List[str]
    measurable_kpis: List[str]
    red_flags: List[str]
    evidence: List[ESGEvidence]


class CopilotRequest(BaseModel):
    company_id: Optional[str] = None
    question: str


class CopilotResponse(BaseModel):
    answer: str
    retrieved_chunks: List[str]


class GenerateReportRequest(BaseModel):
    company_id: str
    include_analysis_text: Optional[str] = None


class GenerateReportResponse(BaseModel):
    company_id: str
    company_name: str
    title: str
    report_markdown: str


class SummaryResponse(BaseModel):
    company_count: int
    average_esg_score: float
    total_latest_emissions_tco2e: float
    high_risk_companies: int
    top_sector: str
