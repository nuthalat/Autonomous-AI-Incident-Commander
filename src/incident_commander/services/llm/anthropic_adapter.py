"""Anthropic Claude model adapter interface.

Stage 1 provides a typed, injectable client with configuration validation and
explicit failure modes. Live prompt orchestration and agent calls are deferred
to later stages; ``complete`` raises until the optional ``anthropic`` extra is
installed and a real transport is wired.
"""

from __future__ import annotations

from typing import Any

from incident_commander.domain.exceptions import ConfigurationError, ModelError
from incident_commander.models.llm import (
    ChatMessage,
    ModelRequest,
    ModelResponse,
    ModelUsage,
    Role,
)
from incident_commander.services.llm.base import ModelClient


class AnthropicModelClient(ModelClient):
    """Adapter for the official Anthropic Python SDK.

    This class defines the integration boundary expected by agents:

    * typed :class:`ModelRequest` / :class:`ModelResponse`
    * timeout and retry knobs
    * message role mapping for Claude Messages API

    Stage 1 does **not** issue network calls. Calling :meth:`complete` without
    an injected transport raises :class:`ModelError` so the default local path
    remains the deterministic fake client.
    """

    provider_name = "anthropic"

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
        transport: Any | None = None,
    ) -> None:
        if not api_key:
            raise ConfigurationError(
                "AnthropicModelClient requires a non-empty api_key",
                code="missing_anthropic_api_key",
            )
        self._api_key = api_key
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._transport = transport
        self._closed = False

    @property
    def model_name(self) -> str:
        """Configured Claude model identifier."""
        return self._model_name

    @property
    def timeout_seconds(self) -> float:
        """Per-request timeout in seconds."""
        return self._timeout_seconds

    @property
    def max_retries(self) -> int:
        """Maximum retry attempts for transient failures."""
        return self._max_retries

    def build_messages_payload(self, request: ModelRequest) -> dict[str, Any]:
        """Map a :class:`ModelRequest` to Anthropic Messages API fields.

        System messages are extracted into the top-level ``system`` field;
        user/assistant messages remain in ``messages``.
        """
        system_parts: list[str] = []
        messages: list[dict[str, str]] = []

        for message in request.messages:
            if message.role == Role.SYSTEM:
                system_parts.append(message.content)
            else:
                messages.append(
                    {
                        "role": self._map_role(message),
                        "content": message.content,
                    }
                )

        if not messages:
            raise ModelError(
                "Anthropic requests require at least one non-system message",
                code="invalid_model_request",
            )

        payload: dict[str, Any] = {
            "model": request.model or self._model_name,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages,
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)
        return payload

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Execute a completion via injected transport, or fail closed.

        When a transport with ``messages_create`` is provided (tests / later
        stages), it is awaited. Otherwise this method raises to avoid silent
        fake behavior under the Anthropic provider name.
        """
        if self._closed:
            raise ModelError(
                "AnthropicModelClient is closed",
                code="model_client_closed",
            )

        payload = self.build_messages_payload(request)

        if self._transport is None:
            raise ModelError(
                "Anthropic transport is not configured. Install the 'anthropic' "
                "extra and wire the SDK client in a later stage, or use "
                "model_provider=fake for local development.",
                code="anthropic_transport_unavailable",
                details={
                    "model": payload["model"],
                    "timeout_seconds": self._timeout_seconds,
                    "max_retries": self._max_retries,
                },
            )

        try:
            raw = await self._transport.messages_create(
                **payload,
                timeout=self._timeout_seconds,
            )
        except TimeoutError as exc:
            from incident_commander.domain.exceptions import ModelTimeoutError

            raise ModelTimeoutError(
                "Anthropic request timed out",
                details={"model": payload["model"]},
            ) from exc
        except Exception as exc:
            raise ModelError(
                f"Anthropic request failed: {exc}",
                code="anthropic_request_failed",
                details={"model": payload["model"]},
            ) from exc

        return self._normalize_response(raw, fallback_model=str(payload["model"]))

    async def aclose(self) -> None:
        """Mark the client closed and close an injected transport if present."""
        self._closed = True
        close = getattr(self._transport, "aclose", None)
        if callable(close):
            await close()

    @staticmethod
    def _map_role(message: ChatMessage) -> str:
        if message.role == Role.ASSISTANT:
            return "assistant"
        return "user"

    def _normalize_response(self, raw: Any, *, fallback_model: str) -> ModelResponse:
        """Normalize SDK-like objects or dicts into :class:`ModelResponse`."""
        if isinstance(raw, ModelResponse):
            return raw

        if isinstance(raw, dict):
            content = str(raw.get("content", ""))
            model = str(raw.get("model", fallback_model))
            usage_raw = raw.get("usage") or {}
            input_tokens = int(usage_raw.get("input_tokens", 0))
            output_tokens = int(usage_raw.get("output_tokens", 0))
            return ModelResponse(
                content=content,
                model=model,
                provider=self.provider_name,
                finish_reason=str(raw.get("finish_reason", "stop")),
                raw_reference=str(raw.get("id")) if raw.get("id") else None,
                metadata={"raw_keys": sorted(raw.keys())},
                usage=ModelUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                ),
            )

        content_blocks = getattr(raw, "content", None)
        if content_blocks is not None:
            texts: list[str] = []
            for block in content_blocks:
                text = getattr(block, "text", None)
                if text:
                    texts.append(str(text))
            usage_obj = getattr(raw, "usage", None)
            input_tokens = int(getattr(usage_obj, "input_tokens", 0) or 0)
            output_tokens = int(getattr(usage_obj, "output_tokens", 0) or 0)
            return ModelResponse(
                content="\n".join(texts),
                model=str(getattr(raw, "model", fallback_model)),
                provider=self.provider_name,
                finish_reason=str(getattr(raw, "stop_reason", "stop") or "stop"),
                raw_reference=str(getattr(raw, "id", "")) or None,
                usage=ModelUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                ),
            )

        raise ModelError(
            "Unrecognized Anthropic response shape",
            code="malformed_model_output",
            details={"type": type(raw).__name__},
        )
