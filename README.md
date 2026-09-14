# AGENTOPS OBSERVATORY

<div align="center">

[![CI](https://github.com/vijaymahes9080/AgentOps-Observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/vijaymahes9080/AgentOps-Observatory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Compatible-orange.svg)](https://opentelemetry.io)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Production-grade Observability, Governance, and Audit Platform for AI Agents, MCP Servers, RAG Pipelines, and n8n Workflows.**  
*Records what happened during an agent execution without exposing secrets or unnecessary personal data.*

</div>

---

## 🌟 Key Features

1. **Agent Telemetry Collection**: Captures and correlates multi-agent execution events, parent-child span trees, and task goals.
2. **Model Call Tracking**: Records prompt/completion tokens, latency, temperature, model names, finish reasons, and cost calculations.
3. **Model Context Protocol (MCP) Observer**: Native adapter for MCP `tools/call`, `tools/list`, and resource readings.
4. **n8n Workflow Tracking**: Webhook listener mapping node executions, triggers, and HMAC signature validations.
5. **Interactive Trace Timeline & DAG**: Visual Gantt-style timeline offset bars and parent-child span trees with failure propagation.
6. **Multi-Dimensional Metrics**: Real-time calculation of latency, tokens, financial cost ($ USD), electrical energy (kWh), and carbon emissions (gCO2eq).
7. **Deterministic Redaction Engine**: Masks API keys (OpenAI, Anthropic, AWS, JWTs), Bearer tokens, passwords, emails, SSNs, and credit cards (validated via Luhn algorithm).
8. **10 Security Guardrails**: Enforces policies against unauthorized tools, sensitive data access, external network calls, destructive commands, retry loops, missing approvals, cross-user access, unknown MCP servers, unsigned webhooks, and prompt injections.
9. **Anomaly Detection**: Catches Markov sequence transition anomalies, sudden retry bursts, unusually large payloads, and novel network destinations.
10. **Tamper-Evident Append-Only Storage**: Mathematical SHA-256 hash chaining (`current_hash = SHA256(prev_hash + canonical_event_json)`).
11. **Interactive CLI (`agentops-cli`)**: Terminal dashboard for monitoring system health, streaming live agent runs, and inspecting hashes.
12. **OpenTelemetry (OTel) Compatibility**: Exports OTLP-compliant trace resource spans to Jaeger, Grafana Tempo, and SigNoz.
13. **Intelligent Model Router**: Complexity evaluator and routing engine recommending lighter models for 85%+ cost savings.
14. **Live WebSocket Streaming**: Real-time bidirectional telemetry streaming endpoint (`/ws/telemetry`).
15. **Multi-Channel Alerting**: Instant dispatching of security breaches to Slack and Discord webhooks.
16. **Adversarial Sandbox**: Multi-agent red-teaming simulator evaluating jailbreak resistance.
17. **High-Density Glassmorphic Dashboard**: 11 dedicated views with modern typography, dark theme, and keyboard navigation.

---

## 📊 Evaluation Benchmark & SLA Targets

Verified against **200 synthetic evaluation runs** (100 normal runs + 20 unauthorized tools + 20 credential leaks + 20 repeated failure loops + 20 prompt injection attempts + 20 partial traces):

| Metric | Target SLA | Observatory Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Trace Completeness** | $\ge 95\%$ | **100.0%** | **PASS** |
| **Seeded Secret Masking** | $100\%$ | **100.0%** | **PASS** |
| **Policy Detection Recall** | $\ge 85\%$ | **100.0%** | **PASS** |
| **Policy Precision** | $\ge 85\%$ | **100.0%** | **PASS** |
| **Cross-User Data Leakage** | $0$ | **0 leaks** | **PASS** |
| **Partial Trace Detection** | $100\%$ | **100.0% (20/20)** | **PASS** |

---

## 🏛️ System Architecture

```
[Agent Frameworks / MCP Servers / n8n Webhooks]
                       │
                       ▼ HTTP POST /events (Idempotency, Request-ID)
┌────────────────────────────────────────────────────────────────────────┐
│                   INGESTION & GOVERNANCE PIPELINE                      │
│                                                                        │
│  1. Duplicate & Idempotency Check                                      │
│  2. Deterministic Redaction Engine (Regex, Luhn algorithm, AST)        │
│  3. Deterministic Policy Engine (10 Guardrails)                        │
│  4. Anomaly Engine (Markov State Transitions & Spike Detection)        │
│  5. Cost, Latency, Energy & Carbon Calculator                          │
│  6. Tamper-Evident SHA-256 Hash Chaining (prev_hash -> current_hash)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  STORAGE & RETRIEVAL ENGINE                            │
│  SQLite (Local-First Zero-Config) / PostgreSQL + pgvector (Production) │
│  Redis In-Memory Queue & Rate Limiter                                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             OBSERVATORY DASHBOARD & REPORT EXPORT                      │
│  React + TypeScript + Vite + Glassmorphic Dark Design System           │
│  DAG Span Graphs, Trace Timelines, Policy Triage, SOC2 Audit Reports   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Local-First Development (Zero External Container Dependencies)

```bash
# Clone repository
git clone https://github.com/vijaymahes9080/AgentOps-Observatory.git
cd AgentOps-Observatory

# Install backend dependencies
pip install -e .

# Start Backend API Server (SQLite local-first default)
python -m uvicorn backend.main:app --port 8000 --reload
```
Interactive API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

```bash
# In a separate terminal, seed demo data and run benchmark evaluation
python scripts/seed.py
python -m evaluation.evaluator

# Start Frontend Dashboard
cd frontend
npm install
npm run dev
```
Interactive Dashboard: [http://localhost:5173](http://localhost:5173)

---

### 2. Using the Interactive CLI (`agentops-cli`)

```bash
# Check observatory system health
python cli/agentops_cli.py status

# Stream recent agent runs in your terminal
python cli/agentops_cli.py runs --limit 15
```

---

### 3. Docker Compose Production Deployment

```bash
docker compose up --build -d
```
Services deployed:
- **Dashboard**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL (pgvector)**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

---

## 🧪 Testing

Run the complete unit, API, stress, and adversarial injection test suite:

```bash
pytest tests/ -v
```

Run the ingestion performance load test:

```bash
python scripts/load_test.py
```

---

## 📁 Repository Structure

```
/
  backend/
    app/
      core/               # Security, RBAC, hash chaining, config
      models/             # SQLAlchemy ORM models (AgentRun, DBEvent, Violations, Audits)
      schemas/            # Pydantic v2 event schemas (Phase 1)
      api/                # FastAPI routers (events, runs, timeline, metrics, exports)
      services/           # Ingestion, trace DAG builder, metrics calculator, OTel
    main.py               # Application entrypoint with security middleware
  frontend/
    src/
      components/         # Sidebar, Header, DagVisualizer, CommandPalette
      pages/              # 11 Dashboard pages (Overview, LiveRuns, RunDetail, MCP, n8n, etc.)
      services/           # API client and WebSocket streaming hook
      types/              # TypeScript telemetry types
  collectors/
    agent/                # Python Agent SDK, LangChain/AutoGen callbacks, Node.js SDK
    mcp/                  # Model Context Protocol adapter & emulator
    n8n/                  # n8n webhook listener & HMAC verifier
  policy/                 # Deterministic policy engine (10 guardrails) & DSL engine
  redaction/              # Deterministic secret & PII redaction engine (Luhn algorithm)
  anomaly/                # Deterministic anomaly detection engine & clustering
  evaluation/             # Synthetic fixture generator & benchmark runner
  tests/                  # Unit, API, stress, and injection test suite (31 tests)
  docs/                   # Architecture, API, Policy, Deployment, and Threat Model docs
  cli/                    # Interactive command line tool (agentops-cli)
  scripts/                # Seeder and load test scripts
  docker-compose.yml      # Multi-container production deployment
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Vijay Mahes (Vijaypradhap2004@gmail.com).
