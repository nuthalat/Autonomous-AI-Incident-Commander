"""Shared LangGraph investigation state."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from incident_commander.domain.enums import ApprovalStatus, IncidentPhase, Severity
from incident_commander.domain.models.evidence import Evidence
from incident_commander.domain.models.execution import ExecutionRecord
from incident_commander.domain.models.hypothesis import Hypothesis
from incident_commander.domain.models.impact import ImpactAssessment
from incident_commander.domain.models.investigation import InvestigationPlan
from incident_commander.domain.models.remediation import ApprovalRequest, RemediationAction
from incident_commander.domain.models.report import FinalIncidentReport
from incident_commander.domain.types import NonEmptyStr


class IncidentState(BaseModel):
    """Strongly typed shared state for the investigation graph.

    Parallel investigators append to ``evidence`` via
    :func:`incident_commander.domain.reducers.reduce_evidence`.
    """

    model_config = ConfigDict(extra="forbid")

    incident_id: NonEmptyStr
    title: NonEmptyStr
    description: NonEmptyStr
    reported_at: datetime
    severity: Severity = Severity.UNKNOWN
    affected_services: list[str] = Field(default_factory=list)
    symptoms: list[str] = Field(default_factory=list)
    investigation_plan: InvestigationPlan | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    impact_assessment: ImpactAssessment | None = None
    proposed_actions: list[RemediationAction] = Field(default_factory=list)
    approval_requests: list[ApprovalRequest] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    current_phase: IncidentPhase = IncidentPhase.INTAKE
    retry_count: int = Field(default=0, ge=0)
    reinvestigation_count: int = Field(default=0, ge=0)
    execution_history: list[ExecutionRecord] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    final_report: FinalIncidentReport | None = None
    dry_run: bool = True
    read_only: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("evidence")
    @classmethod
    def _unique_evidence_ids(cls, value: list[Evidence]) -> list[Evidence]:
        seen: set[str] = set()
        for item in value:
            if item.evidence_id in seen:
                raise ValueError(f"duplicate evidence_id: {item.evidence_id}")
            seen.add(item.evidence_id)
        return value

    @field_validator("hypotheses")
    @classmethod
    def _unique_hypothesis_ids(cls, value: list[Hypothesis]) -> list[Hypothesis]:
        seen: set[str] = set()
        for item in value:
            if item.hypothesis_id in seen:
                raise ValueError(f"duplicate hypothesis_id: {item.hypothesis_id}")
            seen.add(item.hypothesis_id)
        return value

    def evidence_ids(self) -> set[str]:
        """Return the set of evidence IDs currently in state."""
        return {item.evidence_id for item in self.evidence}

    def has_approved_actions(self) -> bool:
        """Return True when at least one approval request is approved."""
        return any(
            request.status is ApprovalStatus.APPROVED for request in self.approval_requests
        ) or self.approval_status is ApprovalStatus.APPROVED
