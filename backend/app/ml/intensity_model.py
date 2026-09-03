from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from app.core.exceptions import ModelInferenceError
from app.ml.base_model import BaseModel
from app.utils.validation import classify_intensity


class IntensityModel(BaseModel):
    """Wind speed / intensity-category regression model interface."""

    def __init__(self, model_path: Optional[str] = None):
        super().__init__(name="intensity", model_path=model_path)

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
        raise ModelInferenceError(f"Unsupported intensity model format: {suffix}")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required = {"cyclone_id", "latitude", "longitude", "current_wind_speed"}
        missing = [k for k in required if input_data.get(k) is None]
        if missing:
            raise ModelInferenceError(
                f"Missing fields for intensity prediction: {missing}",
                details={"missing": missing},
            )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_loaded()
        self.validate_input(input_data)
        raise NotImplementedError("Concrete intensity model must override predict()")


class MockIntensityModel(IntensityModel):
    """Deterministic mock — projects current wind speed forward and classifies."""

    def __init__(self):
        super().__init__(model_path=None)
        self._loaded = True

    @property
    def is_mock(self) -> bool:
        return True

    def load(self) -> bool:
        self._loaded = True
        return True

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_loaded()
        self.validate_input(input_data)
        wind = float(input_data["current_wind_speed"])
        pressure = float(input_data.get("pressure") or 1000.0)
        temp = float(input_data.get("temperature") or 28.0)
        humidity = float(input_data.get("humidity") or 70.0)

        rng = np.random.default_rng(seed=abs(int(wind * 100 + pressure)) % (2**31 - 1))

        pressure_deficit = max(0.0, 1010.0 - pressure)
        warm_factor = max(0.0, temp - 26.0) / 10.0
        humid_factor = max(0.0, humidity - 60.0) / 60.0
        intensification = pressure_deficit * 0.18 + warm_factor * 18.0 + humid_factor * 10.0 + rng.normal(0, 2.5)

        predicted_wind = float(np.clip(wind + intensification, 0.0, 300.0))
        category = classify_intensity(predicted_wind)
        confidence = float(np.clip(0.72 + rng.normal(0, 0.06), 0.5, 0.98))

        return {
            "cyclone_id": input_data["cyclone_id"],
            "predicted_wind_speed": round(predicted_wind, 2),
            "intensity_category": category,
            "confidence": round(confidence, 4),
        }
