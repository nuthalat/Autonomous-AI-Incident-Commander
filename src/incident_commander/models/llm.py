"""Typed request/response models for LLM clients."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Chat message roles accepted by model clients."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """A single chat message exchanged with a model provider."""

    role: Role
    content: str = Field(min_length=1)


class ModelUsage(BaseModel):
    """Token usage reported by a model provider (or estimated by fake)."""

    input_tokens: int = Field(ge=0, default=0)
    output_tokens: int = Field(ge=0, default=0)
    total_tokens: int = Field(ge=0, default=0)


class ModelRequest(BaseModel):
    """Normalized request sent to a model client."""

    messages: list[ChatMessage] = Field(min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel):
    """Normalized response returned by a model client."""

    content: str
    model: str
    provider: str
    usage: ModelUsage = Field(default_factory=ModelUsage)
    finish_reason: str = "stop"
    raw_reference: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
