"""
AgentOps Observatory - Custom Policy Rule Definition Language (DSL) (Phase 4+)
Allows operators and security architects to define custom dynamic guardrails
via declarative JSON/YAML without recompiling backend code.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.events import BaseEvent, PolicyEvent, PolicySeverity, SourceType, ToolCall, ModelCall


class DSLRule(BaseModel):
    id: str
    name: str
    severity: PolicySeverity = PolicySeverity.HIGH
    event_type: Optional[str] = None  # "ToolCall", "ModelCall", "Span", or None for all
    condition_field: str              # e.g. "duration_ms", "prompt_redacted", "tool_name"
    operator: str                     # "gt", "lt", "contains", "not_contains", "regex_match", "in"
    value: Any
    remediation: str
    confidence: float = 1.0


class PolicyDSLEngine:
    """Evaluates arbitrary dynamic DSL rules against telemetry event streams."""

    def __init__(self, rules: Optional[List[DSLRule]] = None):
        self.rules: List[DSLRule] = rules or []

    def add_rule(self, rule: DSLRule):
        self.rules.append(rule)

    def evaluate(self, event: BaseEvent) -> List[PolicyEvent]:
        violations: List[PolicyEvent] = []
        event_dict = event.model_dump()

        for rule in self.rules:
            # Check event type constraint
            if rule.event_type and event.__class__.__name__ != rule.event_type:
                continue

            field_val = event_dict.get(rule.condition_field)
            # If not in top-level, check nested attributes
            if field_val is None and "attributes" in event_dict:
                field_val = event_dict["attributes"].get(rule.condition_field)

            if field_val is None:
                continue

            is_match = False
            try:
                if rule.operator == "gt":
                    is_match = float(field_val) > float(rule.value)
                elif rule.operator == "lt":
                    is_match = float(field_val) < float(rule.value)
                elif rule.operator == "contains":
                    is_match = str(rule.value).lower() in str(field_val).lower()
                elif rule.operator == "not_contains":
                    is_match = str(rule.value).lower() not in str(field_val).lower()
                elif rule.operator == "regex_match":
                    is_match = bool(re.search(str(rule.value), str(field_val), re.IGNORECASE))
                elif rule.operator == "in":
                    is_match = field_val in rule.value
            except Exception:
                is_match = False

            if is_match:
                violations.append(PolicyEvent(
                    rule_id=f"dsl_{rule.id}",
                    rule_name=rule.name,
                    severity=rule.severity,
                    evidence=f"DSL Condition '{rule.condition_field} {rule.operator} {rule.value}' triggered with value '{field_val}'",
                    affected_event_id=event.event_id,
                    remediation=rule.remediation,
                    confidence=rule.confidence,
                    run_id=event.run_id,
                    source=SourceType.SYSTEM
                ))

        return violations
