from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.models.schemas import AlertEvaluationRequest, AlertEvaluationResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/evaluate", response_model=AlertEvaluationResponse)
def evaluate_alert(
    request: AlertEvaluationRequest,
    db: Session = Depends(get_db_session),
) -> AlertEvaluationResponse:
    service = AlertService(db_session=db)
    return service.evaluate(request)
