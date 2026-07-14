"""Investigation planning models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from incident_commander.domain.types import NonEmptyStr


class InvestigationStep(BaseModel):
    """A single planned investigation action."""

    model_config = ConfigDict(extra="forbid")

    step_id: NonEmptyStr
    agent: NonEmptyStr
    objective: NonEmptyStr
    tools: list[str] = Field(default_factory=list)
    target_services: list[str] = Field(default_factory=list)
    priority: int = Field(default=1, ge=1, le=100)
    parallel_group: str | None = None
    completed: bool = False
    notes: str | None = None


class InvestigationPlan(BaseModel):
    """Ordered investigation plan produced by the planner agent."""

    model_config = ConfigDict(extra="forbid")

    plan_id: NonEmptyStr
    summary: NonEmptyStr
    steps: list[InvestigationStep] = Field(default_factory=list)
    max_reinvestigation_loops: int = Field(default=2, ge=0)
    notes: list[str] = Field(default_factory=list)
