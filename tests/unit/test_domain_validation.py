"""Invalid-input validation tests for domain models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from incident_commander.domain.enums import EvidenceSource, RemediationActionType
from incident_commander.domain.models import (
    Evidence,
    FinalIncidentReport,
    Hypothesis,
    ObservedFact,
    RemediationAction,
)


def test_confidence_score_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            evidence_id="ev-bad",
            source=EvidenceSource.METRICS,
            tool_name="query_metric",
            timestamp=datetime.now(UTC),
            finding="x",
            confidence=1.5,
            evidence_uri="fixture://x",
            raw_reference_id="x",
        )


def test_hypothesis_rejects_overlapping_evidence_ids() -> None:
    with pytest.raises(ValidationError):
        Hypothesis(
            hypothesis_id="h1",
            statement="test",
            supporting_evidence_ids=["ev-1"],
            contradicting_evidence_ids=["ev-1"],
            confidence=0.5,
        )


def test_observed_fact_requires_evidence_reference() -> None:
    with pytest.raises(ValidationError):
        ObservedFact(statement="fact without evidence", evidence_ids=[])


def test_final_report_requires_evidence_for_facts() -> None:
    with pytest.raises(ValidationError):
        FinalIncidentReport(
            report_id="r1",
            incident_id="inc-1",
            generated_at=datetime.now(UTC),
            title="t",
            executive_summary="s",
            observed_facts=[
                ObservedFact(statement="unsupported", evidence_ids=[]),
            ],
            overall_confidence=0.5,
        )


def test_destructive_action_must_require_approval() -> None:
    with pytest.raises(ValidationError):
        RemediationAction(
            action_id="a1",
            action_type=RemediationActionType.ROLLBACK,
            title="Rollback",
            description="Roll back service",
            is_destructive=True,
            requires_approval=False,
            is_safe=True,
        )
