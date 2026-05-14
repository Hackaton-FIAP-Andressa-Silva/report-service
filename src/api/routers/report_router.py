import logging
import uuid as uuid_lib
from dataclasses import asdict

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from src.api.schemas.report_schema import CreateReportRequest, ReportResponse
from src.application.use_cases.create_report_use_case import CreateReportUseCase
from src.application.use_cases.get_report_use_case import GetReportUseCase, ReportNotFoundError
from src.infrastructure.config import settings
from src.infrastructure.database.mongodb_report_repository import MongoDBReportRepository

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_valid_uuid(upload_id: str) -> str:
    try:
        val = uuid_lib.UUID(upload_id, version=4)
        if str(val) != upload_id:
            raise ValueError
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail={"error": "Invalid upload_id format", "code": "INVALID_UUID"})
    return upload_id


def get_create_use_case() -> CreateReportUseCase:
    return CreateReportUseCase(MongoDBReportRepository())


def get_report_use_case() -> GetReportUseCase:
    return GetReportUseCase(MongoDBReportRepository())


@router.post("/reports", status_code=201)
async def create_report(
    request: Request,
    body: CreateReportRequest,
    x_internal_token: str = Header(..., alias="X-Internal-Token"),
):
    """Internal endpoint — called only by ai-processing-service."""
    if x_internal_token != settings.INTERNAL_SERVICE_TOKEN:
        trace_id = getattr(request.state, "trace_id", "unknown")
        return JSONResponse(status_code=403, content={"error": "Forbidden", "code": "FORBIDDEN", "trace_id": trace_id})

    use_case = get_create_use_case()
    report = await use_case.execute(
        upload_id=body.upload_id,
        summary=body.summary,
        components=[c.model_dump() for c in body.components],
        risks=[r.model_dump() for r in body.risks],
        recommendations=[rec.model_dump() for rec in body.recommendations],
        ai_model=body.ai_model,
        processing_time_seconds=body.processing_time_seconds,
    )
    return {"report_id": report.id, "upload_id": report.upload_id}


@router.get("/reports/{upload_id}", response_model=ReportResponse)
async def get_report(request: Request, upload_id: str = Depends(_require_valid_uuid)):
    use_case = get_report_use_case()
    try:
        report = await use_case.execute(upload_id)
    except ReportNotFoundError:
        trace_id = getattr(request.state, "trace_id", "unknown")
        return JSONResponse(
            status_code=404,
            content={"error": f"Report not found for upload_id '{upload_id}'", "code": "REPORT_NOT_FOUND", "trace_id": trace_id},
        )

    return ReportResponse(
        report_id=report.id,
        upload_id=report.upload_id,
        summary=report.summary,
        components=[asdict(c) for c in report.components],
        risks=[asdict(r) for r in report.risks],
        recommendations=[asdict(rec) for rec in report.recommendations],
        ai_model=report.ai_model,
        processing_time_seconds=report.processing_time_seconds,
        created_at=report.created_at,
    )
