# API Specification: AGENTOPS OBSERVATORY

All endpoints are mounted under `/api/v1` and at the root `/`.

---

## 1. System & Collector Endpoints

### `GET /health`
Returns system operational state and connected services.
```json
{
  "status": "healthy",
  "service": "AgentOps Observatory",
  "version": "1.0.0",
  "database": "connected (sqlite/postgres)"
}
```

### `GET /version`
Returns schema specification version and active rule versions.

### `POST /events`
Ingest single event with optional idempotency key.
- Header: `Idempotency-Key: <unique-key>`
- Header: `X-AgentOps-API-Key: <api-key>`

### `POST /events/batch`
Ingest an array of events atomically.

---

## 2. Telemetry & Trace Endpoints

### `GET /runs`
Query runs with pagination and filtering.
- Query parameters: `status`, `agent_name`, `is_partial`, `limit`, `offset`.

### `GET /runs/{id}`
Returns complete run details, aggregate metrics, and all associated events.

### `GET /runs/{id}/timeline`
Returns assembled Directed Acyclic Graph (DAG) trace, parent-child relationships, relative timeline offset bars, and orphan warnings.

---

## 3. Governance & Audit Endpoints

### `GET /policies/violations`
Feed of detected guardrail violations filtered by severity (`CRITICAL`, `HIGH`, `MEDIUM`).

### `GET /incidents`
Aggregated incident tickets created from high-impact violations.

### `GET /redactions`
Audit log of all masked secrets, locations, and surrogate placeholders.

### `GET /metrics/overview`
Aggregated platform KPI metrics: total runs, compliance rate, cost, energy, carbon.

### `GET /export/runs/{id}`
Sanitized JSON export of an agent run and its hash chain.
