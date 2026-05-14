import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from src.application.use_cases.create_report_use_case import CreateReportUseCase
from src.domain.entities.report import Report, ReportComponent, ReportRisk, ReportRecommendation


def sample_report():
    return Report(
        id="report-id-1",
        upload_id="upload-id-1",
        summary="Test architecture",
        components=[ReportComponent("API GW", "Gateway", "Entry point", "Kong")],
        risks=[ReportRisk("SPOF", "HIGH", "Single point of failure", "Downtime")],
        recommendations=[ReportRecommendation("Add HA", "HIGH", "Deploy multiple instances", "Availability")],
        ai_model="gpt-4o",
        processing_time_seconds=5.0,
        created_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_create_report_success():
    repo = AsyncMock()
    repo.find_by_upload_id = AsyncMock(return_value=None)
    repo.save = AsyncMock(side_effect=lambda r: r)
    use_case = CreateReportUseCase(repo)

    report = await use_case.execute(
        upload_id="upload-id-1",
        summary="Test architecture",
        components=[{"name": "API GW", "type": "Gateway", "description": "Entry point", "technology": "Kong"}],
        risks=[{"title": "SPOF", "severity": "HIGH", "description": "...", "impact": "...", "affected_components": []}],
        recommendations=[{"title": "Add HA", "priority": "HIGH", "description": "...", "rationale": "..."}],
        ai_model="gpt-4o",
        processing_time_seconds=5.0,
    )

    assert report.upload_id == "upload-id-1"
    repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_create_report_idempotent():
    existing = sample_report()
    repo = AsyncMock()
    repo.find_by_upload_id = AsyncMock(return_value=existing)
    use_case = CreateReportUseCase(repo)

    result = await use_case.execute(
        upload_id="upload-id-1",
        summary="Different summary",
        components=[], risks=[], recommendations=[],
        ai_model="gpt-4o", processing_time_seconds=1.0,
    )

    assert result.id == "report-id-1"
    repo.save.assert_not_called()
