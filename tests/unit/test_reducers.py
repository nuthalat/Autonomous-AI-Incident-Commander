"""Tests for parallel evidence aggregation reducers."""

from __future__ import annotations

from datetime import UTC, datetime

from incident_commander.domain.enums import EvidenceSource
from incident_commander.domain.models import Evidence
from incident_commander.domain.reducers import append_unique_strings, reduce_evidence


def _ev(evidence_id: str, finding: str) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source=EvidenceSource.LOGS,
        tool_name="search_logs",
        timestamp=datetime.now(UTC),
        finding=finding,
        confidence=0.7,
        evidence_uri=f"fixture://{evidence_id}",
        raw_reference_id=evidence_id,
    )


def test_reduce_evidence_merges_parallel_results() -> None:
    left = [_ev("ev-1", "from logs")]
    right = [_ev("ev-2", "from metrics")]
    merged = reduce_evidence(left, right)
    assert {item.evidence_id for item in merged} == {"ev-1", "ev-2"}


def test_reduce_evidence_last_writer_wins_on_id() -> None:
    existing = [_ev("ev-1", "old finding")]
    updated = _ev("ev-1", "refined finding")
    merged = reduce_evidence(existing, updated)
    assert len(merged) == 1
    assert merged[0].finding == "refined finding"


def test_append_unique_strings_preserves_order() -> None:
    assert append_unique_strings(["a", "b"], ["b", "c"]) == ["a", "b", "c"]
