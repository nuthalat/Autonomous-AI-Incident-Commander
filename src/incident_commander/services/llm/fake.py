"""Deterministic fake model client for local development and tests."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from incident_commander.models.llm import ModelRequest, ModelResponse, ModelUsage, Role
from incident_commander.services.llm.base import ModelClient


class FakeModelClient(ModelClient):
    """Deterministic model implementation that requires no API key.

    Responses are derived from a stable hash of the request so that repeated
    calls with the same messages produce identical output. This enables
    offline demos, CI, and evaluation without a paid model provider.
    """

    provider_name = "fake"

    def __init__(self, model_name: str = "fake-deterministic-v1") -> None:
        self._model_name = model_name
        self._call_count = 0

    @property
    def call_count(self) -> int:
        """Number of complete() invocations since construction."""
        return self._call_count

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Return a deterministic structured-style completion."""
        self._call_count += 1
        model = request.model or self._model_name
        fingerprint = self._fingerprint(request)
        user_text = self._last_user_content(request)

        content = self._build_content(
            fingerprint=fingerprint,
            user_text=user_text,
            metadata=request.metadata,
        )
        input_tokens = max(1, sum(len(message.content) for message in request.messages) // 4)
        output_tokens = max(1, len(content) // 4)

        return ModelResponse(
            content=content,
            model=model,
            provider=self.provider_name,
            usage=ModelUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
            finish_reason="stop",
            raw_reference=f"fake://completion/{fingerprint}",
            metadata={
                "deterministic": True,
                "fingerprint": fingerprint,
                "call_index": self._call_count,
            },
        )

    async def aclose(self) -> None:
        """No network resources to release."""

    def _fingerprint(self, request: ModelRequest) -> str:
        payload = {
            "messages": [m.model_dump(mode="json") for m in request.messages],
            "model": request.model or self._model_name,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "metadata": request.metadata,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()[:16]

    @staticmethod
    def _last_user_content(request: ModelRequest) -> str:
        for message in reversed(request.messages):
            if message.role == Role.USER:
                return message.content
        return request.messages[-1].content

    @staticmethod
    def _build_content(
        *,
        fingerprint: str,
        user_text: str,
        metadata: dict[str, Any],
    ) -> str:
        scenario = metadata.get("scenario", "generic")
        excerpt = user_text.strip().replace("\n", " ")
        if len(excerpt) > 160:
            excerpt = f"{excerpt[:157]}..."
        return (
            "FAKE_MODEL_RESPONSE\n"
            f"fingerprint={fingerprint}\n"
            f"scenario={scenario}\n"
            "status=deterministic_fallback\n"
            "summary=Insufficient live model capacity; returning structured offline response.\n"
            f"user_excerpt={excerpt}\n"
            "hypotheses=[]\n"
            "confidence=0.0\n"
            "next_action=await_real_model_or_continue_with_fixtures\n"
        )
