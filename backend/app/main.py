from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.routes import advisory as advisory_routes
from app.api.routes import alerts as alerts_routes
from app.api.routes import analytics as analytics_routes
from app.api.routes import cyclone as cyclone_routes
from app.api.routes import health as health_routes
from app.api.routes import prediction as prediction_routes
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging_config import get_logger, setup_logging
from app.database.connection import get_database
from app.ml.model_loader import get_model_loader
from app.utils.helpers import utc_now

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info(
        "Starting %s v%s (env=%s)",
        settings.app_title,
        settings.app_version,
        settings.app_env,
    )

    db = get_database()
    db.create_tables()
    app.state.db_available = db.check_available()
    logger.info("Database initialised (available=%s)", app.state.db_available)

    models_status = get_model_loader().load_all()
    app.state.models_status = models_status
    logger.info("ML models initialised: %s", models_status)

    logger.info("Application startup complete")

    yield

    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description="AI-powered tropical cyclone platform for India — detection, intensity prediction, trajectory forecasting, advisories and analytics.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_routes.router)
    app.include_router(cyclone_routes.router)
    app.include_router(prediction_routes.router)
    app.include_router(advisory_routes.router)
    app.include_router(alerts_routes.router)
    app.include_router(analytics_routes.router)

    register_exception_handlers(app)
    register_websocket_endpoints(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error("[%s] %s: %s", exc.code, exc.message, exc.details)
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        issues = []
        for err in exc.errors():
            loc = " -> ".join(str(x) for x in err.get("loc", []))
            issues.append({"field": loc or "body", "message": err.get("msg", "Invalid value"), "type": err.get("type", "unknown")})
        logger.warning("Request validation failed: %s", issues)
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": {"issues": issues},
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        issues = [str(e) for e in exc.errors()]
        return JSONResponse(
            status_code=400,
            content={"error": "Validation failed", "code": "VALIDATION_ERROR", "details": {"issues": issues}},
        )

    @app.exception_handler(Exception)
    async def catch_all_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )


def register_websocket_endpoints(app: FastAPI) -> None:
    @app.websocket("/ws/cyclone/{cyclone_id}")
    async def cyclone_updates(websocket: WebSocket, cyclone_id: str):
        """Simple mock WebSocket endpoint for future real-time cyclone updates.

        Sends lightweight status updates every ~5 seconds.
        """
        await websocket.accept()
        logger.info("WebSocket client connected for cyclone=%s", cyclone_id)
        tick = 0
        try:
            while True:
                payload: Dict[str, Any] = {
                    "cyclone_id": cyclone_id,
                    "timestamp": utc_now().isoformat(),
                    "tick": tick,
                    "event": "position_update",
                    "data": {
                        "latitude": 15.52 + 0.001 * tick,
                        "longitude": 73.21 + 0.002 * tick,
                        "wind_speed": 120 + (tick % 20),
                        "status": "mock_live_feed",
                    },
                }
                await websocket.send_json(payload)
                tick += 1
                await asyncio.sleep(5)
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected for cyclone=%s", cyclone_id)
        except Exception as exc:
            logger.warning("WebSocket error for cyclone=%s: %s", cyclone_id, exc)


app = create_app()
