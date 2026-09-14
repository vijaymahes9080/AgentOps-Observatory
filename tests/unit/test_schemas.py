import pytest
from backend.app.schemas.events import (
    BaseEvent,
    CostEstimate,
    EnergyEstimate,
    EventStatus,
    ModelCall,
    PolicyEvent,
    PolicySeverity,
    RedactionEvent,
    SensitivityLevel,
    SourceType,
    Span,
    ToolCall,
    WorkflowEvent,
)


def test_base_event_defaults():
    ev = BaseEvent(run_id="run-123")
    assert ev.run_id == "run-123"
    assert ev.source == SourceType.AGENT
    assert ev.status == EventStatus.SUCCESS
    assert ev.version == "1.0.0"
    assert ev.event_id is not None
    assert ev.timestamp is not None


def test_model_call_schema():
    mc = ModelCall(
        run_id="run-1",
        model_name="gpt-4o",
        prompt_redacted="Hello AI",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        cost_estimate=CostEstimate(estimated_cost_usd=0.0003, model="gpt-4o")
    )
    assert mc.model_name == "gpt-4o"
    assert mc.total_tokens == 30
    assert mc.cost_estimate.estimated_cost_usd == 0.0003


def test_tool_call_schema():
    tc = ToolCall(
        run_id="run-2",
        tool_name="mcp_fetch_weather",
        is_mcp=True,
        mcp_server="mcp-weather",
        arguments_redacted={"city": "San Francisco"},
        result_redacted={"temp": 68}
    )
    assert tc.is_mcp is True
    assert tc.mcp_server == "mcp-weather"
    assert tc.tool_name == "mcp_fetch_weather"


def test_workflow_event_schema():
    wf = WorkflowEvent(
        run_id="run-3",
        workflow_id="wf-001",
        workflow_name="SlackNotifier",
        execution_id="exec-99",
        node_name="WebhookTrigger",
        node_type="n8n-nodes-base.webhook",
        webhook_verified=True
    )
    assert wf.workflow_name == "SlackNotifier"
    assert wf.webhook_verified is True
