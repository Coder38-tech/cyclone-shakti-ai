from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.exceptions import ModelInferenceError
from app.core.logging_config import get_logger

logger = get_logger("ml.base")


class BaseModel(ABC):
    """Abstract interface that every ML/CV/trajectory model must implement.

    Models are loaded once on startup (see model_loader.py). If a real model
    file is missing or loading fails, we fall back to the Mock*Model
    implementations below so the API stays online.
    """

    def __init__(self, name: str, model_path: Optional[str] = None):
        self.name = name
        self.model_path = model_path
        self._model: Any = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def is_mock(self) -> bool:
        return False

    def load(self) -> bool:
        """Load model weights into memory. Returns True on success."""
        if self._loaded:
            return True
        path = self._resolve_path()
        if path is None or not path.exists():
            logger.warning(
                "[%s] Real model file not found at %s — falling back to mock inference.",
                self.name,
                path,
            )
            self._loaded = True
            return False
        try:
            self._model = self._load_impl(path)
            self._loaded = True
            logger.info("[%s] Model loaded successfully from %s", self.name, path)
            return True
        except Exception as exc:  # pragma: no cover - real ML failures are environment-dependent
            logger.exception("[%s] Failed to load real model, using mock fallback: %s", self.name, exc)
            self._loaded = True
            return False

    def _resolve_path(self) -> Optional[Path]:
        if not self.model_path:
            return None
        return Path(self.model_path)

    @abstractmethod
    def _load_impl(self, path: Path) -> Any:
        """Subclass hook — actually deserialize the model file."""

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Raise ModelInferenceError if the input dict is missing shape/fields."""

    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference; returns domain-specific prediction dict."""

    def _require_loaded(self) -> None:
        if not self._loaded:
            raise ModelInferenceError(f"Model '{self.name}' is not loaded", details={"step": "before predict"})
