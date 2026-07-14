"""Schema for synthetic incident scenario fixture packs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from incident_commander.domain.models.evidence import Evidence
from incident_commander.domain.models.incident import Incident
from incident_commander.domain.models.remediation import RemediationAction
from incident_commander.domain.types import NonEmptyStr


class ServiceNode(BaseModel):
    """A service in the synthetic topology."""

    model_config = ConfigDict(extra="forbid")

    name: NonEmptyStr
    kind: NonEmptyStr
    owner: str | None = None
    language: str | None = None
    depends_on: list[str] = Field(default_factory=list)


class ServiceTopology(BaseModel):
    """Directed service dependency graph for a scenario."""

    model_config = ConfigDict(extra="forbid")

    environment: str = "production"
    services: list[ServiceNode] = Field(min_length=1)


class MetricPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    value: float


class MetricSeries(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_id: NonEmptyStr
    name: NonEmptyStr
    service: NonEmptyStr
    unit: str = "count"
    labels: dict[str, str] = Field(default_factory=dict)
    points: list[MetricPoint] = Field(min_length=1)


class LogEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    log_id: NonEmptyStr
    timestamp: datetime
    service: NonEmptyStr
    level: NonEmptyStr
    message: NonEmptyStr
    fields: dict[str, Any] = Field(default_factory=dict)


class SpanRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    span_id: NonEmptyStr
    parent_span_id: str | None = None
    service: NonEmptyStr
    operation: NonEmptyStr
    duration_ms: float = Field(ge=0)
    status: str = "ok"
    attributes: dict[str, Any] = Field(default_factory=dict)


class TraceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: NonEmptyStr
    root_service: NonEmptyStr
    root_operation: NonEmptyStr
    duration_ms: float = Field(ge=0)
    status: str = "error"
    spans: list[SpanRecord] = Field(min_length=1)


class DeploymentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deployment_id: NonEmptyStr
    service: NonEmptyStr
    version: NonEmptyStr
    previous_version: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "success"
    commit_sha: str | None = None
    changelog: str | None = None


class ConfigChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    change_id: NonEmptyStr
    service: NonEmptyStr
    key: NonEmptyStr
    old_value: str | None = None
    new_value: str | None = None
    changed_at: datetime
    actor: str | None = None
    change_type: str = "config"


class CodeChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    change_id: NonEmptyStr
    service: NonEmptyStr
    commit_sha: NonEmptyStr
    title: NonEmptyStr
    author: str | None = None
    committed_at: datetime
    files_changed: list[str] = Field(default_factory=list)
    diff_excerpt: str | None = None
    pull_request: str | None = None


class Runbook(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runbook_id: NonEmptyStr
    title: NonEmptyStr
    service: NonEmptyStr
    summary: NonEmptyStr
    steps: list[str] = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)


class HistoricalIncident(BaseModel):
    model_config = ConfigDict(extra="forbid")

    incident_id: NonEmptyStr
    title: NonEmptyStr
    summary: NonEmptyStr
    root_cause: NonEmptyStr
    services: list[str] = Field(default_factory=list)
    resolved_at: datetime | None = None
    similarity_notes: str | None = None


class ScenarioBundle(BaseModel):
    """Complete synthetic incident scenario used for demos and evaluation."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: NonEmptyStr
    name: NonEmptyStr
    description: NonEmptyStr
    incident: Incident
    topology: ServiceTopology
    metrics: list[MetricSeries] = Field(default_factory=list)
    logs: list[LogEvent] = Field(default_factory=list)
    traces: list[TraceSummary] = Field(default_factory=list)
    deployments: list[DeploymentRecord] = Field(default_factory=list)
    configuration_changes: list[ConfigChange] = Field(default_factory=list)
    code_changes: list[CodeChange] = Field(default_factory=list)
    runbooks: list[Runbook] = Field(default_factory=list)
    historical_incidents: list[HistoricalIncident] = Field(default_factory=list)
    seed_evidence: list[Evidence] = Field(default_factory=list)
    expected_root_cause: NonEmptyStr
    expected_evidence_ids: list[str] = Field(min_length=1)
    safe_remediation_options: list[RemediationAction] = Field(min_length=1)
    unsafe_remediation_options: list[RemediationAction] = Field(min_length=1)
    evidence_required_for_evaluation: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_internal_consistency(self) -> ScenarioBundle:
        service_names = {node.name for node in self.topology.services}
        for service in self.incident.affected_services:
            if service not in service_names:
                raise ValueError(
                    f"incident affected service {service!r} missing from topology"
                )

        seed_ids = {item.evidence_id for item in self.seed_evidence}
        missing_expected = set(self.expected_evidence_ids) - seed_ids
        if missing_expected:
            raise ValueError(
                "expected_evidence_ids must exist in seed_evidence: "
                f"{sorted(missing_expected)}"
            )

        eval_missing = set(self.evidence_required_for_evaluation) - seed_ids
        if eval_missing:
            raise ValueError(
                "evidence_required_for_evaluation must exist in seed_evidence: "
                f"{sorted(eval_missing)}"
            )

        safe_ids = {action.action_id for action in self.safe_remediation_options}
        unsafe_ids = {action.action_id for action in self.unsafe_remediation_options}
        overlap = safe_ids & unsafe_ids
        if overlap:
            raise ValueError(f"safe/unsafe remediation action_id overlap: {sorted(overlap)}")

        for action in self.safe_remediation_options:
            if not action.is_safe:
                raise ValueError(f"safe remediation {action.action_id} has is_safe=False")
        for action in self.unsafe_remediation_options:
            if action.is_safe:
                raise ValueError(f"unsafe remediation {action.action_id} has is_safe=True")

        if not self.metrics or not self.logs or not self.traces:
            raise ValueError("scenario must include metrics, logs, and traces")
        if not self.deployments:
            raise ValueError("scenario must include deployment history")
        if not self.runbooks:
            raise ValueError("scenario must include at least one runbook")
        if not self.historical_incidents:
            raise ValueError("scenario must include historical incidents")

        return self
