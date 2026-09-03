from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import CycloneNotFoundError, ModelInferenceError
from app.core.logging_config import get_logger
from app.database.repository import CycloneRepository
from app.ml.model_loader import ModelLoader, get_model_loader
from app.models.schemas import IntensityRequest, IntensityResponse
from app.utils.helpers import utc_now
from app.utils.validation import validate_location

logger = get_logger("services.intensity")


class IntensityService:
    """Predicts wind speed + category, persists predictions."""

    def __init__(self, db_session: Optional[Session] = None, model_loader: Optional[ModelLoader] = None):
        self.db_session = db_session
        self.model_loader = model_loader or get_model_loader()

    def predict(self, request: IntensityRequest) -> IntensityResponse:
        validate_location(request.latitude, request.longitude)

        if self.db_session is not None:
            repo = CycloneRepository(self.db_session)
            if repo.get_cyclone(request.cyclone_id) is None:
                logger.warning("Cyclone %s not in DB yet for intensity prediction — will create on save", request.cyclone_id)

        input_dict: Dict[str, Any] = {
            "cyclone_id": request.cyclone_id,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "current_wind_speed": request.current_wind_speed,
            "pressure": request.pressure,
            "temperature": request.temperature,
            "humidity": request.humidity,
            "timestamp": request.timestamp or utc_now(),
        }

        logger.info("Intensity prediction request cyclone=%s current_ws=%.2f", request.cyclone_id, request.current_wind_speed)

        try:
            raw = self.model_loader.intensity.predict(input_dict)
        except ModelInferenceError:
            raise
        except Exception as exc:
            logger.exception("Intensity model predict failed: %s", exc)
            raise ModelInferenceError("Intensity model failed during predict", details={"step": "predict"}) from exc

        response = IntensityResponse(
            cyclone_id=raw["cyclone_id"],
            predicted_wind_speed=float(raw["predicted_wind_speed"]),
            intensity_category=str(raw["intensity_category"]),
            confidence=float(raw["confidence"]),
        )

        if self.db_session is not None:
            repo = CycloneRepository(self.db_session)
            repo.create_cyclone(response.cyclone_id, status="active")
            repo.add_observation(
                cyclone_id=response.cyclone_id,
                latitude=request.latitude,
                longitude=request.longitude,
                wind_speed=request.current_wind_speed,
                pressure=request.pressure,
                temperature=request.temperature,
                humidity=request.humidity,
                observation_type="input",
                timestamp=utc_now(),
            )
            repo.add_prediction(
                cyclone_id=response.cyclone_id,
                prediction_type="intensity",
                wind_speed=response.predicted_wind_speed,
                intensity_category=response.intensity_category,
                confidence=response.confidence,
                timestamp=utc_now(),
            )
            repo.commit()

        logger.info(
            "Intensity prediction cyclone=%s ws=%.2f category=%s conf=%.3f",
            response.cyclone_id,
            response.predicted_wind_speed,
            response.intensity_category,
            response.confidence,
        )
        return response
