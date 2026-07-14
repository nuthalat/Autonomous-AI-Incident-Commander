"""Customer and system impact assessment models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from incident_commander.domain.enums import Severity
from incident_commander.domain.types import ConfidenceScore, NonEmptyStr


class ImpactAssessment(BaseModel):
    """Estimated blast radius for customers and systems."""

    model_config = ConfigDict(extra="forbid")

    summary: NonEmptyStr
    severity: Severity
    affected_services: list[str] = Field(default_factory=list)
    estimated_affected_users: int | None = Field(default=None, ge=0)
    customer_impact: NonEmptyStr
    system_impact: NonEmptyStr
    confidence: ConfidenceScore
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    time_to_mitigation_minutes: int | None = Field(default=None, ge=0)
