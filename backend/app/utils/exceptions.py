from typing import Any, Dict, Optional


class ITMSException(Exception):
    """Base exception for ITMS application."""

    def __init__(
        self,
        message: str,
        code: str = "ITMS_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(ITMSException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="NOT_FOUND", status_code=404, details=details)


class AuthorizationError(ITMSException):
    """Authorization failed."""

    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FORBIDDEN", status_code=403, details=details)


class ValidationError(ITMSException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, details=details)


class AuthenticationError(ITMSException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="UNAUTHORIZED", status_code=401, details=details)


class ConflictError(ITMSException):
    """Resource conflict."""

    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFLICT", status_code=409, details=details)