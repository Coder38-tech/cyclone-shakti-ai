from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.core.exceptions import ValidationError
from app.core.logging_config import get_logger
from app.data.data_loader import RawObservation
from app.utils.geojson import validate_coordinates
from app.utils.helpers import clamp, utc_now

logger = get_logger("preprocessing")


class Preprocessor:
    """Clean + normalize raw observations into ML-ready inputs.

    For the demo this is deliberately lightweight.
    Real satellite imagery/weather processing can be plugged in here.
    """

    def __init__(self) -> None:
        self.numeric_fields = [
            "latitude",
            "longitude",
            "wind_speed",
            "pressure",
            "temperature",
            "humidity",
        ]

    def clean(self, observation: RawObservation) -> Dict[str, Any]:
        """Apply cleaning rules to a single raw observation."""
        cleaned: Dict[str, Any] = {
            "cyclone_id": observation.cyclone_id,
            "source": observation.source or "unknown",
            "timestamp": observation.timestamp or utc_now(),
        }

        if observation.latitude is not None and observation.longitude is not None:
            try:
                validate_coordinates(float(observation.latitude), float(observation.longitude))
                cleaned["latitude"] = float(observation.latitude)
                cleaned["longitude"] = float(observation.longitude)
            except ValidationError:
                raise

        for field_name in ["wind_speed", "pressure", "temperature", "humidity"]:
            value = getattr(observation, field_name, None)
            if value is None:
                continue
            try:
                num = float(value)
                if field_name == "wind_speed":
                    num = clamp(num, 0.0, 500.0)
                elif field_name == "pressure":
                    num = clamp(num, 800.0, 1100.0)
                elif field_name == "temperature":
                    num = clamp(num, -60.0, 60.0)
                elif field_name == "humidity":
                    num = clamp(num, 0.0, 100.0)
                cleaned[field_name] = num
            except (TypeError, ValueError):
                logger.warning("Skipping non-numeric %s=%s for %s", field_name, value, observation.cyclone_id)

        if observation.raw:
            cleaned["raw"] = observation.raw

        return cleaned

    def to_features(self, cleaned: Dict[str, Any]) -> np.ndarray:
        """Convert cleaned observation dict to a numpy feature vector.

        The output shape and ordering is a contract with ML models.
        Order: [latitude, longitude, wind_speed, pressure, temperature, humidity]
        Missing values default to 0.
        """
        values: List[float] = []
        for field_name in self.numeric_fields:
            values.append(float(cleaned.get(field_name, 0.0) or 0.0))
        return np.asarray(values, dtype=np.float32)

    def clean_batch(self, observations: List[RawObservation]) -> pd.DataFrame:
        rows = [self.clean(obs) for obs in observations]
        return pd.DataFrame(rows)


def get_preprocessor() -> Preprocessor:
    return Preprocessor()
