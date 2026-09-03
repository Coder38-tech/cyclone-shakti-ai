from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger
from app.core.exceptions import AppError

logger = get_logger("data_loader")


@dataclass
class RawObservation:
    cyclone_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[datetime] = None
    source: str = "mock"
    raw: Dict[str, Any] = field(default_factory=dict)


class DataLoader:
    """Abstracts loading cyclone observations from multiple sources.

    The default implementation ships with mock data so the API works out of the
    box. The intent is that this will be extended with satellite/weather
    downloaders without touching routes or services.
    """

    def __init__(self) -> None:
        self.sources: Dict[str, Any] = {"mock": None}

    def register_source(self, name: str, loader: Any) -> None:
        self.sources[name] = loader

    def load_latest(self, source: str = "mock") -> List[RawObservation]:
        if source not in self.sources:
            raise AppError(
                message=f"Unknown data source: {source}",
                code="UNKNOWN_DATA_SOURCE",
                status_code=400,
            )
        if source == "mock":
            return self._load_mock()
        loader = self.sources[source]
        if hasattr(loader, "load_latest"):
            return list(loader.load_latest())
        raise AppError(
            message=f"Data source {source} does not implement load_latest()",
            code="DATA_SOURCE_ERROR",
            status_code=500,
        )

    def _load_mock(self) -> List[RawObservation]:
        from app.data.mock_data import get_mock_current_observation, get_mock_observations

        try:
            return get_mock_observations()
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to load mock data: %s", exc)
            obs = get_mock_current_observation()
            return [obs]


def get_data_loader() -> DataLoader:
    return DataLoader()
