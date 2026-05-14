import logging
from dataclasses import asdict
from typing import List

from src.domain.entities.report import Report, ReportComponent, ReportRisk, ReportRecommendation
from src.domain.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


class CreateReportUseCase:
    def __init__(self, report_repository: ReportRepository) -> None:
        self._repository = report_repository

    async def execute(
        self,
        upload_id: str,
        summary: str,
        components: List[dict],
        risks: List[dict],
        recommendations: List[dict],
        ai_model: str,
        processing_time_seconds: float,
    ) -> Report:
        # Idempotency: return existing if already exists
        existing = await self._repository.find_by_upload_id(upload_id)
        if existing is not None:
            logger.info("Report already exists (idempotent)", extra={"upload_id": upload_id})
            return existing

        report = Report.create(
            upload_id=upload_id,
            summary=summary,
            components=[ReportComponent(**c) for c in components],
            risks=[ReportRisk(**r) for r in risks],
            recommendations=[ReportRecommendation(**rec) for rec in recommendations],
            ai_model=ai_model,
            processing_time_seconds=processing_time_seconds,
        )

        saved = await self._repository.save(report)
        logger.info("Report created", extra={"upload_id": upload_id, "report_id": saved.id})
        return saved
