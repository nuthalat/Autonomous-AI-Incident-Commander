"""Incident phase transition validation and remediation execution gates."""

from __future__ import annotations

from incident_commander.domain.enums import (
    ApprovalStatus,
    IncidentPhase,
    RemediationActionType,
)
from incident_commander.domain.exceptions import (
    ApprovalDeniedError,
    InvalidStateTransitionError,
)
from incident_commander.domain.models.remediation import RemediationAction
from incident_commander.domain.models.state import IncidentState

# Phases considered part of active investigation (pre-impact).
INVESTIGATION_PHASES: frozenset[IncidentPhase] = frozenset(
    {
        IncidentPhase.INTAKE,
        IncidentPhase.PLANNING,
        IncidentPhase.TOPOLOGY,
        IncidentPhase.PARALLEL_INVESTIGATION,
        IncidentPhase.EVIDENCE_AGGREGATION,
        IncidentPhase.HYPOTHESIS_GENERATION,
        IncidentPhase.SKEPTIC_REVIEW,
        IncidentPhase.REINVESTIGATION,
    }
)

# Phases where write/destructive execution is never allowed.
PRE_APPROVAL_PHASES: frozenset[IncidentPhase] = frozenset(
    {
        *INVESTIGATION_PHASES,
        IncidentPhase.IMPACT_ANALYSIS,
        IncidentPhase.REMEDIATION_PLANNING,
        IncidentPhase.SAFETY_VALIDATION,
        IncidentPhase.HUMAN_APPROVAL,
    }
)

ALLOWED_TRANSITIONS: dict[IncidentPhase, frozenset[IncidentPhase]] = {
    IncidentPhase.INTAKE: frozenset({IncidentPhase.PLANNING, IncidentPhase.FAILED}),
    IncidentPhase.PLANNING: frozenset({IncidentPhase.TOPOLOGY, IncidentPhase.FAILED}),
    IncidentPhase.TOPOLOGY: frozenset(
        {IncidentPhase.PARALLEL_INVESTIGATION, IncidentPhase.FAILED}
    ),
    IncidentPhase.PARALLEL_INVESTIGATION: frozenset(
        {IncidentPhase.EVIDENCE_AGGREGATION, IncidentPhase.FAILED}
    ),
    IncidentPhase.EVIDENCE_AGGREGATION: frozenset(
        {IncidentPhase.HYPOTHESIS_GENERATION, IncidentPhase.FAILED}
    ),
    IncidentPhase.HYPOTHESIS_GENERATION: frozenset(
        {IncidentPhase.SKEPTIC_REVIEW, IncidentPhase.FAILED}
    ),
    IncidentPhase.SKEPTIC_REVIEW: frozenset(
        {
            IncidentPhase.REINVESTIGATION,
            IncidentPhase.IMPACT_ANALYSIS,
            IncidentPhase.FAILED,
        }
    ),
    IncidentPhase.REINVESTIGATION: frozenset(
        {
            IncidentPhase.PARALLEL_INVESTIGATION,
            IncidentPhase.EVIDENCE_AGGREGATION,
            IncidentPhase.FAILED,
        }
    ),
    IncidentPhase.IMPACT_ANALYSIS: frozenset(
        {IncidentPhase.REMEDIATION_PLANNING, IncidentPhase.FAILED}
    ),
    IncidentPhase.REMEDIATION_PLANNING: frozenset(
        {IncidentPhase.SAFETY_VALIDATION, IncidentPhase.FAILED}
    ),
    IncidentPhase.SAFETY_VALIDATION: frozenset(
        {
            IncidentPhase.HUMAN_APPROVAL,
            IncidentPhase.FINAL_REPORT,  # read-only / no-action path
            IncidentPhase.FAILED,
        }
    ),
    IncidentPhase.HUMAN_APPROVAL: frozenset(
        {
            IncidentPhase.APPROVED_WRITES,
            IncidentPhase.FINAL_REPORT,  # rejected or no writes
            IncidentPhase.FAILED,
        }
    ),
    IncidentPhase.APPROVED_WRITES: frozenset(
        {IncidentPhase.FINAL_REPORT, IncidentPhase.FAILED}
    ),
    IncidentPhase.FINAL_REPORT: frozenset({IncidentPhase.COMPLETED, IncidentPhase.FAILED}),
    IncidentPhase.COMPLETED: frozenset(),
    IncidentPhase.FAILED: frozenset(),
}


def validate_phase_transition(
    current: IncidentPhase,
    target: IncidentPhase,
) -> None:
    """Raise if transitioning from ``current`` to ``target`` is illegal.

    Notably, investigation phases cannot jump directly to ``approved_writes``
    or any action-execution phase.
    """
    if current is target:
        return

    # Hard safety rule: never jump from investigation straight to execution.
    if current in INVESTIGATION_PHASES and target is IncidentPhase.APPROVED_WRITES:
        raise InvalidStateTransitionError(
            "Cannot transition directly from investigation to action execution; "
            "approval is required",
            details={"from": current.value, "to": target.value},
        )

    allowed = ALLOWED_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        raise InvalidStateTransitionError(
            f"Illegal phase transition: {current.value} -> {target.value}",
            details={
                "from": current.value,
                "to": target.value,
                "allowed": sorted(phase.value for phase in allowed),
            },
        )


def transition_phase(state: IncidentState, target: IncidentPhase) -> IncidentState:
    """Return a copy of ``state`` advanced to ``target`` after validation."""
    validate_phase_transition(state.current_phase, target)
    return state.model_copy(update={"current_phase": target})


def action_requires_approval(action: RemediationAction) -> bool:
    """Return whether an action is gated on human approval."""
    if action.action_type in {
        RemediationActionType.NO_ACTION,
        RemediationActionType.INVESTIGATE_FURTHER,
    }:
        return False
    return action.requires_approval or action.is_destructive


def assert_can_execute_remediation(
    state: IncidentState,
    action: RemediationAction,
    *,
    approval_token: str | None = None,
) -> None:
    """Enforce approval and phase gates before executable remediation.

    Raises:
        ApprovalDeniedError: when approval/token/phase requirements are unmet.
        InvalidStateTransitionError: when the current phase forbids execution.
    """
    if state.current_phase in PRE_APPROVAL_PHASES:
        raise InvalidStateTransitionError(
            "Executable remediation is not allowed before approved_writes phase",
            details={"phase": state.current_phase.value, "action_id": action.action_id},
        )

    if state.current_phase not in {
        IncidentPhase.APPROVED_WRITES,
        IncidentPhase.FINAL_REPORT,
    }:
        raise InvalidStateTransitionError(
            f"Executable remediation forbidden in phase {state.current_phase.value}",
            details={"phase": state.current_phase.value, "action_id": action.action_id},
        )

    if not action_requires_approval(action):
        return

    if state.approval_status is not ApprovalStatus.APPROVED and not state.has_approved_actions():
        raise ApprovalDeniedError(
            "Human approval required before executing remediation",
            details={"action_id": action.action_id},
        )

    matching = [
        request
        for request in state.approval_requests
        if request.status is ApprovalStatus.APPROVED and action.action_id in request.action_ids
    ]
    if not matching:
        raise ApprovalDeniedError(
            "No approved approval request covers this action",
            details={"action_id": action.action_id},
        )

    if approval_token is None:
        raise ApprovalDeniedError(
            "Approval token required for executable remediation",
            details={"action_id": action.action_id},
        )

    if not any(request.approval_token == approval_token for request in matching):
        raise ApprovalDeniedError(
            "Approval token is invalid for this action",
            details={"action_id": action.action_id},
        )
