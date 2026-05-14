from dataclasses import asdict
from typing import Optional

from src.domain.entities.report import (
    Report,
    ReportComponent,
    ReportRisk,
    ReportRecommendation,
)
from src.domain.repositories.report_repository import ReportRepository
from src.infrastructure.database.mongodb_connection import get_database

COLLECTION_NAME = "reports"


class MongoDBReportRepository(ReportRepository):
    def __init__(self) -> None:
        self._db = get_database()

    async def save(self, report: Report) -> Report:
        doc = self._to_document(report)
        collection = self._db[COLLECTION_NAME]

        await collection.create_index("upload_id", unique=True, background=True)
        await collection.insert_one(doc)
        return report

    async def find_by_upload_id(self, upload_id: str) -> Optional[Report]:
        collection = self._db[COLLECTION_NAME]
        doc = await collection.find_one({"upload_id": upload_id})
        if doc is None:
            return None
        return self._to_entity(doc)

    @staticmethod
    def _to_document(report: Report) -> dict:
        return {
            "_id": report.id,
            "upload_id": report.upload_id,
            "summary": report.summary,
            "components": [asdict(c) for c in report.components],
            "risks": [asdict(r) for r in report.risks],
            "recommendations": [asdict(rec) for rec in report.recommendations],
            "ai_model": report.ai_model,
            "processing_time_seconds": report.processing_time_seconds,
            "created_at": report.created_at,
        }

    @staticmethod
    def _to_entity(doc: dict) -> Report:
        return Report(
            id=doc["_id"],
            upload_id=doc["upload_id"],
            summary=doc["summary"],
            components=[ReportComponent(**c) for c in doc.get("components", [])],
            risks=[ReportRisk(**r) for r in doc.get("risks", [])],
            recommendations=[ReportRecommendation(**rec) for rec in doc.get("recommendations", [])],
            ai_model=doc.get("ai_model", "unknown"),
            processing_time_seconds=doc.get("processing_time_seconds", 0.0),
            created_at=doc["created_at"],
        )
