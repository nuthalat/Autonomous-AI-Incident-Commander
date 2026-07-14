"""Tests for the domain exception hierarchy."""

from __future__ import annotations

from incident_commander.domain.exceptions import (
    ApprovalDeniedError,
    IncidentCommanderError,
    ModelTimeoutError,
    SafetyError,
)


def test_exception_to_dict() -> None:
    err = IncidentCommanderError(
        "boom",
        code="test_error",
        details={"service": "checkout-api"},
    )
    assert err.to_dict() == {
        "error": "test_error",
        "message": "boom",
        "details": {"service": "checkout-api"},
    }


def test_approval_denied_is_safety_error() -> None:
    err = ApprovalDeniedError()
    assert isinstance(err, SafetyError)
    assert err.code == "approval_denied"


def test_model_timeout_default_code() -> None:
    err = ModelTimeoutError()
    assert err.code == "model_timeout"
