from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError
from app.core.logging_config import get_logger
from app.models.database_models import (
    AlertDB,
    CycloneDB,
    ForecastPointDB,
    ObservationDB,
    PredictionDB,
)

logger = get_logger("database.repository")


class CycloneRepository:
    """Repository layer — keeps SQLAlchemy out of routes and services."""

    def __init__(self, session: Session):
        self.session = session

    # Cyclones

    def create_cyclone(self, cyclone_id: str, name: Optional[str] = None, status: str = "active") -> CycloneDB:
        try:
            existing = self.session.query(CycloneDB).filter(CycloneDB.cyclone_id == cyclone_id).one_or_none()
            if existing is not None:
                return existing
            obj = CycloneDB(cyclone_id=cyclone_id, name=name, status=status)
            self.session.add(obj)
            self.session.flush()
            return obj
        except Exception as exc:
            logger.exception("create_cyclone failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to save cyclone") from exc

    def get_cyclone(self, cyclone_id: str) -> Optional[CycloneDB]:
        try:
            return self.session.query(CycloneDB).filter(CycloneDB.cyclone_id == cyclone_id).one_or_none()
        except Exception as exc:
            logger.exception("get_cyclone failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to retrieve cyclone") from exc

    def list_cyclones(self, status: Optional[str] = None) -> List[CycloneDB]:
        try:
            q = self.session.query(CycloneDB)
            if status:
                q = q.filter(CycloneDB.status == status)
            return q.order_by(CycloneDB.created_at.desc()).all()
        except Exception as exc:
            logger.exception("list_cyclones failed: %s", exc)
            raise DatabaseError("Failed to list cyclones") from exc

    def count_cyclones(self, status: Optional[str] = None) -> int:
        try:
            q = self.session.query(CycloneDB)
            if status:
                q = q.filter(CycloneDB.status == status)
            return int(q.count())
        except Exception as exc:
            logger.exception("count_cyclones failed: %s", exc)
            return 0

    # Observations

    def add_observation(self, cyclone_id: str, **fields: Any) -> ObservationDB:
        try:
            self.create_cyclone(cyclone_id)
            obj = ObservationDB(cyclone_id=cyclone_id, **fields)
            self.session.add(obj)
            self.session.flush()
            return obj
        except Exception as exc:
            logger.exception("add_observation failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to save observation") from exc

    def list_observations(self, cyclone_id: str, limit: int = 50) -> List[ObservationDB]:
        try:
            return (
                self.session.query(ObservationDB)
                .filter(ObservationDB.cyclone_id == cyclone_id)
                .order_by(ObservationDB.timestamp.desc())
                .limit(limit)
                .all()
            )
        except Exception as exc:
            logger.exception("list_observations failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to retrieve observations") from exc

    # Predictions

    def add_prediction(self, cyclone_id: str, **fields: Any) -> PredictionDB:
        try:
            self.create_cyclone(cyclone_id)
            obj = PredictionDB(cyclone_id=cyclone_id, **fields)
            self.session.add(obj)
            self.session.flush()
            return obj
        except Exception as exc:
            logger.exception("add_prediction failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to save prediction") from exc

    def list_predictions(self, cyclone_id: str, prediction_type: Optional[str] = None, limit: int = 50) -> List[PredictionDB]:
        try:
            q = self.session.query(PredictionDB).filter(PredictionDB.cyclone_id == cyclone_id)
            if prediction_type:
                q = q.filter(PredictionDB.prediction_type == prediction_type)
            return q.order_by(PredictionDB.timestamp.desc()).limit(limit).all()
        except Exception as exc:
            logger.exception("list_predictions failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to retrieve predictions") from exc

    def average_confidence(self, prediction_type: Optional[str] = None, min_samples: int = 5) -> Optional[float]:
        try:
            from sqlalchemy import func

            q = self.session.query(func.avg(PredictionDB.confidence)).filter(PredictionDB.confidence.isnot(None))
            if prediction_type:
                q = q.filter(PredictionDB.prediction_type == prediction_type)
            count_q = self.session.query(func.count(PredictionDB.id)).filter(PredictionDB.confidence.isnot(None))
            if prediction_type:
                count_q = count_q.filter(PredictionDB.prediction_type == prediction_type)
            count = count_q.scalar() or 0
            if count < min_samples:
                return None
            avg = q.scalar()
            return float(avg) if avg is not None else None
        except Exception as exc:
            logger.exception("average_confidence failed: %s", exc)
            return None

    # Forecast points

    def add_forecast_point(
        self, cyclone_id: str, prediction_id: Optional[int], hour: int, latitude: float, longitude: float, wind_speed: Optional[float] = None
    ) -> ForecastPointDB:
        try:
            obj = ForecastPointDB(
                cyclone_id=cyclone_id,
                prediction_id=prediction_id,
                hour=hour,
                latitude=latitude,
                longitude=longitude,
                wind_speed=wind_speed,
            )
            self.session.add(obj)
            self.session.flush()
            return obj
        except Exception as exc:
            logger.exception("add_forecast_point failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to save forecast point") from exc

    def list_forecast_points(self, cyclone_id: str, prediction_id: Optional[int] = None) -> List[ForecastPointDB]:
        try:
            q = self.session.query(ForecastPointDB).filter(ForecastPointDB.cyclone_id == cyclone_id)
            if prediction_id is not None:
                q = q.filter(ForecastPointDB.prediction_id == prediction_id)
            return q.order_by(ForecastPointDB.hour.asc()).all()
        except Exception as exc:
            logger.exception("list_forecast_points failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to retrieve forecast points") from exc

    # Alerts

    def add_alert(
        self, cyclone_id: str, severity: str, triggered: bool, reason: str, message: str, language: str = "English"
    ) -> AlertDB:
        try:
            self.create_cyclone(cyclone_id)
            obj = AlertDB(
                cyclone_id=cyclone_id,
                severity=severity,
                triggered=triggered,
                reason=reason,
                message=message,
                language=language,
            )
            self.session.add(obj)
            self.session.flush()
            return obj
        except Exception as exc:
            logger.exception("add_alert failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to save alert") from exc

    def list_alerts(self, cyclone_id: str, limit: int = 20) -> List[AlertDB]:
        try:
            return (
                self.session.query(AlertDB)
                .filter(AlertDB.cyclone_id == cyclone_id)
                .order_by(AlertDB.timestamp.desc())
                .limit(limit)
                .all()
            )
        except Exception as exc:
            logger.exception("list_alerts failed for %s: %s", cyclone_id, exc)
            raise DatabaseError("Failed to retrieve alerts") from exc

    def commit(self) -> None:
        try:
            self.session.commit()
        except Exception as exc:
            logger.exception("commit failed: %s", exc)
            self.session.rollback()
            raise DatabaseError("Failed to commit transaction") from exc
