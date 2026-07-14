# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
