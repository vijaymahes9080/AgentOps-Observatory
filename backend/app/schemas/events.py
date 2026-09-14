"""
AgentOps Observatory - Event Schemas (Phase 1)
Production-grade Pydantic v2 event definitions for AI agents, MCP servers, RAG pipelines, and n8n workflows.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class SourceType(str, Enum):
    AGENT = "agent"
    MCP = "mcp"
    N8N = "n8n"
    MODEL = "model"
    RAG = "rag"
    SYSTEM = "system"


class EventStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    VIOLATED = "violated"
    REDACTED = "redacted"
    PARTIAL = "partial"


class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class MetricLabel(str, Enum):
    MEASURED = "measured"
    ESTIMATED = "estimated"
    SIMULATED = "simulated"


class BaseEvent(BaseModel):
    """
    Standard base event conforming to AgentOps Observatory Phase 1 requirements.
    All events inherit common metadata, audit fields, and provenance.
    """
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    run_id: str = Field(description="Correlated agent run identifier")
    parent_id: Optional[str] = Field(default=None, description="Parent event or span identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO 8601 UTC timestamp of occurrence"
    )
    source: SourceType = Field(default=SourceType.AGENT, description="Originating telemetry source")
    actor: str = Field(default="system", description="Initiator (e.g. user_id, service_account, agent_role)")
    tool_or_model_name: Optional[str] = Field(default=None, description="Model, tool, or node identifier")
    status: EventStatus = Field(default=EventStatus.SUCCESS, description="Execution status")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Duration of execution in milliseconds")
    sensitivity: SensitivityLevel = Field(default=SensitivityLevel.INTERNAL, description="Data sensitivity level")
    provenance: Dict[str, Any] = Field(
        default_factory=lambda: {"env": "production", "version": "1.0.0", "host": "localhost"},
        description="Lineage, environment, runtime metadata"
    )
    version: str = Field(default="1.0.0", description="Schema specification version")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Any) -> datetime:
        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                pass
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v
        return datetime.now(timezone.utc)


class CostEstimate(BaseModel):
    """Estimated cost metrics for model and tool invocations."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model: str = "unknown"
    currency: str = "USD"
    label: MetricLabel = MetricLabel.ESTIMATED


class EnergyEstimate(BaseModel):
    """Estimated energy consumption and carbon footprint."""
    energy_kwh: float = Field(default=0.0, description="Estimated electrical energy in kilowatt-hours")
    carbon_gco2eq: float = Field(default=0.0, description="Estimated carbon emissions in grams CO2 equivalent")
    pue: float = Field(default=1.2, description="Power Usage Effectiveness of hosting facility")
    grid_carbon_intensity: float = Field(default=385.0, description="Carbon intensity in gCO2/kWh")
    label: MetricLabel = MetricLabel.ESTIMATED


class Span(BaseEvent):
    """Hierarchical execution span representing an operation or sub-step."""
    span_id: str = Field(default_factory=lambda: str(uuid4()), description="Span identifier")
    name: str = Field(description="Human-readable span operation name")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary span attributes")
    error_message: Optional[str] = None
    is_root: bool = False


class ModelCall(BaseEvent):
    """LLM or SLM invocation record."""
    model_name: str = Field(description="Name of the model (e.g. gpt-4o, claude-3-5-sonnet, llama-3)")
    provider: str = Field(default="openai", description="Model provider (e.g. openai, anthropic, ollama, vllm)")
    prompt_redacted: Optional[str] = Field(default=None, description="Redacted prompt content")
    response_redacted: Optional[str] = Field(default=None, description="Redacted completion content")
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    temperature: Optional[float] = None
    cost_estimate: Optional[CostEstimate] = None
    energy_estimate: Optional[EnergyEstimate] = None
    finish_reason: Optional[str] = "stop"


