"""Tests for the Anthropic model adapter interface."""

from __future__ import annotations

import pytest

from incident_commander.domain.exceptions import ConfigurationError, ModelError
from incident_commander.models.llm import ChatMessage, ModelRequest, ModelResponse, Role
from incident_commander.services.llm.anthropic_adapter import AnthropicModelClient


def test_empty_api_key_rejected() -> None:
    with pytest.raises(ConfigurationError):
        AnthropicModelClient(api_key="", model_name="claude-test")


def test_build_messages_payload_extracts_system() -> None:
    client = AnthropicModelClient(api_key="test-key", model_name="claude-test")
    request = ModelRequest(
        messages=[
            ChatMessage(role=Role.SYSTEM, content="Be careful."),
            ChatMessage(role=Role.USER, content="Investigate checkout."),
        ],
        max_tokens=256,
        temperature=0.0,
    )
    payload = client.build_messages_payload(request)
    assert payload["system"] == "Be careful."
    assert payload["messages"] == [
        {"role": "user", "content": "Investigate checkout."},
    ]
    assert payload["model"] == "claude-test"
    assert payload["max_tokens"] == 256


@pytest.mark.asyncio
async def test_complete_without_transport_fails_closed() -> None:
    client = AnthropicModelClient(api_key="test-key", model_name="claude-test")
    request = ModelRequest(
        messages=[ChatMessage(role=Role.USER, content="hello")],
    )
    with pytest.raises(ModelError) as exc_info:
        await client.complete(request)
    assert exc_info.value.code == "anthropic_transport_unavailable"


@pytest.mark.asyncio
async def test_complete_with_injected_transport() -> None:
    class _Transport:
        async def messages_create(self, **kwargs: object) -> dict[str, object]:
            assert kwargs["model"] == "claude-test"
            return {
                "id": "msg_test",
                "content": "synthetic anthropic reply",
                "model": "claude-test",
                "usage": {"input_tokens": 3, "output_tokens": 5},
            }

    client = AnthropicModelClient(
        api_key="test-key",
        model_name="claude-test",
        transport=_Transport(),
    )
    response = await client.complete(
        ModelRequest(messages=[ChatMessage(role=Role.USER, content="ping")])
    )
    assert isinstance(response, ModelResponse)
    assert response.content == "synthetic anthropic reply"
    assert response.provider == "anthropic"
    assert response.usage.total_tokens == 8
