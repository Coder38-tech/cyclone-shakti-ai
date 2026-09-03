from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.exceptions import ModelInferenceError
from app.ml.base_model import BaseModel
from app.models.schemas import ForecastPoint
from app.utils.geojson import validate_coordinates


class TrajectoryModel(BaseModel):
    """Cyclone track / trajectory forecasting interface."""

    def __init__(self, model_path: Optional[str] = None):
        super().__init__(name="trajectory", model_path=model_path)

    def _load_impl(self, path: Path) -> Any:
        suffix = path.suffix.lower()
        if suffix in {".pth", ".pt"}:  # pragma: no cover
            try:
                import torch  # type: ignore
                return torch.load(path, map_location="cpu")
            except ImportError as exc:
                raise ModelInferenceError("PyTorch is not installed", details={"missing": "torch"}) from exc
        if suffix in {".h5", ".pb"}:  # pragma: no cover
            try:
                from tensorflow import keras  # type: ignore
                return keras.models.load_model(path)
            except ImportError as exc:
                raise ModelInferenceError("TensorFlow is not installed", details={"missing": "tensorflow"}) from exc
        if suffix in {".pkl", ".joblib"}:  # pragma: no cover
            try:
                import joblib  # type: ignore
                return joblib.load(path)
            except ImportError as exc:
                raise ModelInferenceError("scikit-learn helpers not installed", details={"missing": "joblib"}) from exc
        if suffix == ".onnx":  # pragma: no cover
            try:
                import onnxruntime as ort  # type: ignore
                return ort.InferenceSession(str(path))
            except ImportError as exc:
                raise ModelInferenceError("ONNX runtime not installed", details={"missing": "onnxruntime"}) from exc
        raise ModelInferenceError(f"Unsupported trajectory model format: {suffix}")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required = {"cyclone_id", "current_position", "current_wind_speed", "forecast_hours"}
        missing = [k for k in required if input_data.get(k) is None]
        if missing:
            raise ModelInferenceError(
                f"Missing fields for track prediction: {missing}",
                details={"missing": missing},
            )
        pos = input_data["current_position"]
        try:
            validate_coordinates(float(pos["latitude"]), float(pos["longitude"]))
        except Exception as exc:
            raise ModelInferenceError("Invalid current_position coordinates") from exc
        if not (6 <= int(input_data["forecast_hours"]) <= 240):
            raise ModelInferenceError("forecast_hours must be between 6 and 240 hours")

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_loaded()
        self.validate_input(input_data)
        raise NotImplementedError("Concrete trajectory model must override predict()")


class MockTrajectoryModel(TrajectoryModel):
    """Deterministic mock — advects the cyclone N/NE with a curved path."""

    def __init__(self):
        super().__init__(model_path=None)
        self._loaded = True

    @property
    def is_mock(self) -> bool:
        return True

    def load(self) -> bool:
        self._loaded = True
        return True

    @staticmethod
    def _time_steps(forecast_hours: int) -> List[int]:
        hours = sorted({0, 12, 24, 48, 72, 96, 120, forecast_hours})
        return [h for h in hours if 0 <= h <= forecast_hours]

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_loaded()
        self.validate_input(input_data)

        pos = input_data["current_position"]
        lat0 = float(pos["latitude"])
        lon0 = float(pos["longitude"])
        wind0 = float(input_data["current_wind_speed"])
        forecast_hours = int(input_data["forecast_hours"])
        pressure = float(input_data.get("pressure") or 1000.0)

        seed_key = int(lat0 * 10000 + lon0 * 100 + wind0)
        rng = np.random.default_rng(seed=abs(seed_key) % (2**31 - 1))

        speed_kn = wind0 / 1.852
        translational_km_per_h = np.clip(0.03 * speed_kn + 4.0, 4.0, 22.0)
        pressure_component = np.clip((1010.0 - pressure) / 10.0, 0.0, 3.0)
        translational_km_per_h += pressure_component

        km_per_deg_lat = 111.0
        km_per_deg_lon = 111.0 * np.cos(np.radians(lat0))

        points: List[ForecastPoint] = []
        for h in self._time_steps(forecast_hours):
            t = h / 48.0
            base_bearing = np.radians(25.0 + 20.0 * np.sin(t * np.pi / 2.0))
            jitter = rng.normal(0, 0.05, size=2)
            dist_km = translational_km_per_h * h
            dlat = (dist_km * np.cos(base_bearing) / km_per_deg_lat) + jitter[0]
            dlon = (dist_km * np.sin(base_bearing) / max(0.01, km_per_deg_lon)) + jitter[1]

            lat = float(np.clip(lat0 + dlat, -80.0, 80.0))
            lon = float(np.clip(lon0 + dlon, -179.9, 179.9))

            intensify = np.clip(0.08 * wind0 * np.sin(np.clip(t, 0, 1) * np.pi) + rng.normal(0, 1.5), -15.0, 40.0)
            ws = float(np.clip(wind0 + intensify, 0.0, 300.0))

            points.append(ForecastPoint(hour=h, latitude=round(lat, 4), longitude=round(lon, 4), wind_speed=round(ws, 2)))

        return {
            "cyclone_id": input_data["cyclone_id"],
            "forecast_hours": forecast_hours,
            "forecast_points": points,
        }
