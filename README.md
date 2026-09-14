# AGENTOPS OBSERVATORY

[![CI](https://github.com/vijaymahes9080/AgentOps-Observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/vijaymahes9080/AgentOps-Observatory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev)

> **Observability, Governance, and Audit Platform for AI Agents, MCP Servers, RAG Pipelines, and n8n Workflows.**
> Records what happened during an agent execution without exposing secrets or unnecessary personal data.

---

## Key Features

1. **Agent Telemetry Collection**: Capture and correlate multi-agent runs, spans, and child operations with parent ID lineage.
2. **Model Call Tracking**: Monitor prompt and completion tokens, latency, temperature, model names, and finish reasons.
3. **MCP Tool Call Tracking**: Native observer for Model Context Protocol (MCP) `tools/call`, `tools/list`, and resource readings.
4. **n8n Workflow Tracking**: Webhook listener mapping node executions, triggers, and HMAC signature validations.
5. **Interactive Trace Timeline & DAG**: Visual Gantt-style timeline offset bars and parent-child span trees with failure propagation.
6. **Multi-Dimensional Metrics**: Real-time calculation of latency, tokens, estimated financial cost ($), energy (kWh), and carbon emissions (gCO2eq).
7. **Deterministic Redaction Engine**: Masks API keys (OpenAI, Anthropic, AWS, JWTs), Bearer tokens, passwords, emails, SSNs, and credit cards (validated via Luhn algorithm).
8. **10 Security Guardrails**: Enforce policies against unauthorized tools, sensitive data access, external network calls, destructive commands, retry loops, missing approvals, cross-user access, unknown MCP servers, unsigned webhooks, and prompt injections.
9. **Anomaly Detection**: Catch Markov sequence transition anomalies, sudden retry bursts, unusually large payloads, and novel network destinations.
10. **Tamper-Evident Append-Only Storage**: Mathematical SHA-256 hash chaining (`current_hash = SHA256(prev_hash + canonical_event_json)`).
11. **Local-First & Cloud Ready**: Zero-dependency SQLite local mode + PostgreSQL/Redis Docker Compose production mode.
12. **High-Density Glassmorphic Dashboard**: 11 dedicated views with modern typography, dark theme, and keyboard navigation.

---

## Evaluation Benchmark & SLA Targets

Tested against **200 synthetic runs** (100 normal runs + 20 unauthorized tools + 20 credential leaks + 20 repeated failure loops + 20 prompt injection attempts + 20 partial traces):

| Metric | Target SLA | Observatory Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Trace Completeness** | $\ge 95\%$ | **100.0%** | **PASS** |
| **Seeded Secret Masking** | $100\%$ | **100.0%** | **PASS** |
| **Policy Detection Recall** | $\ge 85\%$ | **100.0%** | **PASS** |
| **Policy Precision** | $\ge 85\%$ | **100.0%** | **PASS** |
| **Cross-User Data Leakage** | $0$ | **0 leaks** | **PASS** |
| **Partial Trace Detection** | $100\%$ | **100.0% (20/20)** | **PASS** |

---

## Repository Structure

```
/
  backend/
    app/
      core/               # Configuration, security, RBAC, hash chaining
      models/             # SQLAlchemy ORM models (AgentRun, Event, Violations, Audits)
      schemas/            # Pydantic v2 schemas (Phase 1 Event Schemas)
      api/                # FastAPI routes (events, runs, timeline, metrics, exports)
      services/           # Ingestion, trace graph DAG generator, metrics calculator
    main.py               # FastAPI application entrypoint
  frontend/
    src/
      components/         # Sidebar, Header
      pages/              # 11 Dashboard pages (Overview, LiveRuns, RunDetail, MCP, n8n, etc.)
      services/           # API client
      types/              # TypeScript telemetry types
  collectors/
    agent/                # Python Agent SDK & `@observe_tool` decorator
    mcp/                  # Model Context Protocol adapter
    n8n/                  # n8n webhook listener & HMAC verifier
  policy/                 # Deterministic policy engine (10 guardrails)
  redaction/              # Deterministic secret & PII redaction engine (Luhn algorithm)
  anomaly/                # Deterministic anomaly detection engine
  evaluation/             # Synthetic fixture generator & benchmark runner
  tests/                  # Unit & API test suite (20 tests)
  docs/                   # Architecture, API, Policy, and Deployment documentation
  docker-compose.yml      # Multi-container production deployment
```

---

## Quick Start (Local-First)

### 1. Install & Run Backend
```bash
python -m uvicorn backend.main:app --port 8000 --reload
```

### 2. Seed Initial Telemetry & Run Benchmark
```bash
python scripts/seed.py
python -m evaluation.evaluator
```

### 3. Start Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## Quick Start (Docker Compose)

```bash
docker compose up --build -d
```
Access the dashboard at [http://localhost:5173](http://localhost:5173) and backend API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## License

MIT License. Designed and built for enterprise-grade autonomous AI governance.
