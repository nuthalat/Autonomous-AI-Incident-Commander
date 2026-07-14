"""State-transition and approval-gate tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from incident_commander.domain.enums import (
    ApprovalDecision,
    ApprovalStatus,
    IncidentPhase,
    RemediationActionType,
    Severity,
)
from incident_commander.domain.exceptions import (
    ApprovalDeniedError,
    InvalidStateTransitionError,
)
from incident_commander.domain.models import (
    ApprovalRequest,
    IncidentState,
    RemediationAction,
)
from incident_commander.domain.transitions import (
    assert_can_execute_remediation,
    transition_phase,
    validate_phase_transition,
)


def _state(phase: IncidentPhase) -> IncidentState:
    return IncidentState(
        incident_id="inc-1",
        title="t",
        description="d",
        reported_at=datetime.now(UTC),
        severity=Severity.SEV2,
        current_phase=phase,
    )


def _action() -> RemediationAction:
    return RemediationAction(
        action_id="act-1",
        action_type=RemediationActionType.ROLLBACK,
        title="Rollback",
        description="Roll back checkout-api",
        is_destructive=True,
        requires_approval=True,
        is_safe=True,
    )


def test_allows_normal_investigation_progression() -> None:
    validate_phase_transition(IncidentPhase.INTAKE, IncidentPhase.PLANNING)
    validate_phase_transition(
        IncidentPhase.SKEPTIC_REVIEW, IncidentPhase.IMPACT_ANALYSIS
    )


def test_prevents_direct_investigation_to_action_execution() -> None:
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        validate_phase_transition(
            IncidentPhase.PARALLEL_INVESTIGATION,
            IncidentPhase.APPROVED_WRITES,
        )
    assert exc_info.value.code == "invalid_state_transition"


def test_transition_phase_updates_state() -> None:
    state = _state(IncidentPhase.INTAKE)
    next_state = transition_phase(state, IncidentPhase.PLANNING)
    assert next_state.current_phase is IncidentPhase.PLANNING
    assert state.current_phase is IncidentPhase.INTAKE


def test_execution_requires_approval_token() -> None:
    now = datetime.now(UTC)
    state = _state(IncidentPhase.APPROVED_WRITES).model_copy(
        update={
            "approval_status": ApprovalStatus.APPROVED,
            "approval_requests": [
                ApprovalRequest(
                    request_id="apr-1",
                    action_ids=["act-1"],
                    status=ApprovalStatus.APPROVED,
                    decision=ApprovalDecision.APPROVE,
                    requested_at=now,
                    decided_at=now,
                    expires_at=now + timedelta(hours=1),
                    approval_token="token-abc",
                    decided_by="human",
                )
            ],
        }
    )
    with pytest.raises(ApprovalDeniedError):
        assert_can_execute_remediation(state, _action(), approval_token=None)

    assert_can_execute_remediation(state, _action(), approval_token="token-abc")


def test_execution_blocked_before_approval_phase() -> None:
    state = _state(IncidentPhase.REMEDIATION_PLANNING)
    with pytest.raises(InvalidStateTransitionError):
        assert_can_execute_remediation(state, _action(), approval_token="token-abc")
