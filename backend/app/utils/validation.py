from typing import Any, Dict, List

from app.core.config import get_intensity_thresholds, get_alert_rules
from app.core.exceptions import ValidationError
from app.utils.geojson import validate_coordinates


def validate_request_dict(payload: Dict[str, Any], required: List[str]) -> None:
    missing = [field for field in required if payload.get(field) in (None, "", [])]
    if missing:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing)}",
            code="MISSING_FIELDS",
            details={"missing": missing},
        )


def classify_intensity(wind_speed: float) -> str:
    """Classify wind speed into a cyclone intensity category.

    Thresholds are fully configurable via CycloneIntensityThresholds in
    app/core/config so they can be updated per the official standard.
    """
    if wind_speed is None:
        raise ValidationError("wind_speed is required", code="MISSING_FIELDS")
    thresholds = get_intensity_thresholds()
    wind_speed = float(wind_speed)
    for th in thresholds.thresholds:
        if th["min_wind_speed"] <= wind_speed < th["max_wind_speed"]:
            return th["category"]
    return thresholds.thresholds[-1]["category"]


def get_intensity_category_order() -> List[str]:
    thresholds = get_intensity_thresholds()
    return [t["category"] for t in thresholds.thresholds]


def severity_from_wind_speed(wind_speed: float, confidence: float) -> str:
    """Map wind speed + confidence to a severity level using configured rules."""
    rules = get_alert_rules()
    wind_speed = float(wind_speed or 0)
    confidence = float(confidence or 0)
    selected = "LOW"
    for rule in rules.rules:
        if wind_speed >= rule["min_wind_speed"] and confidence >= rule["min_confidence"]:
            selected = rule["severity"]
    return selected


def severity_from_category(intensity_category: str, confidence: float) -> str:
    rules = get_alert_rules()
    confidence = float(confidence or 0)
    selected = "LOW"
    for rule in rules.rules:
        if intensity_category in rule["trigger_categories"] and confidence >= rule["min_confidence"]:
            selected = rule["severity"]
    return selected


def get_default_reason(severity: str) -> str:
    rules = get_alert_rules()
    return rules.default_reasons.get(severity, rules.default_reasons["LOW"])


def validate_location(latitude: Any, longitude: Any) -> None:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            message="latitude and longitude must be numeric",
            code="INVALID_COORDINATES",
        ) from exc
    validate_coordinates(lat, lon)
