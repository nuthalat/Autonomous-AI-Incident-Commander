# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- README and architecture docs on porting the agentic control plane to other
  systems (env settings, model adapters, MCP backends, fixtures/topology).
- Stage 2 domain model: `Incident`, `IncidentState`, `Evidence`, `Hypothesis`,
  investigation/impact/remediation/approval/report models with confidence
  validation in `[0, 1]`.
- Evidence aggregation reducers for parallel investigators.
- Phase-transition validation that blocks investigation → action execution jumps
  and requires approval tokens before executable remediation.
- Final report model separating observed facts, inferences, and uncertainty,
  with mandatory evidence citations on factual claims.
- Five synthetic incident scenario packs with topology, telemetry, deployments,
  config/code changes, runbooks, historical incidents, seed evidence, and
  safe/unsafe remediation options.
- Fixture loader with schema validation and CLI `list-scenarios` /
  `show-scenario` commands.
- Stage 1 repository foundation: Python 3.12 src layout, tooling, Docker, and docs.
- Typed application settings via `pydantic-settings`.
- Structured logging with `structlog`.
- Domain exception hierarchy for configuration, model, safety, and dependency failures.
- FastAPI application with `GET /health` and `GET /ready` endpoints.
- Deterministic `FakeModelClient` (default; no API key required).
- `AnthropicModelClient` adapter interface for future Claude integration.
- Injectable dependency health checks for readiness probes.
- Initial unit and API tests.
- GitHub Actions CI for lint, typecheck, and tests.
- Apache License 2.0, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, and community templates.

## [0.1.0] - 2026-07-14

### Added

- Initial public project scaffolding.
