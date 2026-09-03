from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class CycloneIntensityThresholds:
    """
    Configurable wind-speed thresholds for cyclone intensity categorization.

    Thresholds are based on common cyclone classification systems.
    Adjust values via config; final thresholds can be updated per official standards.
    Wind speed unit: knots or km/h — configured per project standard.
    """

    def __init__(self):
        self.thresholds = [
            {"category": "Depression", "min_wind_speed": 0, "max_wind_speed": 50},
            {"category": "Deep Depression", "min_wind_speed": 50, "max_wind_speed": 62},
            {"category": "Cyclonic Storm", "min_wind_speed": 62, "max_wind_speed": 88},
            {"category": "Severe Cyclonic Storm", "min_wind_speed": 88, "max_wind_speed": 117},
            {"category": "Very Severe Cyclonic Storm", "min_wind_speed": 117, "max_wind_speed": 157},
            {"category": "Extremely Severe Cyclonic Storm", "min_wind_speed": 157, "max_wind_speed": 221},
            {"category": "Super Cyclonic Storm", "min_wind_speed": 221, "max_wind_speed": 9999},
        ]


class AlertRules:
    """Configurable alert evaluation rules."""

    def __init__(self):
        self.rules = [
            {"severity": "LOW", "min_wind_speed": 0, "min_confidence": 0.5, "trigger_categories": ["Depression", "Deep Depression"]},
            {"severity": "MODERATE", "min_wind_speed": 62, "min_confidence": 0.6, "trigger_categories": ["Cyclonic Storm"]},
            {"severity": "HIGH", "min_wind_speed": 88, "min_confidence": 0.7, "trigger_categories": ["Severe Cyclonic Storm"]},
            {"severity": "EXTREME", "min_wind_speed": 117, "min_confidence": 0.8, "trigger_categories": ["Very Severe Cyclonic Storm", "Extremely Severe Cyclonic Storm", "Super Cyclonic Storm"]},
        ]
        self.default_reasons = {
            "LOW": "Low intensity cyclone activity detected",
            "MODERATE": "Moderate cyclone intensity, prepare for potential impacts",
            "HIGH": "High predicted wind speed and severe cyclonic activity",
            "EXTREME": "Extreme cyclone threat — immediate action required",
        }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_title: str = "Cyclone Shakti AI Backend"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./cyclone.db"
    frontend_url: str = "http://localhost:5173"

    openai_api_key: str = ""
    gemini_api_key: str = ""

    @property
    def cors_origins(self) -> List[str]:
        origins = [self.frontend_url]
        if self.app_env == "development":
            origins.extend([
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
            ])
        return list(dict.fromkeys(origins))

    @property
    def is_dev(self) -> bool:
        return self.app_env.lower() in {"dev", "development"}

    @property
    def is_prod(self) -> bool:
        return self.app_env.lower() in {"prod", "production"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_intensity_thresholds() -> CycloneIntensityThresholds:
    return CycloneIntensityThresholds()


@lru_cache(maxsize=1)
def get_alert_rules() -> AlertRules:
    return AlertRules()
