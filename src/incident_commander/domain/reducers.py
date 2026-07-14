"""Reducer helpers for parallel LangGraph state updates."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from incident_commander.domain.models.evidence import Evidence
from incident_commander.domain.models.execution import ExecutionRecord
from incident_commander.domain.models.hypothesis import Hypothesis


def reduce_evidence(
    existing: Sequence[Evidence] | None,
    new: Evidence | Sequence[Evidence] | None,
) -> list[Evidence]:
    """Merge evidence lists from parallel investigators.

    Items are keyed by ``evidence_id``. Later writes with the same ID replace
    earlier ones (last-writer-wins) so retries can refine a finding without
    duplicating IDs.
    """
    merged: dict[str, Evidence] = {}
    for item in existing or []:
        merged[item.evidence_id] = item
    for item in _as_evidence_iter(new):
        merged[item.evidence_id] = item
    return list(merged.values())


def append_unique_strings(
    existing: Sequence[str] | None,
    new: str | Sequence[str] | None,
) -> list[str]:
    """Append strings while preserving order and dropping duplicates."""
    result: list[str] = list(existing or [])
    seen = set(result)
    for item in _as_str_iter(new):
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def reduce_hypotheses(
    existing: Sequence[Hypothesis] | None,
    new: Hypothesis | Sequence[Hypothesis] | None,
) -> list[Hypothesis]:
    """Merge hypotheses by ``hypothesis_id`` (last-writer-wins)."""
    merged: dict[str, Hypothesis] = {}
    for item in existing or []:
        merged[item.hypothesis_id] = item
    if new is None:
        return list(merged.values())
    if isinstance(new, Hypothesis):
        items: Iterable[Hypothesis] = (new,)
    else:
        items = new
    for item in items:
        merged[item.hypothesis_id] = item
    return list(merged.values())


def reduce_execution_history(
    existing: Sequence[ExecutionRecord] | None,
    new: ExecutionRecord | Sequence[ExecutionRecord] | None,
) -> list[ExecutionRecord]:
    """Append execution records, replacing duplicates by ``execution_id``."""
    merged: dict[str, ExecutionRecord] = {}
    for item in existing or []:
        merged[item.execution_id] = item
    if new is None:
        return list(merged.values())
    if isinstance(new, ExecutionRecord):
        items: Iterable[ExecutionRecord] = (new,)
    else:
        items = new
    for item in items:
        merged[item.execution_id] = item
    return list(merged.values())


def _as_evidence_iter(value: Evidence | Sequence[Evidence] | None) -> Iterable[Evidence]:
    if value is None:
        return ()
    if isinstance(value, Evidence):
        return (value,)
    return value


def _as_str_iter(value: str | Sequence[str] | None) -> Iterable[str]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return value
