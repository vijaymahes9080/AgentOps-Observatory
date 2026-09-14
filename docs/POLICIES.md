# Deterministic Guardrails & Policy Specifications (Phase 4)

AgentOps Observatory implements 10 deterministic security rules:

| Rule ID | Name | Severity | Detection Logic | Remediation |
| :--- | :--- | :--- | :--- | :--- |
| `unauthorized_tool` | Unauthorized Tool Invocation | HIGH | Invoked tool is absent from role/context whitelist | Add tool to whitelist or restrict agent capabilities |
| `sensitive_data_access` | Sensitive Data Access Attempt | CRITICAL | Path matches `/etc/shadow`, `.ssh/id_rsa`, `.env`, SAM | Enforce container sandbox isolation |
| `external_network_call` | Disallowed External Network Connection | CRITICAL | Egress to cloud metadata (169.254.169.254) or darkweb | Block egress via firewall / proxy rules |
| `destructive_action` | Destructive Command Detected | CRITICAL | Patterns matching `rm -rf`, `DROP TABLE`, `chmod 777` | Require immutable filesystems and query whitelisting |
| `excessive_retries` | Excessive Failure Retries | MEDIUM | Tool failure or retry count exceeds threshold (>= 3) | Apply exponential backoff and circuit breakers |
| `missing_approval` | Missing Human Approval | HIGH | High-impact actions executed without human sign-off | Enforce human-in-the-loop approval gate |
| `cross_user_access` | Cross-Tenant / Cross-User Access | CRITICAL | Actor tenant differs from target resource tenant | Enforce strict tenant boundary checks |
| `unknown_mcp_server` | Unknown MCP Server | HIGH | Tool invoked on unverified/unregistered MCP endpoint | Register MCP server in verified inventory |
| `untrusted_workflow_input`| Untrusted Workflow Trigger | HIGH | n8n webhook execution without valid HMAC signature | Enable HMAC webhook signing in n8n triggers |
| `prompt_injection_indicator` | Prompt Injection / Jailbreak | HIGH | Prompt overrides ("ignore previous instructions", DAN) | Apply prompt boundary delimiters and sanitization |
