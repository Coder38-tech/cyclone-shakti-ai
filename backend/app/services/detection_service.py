from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ModelInferenceError
from app.core.logging_config import get_logger
from app.data.data_loader import RawObservation, get_data_loader
from app.data.preprocessing import get_preprocessor
from app.database.repository import CycloneRepository
from app.ml.model_loader import ModelLoader, get_model_loader
from app.models.schemas import Center, DetectionRequest, DetectionResponse
from app.utils.geojson import validate_coordinates
from app.utils.helpers import generate_cyclone_id, utc_now

logger = get_logger("services.detection")


class DetectionService:
    """Runs cyclone detection, persists observations, returns standardized response."""

    def __init__(self, db_session: Optional[Session] = None, model_loader: Optional[ModelLoader] = None):
        self.db_session = db_session
        self.model_loader = model_loader or get_model_loader()
        self.preprocessor = get_preprocessor()
        self.data_loader = get_data_loader()

    def detect(self, request: DetectionRequest) -> DetectionResponse:
        if request.latitude is not None and request.longitude is not None:
            validate_coordinates(float(request.latitude), float(request.longitude))

        input_dict: Dict[str, Any] = {
            "image_path": request.image_path,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "timestamp": request.timestamp or utc_now(),
            "metadata": request.metadata or {},
        }

        logger.info("Detection request received lat=%s lon=%s image=%s", request.latitude, request.longitude, bool(request.image_path))

        try:
            raw_prediction = self.model_loader.detection.predict(input_dict)
        except ModelInferenceError:
            raise
        except Exception as exc:
            logger.exception("Detection model predict failed: %s", exc)
            raise ModelInferenceError("Detection model failed during predict", details={"step": "predict"}) from exc

        cyclone_id = raw_prediction.get("cyclone_id")
        if raw_prediction.get("cyclone_detected") and not cyclone_id:
            cyclone_id = generate_cyclone_id()
            raw_prediction["cyclone_id"] = cyclone_id

        if self.db_session is not None and raw_prediction.get("cyclone_detected"):
            center = raw_prediction.get("center") or {}
            repo = CycloneRepository(self.db_session)
            repo.create_cyclone(cyclone_id=cyclone_id, status="active")
            repo.add_observation(
                cyclone_id=cyclone_id,
                latitude=center.get("latitude"),
                longitude=center.get("longitude"),
                observation_type="detection",
                timestamp=utc_now(),
            )
            repo.commit()

        center_payload = None
        center = raw_prediction.get("center")
        if center:
            center_payload = Center(latitude=float(center["latitude"]), longitude=float(center["longitude"]))

        response = DetectionResponse(
            cyclone_detected=bool(raw_prediction.get("cyclone_detected", False)),
            confidence=float(raw_prediction.get("confidence", 0.0)),
            center=center_payload,
            cyclone_id=raw_prediction.get("cyclone_id"),
        )
        logger.info("Detection result cyclone=%s detected=%s conf=%.3f", response.cyclone_id, response.cyclone_detected, response.confidence)
        return response

    def detect_from_raw_observation(self, obs: RawObservation) -> DetectionResponse:
        request = DetectionRequest(
            latitude=obs.latitude,
            longitude=obs.longitude,
            timestamp=obs.timestamp,
        )
        return self.detect(request)
