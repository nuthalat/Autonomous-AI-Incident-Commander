"""Abstract model client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from incident_commander.models.llm import ModelRequest, ModelResponse


@runtime_checkable
class SupportsComplete(Protocol):
    """Structural protocol for async chat completion clients."""

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Generate a model completion for the given request."""
        ...


class ModelClient(ABC):
    """Base class for LLM providers used by investigation agents.

    Implementations must be safe to inject via FastAPI dependencies and must
    not rely on process-global mutable state.
    """

    provider_name: str

    @abstractmethod
    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Generate a completion for ``request``."""

    @abstractmethod
    async def aclose(self) -> None:
        """Release any underlying network resources."""

    async def __aenter__(self) -> ModelClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
