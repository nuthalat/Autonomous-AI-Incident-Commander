"""Health and readiness response models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class HealthStatus(StrEnum):
    """Aggregate health status values."""

    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class DependencyStatus(BaseModel):
    """Status of a single injectable dependency health check."""

    name: str
    healthy: bool
    latency_ms: float | None = None
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Liveness probe response — process is up and serving HTTP."""

    status: HealthStatus = HealthStatus.OK
    service: str
    version: str
    timestamp: datetime


class ReadinessResponse(BaseModel):
    """Readiness probe response — dependencies required to serve traffic."""

    status: HealthStatus
    service: str
    version: str
    timestamp: datetime
    checks: list[DependencyStatus] = Field(default_factory=list)
    ready: bool
