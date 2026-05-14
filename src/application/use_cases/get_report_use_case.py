import logging

from src.domain.entities.report import Report
from src.domain.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


class ReportNotFoundError(Exception):
    pass


class GetReportUseCase:
    def __init__(self, report_repository: ReportRepository) -> None:
        self._repository = report_repository

    async def execute(self, upload_id: str) -> Report:
        report = await self._repository.find_by_upload_id(upload_id)

        if report is None:
            raise ReportNotFoundError(f"No report found for upload_id '{upload_id}'")

        logger.info("Report retrieved", extra={"upload_id": upload_id, "report_id": report.id})
        return report
