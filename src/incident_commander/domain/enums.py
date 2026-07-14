"""Shared enumerations for the incident investigation domain."""

from __future__ import annotations

from enum import StrEnum


class Severity(StrEnum):
    """Incident severity classification."""

    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"
    UNKNOWN = "unknown"


class IncidentPhase(StrEnum):
    """Lifecycle phase of an investigation workflow."""

    INTAKE = "intake"
    PLANNING = "planning"
    TOPOLOGY = "topology"
    PARALLEL_INVESTIGATION = "parallel_investigation"
    EVIDENCE_AGGREGATION = "evidence_aggregation"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    SKEPTIC_REVIEW = "skeptic_review"
    REINVESTIGATION = "reinvestigation"
    IMPACT_ANALYSIS = "impact_analysis"
    REMEDIATION_PLANNING = "remediation_planning"
    SAFETY_VALIDATION = "safety_validation"
    HUMAN_APPROVAL = "human_approval"
    APPROVED_WRITES = "approved_writes"
    FINAL_REPORT = "final_report"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceSource(StrEnum):
    """Origin system for an evidence item."""

    METRICS = "metrics"
    LOGS = "logs"
    TRACES = "traces"
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    CODE = "code"
    RUNBOOK = "runbook"
    HISTORICAL_INCIDENT = "historical_incident"
    TOPOLOGY = "topology"
    USER_REPORT = "user_report"
    SYNTHETIC = "synthetic"


class RedactionStatus(StrEnum):
    """Whether evidence content has been redacted for secrets/PII."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    REDACTED = "redacted"
    FAILED = "failed"


class HypothesisStatus(StrEnum):
    """Lifecycle status of a root-cause hypothesis."""

    CANDIDATE = "candidate"
    LEADING = "leading"
    CHALLENGED = "challenged"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class ApprovalStatus(StrEnum):
    """Aggregate approval state for proposed remediation actions."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalDecision(StrEnum):
    """Human decision on an approval request."""

    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"


class RemediationActionType(StrEnum):
    """Classification of remediation actions."""

    ROLLBACK = "rollback"
    CONFIG_CHANGE = "config_change"
    FEATURE_FLAG = "feature_flag"
    SCALE = "scale"
    RESTART = "restart"
    MITIGATION = "mitigation"
    INVESTIGATE_FURTHER = "investigate_further"
    NO_ACTION = "no_action"


class ExecutionStatus(StrEnum):
    """Outcome of an attempted write or remediation action."""

    DRY_RUN = "dry_run"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
