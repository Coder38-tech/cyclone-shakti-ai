from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ModelInferenceError
from app.core.logging_config import get_logger
from app.database.repository import CycloneRepository
from app.ml.model_loader import ModelLoader, get_model_loader
from app.models.schemas import ForecastPoint, TrackRequest, TrackResponse
from app.utils.geojson import forecast_points_to_geojson, validate_coordinates
from app.utils.helpers import utc_now

logger = get_logger("services.trajectory")


class TrajectoryService:
    """Predicts cyclone track, converts to GeoJSON, persists to DB."""

    def __init__(self, db_session: Optional[Session] = None, model_loader: Optional[ModelLoader] = None):
        self.db_session = db_session
        self.model_loader = model_loader or get_model_loader()

    def predict(self, request: TrackRequest) -> TrackResponse:
        validate_coordinates(request.current_position.latitude, request.current_position.longitude)

        input_dict: Dict[str, Any] = {
            "cyclone_id": request.cyclone_id,
            "current_position": {
                "latitude": request.current_position.latitude,
                "longitude": request.current_position.longitude,
            },
            "current_wind_speed": request.current_wind_speed,
            "forecast_hours": request.forecast_hours,
            "pressure": request.pressure,
            "timestamp": request.timestamp or utc_now(),
        }

        logger.info(
            "Track prediction request cyclone=%s hours=%s start=(%.2f, %.2f)",
            request.cyclone_id,
            request.forecast_hours,
            request.current_position.latitude,
            request.current_position.longitude,
        )

        try:
            raw = self.model_loader.trajectory.predict(input_dict)
        except ModelInferenceError:
            raise
        except Exception as exc:
            logger.exception("Trajectory model predict failed: %s", exc)
            raise ModelInferenceError("Trajectory model failed during predict", details={"step": "predict"}) from exc

        forecast_points: list[ForecastPoint] = [
            ForecastPoint(
                hour=int(fp.hour),
                latitude=float(fp.latitude),
                longitude=float(fp.longitude),
                wind_speed=float(fp.wind_speed),
            )
            for fp in raw["forecast_points"]
        ]

        geojson = forecast_points_to_geojson(forecast_points)

        response = TrackResponse(
            cyclone_id=raw["cyclone_id"],
            forecast_hours=int(raw["forecast_hours"]),
            forecast_points=forecast_points,
            geojson=geojson,
        )

        if self.db_session is not None:
            repo = CycloneRepository(self.db_session)
            repo.create_cyclone(response.cyclone_id, status="active")
            pred = repo.add_prediction(
                cyclone_id=response.cyclone_id,
                prediction_type="track",
                latitude=request.current_position.latitude,
                longitude=request.current_position.longitude,
                forecast_hours=response.forecast_hours,
                timestamp=utc_now(),
            )
            for fp in response.forecast_points:
                repo.add_forecast_point(
                    cyclone_id=response.cyclone_id,
                    prediction_id=pred.id,
                    hour=fp.hour,
                    latitude=fp.latitude,
                    longitude=fp.longitude,
                    wind_speed=fp.wind_speed,
                )
            repo.commit()

        logger.info(
            "Track prediction cyclone=%s points=%d forecast_hours=%d",
            response.cyclone_id,
            len(response.forecast_points),
            response.forecast_hours,
        )
        return response
