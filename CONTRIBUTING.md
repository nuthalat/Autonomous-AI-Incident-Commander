# Contributing

Thank you for contributing to **Autonomous AI Incident Commander**.

## Development setup

1. Use Python 3.12+.
2. Create a virtual environment and install development dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   make install-dev
   ```

3. Copy environment defaults:

   ```bash
   cp .env.example .env
   ```

4. Run the local API (uses the deterministic fake model by default):

   ```bash
   make run
   ```

## Quality gates

Before opening a pull request, run:

```bash
make check
```

This executes:

- `ruff check .`
- `mypy src`
- `pytest`

## Coding standards

- Prefer typed, small modules (keep files under ~400 lines when practical).
- Use Pydantic models at system boundaries.
- Use structured logging (`structlog`); do not use `print` in production modules.
- Do not hardcode secrets.
- Catch only expected exception types; raise domain-specific errors from
  `incident_commander.domain.exceptions`.
- Keep external integrations behind interfaces and inject dependencies.
- Never enable autonomous destructive actions. Write tools require human approval.

## Pull requests

1. Create a focused branch from `dev`.
2. Keep changes scoped to one concern when possible.
3. Add or update tests for behavior changes.
4. Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.
5. Fill out the pull request template completely.

## Testing guidance

- Unit tests cover success, failure, timeout, malformed input, and denied approval paths.
- Integration tests may require Docker Compose services.
- Do not fabricate evaluation metrics; run the evaluation harness against fixtures.

## Security reports

Do not open public issues for vulnerabilities. Follow [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
