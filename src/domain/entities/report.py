from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class ReportComponent:
    name: str
    type: str
    description: str
    technology: str


@dataclass
class ReportRisk:
    title: str
    severity: str
    description: str
    impact: str
    affected_components: List[str] = field(default_factory=list)


@dataclass
class ReportRecommendation:
    title: str
    priority: str
    description: str
    rationale: str


@dataclass
class Report:
    id: str
    upload_id: str
    summary: str
    components: List[ReportComponent]
    risks: List[ReportRisk]
    recommendations: List[ReportRecommendation]
    ai_model: str
    processing_time_seconds: float
    created_at: datetime

    @classmethod
    def create(
        cls,
        upload_id: str,
        summary: str,
        components: List[ReportComponent],
        risks: List[ReportRisk],
        recommendations: List[ReportRecommendation],
        ai_model: str,
        processing_time_seconds: float,
    ) -> "Report":
        return cls(
            id=str(uuid.uuid4()),
            upload_id=upload_id,
            summary=summary,
            components=components,
            risks=risks,
            recommendations=recommendations,
            ai_model=ai_model,
            processing_time_seconds=processing_time_seconds,
            created_at=datetime.utcnow(),
        )
