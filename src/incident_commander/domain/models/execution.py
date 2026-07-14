"""Execution audit records for approved write actions."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from incident_commander.domain.enums import ExecutionStatus
from incident_commander.domain.types import NonEmptyStr


class ExecutionRecord(BaseModel):
    """Audit record for a dry-run or executed remediation action."""

    model_config = ConfigDict(extra="forbid")

    execution_id: NonEmptyStr
    action_id: NonEmptyStr
    tool_name: NonEmptyStr
    status: ExecutionStatus
    started_at: datetime
    completed_at: datetime | None = None
    dry_run: bool = True
    approval_token_used: str | None = None
    result_summary: str | None = None
    error_message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