class ToolCall(BaseEvent):
    """Tool invocation event (MCP, native function calling, Python tools)."""
    tool_name: str = Field(description="Invoked tool name")
    mcp_server: Optional[str] = Field(default=None, description="MCP server name or endpoint if applicable")
    arguments_redacted: Dict[str, Any] = Field(default_factory=dict, description="Redacted arguments payload")
    result_redacted: Optional[Any] = Field(
        default=None, description="Redacted tool response"
    )
    is_mcp: bool = False
    retry_count: int = 0
    error_details: Optional[str] = None


class WorkflowEvent(BaseEvent):
    """n8n or external orchestration workflow event."""
    workflow_id: str = Field(description="Workflow identifier")
    workflow_name: str = Field(description="Human readable workflow name")
    execution_id: str = Field(description="Workflow execution run ID")
    node_name: str = Field(description="Triggered node name")
    node_type: str = Field(description="Node type (e.g. n8n-nodes-base.webhook)")
    input_redacted: Optional[Dict[str, Any]] = None
    output_redacted: Optional[Dict[str, Any]] = None
    webhook_verified: bool = True


class PolicySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PolicyEvent(BaseEvent):
    """Security or operational policy violation event."""
    rule_id: str = Field(description="Policy rule identifier (e.g. unauthorized_tool, prompt_injection_indicator)")
    rule_name: str = Field(description="Human readable policy title")
    severity: PolicySeverity = Field(default=PolicySeverity.HIGH, description="Violation severity")
    evidence: str = Field(description="Redacted evidence snippet demonstrating the violation")
    affected_event_id: Optional[str] = Field(default=None, description="Associated event ID")
    remediation: str = Field(description="Recommended corrective action")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Detection confidence score")


class RedactionEvent(BaseEvent):
    """Audit log of secret or PII redaction event. NEVER stores the raw secret."""
    redaction_type: str = Field(description="Type of secret/PII masked (e.g. API_KEY, BEARER_TOKEN, SSN, EMAIL)")
    masked_placeholder: str = Field(description="Safe placeholder inserted into payload")
    location: str = Field(description="JSONPath, key name, or parameter where token was found")
    policy_version: str = Field(default="1.0.0", description="Redaction rule policy version")
    character_count: int = Field(default=0, ge=0, description="Length of original redacted value")


class Incident(BaseEvent):
    """Aggregated incident ticket generated from critical policy violations or fatal failures."""
    incident_id: str = Field(default_factory=lambda: f"INC-{uuid4().hex[:8].upper()}")
    title: str = Field(description="Brief incident title")
    summary: str = Field(description="Description of incident root cause")
    severity: PolicySeverity = Field(default=PolicySeverity.HIGH)
    related_event_ids: List[str] = Field(default_factory=list)
    resolved: bool = False
    resolution_notes: Optional[str] = None


class AuditEvent(BaseEvent):
    """Append-only tamper-evident audit record with cryptographic hash chaining."""
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    action: str = Field(description="Audit action (e.g. EVENT_INGEST, POLICY_VIOLATION, EXPORT_GENERATED)")
    actor_id: str = Field(description="User or service performing the action")
    details: Dict[str, Any] = Field(default_factory=dict)
    prev_hash: str = Field(description="SHA-256 hash of previous audit record in chain")
    event_hash: str = Field(description="SHA-256 hash of this record's canonical representation")


class AgentRun(BaseEvent):
    """Top-level agent execution session aggregating overall run metrics and status."""
    agent_name: str = Field(default="agent-default", description="Identifier of the executing AI agent")
    goal: Optional[str] = Field(default=None, description="Stated objective or high-level prompt")
    root_span_id: Optional[str] = Field(default=None, description="ID of root execution span")
    is_partial: bool = Field(default=False, description="True if telemetry is missing, timed out, or incomplete")
    missing_telemetry_reasons: List[str] = Field(default_factory=list, description="Explanations for partial marking")
    total_events: int = 0
    total_duration_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_energy_kwh: float = 0.0
    total_carbon_gco2eq: float = 0.0
    policy_violation_count: int = 0
    redaction_count: int = 0
    tags: List[str] = Field(default_factory=list)
