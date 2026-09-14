# Architecture: AGENTOPS OBSERVATORY

AGENTOPS OBSERVATORY is an open-source, local-first and enterprise-ready observability, governance, and audit platform for autonomous AI agents, Model Context Protocol (MCP) servers, RAG pipelines, and n8n workflows.

---

## High-Level Architecture Diagram

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

## Core Tenets

1. **Zero-Trust Privacy**: Raw credentials, private keys, and PII are redacted *prior* to persistence and logging. Surrogates (e.g. `[REDACTED_API_KEY_abc123]`) allow audit correlation without exposure.
2. **Append-Only Tamper-Evident Auditability**: Every event stores `current_hash = SHA256(prev_hash + canonical_json(event))`, providing cryptographic proof of sequential integrity.
3. **No False Observability Claims**: Partial traces with orphan spans or unfinished parent contexts are explicitly flagged with `is_partial=True` and visual warning banners.
4. **Deterministic First, AI Second**: Guardrails and anomaly thresholds are evaluated using deterministic finite-state rules for low latency and zero hallucination.
