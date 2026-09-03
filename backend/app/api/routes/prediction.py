from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.ml.model_loader import get_model_loader
from app.models.schemas import (
    DetectionRequest,
    DetectionResponse,
    IntensityRequest,
    IntensityResponse,
    TrackRequest,
    TrackResponse,
)
from app.services.detection_service import DetectionService
from app.services.intensity_service import IntensityService
from app.services.trajectory_service import TrajectoryService

router = APIRouter(prefix="", tags=["prediction"])


@router.post("/predict-detection", response_model=DetectionResponse)
def predict_detection(
    request: DetectionRequest,
    db: Session = Depends(get_db_session),
) -> DetectionResponse:
    loader = get_model_loader()
    service = DetectionService(db_session=db, model_loader=loader)
    return service.detect(request)


@router.post("/predict-intensity", response_model=IntensityResponse)
def predict_intensity(
    request: IntensityRequest,
    db: Session = Depends(get_db_session),
) -> IntensityResponse:
    loader = get_model_loader()
    service = IntensityService(db_session=db, model_loader=loader)
    return service.predict(request)


@router.post("/predict-track", response_model=TrackResponse)
def predict_track(
    request: TrackRequest,
    db: Session = Depends(get_db_session),
) -> TrackResponse:
    loader = get_model_loader()
    service = TrajectoryService(db_session=db, model_loader=loader)
    return service.predict(request)
