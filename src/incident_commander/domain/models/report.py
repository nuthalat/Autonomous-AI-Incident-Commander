"""Final incident report models with fact/inference separation."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from incident_commander.domain.types import ConfidenceScore, NonEmptyStr


class ObservedFact(BaseModel):
    """An observed fact that must cite supporting evidence IDs."""

    model_config = ConfigDict(extra="forbid")

    statement: NonEmptyStr
    evidence_ids: list[str] = Field(min_length=1)
    confidence: ConfidenceScore = 1.0


class InferredConclusion(BaseModel):
    """An inferred conclusion distinct from raw observations."""

    model_config = ConfigDict(extra="forbid")

    statement: NonEmptyStr
    based_on_fact_indices: list[int] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceScore
    reasoning: str | None = None


class UnresolvedUncertainty(BaseModel):
    """Explicit gap or unresolved question remaining after investigation."""

    model_config = ConfigDict(extra="forbid")

    statement: NonEmptyStr
    missing_evidence: list[str] = Field(default_factory=list)
    impact_on_confidence: ConfidenceScore | None = None


class FinalIncidentReport(BaseModel):
    """Evidence-backed final report distinguishing facts from inferences."""

    model_config = ConfigDict(extra="forbid")

    report_id: NonEmptyStr
    incident_id: NonEmptyStr
    generated_at: datetime
    title: NonEmptyStr
    executive_summary: NonEmptyStr
    observed_facts: list[ObservedFact] = Field(default_factory=list)
    inferred_conclusions: list[InferredConclusion] = Field(default_factory=list)
    unresolved_uncertainty: list[UnresolvedUncertainty] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    approved_actions: list[str] = Field(default_factory=list)
    executed_actions: list[str] = Field(default_factory=list)
    leading_hypothesis_id: str | None = None
    overall_confidence: ConfidenceScore
    evidence_ids_cited: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _facts_require_evidence_and_citations_consistent(self) -> FinalIncidentReport:
        if not self.observed_facts and self.overall_confidence > 0.8:
            raise ValueError(
                "high-confidence reports must include at least one observed fact with evidence"
            )

        for fact in self.observed_facts:
            if not fact.evidence_ids:
                raise ValueError("observed facts must reference at least one evidence_id")

        for conclusion in self.inferred_conclusions:
            for index in conclusion.based_on_fact_indices:
                if index < 0 or index >= len(self.observed_facts):
                    raise ValueError(
                        f"based_on_fact_indices contains out-of-range index {index}"
                    )

        if self.evidence_ids_cited:
            fact_ids = {eid for fact in self.observed_facts for eid in fact.evidence_ids}
            uncovered = fact_ids - set(self.evidence_ids_cited)
            if uncovered:
                raise ValueError(
                    "evidence_ids_cited must include all observed-fact evidence IDs; "
                    f"missing {sorted(uncovered)}"
                )

        return self
