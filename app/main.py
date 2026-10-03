"""TaskFlow API application entrypoint."""

import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.config import settings
from app.database import Base, engine
from app.metrics import metrics
from app.routes.tasks import router as tasks_router

logging.basicConfig(
    level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.version)
app.include_router(tasks_router)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("TaskFlow started version=%s", settings.version)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        metrics.record(500)
        logger.exception(
            "Unhandled request error method=%s path=%s",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )
    metrics.record(response.status_code)
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        (perf_counter() - started) * 1000,
    )
    return response


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "healthy", "version": settings.version}


@app.get("/metrics", response_class=PlainTextResponse, tags=["operations"])
def prometheus_metrics() -> PlainTextResponse:
    return PlainTextResponse(
        metrics.render(settings.version), media_type="text/plain; version=0.0.4"
    )


@app.get("/api/demo/failure", tags=["demo"])
def simulated_failure() -> dict[str, str]:
    """Controlled demo endpoint; disabled installations remain healthy."""
    if settings.simulate_failure:
        raise RuntimeError("Controlled failure simulation enabled")
    return {
        "status": "disabled",
        "message": "Set SIMULATE_FAILURE=true to demonstrate rollback.",
    }
