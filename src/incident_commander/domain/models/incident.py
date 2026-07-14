"""Incident intake and symptom models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from incident_commander.domain.enums import Severity
from incident_commander.domain.types import ConfidenceScore, NonEmptyStr


class Symptom(BaseModel):
    """Observable symptom reported or discovered during intake."""

    model_config = ConfigDict(extra="forbid")

    symptom_id: NonEmptyStr
    description: NonEmptyStr
    service: NonEmptyStr | None = None
    first_seen_at: datetime | None = None
    confidence: ConfidenceScore = 1.0
    tags: list[str] = Field(default_factory=list)


class Incident(BaseModel):
    """Normalized incident report accepted by the platform."""

    model_config = ConfigDict(extra="forbid")

    incident_id: NonEmptyStr
    title: NonEmptyStr
    description: NonEmptyStr
    reported_at: datetime
    severity: Severity = Severity.UNKNOWN
    reporter: str | None = None
    environment: str = "production"
    affected_services: list[str] = Field(default_factory=list)
    symptoms: list[Symptom] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source: str = "api"
    metadata: dict[str, str] = Field(default_factory=dict)
