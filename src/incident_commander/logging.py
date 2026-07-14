"""Structured logging configuration using structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from incident_commander.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure process-wide structured logging.

    JSON logs are emitted when ``settings.log_json`` is True; otherwise a
    console-friendly renderer is used for local development.
    """
    log_level = getattr(logging, settings.log_level, logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_json:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=not settings.is_production)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Emit logs on stderr so CLI stdout remains machine-parseable.
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Keep noisy third-party loggers at WARNING unless debugging.
    for noisy in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING if not settings.debug else log_level)


def get_logger(name: str | None = None, **initial_context: Any) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger with optional initial context."""
    logger = structlog.stdlib.get_logger(name)
    if initial_context:
        return logger.bind(**initial_context)
    return logger
