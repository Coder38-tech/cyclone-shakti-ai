from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from app.core.exceptions import ModelInferenceError
from app.core.logging_config import get_logger
from app.ml.base_model import BaseModel
from app.ml.detection_model import DetectionModel, MockDetectionModel
from app.ml.intensity_model import IntensityModel, MockIntensityModel
from app.ml.trajectory_model import TrajectoryModel, MockTrajectoryModel

logger = get_logger("ml.model_loader")


_MODEL_FILE_EXTENSIONS = {
    ".pth": "pytorch",
    ".pt": "pytorch",
    ".h5": "tensorflow",
    ".pb": "tensorflow",
    ".pkl": "sklearn",
    ".joblib": "sklearn",
    ".onnx": "onnx",
}


class ModelLoader:
    """Loads ML models once at startup; falls back to mock implementations.

    Intentionally avoids importing PyTorch/TensorFlow/Sklearn/ONNX at module
    import time — only the concrete real-model subclasses do so, which keeps
    the default install lean and lets the ML teammate plug in real models
    incrementally.
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.detection: DetectionModel = MockDetectionModel()
        self.intensity: IntensityModel = MockIntensityModel()
        self.trajectory: TrajectoryModel = MockTrajectoryModel()

    @staticmethod
    def _detect_backend(path: Path) -> Optional[str]:
        return _MODEL_FILE_EXTENSIONS.get(path.suffix.lower())

    def _find_candidate(self, filename_tokens: set[str]) -> Optional[Path]:
        for candidate in sorted(self.models_dir.glob("*")):
            if not candidate.is_file():
                continue
            stem = candidate.stem.lower()
            if any(token in stem for token in filename_tokens):
                return candidate
        return None

    def load_all(self) -> Dict[str, Any]:
        status: Dict[str, Any] = {}

        det_candidate = self._find_candidate({"detection", "detect", "yolo", "cv", "satellite"})
        if det_candidate is not None:
            self.detection = DetectionModel(model_path=str(det_candidate))
        det_ok = self.detection.load()
        status["detection"] = {"loaded": det_ok, "mock": isinstance(self.detection, MockDetectionModel) or not det_ok}

        int_candidate = self._find_candidate({"intensity", "wind", "regression"})
        if int_candidate is not None:
            self.intensity = IntensityModel(model_path=str(int_candidate))
        int_ok = self.intensity.load()
        status["intensity"] = {"loaded": int_ok, "mock": isinstance(self.intensity, MockIntensityModel) or not int_ok}

        traj_candidate = self._find_candidate({"trajectory", "track", "forecast", "lstm", "seq"})
        if traj_candidate is not None:
            self.trajectory = TrajectoryModel(model_path=str(traj_candidate))
        traj_ok = self.trajectory.load()
        status["trajectory"] = {"loaded": traj_ok, "mock": isinstance(self.trajectory, MockTrajectoryModel) or not traj_ok}

        logger.info("Model loading complete: %s", status)
        return status

    def get(self, kind: str) -> BaseModel:
        if kind == "detection":
            return self.detection
        if kind == "intensity":
            return self.intensity
        if kind == "trajectory":
            return self.trajectory
        raise ModelInferenceError(f"Unknown model kind: {kind}")


_loader: Optional[ModelLoader] = None


def get_model_loader(models_dir: str = "models") -> ModelLoader:
    global _loader
    if _loader is None:
        _loader = ModelLoader(models_dir=models_dir)
        _loader.load_all()
    return _loader


def reset_model_loader() -> None:
    global _loader
    _loader = None
