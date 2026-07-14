"""LangGraph orchestration for the incident investigation workflow.

Stage 1 reserves this package. Checkpointing, interrupts, and the full
investigation graph are added in later stages.
"""

from __future__ import annotations

from incident_commander.domain.enums import IncidentPhase

WORKFLOW_PHASES: tuple[IncidentPhase, ...] = (
    IncidentPhase.INTAKE,
    IncidentPhase.PLANNING,
    IncidentPhase.TOPOLOGY,
    IncidentPhase.PARALLEL_INVESTIGATION,
    IncidentPhase.EVIDENCE_AGGREGATION,
    IncidentPhase.HYPOTHESIS_GENERATION,
    IncidentPhase.SKEPTIC_REVIEW,
    IncidentPhase.REINVESTIGATION,
    IncidentPhase.IMPACT_ANALYSIS,
    IncidentPhase.REMEDIATION_PLANNING,
    IncidentPhase.SAFETY_VALIDATION,
    IncidentPhase.HUMAN_APPROVAL,
    IncidentPhase.APPROVED_WRITES,
    IncidentPhase.FINAL_REPORT,
)

__all__ = ["WORKFLOW_PHASES"]
