from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from app.core.exceptions import ModelInferenceError
from app.ml.base_model import BaseModel
from app.utils.helpers import generate_cyclone_id


class DetectionModel(BaseModel):
    """Cyclone detection model interface.

    Real CV/satellite subclasses only need to implement `_load_impl` and
    override `predict`; the routes never need to change.
    """

    def __init__(self, model_path: Optional[str] = None):
        super().__init__(name="detection", model_path=model_path)

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
        raise ModelInferenceError(f"Unsupported detection model format: {suffix}")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        has_loc = input_data.get("latitude") is not None and input_data.get("longitude") is not None
        has_image = bool(input_data.get("image_path"))
        if not (has_loc or has_image):
            raise ModelInferenceError(
                "Detection request must provide (latitude, longitude) or image_path",
                details={"received_keys": list(input_data.keys())},
            )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_loaded()
        self.validate_input(input_data)
        # Real subclass: run actual CV inference, return bbox + confidences.
        raise NotImplementedError("Concrete detection model must override predict()")


class MockDetectionModel(DetectionModel):
    """Deterministic mock — returns plausible detection output for demo purposes."""

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
        lat = float(input_data.get("latitude") or 15.52)
        lon = float(input_data.get("longitude") or 73.21)
        image_path = input_data.get("image_path")
        rng = np.random.default_rng(
            seed=abs(int((lat * 1e6) + (lon * 1e3))) % (2**31 - 1)
        )
        base_conf = 0.82 if not image_path else 0.9
        conf = float(np.clip(base_conf + rng.normal(0, 0.04), 0.5, 0.99))
        detected = conf > 0.55
        return {
            "cyclone_detected": detected,
            "confidence": round(conf, 4),
            "center": {"latitude": round(lat, 4), "longitude": round(lon, 4)},
            "cyclone_id": generate_cyclone_id() if detected else None,
        }
