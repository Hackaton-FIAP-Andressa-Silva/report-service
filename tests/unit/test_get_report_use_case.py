import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from src.application.use_cases.get_report_use_case import GetReportUseCase, ReportNotFoundError
from src.domain.entities.report import Report, ReportComponent, ReportRisk, ReportRecommendation


@pytest.fixture
def sample_report():
    return Report(
        id="report-id-1",
        upload_id="upload-id-abc",
        summary="Microservices architecture",
        components=[ReportComponent("API GW", "Gateway", "Entry point", "Kong")],
        risks=[ReportRisk("SPOF", "HIGH", "Single point of failure", "Downtime")],
        recommendations=[ReportRecommendation("Add HA", "HIGH", "Deploy multiple", "Availability")],
        ai_model="gpt-4o",
        processing_time_seconds=10.0,
        created_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_get_report_found(sample_report):
    repo = AsyncMock()
    repo.find_by_upload_id = AsyncMock(return_value=sample_report)
    use_case = GetReportUseCase(repo)

    result = await use_case.execute("upload-id-abc")
    assert result.upload_id == "upload-id-abc"
    assert result.summary == "Microservices architecture"


@pytest.mark.asyncio
async def test_get_report_not_found():
    repo = AsyncMock()
    repo.find_by_upload_id = AsyncMock(return_value=None)
    use_case = GetReportUseCase(repo)

    with pytest.raises(ReportNotFoundError):
        await use_case.execute("non-existent-id")
