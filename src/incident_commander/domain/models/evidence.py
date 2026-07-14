"""Evidence item model collected during investigation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from incident_commander.domain.enums import EvidenceSource, RedactionStatus
from incident_commander.domain.types import ConfidenceScore, NonEmptyStr


class Evidence(BaseModel):
    """A single piece of investigation evidence with provenance."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: NonEmptyStr
    source: EvidenceSource
    tool_name: NonEmptyStr
    query_or_parameters: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    finding: NonEmptyStr
    confidence: ConfidenceScore
    evidence_uri: HttpUrl | NonEmptyStr
    raw_reference_id: NonEmptyStr
    redaction_status: RedactionStatus = RedactionStatus.NOT_REQUIRED
    related_services: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
