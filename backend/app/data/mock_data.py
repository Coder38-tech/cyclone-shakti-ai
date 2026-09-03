from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.data.data_loader import RawObservation
from app.models.schemas import (
    Advisory,
    Center,
    CurrentCyclone,
    ForecastPoint,
    GeoJSONLineString,
    Intensity,
    Track,
)
from app.utils.geojson import forecast_points_to_geojson
from app.utils.helpers import utc_now


MOCK_CYCLONE_ID = "CY001"
MOCK_CENTER_LAT = 15.52
MOCK_CENTER_LON = 73.21


def get_mock_current_observation() -> RawObservation:
    return RawObservation(
        cyclone_id=MOCK_CYCLONE_ID,
        latitude=MOCK_CENTER_LAT,
        longitude=MOCK_CENTER_LON,
        wind_speed=120.0,
        pressure=980.0,
        temperature=28.5,
        humidity=80.0,
        timestamp=utc_now(),
        source="mock",
        raw={},
    )


def get_mock_observations() -> List[RawObservation]:
    base = utc_now()
    obs_list: List[RawObservation] = []
    for i in range(6):
        t = base - timedelta(hours=i * 6)
        lat = MOCK_CENTER_LAT - i * 0.15
        lon = MOCK_CENTER_LON - i * 0.2
        ws = 120.0 - i * 3.0
        obs_list.append(
            RawObservation(
                cyclone_id=MOCK_CYCLONE_ID,
                latitude=round(lat, 2),
                longitude=round(lon, 2),
                wind_speed=round(ws, 1),
                pressure=980.0 + i,
                temperature=28.5,
                humidity=80.0,
                timestamp=t,
                source="mock",
            )
        )
    return obs_list


def get_mock_current_cyclone() -> CurrentCyclone:
    forecast_points: List[ForecastPoint] = [
        ForecastPoint(hour=0, latitude=15.52, longitude=73.21, wind_speed=120),
        ForecastPoint(hour=12, latitude=16.2, longitude=73.8, wind_speed=128),
        ForecastPoint(hour=24, latitude=17.1, longitude=74.5, wind_speed=138),
        ForecastPoint(hour=48, latitude=18.8, longitude=76.0, wind_speed=145),
    ]
    geojson = forecast_points_to_geojson(forecast_points)
    return CurrentCyclone(
        cyclone_id=MOCK_CYCLONE_ID,
        center=Center(latitude=MOCK_CENTER_LAT, longitude=MOCK_CENTER_LON),
        detection_confidence=0.94,
        intensity=Intensity(
            predicted_wind_speed=145.2,
            intensity_category="Severe Cyclonic Storm",
            confidence=0.87,
        ),
        track=Track(
            forecast_hours=48,
            forecast_points=forecast_points,
            geojson=geojson,
        ),
        advisory=Advisory(
            severity="HIGH",
            language="Hindi",
            message="Cyclone activity detected. Please follow official disaster management advisories.",
        ),
    )


def get_mock_historical_observations(cyclone_id: str) -> List[Dict[str, Any]]:
    now = utc_now()
    return [
        {
            "timestamp": now - timedelta(hours=24),
            "observation_type": "satellite",
            "latitude": 14.2,
            "longitude": 72.0,
            "wind_speed": 95.0,
            "pressure": 988.0,
            "confidence": 0.90,
        },
        {
            "timestamp": now - timedelta(hours=18),
            "observation_type": "buoy",
            "latitude": 14.7,
            "longitude": 72.5,
            "wind_speed": 102.0,
            "pressure": 985.0,
            "confidence": 0.91,
        },
        {
            "timestamp": now - timedelta(hours=12),
            "observation_type": "satellite",
            "latitude": 15.1,
            "longitude": 73.0,
            "wind_speed": 112.0,
            "pressure": 982.0,
            "confidence": 0.93,
        },
        {
            "timestamp": now - timedelta(hours=6),
            "observation_type": "satellite",
            "latitude": 15.52,
            "longitude": 73.21,
            "wind_speed": 120.0,
            "pressure": 980.0,
            "confidence": 0.94,
        },
    ]


def get_mock_historical_predictions(cyclone_id: str) -> List[Dict[str, Any]]:
    now = utc_now()
    return [
        {
            "timestamp": now - timedelta(hours=18),
            "observation_type": "intensity",
            "wind_speed": 106.0,
            "confidence": 0.82,
            "details": {"intensity_category": "Cyclonic Storm"},
        },
        {
            "timestamp": now - timedelta(hours=12),
            "observation_type": "intensity",
            "wind_speed": 122.0,
            "confidence": 0.84,
            "details": {"intensity_category": "Severe Cyclonic Storm"},
        },
        {
            "timestamp": now - timedelta(hours=6),
            "observation_type": "track",
            "latitude": 18.8,
            "longitude": 76.0,
            "confidence": 0.87,
            "details": {"forecast_hours": 48},
        },
        {
            "timestamp": now,
            "observation_type": "intensity",
            "wind_speed": 145.2,
            "confidence": 0.87,
            "details": {"intensity_category": "Severe Cyclonic Storm"},
        },
    ]
