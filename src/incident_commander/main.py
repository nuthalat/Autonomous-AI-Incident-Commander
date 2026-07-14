"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from incident_commander import __version__
from incident_commander.api.routes import health_router
from incident_commander.config import Settings, get_settings
from incident_commander.logging import configure_logging, get_logger
from incident_commander.services.health import HealthService, always_healthy_check
from incident_commander.services.llm import create_model_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down application resources."""
    logger = get_logger(__name__)
    settings: Settings = app.state.settings
    model_client = app.state.model_client
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=__version__,
        environment=settings.environment,
        model_provider=settings.model_provider,
        dry_run=settings.dry_run,
        read_only=settings.read_only,
    )
    try:
        yield
    finally:
        await model_client.aclose()
        logger.info("application_shutdown", version=__version__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override for tests. When omitted, settings
            are loaded from the environment via :func:`get_settings`.
    """
    resolved = settings or get_settings()
    configure_logging(resolved)

    app = FastAPI(
        title=resolved.app_name,
        version=__version__,
        description=(
            "Autonomous AI Incident Commander — agentic incident-response platform "
            "with human-approved remediation actions."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    health_service = HealthService(
        settings=resolved,
        dependency_checks=[always_healthy_check],
    )
    model_client = create_model_client(resolved)

    app.state.settings = resolved
    app.state.health_service = health_service
    app.state.model_client = model_client

    app.include_router(health_router)

    return app


app = create_app()
