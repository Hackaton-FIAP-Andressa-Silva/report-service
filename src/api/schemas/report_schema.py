from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ComponentSchema(BaseModel):
    name: str
    type: str
    description: str
    technology: str


class RiskSchema(BaseModel):
    title: str
    severity: str
    description: str
    impact: str
    affected_components: List[str] = []


class RecommendationSchema(BaseModel):
    title: str
    priority: str
    description: str
    rationale: str


class CreateReportRequest(BaseModel):
    upload_id: str
    summary: str
    components: List[ComponentSchema]
    risks: List[RiskSchema]
    recommendations: List[RecommendationSchema]
    ai_model: str = "gpt-4o"
    processing_time_seconds: float = 0.0


class ReportResponse(BaseModel):
    report_id: str
    upload_id: str
    summary: str
    components: List[ComponentSchema]
    risks: List[RiskSchema]
    recommendations: List[RecommendationSchema]
    ai_model: str
    processing_time_seconds: float
    created_at: datetime
