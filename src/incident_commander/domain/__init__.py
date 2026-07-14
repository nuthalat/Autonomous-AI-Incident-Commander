"""Domain types, enums, and exception hierarchy."""

from incident_commander.domain.exceptions import (
    AgentError,
    ApprovalDeniedError,
    ConfigurationError,
    DependencyUnavailableError,
    IncidentCommanderError,
    ModelError,
    ModelTimeoutError,
    SafetyError,
    ValidationFailureError,
)

__all__ = [
    "AgentError",
    "ApprovalDeniedError",
    "ConfigurationError",
    "DependencyUnavailableError",
    "IncidentCommanderError",
    "ModelError",
    "ModelTimeoutError",
    "SafetyError",
    "ValidationFailureError",
]
