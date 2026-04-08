from __future__ import annotations

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from sqlalchemy.orm import Session

from .config import APP_NAME, PROCESSED_DIR
from .db import Base, engine, get_db
from .models import GeneratedReport
from .schemas import (
    CompanySummary, CompanyDetail, ForecastResponse, ReportAnalysisRequest, ReportAnalysisResponse,
    CopilotRequest, CopilotResponse, GenerateReportRequest, GenerateReportResponse, SummaryResponse
)
from .services.analyzer import analyze_text
from .services.forecasting import forecast_company
from .services.rag import get_engine
from .services.reporting import generate_report

Base.metadata.create_all(bind=engine)
app = FastAPI(title=APP_NAME, version="1.0.0", description="CarbonLens — ESG & Carbon Intelligence Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

COMPANIES_PATH = PROCESSED_DIR / "company_profiles.csv"

def _load_companies():
    if not COMPANIES_PATH.exists():
        raise FileNotFoundError("Run scripts/generate_sample_data.py first.")
    return pd.read_csv(COMPANIES_PATH)

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME}

@app.get("/summary", response_model=SummaryResponse)
def summary():
    df = _load_companies()
    return {
        "company_count": int(len(df)),
        "average_esg_score": round(float(df["esg_score"].mean()), 1),
        "total_latest_emissions_tco2e": round(float(df["latest_emissions_tco2e"].sum()), 1),
        "high_risk_companies": int((df["controversies_count"] >= 3).sum()),
        "top_sector": str(df["sector"].mode().iloc[0]),
    }

@app.get("/companies", response_model=list[CompanySummary])
def companies():
    df = _load_companies()
    cols = ["company_id", "company_name", "sector", "country", "esg_score", "latest_emissions_tco2e", "renewable_share_pct", "governance_score"]
    return df[cols].to_dict(orient="records")

@app.get("/companies/{company_id}", response_model=CompanyDetail)
def company_detail(company_id: str):
    df = _load_companies()
    row = df.loc[df["company_id"] == company_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Company not found")
    return row.iloc[0].to_dict()

@app.get("/forecast/{company_id}", response_model=ForecastResponse)
def forecast(company_id: str, months: int = 12):
    try:
        return forecast_company(company_id, months)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.post("/analyze-report", response_model=ReportAnalysisResponse)
def analyze_report(payload: ReportAnalysisRequest):
    try:
        return analyze_text(payload.report_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/analyze-upload", response_model=ReportAnalysisResponse)
async def analyze_upload(file: UploadFile = File(...), company_id: str | None = Form(default=None)):
    content = await file.read()
    name = (file.filename or "").lower()
    try:
        if name.endswith(".pdf"):
            from io import BytesIO
            reader = PdfReader(BytesIO(content))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = content.decode("utf-8", errors="ignore")
        return analyze_text(text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not analyze file: {exc}")

@app.post("/copilot/ask", response_model=CopilotResponse)
def copilot(payload: CopilotRequest):
    return get_engine().answer(payload.question, payload.company_id)

@app.post("/generate-report", response_model=GenerateReportResponse)
def gen_report(payload: GenerateReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_report(payload.company_id, payload.include_analysis_text)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    analysis = None
    if payload.include_analysis_text and len(payload.include_analysis_text.strip()) > 30:
        analysis = analyze_text(payload.include_analysis_text)

    row = GeneratedReport(
        company_id=result["company_id"],
        title=result["title"],
        overall_score=analysis["overall_score"] if analysis else None,
        greenwashing_risk=analysis["greenwashing_risk"] if analysis else None,
        report_markdown=result["report_markdown"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return result
