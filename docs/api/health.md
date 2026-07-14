# Health API

## `GET /health`

Liveness probe. Returns whether the HTTP process is alive.

Example:

```bash
curl -s http://localhost:8000/health | jq
```

```json
{
  "status": "ok",
  "service": "Autonomous AI Incident Commander",
  "version": "0.1.0",
  "timestamp": "2026-07-14T21:00:00+00:00"
}
```

## `GET /ready`

Readiness probe. Runs injectable dependency checks. Returns HTTP 503 when not
ready.

Example:

```bash
curl -s http://localhost:8000/ready | jq
```

Stage 1 registers an `application` check that always succeeds. Database and
Redis probes remain opt-in via settings for later stages.
