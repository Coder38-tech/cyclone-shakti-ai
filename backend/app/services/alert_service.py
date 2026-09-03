from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AlertEvaluationError
from app.core.logging_config import get_logger
from app.database.repository import CycloneRepository
from app.models.schemas import AlertEvaluationRequest, AlertEvaluationResponse, SeverityLevel
from app.utils.validation import get_default_reason, severity_from_category, severity_from_wind_speed

logger = get_logger("services.alert")


SEVERITY_ORDER: dict[str, int] = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "EXTREME": 3}
TRIGGER_THRESHOLD_SEVERITY = "LOW"


class AlertService:
    """Configurable alert evaluation engine.

    Alert rules live in core/config (AlertRules), not duplicated across the codebase.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session

    def evaluate(self, request: AlertEvaluationRequest) -> AlertEvaluationResponse:
        try:
            wind_speed = request.wind_speed
            category = request.intensity_category
            confidence = float(request.confidence if request.confidence is not None else 0.75)

            severity_ws: SeverityLevel = "LOW"
            severity_cat: SeverityLevel = "LOW"

            if wind_speed is not None:
                severity_ws = severity_from_wind_speed(wind_speed, confidence)  # type: ignore[assignment]
            if category:
                severity_cat = severity_from_category(category, confidence)  # type: ignore[assignment]

            chosen: SeverityLevel = (
                severity_ws if SEVERITY_ORDER[severity_ws] >= SEVERITY_ORDER[severity_cat] else severity_cat
            )
            triggered = SEVERITY_ORDER[chosen] >= SEVERITY_ORDER[TRIGGER_THRESHOLD_SEVERITY]

            if wind_speed is not None and chosen in {"HIGH", "EXTREME"}:
                reason = "High predicted wind speed"
            elif category and chosen in {"HIGH", "EXTREME"}:
                reason = f"Intensity category is {category}"
            elif chosen == "MODERATE":
                reason = "Moderate cyclone activity detected"
            else:
                reason = get_default_reason(chosen)

            severity_messages = {
                "LOW": "Low risk — stay informed via official weather sources.",
                "MODERATE": "Moderate risk — prepare emergency supplies and know evacuation routes.",
                "HIGH": "High risk — act on official advisories and be ready to evacuate if ordered.",
                "EXTREME": "EXTREME RISK — evacuate immediately to designated shelters and follow NDRF instructions.",
            }
            message = severity_messages[chosen]

            response = AlertEvaluationResponse(
                alert_triggered=triggered,
                severity=chosen,
                reason=reason,
                message=message,
                cyclone_id=request.cyclone_id,
            )

            if self.db_session is not None:
                repo = CycloneRepository(self.db_session)
                repo.create_cyclone(request.cyclone_id, status="active")
                repo.add_alert(
                    cyclone_id=request.cyclone_id,
                    severity=response.severity,
                    triggered=response.alert_triggered,
                    reason=response.reason,
                    message=response.message,
                    language="English",
                )
                repo.commit()

            logger.info(
                "Alert evaluated cyclone=%s triggered=%s severity=%s reason='%s'",
                request.cyclone_id,
                response.alert_triggered,
                response.severity,
                response.reason,
            )
            return response
        except AlertEvaluationError:
            raise
        except Exception as exc:
            logger.exception("Alert evaluation failed for %s: %s", request.cyclone_id, exc)
            raise AlertEvaluationError(str(exc)) from exc
