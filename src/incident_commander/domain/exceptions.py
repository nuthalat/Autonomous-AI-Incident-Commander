"""Domain-specific exception hierarchy for Incident Commander."""

from __future__ import annotations

from typing import Any


class IncidentCommanderError(Exception):
    """Base exception for all application errors.

    Attributes:
        message: Human-readable error description.
        code: Stable machine-readable error code.
        details: Optional structured context for logs and API responses.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "incident_commander_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialize the error for structured logging or API payloads."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(IncidentCommanderError):
    """Raised when application configuration is invalid or incomplete."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "configuration_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class ValidationFailureError(IncidentCommanderError):
    """Raised when domain validation fails for structured inputs/outputs."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "validation_failure",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class ModelError(IncidentCommanderError):
    """Raised when an LLM provider call fails in a non-timeout way."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "model_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class ModelTimeoutError(ModelError):
    """Raised when an LLM provider call exceeds the configured timeout."""

    def __init__(
        self,
        message: str = "Model request timed out",
        *,
        code: str = "model_timeout",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class DependencyUnavailableError(IncidentCommanderError):
    """Raised when a required runtime dependency fails a health check."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "dependency_unavailable",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class SafetyError(IncidentCommanderError):
    """Raised when a safety policy blocks an operation."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "safety_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class ApprovalDeniedError(SafetyError):
    """Raised when a write or destructive action lacks valid approval."""

    def __init__(
        self,
        message: str = "Human approval required before executing this action",
        *,
        code: str = "approval_denied",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class AgentError(IncidentCommanderError):
    """Raised when a specialized investigation agent fails fatally."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "agent_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class InvalidStateTransitionError(ValidationFailureError):
    """Raised when an incident phase transition is not allowed."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_state_transition",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)


class FixtureValidationError(ValidationFailureError):
    """Raised when a synthetic incident fixture fails validation."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "fixture_validation_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, details=details)
