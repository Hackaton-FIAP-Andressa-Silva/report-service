import sys
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

# Stub out motor so tests run without the driver installed locally.
# In CI, motor IS installed and sys.modules already has it — setdefault is a no-op.
_motor_stub = MagicMock()
_motor_stub.AsyncIOMotorClient = MagicMock
sys.modules.setdefault("motor", _motor_stub)
sys.modules.setdefault("motor.motor_asyncio", _motor_stub)

from src.api.routers.report_router import router  # noqa: E402
from src.application.use_cases.get_report_use_case import ReportNotFoundError
from src.domain.entities.report import Report, ReportComponent, ReportRisk, ReportRecommendation
from src.infrastructure.config import settings

VALID_UUID = "a1b2c3d4-e5f6-4789-abcd-ef0123456789"
FIXED_DT = datetime(2026, 5, 14, 10, 0, 0)


def make_sample_report():
    return Report(
        id="report-id-1",
        upload_id=VALID_UUID,
        summary="Microservices arch",
        components=[ReportComponent("API GW", "Gateway", "Entry point", "Kong")],
        risks=[ReportRisk("SPOF", "HIGH", "desc", "impact")],
        recommendations=[ReportRecommendation("Add HA", "HIGH", "deploy more", "better availability")],
        ai_model="gemini-2.0-flash",
        processing_time_seconds=5.0,
        created_at=FIXED_DT,
    )


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.mark.asyncio
async def test_get_report_success(test_app):
    report = make_sample_report()
    mock_uc = AsyncMock()
    mock_uc.execute = AsyncMock(return_value=report)

    with patch("src.api.routers.report_router.get_report_use_case", return_value=mock_uc):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/reports/{VALID_UUID}")

    assert response.status_code == 200
    body = response.json()
    assert body["upload_id"] == VALID_UUID
    assert body["summary"] == "Microservices arch"
    assert body["ai_model"] == "gemini-2.0-flash"


@pytest.mark.asyncio
async def test_get_report_not_found(test_app):
    mock_uc = AsyncMock()
    mock_uc.execute = AsyncMock(side_effect=ReportNotFoundError("not found"))

    with patch("src.api.routers.report_router.get_report_use_case", return_value=mock_uc):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/reports/{VALID_UUID}")

    assert response.status_code == 404
    assert response.json()["code"] == "REPORT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_report_invalid_uuid(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/api/v1/reports/not-a-uuid")
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_UUID"


@pytest.mark.asyncio
async def test_create_report_success(test_app):
    mock_uc = AsyncMock()
    mock_uc.execute = AsyncMock(return_value=make_sample_report())
    token = settings.INTERNAL_SERVICE_TOKEN

    with patch("src.api.routers.report_router.get_create_use_case", return_value=mock_uc):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "upload_id": VALID_UUID,
                    "summary": "Test architecture",
                    "components": [
                        {"name": "API", "type": "Gateway", "description": "entry", "technology": "nginx"}
                    ],
                    "risks": [
                        {"title": "SPOF", "severity": "HIGH", "description": "desc", "impact": "outage"}
                    ],
                    "recommendations": [
                        {"title": "HA", "priority": "HIGH", "description": "deploy more", "rationale": "better"}
                    ],
                    "ai_model": "gemini-2.0-flash",
                    "processing_time_seconds": 5.0,
                },
                headers={"X-Internal-Token": token},
            )

    assert response.status_code == 201
    body = response.json()
    assert body["upload_id"] == VALID_UUID
    assert body["report_id"] == "report-id-1"


@pytest.mark.asyncio
async def test_create_report_wrong_token(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/reports",
            json={
                "upload_id": VALID_UUID,
                "summary": "test",
                "components": [],
                "risks": [],
                "recommendations": [],
                "ai_model": "model",
                "processing_time_seconds": 1.0,
            },
            headers={"X-Internal-Token": "totally-wrong-token-xyz"},
        )
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_create_report_missing_token(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/reports",
            json={
                "upload_id": VALID_UUID,
                "summary": "test",
                "components": [],
                "risks": [],
                "recommendations": [],
                "ai_model": "model",
                "processing_time_seconds": 1.0,
            },
        )
    assert response.status_code == 422
