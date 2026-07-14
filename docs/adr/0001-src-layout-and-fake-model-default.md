# ADR 0001: Src layout and fake-model default

## Status

Accepted (Stage 1)

## Context

The project must run locally and in CI without a paid model API key, while
still defining a clear integration path for Anthropic Claude.

## Decision

1. Use a `src/` layout with the installable package `incident_commander`.
2. Default `INCIDENT_COMMANDER_MODEL_PROVIDER` to `fake`.
3. Implement `FakeModelClient` as a deterministic, hash-based completer.
4. Ship `AnthropicModelClient` as a typed adapter that validates configuration
   and message mapping, but fails closed until a transport is injected.
5. Keep MCP server packages under top-level `servers/` with tool metadata so
   later stages can add transports without reshaping the repository.

## Consequences

- Local demos and tests never require `ANTHROPIC_API_KEY`.
- Selecting `model_provider=anthropic` without a wired SDK transport raises a
  domain `ModelError` instead of silently falling back to the fake client.
- Agents and LangGraph orchestration can depend on the `ModelClient` interface
  without caring which provider is configured.
