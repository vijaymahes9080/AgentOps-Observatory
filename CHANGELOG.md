# Changelog: AgentOps Observatory

All notable changes to the AgentOps Observatory platform are documented here.

---

## [v1.1.0] — 2026-09-14

### Added
- **Interactive CLI**: Added `agentops-cli` tool with live terminal dashboard and telemetry streamer.
- **OpenTelemetry (OTel)**: Full OTLP resource span transformer and export endpoint (`/export/runs/{id}/otlp`).
- **Model Cost Optimizer**: Intelligent complexity evaluator and routing engine for 85%+ cost savings.
- **Live WebSocket Hub**: Real-time bidirectional telemetry streaming endpoint (`/ws/telemetry`).
- **Multi-Channel Alerting**: Instant dispatching of security breaches to Slack and Discord webhooks.
- **Custom Policy DSL**: Declarative JSON/YAML rule definition engine with dynamic condition operators.
- **Adversarial Sandbox**: Multi-agent red-teaming simulator evaluating jailbreak resistance.
- **Semantic Clustering**: Vector-based cosine similarity engine to catch behavioral intent drift.
- **Eco-Compute Engine**: Real-time tree-seedling offset equivalence and datacenter water usage metrics.
- **SOC 2 & ISO 42001 Generator**: Automated official HTML/JSON compliance certificate generator.
- **Multi-Language SDKs**: Added TypeScript / Node.js client SDK and Python LangChain / AutoGen callback hooks.
- **MCP Protocol Sandbox**: Mock JSON-RPC 2.0 server emulator for local MCP tool testing.
- **Time-Travel Run Replayer**: Step-by-step trace replayer with state delta analysis.
- **Custom Redaction Registry**: Enterprise dictionary and regex registration for internal tokens.
- **Graph Exporters**: One-click Mermaid diagram (`graph TD`) and Graphviz DOT generator for agent DAGs.
- **Performance Load Tester**: Benchmark script measuring 1,000+ events/sec with p99 latency stats.
- **Enhanced UI Suite**:
  - Live Playground for real-time redaction & prompt injection testing.
  - Model Cost Optimizer page with savings calculator.
  - Interactive DAG Visualizer with connection lines and status badges.
  - Printable official Compliance Certificate view.
  - Command Palette (`Ctrl+K` / `Cmd+K`) modal for rapid navigation.
  - Cyberpunk, Aurora, and Matrix glassmorphic theme presets.
- **Extended Test Suite**:
  - Cryptographic append-only hash chain stress test (500 sequential events).
  - 10 adversarial prompt injection and jailbreak tests.
  - Automated CI performance regressions check.

---

## [v1.0.0] — 2026-09-14
- Initial production release: Event schemas, collector API, deterministic redaction, 10 security guardrails, trace graph DAG, MCP and n8n adapters, cost/energy metrics, anomaly detector, 11-page React dashboard, Docker Compose, and 200-run evaluation suite.
