"""Evaluation harness for investigation quality metrics.

Stage 1 reserves the package. Scenario runners and baseline comparisons are
implemented once agents and fixtures exist.
"""

from __future__ import annotations

EVALUATION_METRICS: tuple[str, ...] = (
    "root_cause_accuracy",
    "evidence_precision",
    "evidence_recall",
    "unsupported_claim_rate",
    "hypothesis_ranking_quality",
    "remediation_safety",
    "refusal_correctness",
    "approval_policy_compliance",
    "investigation_latency",
    "token_usage",
    "estimated_cost",
    "tool_call_count",
)

__all__ = ["EVALUATION_METRICS"]
