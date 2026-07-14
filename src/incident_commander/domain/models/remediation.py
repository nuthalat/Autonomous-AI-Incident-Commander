"""Remediation actions and human approval models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from incident_commander.domain.enums import (
    ApprovalDecision,
    ApprovalStatus,
    RemediationActionType,
)
from incident_commander.domain.types import ConfidenceScore, NonEmptyStr


class RemediationAction(BaseModel):
    """A proposed remediation option with safety metadata."""

    model_config = ConfigDict(extra="forbid")

    action_id: NonEmptyStr
    action_type: RemediationActionType
    title: NonEmptyStr
    description: NonEmptyStr
    target_services: list[str] = Field(default_factory=list)
    is_destructive: bool = False
    requires_approval: bool = True
    is_safe: bool = True
    reversible: bool = True
    confidence: ConfidenceScore = 0.5
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    risk_notes: str | None = None
    dry_run_supported: bool = True

    @model_validator(mode="after")
    def _destructive_requires_approval(self) -> RemediationAction:
        if self.is_destructive and not self.requires_approval:
            raise ValueError("destructive remediation actions must require approval")
        return self


class ApprovalRequest(BaseModel):
    """Human-in-the-loop approval request for write/destructive actions."""

    model_config = ConfigDict(extra="forbid")

    request_id: NonEmptyStr
    action_ids: list[str] = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision: ApprovalDecision | None = None
    requested_at: datetime
    decided_at: datetime | None = None
    expires_at: datetime
    approval_token: str | None = None
    decided_by: str | None = None
    rationale: str | None = None

    @model_validator(mode="after")
    def _decision_matches_status(self) -> ApprovalRequest:
        if self.decision is ApprovalDecision.APPROVE and self.status != ApprovalStatus.APPROVED:
            raise ValueError("approve decision requires status=approved")
        if self.decision is ApprovalDecision.REJECT and self.status != ApprovalStatus.REJECTED:
            raise ValueError("reject decision requires status=rejected")
        if self.status is ApprovalStatus.APPROVED and not self.approval_token:
            raise ValueError("approved requests must include an approval_token")
        return self
