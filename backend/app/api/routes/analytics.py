from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.models.schemas import AnalyticsSummary, CycloneAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db_session)) -> AnalyticsSummary:
    service = AnalyticsService(db_session=db)
    return service.summary()


@router.get("/cyclone/{cyclone_id}", response_model=CycloneAnalyticsResponse)
def cyclone_analytics(
    cyclone_id: str,
    db: Session = Depends(get_db_session),
) -> CycloneAnalyticsResponse:
    service = AnalyticsService(db_session=db)
    return service.cyclone_analytics(cyclone_id)
