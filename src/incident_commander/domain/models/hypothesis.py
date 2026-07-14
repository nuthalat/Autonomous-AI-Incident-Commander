"""Root-cause hypothesis models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from incident_commander.domain.enums import HypothesisStatus
from incident_commander.domain.types import ConfidenceScore, NonEmptyStr


class Hypothesis(BaseModel):
    """Competing root-cause hypothesis with evidentiary links."""

    model_config = ConfigDict(extra="forbid")

    hypothesis_id: NonEmptyStr
    statement: NonEmptyStr
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    confidence: ConfidenceScore
    falsification_tests: list[str] = Field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.CANDIDATE
    rank: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _no_overlap_between_support_and_contradiction(self) -> Hypothesis:
        overlap = set(self.supporting_evidence_ids) & set(self.contradicting_evidence_ids)
        if overlap:
            msg = (
                "supporting_evidence_ids and contradicting_evidence_ids overlap: "
                f"{sorted(overlap)}"
            )
            raise ValueError(msg)
        return self
