# Operations runbook

## Health checks
- `GET /health`: process-level health.
- `GET /ready`: database connectivity check.
- `GET /metrics`: Prometheus metrics.

## First response
1. `docker compose ps`
2. `docker compose logs --tail=200 backend`
3. Check `http://localhost:9090/targets` for Prometheus scrape status.
4. Check `http://localhost:16686` for traces.
5. Verify PostgreSQL health: `docker compose exec postgres pg_isready -U platform`.
6. Verify Redis: `docker compose exec redis redis-cli ping`.

## Data and safety
- Local Compose credentials are for development only.
- Back up PostgreSQL before upgrades.
- Avoid publishing database, Redis, Kafka, or OpenSearch ports publicly.
- Rotate credentials and use a secret manager for any shared environment.
