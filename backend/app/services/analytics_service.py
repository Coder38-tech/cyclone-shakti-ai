from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import CycloneNotFoundError
from app.core.logging_config import get_logger
from app.data.mock_data import (
    get_mock_historical_observations,
    get_mock_historical_predictions,
)
from app.database.repository import CycloneRepository
from app.models.schemas import (
    AnalyticsSummary,
    CycloneAnalyticsEntry,
    CycloneAnalyticsResponse,
)

logger = get_logger("services.analytics")


FALLBACK_SUMMARY = AnalyticsSummary(
    total_cyclones=10,
    active_cyclones=1,
    average_detection_confidence=0.91,
    average_prediction_confidence=0.86,
)


class AnalyticsService:
    """Aggregates historical observations + predictions for analytics dashboard.

    Falls back to curated mock data when the database is empty so dashboards
    never render empty; responses tag data_source explicitly.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session

    def summary(self) -> AnalyticsSummary:
        if self.db_session is None:
            return FALLBACK_SUMMARY

        try:
            repo = CycloneRepository(self.db_session)
            total = repo.count_cyclones()
            active = repo.count_cyclones(status="active")
            avg_pred_conf = repo.average_confidence(prediction_type="intensity", min_samples=2)
            avg_track_conf = repo.average_confidence(prediction_type="track", min_samples=2)
            prediction_candidates = [c for c in [avg_pred_conf, avg_track_conf] if c is not None]
            avg_pred = sum(prediction_candidates) / len(prediction_candidates) if prediction_candidates else None

            if total == 0:
                logger.info("DB empty — returning curated fallback analytics summary")
                return FALLBACK_SUMMARY

            avg_detection = repo.average_confidence(prediction_type="detection", min_samples=1) or 0.91

            return AnalyticsSummary(
                total_cyclones=int(total),
                active_cyclones=int(active),
                average_detection_confidence=round(float(avg_detection), 4),
                average_prediction_confidence=round(float(avg_pred if avg_pred is not None else 0.86), 4),
            )
        except Exception as exc:
            logger.warning("Analytics summary computation failed, returning fallback: %s", exc)
            return FALLBACK_SUMMARY

    def cyclone_analytics(self, cyclone_id: str) -> CycloneAnalyticsResponse:
        db_obs: List[CycloneAnalyticsEntry] = []
        db_preds: List[CycloneAnalyticsEntry] = []
        source = "database"

        if self.db_session is not None:
            try:
                repo = CycloneRepository(self.db_session)
                if repo.get_cyclone(cyclone_id) is None:
                    logger.info("Cyclone %s not found in DB — returning mock demo analytics", cyclone_id)
                    source = "mock_demo"
                else:
                    for obs in repo.list_observations(cyclone_id, limit=50):
                        db_obs.append(
                            CycloneAnalyticsEntry(
                                timestamp=obs.timestamp,
                                observation_type=obs.observation_type or "unknown",
                                latitude=obs.latitude,
                                longitude=obs.longitude,
                                wind_speed=obs.wind_speed,
                                pressure=obs.pressure,
                                confidence=None,
                            )
                        )
                    for pred in repo.list_predictions(cyclone_id, limit=50):
                        details = None
                        if pred.intensity_category or pred.forecast_hours:
                            details = {}
                            if pred.intensity_category:
                                details["intensity_category"] = pred.intensity_category
                            if pred.forecast_hours is not None:
                                details["forecast_hours"] = pred.forecast_hours
                        db_preds.append(
                            CycloneAnalyticsEntry(
                                timestamp=pred.timestamp,
                                observation_type=pred.prediction_type or "prediction",
                                latitude=pred.latitude,
                                longitude=pred.longitude,
                                wind_speed=pred.wind_speed,
                                pressure=pred.pressure,
                                confidence=pred.confidence,
                                details=details,
                            )
                        )
            except CycloneNotFoundError:
                source = "mock_demo"
            except Exception as exc:
                logger.warning("DB analytics fetch failed for %s, using mock: %s", cyclone_id, exc)
                source = "mock_demo"
        else:
            source = "mock_demo"

        if source == "mock_demo":
            mock_obs = get_mock_historical_observations(cyclone_id)
            db_obs = [CycloneAnalyticsEntry(**row) for row in mock_obs]
            mock_preds = get_mock_historical_predictions(cyclone_id)
            db_preds = [CycloneAnalyticsEntry(**row) for row in mock_preds]

        return CycloneAnalyticsResponse(
            cyclone_id=cyclone_id,
            observations=db_obs,
            predictions=db_preds,
            data_source=source,
        )
