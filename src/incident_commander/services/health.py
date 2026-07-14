"""Injectable health and readiness checks."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from incident_commander import __version__
from incident_commander.config import Settings
from incident_commander.models.health import (
    DependencyStatus,
    HealthResponse,
    HealthStatus,
    ReadinessResponse,
)

DependencyCheck = Callable[[], Awaitable[DependencyStatus]]


class HealthService:
    """Aggregates liveness and readiness information.

    Dependency checks are injected so the API layer does not hold global
    mutable state and tests can substitute fakes.
    """

    def __init__(
        self,
        settings: Settings,
        dependency_checks: list[DependencyCheck] | None = None,
    ) -> None:
        self._settings = settings
        self._dependency_checks = list(dependency_checks or [])

    def add_check(self, check: DependencyCheck) -> None:
        """Register an additional async dependency health check."""
        self._dependency_checks.append(check)

    def liveness(self) -> HealthResponse:
        """Return a simple liveness result (process is alive)."""
        return HealthResponse(
            status=HealthStatus.OK,
            service=self._settings.app_name,
            version=__version__,
            timestamp=datetime.now(UTC),
        )

    async def readiness(self) -> ReadinessResponse:
        """Run all dependency checks and compute readiness."""
        results: list[DependencyStatus] = []
        for check in self._dependency_checks:
            started = time.perf_counter()
            try:
                status = await check()
            except Exception as exc:
                # Readiness probes must never raise; convert probe failures to status.
                status = DependencyStatus(
                    name=getattr(check, "__name__", "unknown_check"),
                    healthy=False,
                    message=f"check raised {type(exc).__name__}: {exc}",
                )
            if status.latency_ms is None:
                status = status.model_copy(
                    update={"latency_ms": (time.perf_counter() - started) * 1000}
                )
            results.append(status)

        healthy_count = sum(1 for item in results if item.healthy)
        if not results or healthy_count == len(results):
            aggregate = HealthStatus.OK
            ready = True
        elif healthy_count == 0:
            aggregate = HealthStatus.UNAVAILABLE
            ready = False
        else:
            aggregate = HealthStatus.DEGRADED
            ready = False

        return ReadinessResponse(
            status=aggregate,
            service=self._settings.app_name,
            version=__version__,
            timestamp=datetime.now(UTC),
            checks=results,
            ready=ready,
        )


async def always_healthy_check() -> DependencyStatus:
    """Built-in check used when no external dependencies are required."""
    return DependencyStatus(
        name="application",
        healthy=True,
        message="application core is configured",
    )
