"""LangGraph orchestration for the incident investigation workflow.

Stage 1 reserves this package. Checkpointing, interrupts, and the full
investigation graph are added in later stages.
"""

from __future__ import annotations

WORKFLOW_PHASES: tuple[str, ...] = (
    "intake",
    "planning",
    "topology",
    "parallel_investigation",
    "evidence_aggregation",
    "hypothesis_generation",
    "skeptic_review",
    "reinvestigation",
    "impact_analysis",
    "remediation_planning",
    "safety_validation",
    "human_approval",
    "approved_writes",
    "final_report",
)

__all__ = ["WORKFLOW_PHASES"]
