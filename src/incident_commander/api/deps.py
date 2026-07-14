"""FastAPI dependency injection helpers.

Dependencies are created per-app via the application lifespan and retrieved
from ``request.app.state`` to avoid module-level mutable singletons.
"""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Request

from incident_commander.config import Settings
from incident_commander.services.health import HealthService
from incident_commander.services.llm.base import ModelClient


def get_settings(request: Request) -> Settings:
    """Return application settings from app state."""
    return cast(Settings, request.app.state.settings)


def get_health_service(request: Request) -> HealthService:
    """Return the shared health service from app state."""
    return cast(HealthService, request.app.state.health_service)


def get_model_client(request: Request) -> ModelClient:
    """Return the configured model client from app state."""
    return cast(ModelClient, request.app.state.model_client)


SettingsDep = Annotated[Settings, Depends(get_settings)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
ModelClientDep = Annotated[ModelClient, Depends(get_model_client)]
