"""Tests for the deterministic fake model client."""

from __future__ import annotations

import pytest

from incident_commander.models.llm import ChatMessage, ModelRequest, Role
from incident_commander.services.llm.fake import FakeModelClient


@pytest.mark.asyncio
async def test_fake_model_is_deterministic() -> None:
    client = FakeModelClient(model_name="fake-test-v1")
    request = ModelRequest(
        messages=[
            ChatMessage(role=Role.SYSTEM, content="You are an incident investigator."),
            ChatMessage(role=Role.USER, content="Checkout errors increased after deploy."),
        ],
        metadata={"scenario": "connection-pool-exhaustion"},
    )

    first = await client.complete(request)
    second = await client.complete(request)

    assert first.content == second.content
    assert first.raw_reference == second.raw_reference
    assert first.provider == "fake"
    assert "FAKE_MODEL_RESPONSE" in first.content
    assert "connection-pool-exhaustion" in first.content
    assert client.call_count == 2


@pytest.mark.asyncio
async def test_fake_model_changes_when_prompt_changes() -> None:
    client = FakeModelClient()
    base = ModelRequest(
        messages=[ChatMessage(role=Role.USER, content="error rate up")],
    )
    altered = ModelRequest(
        messages=[ChatMessage(role=Role.USER, content="latency spike")],
    )

    first = await client.complete(base)
    second = await client.complete(altered)
    assert first.content != second.content
