"""Liveness and readiness HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from incident_commander.api.deps import HealthServiceDep
from incident_commander.models.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
)
async def health(health_service: HealthServiceDep) -> HealthResponse:
    """Return a simple liveness result indicating the process is alive."""
    return health_service.liveness()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    responses={
        503: {"description": "One or more dependency checks failed"},
    },
)
async def ready(
    health_service: HealthServiceDep,
    response: Response,
) -> ReadinessResponse:
    """Validate application dependencies through injectable health checks."""
    result = await health_service.readiness()
    if not result.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
