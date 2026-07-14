"""Serialization round-trip tests for core domain models."""

from __future__ import annotations

from datetime import UTC, datetime

from incident_commander.domain.enums import (
    EvidenceSource,
    HypothesisStatus,
    IncidentPhase,
    Severity,
)
from incident_commander.domain.models import (
    Evidence,
    FinalIncidentReport,
    Hypothesis,
    Incident,
    IncidentState,
    ObservedFact,
    Symptom,
)


def test_incident_json_round_trip() -> None:
    incident = Incident(
        incident_id="inc-1",
        title="Checkout errors",
        description="Errors after deploy",
        reported_at=datetime(2026, 7, 14, 18, 0, tzinfo=UTC),
        severity=Severity.SEV2,
        affected_services=["checkout-api"],
        symptoms=[
            Symptom(
                symptom_id="s1",
                description="error rate up",
                service="checkout-api",
                confidence=0.9,
            )
        ],
    )
    restored = Incident.model_validate_json(incident.model_dump_json())
    assert restored == incident


def test_incident_state_and_evidence_round_trip() -> None:
    evidence = Evidence(
        evidence_id="ev-1",
        source=EvidenceSource.LOGS,
        tool_name="search_logs",
        query_or_parameters={"q": "timeout"},
        timestamp=datetime(2026, 7, 14, 18, 5, tzinfo=UTC),
        finding="Pool timeout",
        confidence=0.88,
        evidence_uri="fixture://evidence/ev-1",
        raw_reference_id="log-1",
    )
    state = IncidentState(
        incident_id="inc-1",
        title="Checkout errors",
        description="Errors after deploy",
        reported_at=datetime(2026, 7, 14, 18, 0, tzinfo=UTC),
        severity=Severity.SEV2,
        current_phase=IncidentPhase.EVIDENCE_AGGREGATION,
        evidence=[evidence],
        hypotheses=[
            Hypothesis(
                hypothesis_id="h1",
                statement="Pool exhaustion",
                supporting_evidence_ids=["ev-1"],
                confidence=0.8,
                status=HypothesisStatus.LEADING,
            )
        ],
    )
    restored = IncidentState.model_validate_json(state.model_dump_json())
    assert restored.evidence[0].evidence_id == "ev-1"
    assert restored.hypotheses[0].status is HypothesisStatus.LEADING


def test_final_report_separates_facts_and_inferences() -> None:
    report = FinalIncidentReport(
        report_id="r1",
        incident_id="inc-1",
        generated_at=datetime(2026, 7, 14, 19, 0, tzinfo=UTC),
        title="Checkout pool exhaustion",
        executive_summary="Pool size regression after deploy.",
        observed_facts=[
            ObservedFact(
                statement="QueuePool limit errors observed",
                evidence_ids=["ev-1"],
                confidence=0.95,
            )
        ],
        inferred_conclusions=[
            {
                "statement": "Deployment caused pool exhaustion",
                "based_on_fact_indices": [0],
                "evidence_ids": ["ev-1"],
                "confidence": 0.85,
            }
        ],
        unresolved_uncertainty=[],
        recommended_actions=["restore pool size"],
        approved_actions=[],
        executed_actions=[],
        overall_confidence=0.85,
        evidence_ids_cited=["ev-1"],
    )
    payload = report.model_dump(mode="json")
    assert "observed_facts" in payload
    assert "inferred_conclusions" in payload
    assert payload["observed_facts"][0]["evidence_ids"] == ["ev-1"]
