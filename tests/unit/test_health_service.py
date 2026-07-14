"""Tests for injectable health and readiness checks."""

from __future__ import annotations

import pytest

from incident_commander.config import Settings
from incident_commander.models.health import DependencyStatus, HealthStatus
from incident_commander.services.health import HealthService, always_healthy_check


@pytest.mark.asyncio
async def test_readiness_ok_with_healthy_checks(test_settings: Settings) -> None:
    service = HealthService(
        settings=test_settings,
        dependency_checks=[always_healthy_check],
    )
    result = await service.readiness()
    assert result.ready is True
    assert result.status == HealthStatus.OK
    assert result.checks[0].name == "application"


@pytest.mark.asyncio
async def test_readiness_fails_when_dependency_unhealthy(test_settings: Settings) -> None:
    async def redis_down() -> DependencyStatus:
        return DependencyStatus(name="redis", healthy=False, message="connection refused")

    service = HealthService(
        settings=test_settings,
        dependency_checks=[always_healthy_check, redis_down],
    )
    result = await service.readiness()
    assert result.ready is False
    assert result.status == HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_readiness_handles_check_exceptions(test_settings: Settings) -> None:
    async def exploding() -> DependencyStatus:
        raise RuntimeError("probe crashed")

    service = HealthService(settings=test_settings, dependency_checks=[exploding])
    result = await service.readiness()
    assert result.ready is False
    assert result.status == HealthStatus.UNAVAILABLE
    assert result.checks[0].healthy is False
    assert "RuntimeError" in (result.checks[0].message or "")
