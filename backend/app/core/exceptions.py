from typing import Any, Dict


class AppError(Exception):
    """Base application exception with a machine-readable code."""

    def __init__(self, message: str, code: str, status_code: int = 500, details: Dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"error": self.message, "code": self.code}
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", code: str = "VALIDATION_ERROR", details: Dict[str, Any] | None = None):
        super().__init__(message, code, status_code=400, details=details)


class CycloneNotFoundError(AppError):
    def __init__(self, cyclone_id: str):
        super().__init__(
            message=f"Cyclone with id '{cyclone_id}' not found",
            code="CYCLONE_NOT_FOUND",
            status_code=404,
        )


class ModelInferenceError(AppError):
    def __init__(self, message: str = "Model inference failed", details: Dict[str, Any] | None = None):
        super().__init__(message, code="MODEL_INFERENCE_ERROR", status_code=503, details=details)


class DatabaseError(AppError):
    def __init__(self, message: str = "Database operation failed", details: Dict[str, Any] | None = None):
        super().__init__(message, code="DATABASE_ERROR", status_code=500, details=details)


class AlertEvaluationError(AppError):
    def __init__(self, message: str = "Alert evaluation failed", details: Dict[str, Any] | None = None):
        super().__init__(message, code="ALERT_EVALUATION_ERROR", status_code=500, details=details)


class UnsupportedLanguageError(AppError):
    def __init__(self, language: str):
        super().__init__(
            message=f"Language '{language}' is not supported",
            code="UNSUPPORTED_LANGUAGE",
            status_code=400,
        )
