from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base: Any = declarative_base()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CycloneDB(Base):
    __tablename__ = "cyclones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cyclone_id = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    observations = relationship("ObservationDB", back_populates="cyclone", cascade="all, delete-orphan")
    predictions = relationship("PredictionDB", back_populates="cyclone", cascade="all, delete-orphan")
    forecast_points = relationship("ForecastPointDB", back_populates="cyclone", cascade="all, delete-orphan")
    alerts = relationship("AlertDB", back_populates="cyclone", cascade="all, delete-orphan")


class ObservationDB(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cyclone_id = Column(String(32), ForeignKey("cyclones.cyclone_id"), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    observation_type = Column(String(64), nullable=False, default="satellite")
    timestamp = Column(DateTime, default=_utcnow, nullable=False)
    raw_data = Column(Text, nullable=True)

    cyclone = relationship("CycloneDB", back_populates="observations")


class PredictionDB(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cyclone_id = Column(String(32), ForeignKey("cyclones.cyclone_id"), nullable=False, index=True)
    prediction_type = Column(String(64), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    intensity_category = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=True)
    forecast_hours = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=_utcnow, nullable=False)
    model_name = Column(String(128), nullable=True)

    cyclone = relationship("CycloneDB", back_populates="predictions")
    forecast_points = relationship("ForecastPointDB", back_populates="prediction", cascade="all, delete-orphan")


class ForecastPointDB(Base):
    __tablename__ = "forecast_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cyclone_id = Column(String(32), ForeignKey("cyclones.cyclone_id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True, index=True)
    hour = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)

    cyclone = relationship("CycloneDB", back_populates="forecast_points")
    prediction = relationship("PredictionDB", back_populates="forecast_points")


class AlertDB(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cyclone_id = Column(String(32), ForeignKey("cyclones.cyclone_id"), nullable=False, index=True)
    severity = Column(String(16), nullable=False)
    triggered = Column(Boolean, default=True, nullable=False)
    reason = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String(16), nullable=False, default="English")
    timestamp = Column(DateTime, default=_utcnow, nullable=False)

    cyclone = relationship("CycloneDB", back_populates="alerts")
