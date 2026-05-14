import logging
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.infrastructure.config import settings
from src.infrastructure.database.mongodb_connection import get_mongo_client
from src.infrastructure.logging_config import setup_logging, trace_id_var

setup_logging(settings.APP_NAME)
logger = logging.getLogger(__name__)

app = FastAPI(title="Report Service", version="1.0.0", docs_url="/docs")


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    token = trace_id_var.set(trace_id)
    try:
        response = await call_next(request)
    finally:
        trace_id_var.reset(token)
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.error("Unhandled exception: %s | path=%s", str(exc), request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "INTERNAL_ERROR", "trace_id": trace_id},
    )


@app.get("/health")
async def health_check():
    checks: dict = {}
    overall = "healthy"

    # --- MongoDB ---
    try:
        client = get_mongo_client()
        await client.admin.command("ping")
        checks["database"] = {"status": "healthy"}
    except Exception as exc:
        logger.error("Health check: MongoDB unreachable: %s", exc)
        checks["database"] = {"status": "unhealthy", "error": "Connection failed"}
        overall = "unhealthy"

    status_code = 503 if overall == "unhealthy" else 200
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "service": settings.APP_NAME,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
        },
    )


from src.api.routers.report_router import router  # noqa: E402
app.include_router(router, prefix="/api/v1")
