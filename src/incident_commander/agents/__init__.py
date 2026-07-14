"""Specialized investigation agents (LangGraph nodes).

Stage 1 establishes the package boundary. Concrete agents with schemas,
tool allowlists, and fallbacks are implemented in later stages.
"""

from __future__ import annotations

AGENT_REGISTRY: tuple[str, ...] = (
    "incident_intake",
    "investigation_planner",
    "service_topology",
    "metrics_investigator",
    "log_investigator",
    "trace_investigator",
    "deployment_configuration",
    "code_investigation",
    "runbook_retrieval",
    "historical_incident",
    "hypothesis_generator",
    "hypothesis_challenger",
    "impact_analysis",
    "remediation_planner",
    "safety_approval_report",
)

__all__ = ["AGENT_REGISTRY"]
