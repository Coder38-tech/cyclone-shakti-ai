from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.connection import get_db_session
from app.database.connection import get_database
from app.models.schemas import HealthResponse

router = APIRouter(prefix="", tags=["health"])


@router.get("/", tags=["root"])
def root() -> dict:
    return {"message": "Cyclone Shakti AI Backend is running"}


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db_session)) -> HealthResponse:
    settings = get_settings()
    db_ok = True
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception:
        database = get_database()
        db_ok = database.check_available()
    return HealthResponse(
        status="online",
        service="cyclone-shakti-ai-backend",
        version=settings.app_version,
        database_available=db_ok,
    )
