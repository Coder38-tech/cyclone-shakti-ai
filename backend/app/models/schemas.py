from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

SeverityLevel = Literal["LOW", "MODERATE", "HIGH", "EXTREME"]


class Center(BaseModel):
    latitude: float = Field(..., description="Cyclone center latitude in degrees (-90 to 90)")
    longitude: float = Field(..., description="Cyclone center longitude in degrees (-180 to 180)")


class Intensity(BaseModel):
    predicted_wind_speed: float = Field(..., description="Predicted sustained wind speed (km/h or knots, per config)")
    intensity_category: str = Field(..., description="Cyclone intensity category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence [0, 1]")


class ForecastPoint(BaseModel):
    hour: int = Field(..., ge=0, description="Forecast hour offset")
    latitude: float
    longitude: float
    wind_speed: float


class GeoJSONLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: List[List[float]] = Field(
        ..., description="Ordered [longitude, latitude] coordinate pairs"
    )


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]


class Track(BaseModel):
    forecast_hours: int
    forecast_points: List[ForecastPoint]
    geojson: GeoJSONLineString


class Advisory(BaseModel):
    severity: SeverityLevel
    language: str
    message: str
    recommended_actions: Optional[List[str]] = None


class Alert(BaseModel):
    alert_triggered: bool
    severity: SeverityLevel
    reason: str
    message: str


class CurrentCyclone(BaseModel):
    cyclone_id: str
    center: Center
    detection_confidence: float
    intensity: Intensity
    track: Track
    advisory: Advisory


# Detection
class DetectionRequest(BaseModel):
    image_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class DetectionResponse(BaseModel):
    cyclone_detected: bool
    confidence: float
    center: Optional[Center] = None
    cyclone_id: Optional[str] = None


# Intensity
class IntensityRequest(BaseModel):
    cyclone_id: str
    latitude: float
    longitude: float
    current_wind_speed: float
    pressure: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[datetime] = None


class IntensityResponse(BaseModel):
    cyclone_id: str
    predicted_wind_speed: float
    intensity_category: str
    confidence: float


# Track
class TrackRequest(BaseModel):
    cyclone_id: str
    current_position: Center
    current_wind_speed: float
    forecast_hours: int = Field(default=48, ge=6, le=240)
    pressure: Optional[float] = None
    timestamp: Optional[datetime] = None


class TrackResponse(BaseModel):
    cyclone_id: str
    forecast_hours: int
    forecast_points: List[ForecastPoint]
    geojson: GeoJSONLineString


# Advisory
class AdvisoryRequest(BaseModel):
    cyclone_id: str
    intensity_category: str
    wind_speed: float
    location: Center
    language: str = Field(default="English", description="Advisory language")
    extra_context: Optional[Dict[str, Any]] = None


class AdvisoryResponse(BaseModel):
    cyclone_id: str
    severity: SeverityLevel
    language: str
    message: str
    recommended_actions: List[str]


# Alerts
class AlertEvaluationRequest(BaseModel):
    cyclone_id: str
    intensity_category: Optional[str] = None
    wind_speed: Optional[float] = None
    confidence: Optional[float] = None
    location: Optional[Center] = None
    timestamp: Optional[datetime] = None


class AlertEvaluationResponse(BaseModel):
    alert_triggered: bool
    severity: SeverityLevel
    reason: str
    message: str
    cyclone_id: str


# Analytics
class AnalyticsSummary(BaseModel):
    total_cyclones: int
    active_cyclones: int
    average_detection_confidence: float
    average_prediction_confidence: float


class CycloneAnalyticsEntry(BaseModel):
    timestamp: datetime
    observation_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    confidence: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class CycloneAnalyticsResponse(BaseModel):
    cyclone_id: str
    observations: List[CycloneAnalyticsEntry]
    predictions: List[CycloneAnalyticsEntry]
    data_source: str = Field(..., description="'database' or 'mock_demo'")


# Health
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database_available: Optional[bool] = None


# Base common config for all response schemas
BaseModel.model_config = ConfigDict(extra="ignore")
