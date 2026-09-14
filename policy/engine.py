"""
AgentOps Observatory - Deterministic Policy & Governance Engine (Phase 4)
Enforces 10 deterministic security guardrails for AI Agents, MCP tool calls, and n8n workflows.
Returns structured PolicyEvent violations with evidence, severity, confidence, and remediation.
"""

import re
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from backend.app.schemas.events import (
    BaseEvent,
    EventStatus,
    ModelCall,
    PolicyEvent,
    PolicySeverity,
    SensitivityLevel,
    SourceType,
    ToolCall,
    WorkflowEvent,
)


class PolicyEngine:
    """
    Deterministic governance engine that inspects events against 10 core security rules.
    """

    DEFAULT_ALLOWED_TOOLS: Set[str] = {
        "read_file", "view_file", "search_web", "list_dir", "grep_search",
        "calculate", "format_json", "http_get", "database_query_readonly",
        "mcp_fetch_weather", "mcp_read_resource", "n8n_notify_slack"
    }

    ALLOWED_MCP_SERVERS: Set[str] = {
        "mcp-local-filesystem", "mcp-github", "mcp-weather", "mcp-database-readonly", "mcp-observatory"
    }

    DESTRUCTIVE_PATTERNS = [
        re.compile(r"\brm\s+-(?:rf|fr|r)\b", re.IGNORECASE),
        re.compile(r"\bDROP\s+(?:TABLE|DATABASE|SCHEMA)\b", re.IGNORECASE),
        re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE),
        re.compile(r"\bDELETE\s+FROM\s+\w+\s*(?:;|$|\s+(?!WHERE))\b", re.IGNORECASE),
        re.compile(r"\bchmod\s+777\b", re.IGNORECASE),
        re.compile(r"\bmkfs(?:\.\w+)?\b", re.IGNORECASE),
        re.compile(r"\bformat\s+[c-z]:", re.IGNORECASE),
        re.compile(r"\bkill\s+-9\b", re.IGNORECASE),
    ]

    SENSITIVE_PATH_PATTERNS = [
        re.compile(r"(?:/etc/passwd|/etc/shadow|\.aws/credentials|\.ssh/id_rsa|\.env\b|id_ed25519)", re.IGNORECASE),
        re.compile(r"(?:c:[\\/]windows[\\/]system32[\\/]config[\\/]sam)", re.IGNORECASE),
        re.compile(r"(?:master\.key|secrets\.yaml|vault_token)", re.IGNORECASE),
    ]

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|directions)", re.IGNORECASE),
        re.compile(r"disregard\s+(?:all\s+)?(?:prior\s+)?(?:safety|system)\s+rules", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(?:DAN|unrestricted|jailbroken|free)", re.IGNORECASE),
        re.compile(r"system\s*override\s*:\s*(?:disable\s*safety|bypass)", re.IGNORECASE),
        re.compile(r"<\s*\|im_start\|\s*>system", re.IGNORECASE),
        re.compile(r"\[SYSTEM\s+PROMPT\s+OVERRIDE\]", re.IGNORECASE),
        re.compile(r"bypass\s+all\s+policy\s+checks", re.IGNORECASE),
    ]

    DISALLOWED_NET_DESTINATIONS = [
        re.compile(r"\b(?:http://|https://)?(?:169\.254\.169\.254|metadata\.google\.internal)\b"),  # Cloud metadata
        re.compile(r"\b(?:http://|https://)?(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?/(?:admin|internal|shutdown)"),
        re.compile(r"\b(?:onion|darkweb|tor2web|tempmail)\b", re.IGNORECASE),
        re.compile(r"\b(?:pastebin\.com|webhook\.site|ngrok\.io|requestcatcher\.com)\b", re.IGNORECASE),
    ]

    HIGH_IMPACT_TOOLS = {
        "deploy_production", "transfer_funds", "send_external_mass_email",
        "delete_user_account", "update_security_firewall", "rotate_master_key"
    }

    def __init__(
        self,
        allowed_tools: Optional[Set[str]] = None,
        allowed_mcp_servers: Optional[Set[str]] = None
    ):
        self.allowed_tools = allowed_tools or set(self.DEFAULT_ALLOWED_TOOLS)
        self.allowed_mcp_servers = allowed_mcp_servers or set(self.ALLOWED_MCP_SERVERS)
        self._tool_retry_history: Dict[str, int] = {}

    def evaluate_event(
        self,
        event: BaseEvent,
        run_context: Optional[Dict[str, Any]] = None
    ) -> List[PolicyEvent]:
        """
        Evaluate an event against all 10 deterministic security policies.
        Returns a list of PolicyEvent violations (empty if fully compliant).
        """
        violations: List[PolicyEvent] = []
        run_context = run_context or {}

        # Rule 1: Unauthorized Tool
        if isinstance(event, ToolCall):
            if event.tool_name not in self.allowed_tools:
                violations.append(self._create_violation(
                    rule_id="unauthorized_tool",
                    rule_name="Unauthorized Tool Invocation",
                    severity=PolicySeverity.HIGH,
                    evidence=f"Tool '{event.tool_name}' is not in approved tool whitelist.",
                    affected_event_id=event.event_id,
                    remediation=f"Add '{event.tool_name}' to approved policies or restrict agent capabilities.",
                    confidence=1.0,
                    run_id=event.run_id
                ))

        # Rule 2: Sensitive Data Access
        target_text = self._extract_text_for_inspection(event)
        for pattern in self.SENSITIVE_PATH_PATTERNS:
            match = pattern.search(target_text)
            if match:
                violations.append(self._create_violation(
                    rule_id="sensitive_data_access",
                    rule_name="Restricted / Sensitive Data Access Attempt",
                    severity=PolicySeverity.CRITICAL,
                    evidence=f"Target path or secret pattern matched: '{match.group(0)}'",
                    affected_event_id=event.event_id,
                    remediation="Block agent access to root keys, credential stores, and host system configurations.",
                    confidence=0.98,
                    run_id=event.run_id
                ))
                break

        # Rule 3: External Network Call to Disallowed Destinations
        for pattern in self.DISALLOWED_NET_DESTINATIONS:
            match = pattern.search(target_text)
            if match:
                violations.append(self._create_violation(
                    rule_id="external_network_call",
                    rule_name="Disallowed External Network Connection",
                    severity=PolicySeverity.CRITICAL,
                    evidence=f"Network target '{match.group(0)}' violates egress boundary constraints.",
                    affected_event_id=event.event_id,
                    remediation="Enforce network isolation policies and block outbound SSRF metadata access.",
                    confidence=0.95,
                    run_id=event.run_id
                ))
                break

        # Rule 4: Destructive Action
        for pattern in self.DESTRUCTIVE_PATTERNS:
            match = pattern.search(target_text)
            if match:
                violations.append(self._create_violation(
                    rule_id="destructive_action",
                    rule_name="Destructive Command Detected",
                    severity=PolicySeverity.CRITICAL,
                    evidence=f"Destructive pattern matched: '{match.group(0)}'",
                    affected_event_id=event.event_id,
                    remediation="Require sandbox filesystem snapshots and strict command parameter whitelisting.",
                    confidence=1.0,
                    run_id=event.run_id
                ))
                break

        # Rule 5: Excessive Retries
        if isinstance(event, ToolCall):
            key = f"{event.run_id}:{event.tool_name}"
            if event.status == EventStatus.ERROR or event.retry_count > 0:
                current = self._tool_retry_history.get(key, 0) + (event.retry_count or 1)
                self._tool_retry_history[key] = current
                if current >= 3:
                    violations.append(self._create_violation(
                        rule_id="excessive_retries",
                        rule_name="Excessive Failure Retries Threshold Exceeded",
                        severity=PolicySeverity.MEDIUM,
                        evidence=f"Tool '{event.tool_name}' failed or was retried {current} times.",
                        affected_event_id=event.event_id,
                        remediation="Halt infinite tool loops with exponential backoff and breaker policies.",
                        confidence=0.99,
                        run_id=event.run_id
                    ))
            elif event.status == EventStatus.SUCCESS and key in self._tool_retry_history:
                self._tool_retry_history.pop(key, None)

        # Rule 6: Missing Approval
        if isinstance(event, ToolCall) and event.tool_name in self.HIGH_IMPACT_TOOLS:
            has_approval = run_context.get("human_approval_granted", False)
            if not has_approval:
                violations.append(self._create_violation(
                    rule_id="missing_approval",
                    rule_name="High-Impact Action Missing Human Approval",
                    severity=PolicySeverity.HIGH,
                    evidence=f"Action '{event.tool_name}' requires human-in-the-loop authorization.",
                    affected_event_id=event.event_id,
                    remediation="Trigger approval gate workflow before proceeding with state-altering actions.",
                    confidence=1.0,
                    run_id=event.run_id
                ))

        # Rule 7: Cross-User Access
        actor_tenant = run_context.get("tenant_id") or run_context.get("user_id")
        accessed_tenant = (
            getattr(event, "provenance", {}).get("target_tenant")
            or (event.attributes.get("target_tenant") if isinstance(event, BaseEvent) and hasattr(event, "attributes") else None)
        )
        if actor_tenant and accessed_tenant and actor_tenant != accessed_tenant:
            violations.append(self._create_violation(
                rule_id="cross_user_access",
                rule_name="Cross-Tenant / Cross-User Resource Violation",
                severity=PolicySeverity.CRITICAL,
                evidence=f"Actor '{actor_tenant}' attempted unauthorized access to tenant '{accessed_tenant}'.",
                affected_event_id=event.event_id,
                remediation="Enforce strict tenant isolation filters at the query and storage boundary.",
                confidence=1.0,
                run_id=event.run_id
            ))

        # Rule 8: Unknown MCP Server
        if isinstance(event, ToolCall) and event.is_mcp:
            if not event.mcp_server or event.mcp_server not in self.allowed_mcp_servers:
                violations.append(self._create_violation(
                    rule_id="unknown_mcp_server",
                    rule_name="Unknown or Untrusted MCP Server Invocation",
                    severity=PolicySeverity.HIGH,
                    evidence=f"MCP Server '{event.mcp_server}' is not registered in the trusted MCP inventory.",
                    affected_event_id=event.event_id,
                    remediation="Register MCP server in configuration or require cryptographic server attestation.",
                    confidence=1.0,
                    run_id=event.run_id
                ))

        # Rule 9: Untrusted Workflow Input (n8n)
        if isinstance(event, WorkflowEvent):
            if not event.webhook_verified:
                violations.append(self._create_violation(
                    rule_id="untrusted_workflow_input",
                    rule_name="Untrusted / Unsigned Workflow Webhook Trigger",
                    severity=PolicySeverity.HIGH,
                    evidence=f"Workflow '{event.workflow_name}' received execution without valid HMAC signature.",
                    affected_event_id=event.event_id,
                    remediation="Enable HMAC webhook signing verification in n8n triggers.",
                    confidence=0.95,
                    run_id=event.run_id
                ))

        # Rule 10: Prompt Injection Indicator
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            match = pattern.search(target_text)
            if match:
                violations.append(self._create_violation(
                    rule_id="prompt_injection_indicator",
                    rule_name="Prompt Injection / Instruction Override Indicator",
                    severity=PolicySeverity.HIGH,
                    evidence=f"Prompt contains jailbreak signature: '{match.group(0)}'",
                    affected_event_id=event.event_id,
                    remediation="Sanitize user inputs, enforce system prompt delimiters, and apply input classifiers.",
                    confidence=0.92,
                    run_id=event.run_id
                ))
                break

        return violations

    def _extract_text_for_inspection(self, event: BaseEvent) -> str:
        """Extract all searchable textual tokens from event payload."""
        text_parts = []
        if isinstance(event, ModelCall):
            if event.prompt_redacted:
                text_parts.append(event.prompt_redacted)
            if event.response_redacted:
                text_parts.append(event.response_redacted)
        elif isinstance(event, ToolCall):
            text_parts.append(str(event.tool_name))
            text_parts.append(str(event.arguments_redacted))
            if event.result_redacted:
                text_parts.append(str(event.result_redacted))
        elif isinstance(event, WorkflowEvent):
            if event.input_redacted:
                text_parts.append(str(event.input_redacted))
            if event.output_redacted:
                text_parts.append(str(event.output_redacted))
        return " ".join(text_parts)

    def _create_violation(
        self,
        rule_id: str,
        rule_name: str,
        severity: PolicySeverity,
        evidence: str,
        affected_event_id: Optional[str],
        remediation: str,
        confidence: float,
        run_id: str
    ) -> PolicyEvent:
        return PolicyEvent(
            event_id=str(uuid4()),
            run_id=run_id,
            source=SourceType.SYSTEM,
            actor="policy-engine",
            status=EventStatus.VIOLATED,
            sensitivity=SensitivityLevel.RESTRICTED,
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            evidence=evidence,
            affected_event_id=affected_event_id,
            remediation=remediation,
            confidence=confidence,
            provenance={"policy_spec": "AgentOps-Guardrail-1.0"}
        )
