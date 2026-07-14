# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY servers ./servers

RUN pip install --upgrade pip \
    && pip install .

FROM base AS runtime

RUN useradd --create-home --uid 10001 appuser
USER appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src
COPY --from=builder /app/servers /app/servers

ENV PYTHONPATH=/app/src \
    INCIDENT_COMMANDER_API_HOST=0.0.0.0 \
    INCIDENT_COMMANDER_API_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:8000/health" || exit 1

CMD ["uvicorn", "incident_commander.main:app", "--host", "0.0.0.0", "--port", "8000"]
