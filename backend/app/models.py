from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text

from .db import Base


class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    overall_score = Column(Float, nullable=True)
    greenwashing_risk = Column(Float, nullable=True)
    report_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
