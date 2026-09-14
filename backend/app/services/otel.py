"""
AgentOps Observatory - OpenTelemetry (OTel) OTLP Transformer & Exporter
Translates AgentOps internal events into standard OpenTelemetry Protocol (OTLP/HTTP)
resource spans and instrumentation scopes for export to Jaeger, Grafana Tempo, or SigNoz.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
from backend.app.schemas.events import BaseEvent, ModelCall, Span, ToolCall


class OTLPTransformer:
    """Transforms AgentOps events into standard W3C / OTel Trace ResourceSpans."""

    @classmethod
    def transform_to_otlp_resource_spans(
        cls,
        run_id: str,
        agent_name: str,
        events: List[BaseEvent]
    ) -> Dict[str, Any]:
        spans_otlp = []

        for ev in events:
            # Convert timestamp to nanoseconds since Unix epoch
            ts_nano = int(ev.timestamp.timestamp() * 1e9)
            duration_nano = int(ev.duration_ms * 1e6)
            end_nano = ts_nano + duration_nano

            attributes = [
                {"key": "agentops.event_id", "value": {"stringValue": ev.event_id}},
                {"key": "agentops.run_id", "value": {"stringValue": ev.run_id}},
                {"key": "agentops.source", "value": {"stringValue": ev.source.value}},
                {"key": "agentops.actor", "value": {"stringValue": ev.actor}},
                {"key": "agentops.sensitivity", "value": {"stringValue": ev.sensitivity.value}},
            ]

            if isinstance(ev, ModelCall):
                attributes.extend([
                    {"key": "gen_ai.system", "value": {"stringValue": ev.provider}},
                    {"key": "gen_ai.request.model", "value": {"stringValue": ev.model_name}},
                    {"key": "gen_ai.usage.prompt_tokens", "value": {"intValue": ev.prompt_tokens}},
                    {"key": "gen_ai.usage.completion_tokens", "value": {"intValue": ev.completion_tokens}},
                    {"key": "gen_ai.usage.total_tokens", "value": {"intValue": ev.total_tokens}},
                ])
            elif isinstance(ev, ToolCall):
                attributes.extend([
                    {"key": "agentops.tool.name", "value": {"stringValue": ev.tool_name}},
                    {"key": "agentops.tool.is_mcp", "value": {"boolValue": ev.is_mcp}},
                ])
                if ev.mcp_server:
                    attributes.append({"key": "agentops.mcp.server", "value": {"stringValue": ev.mcp_server}})

            span_data = {
                "traceId": run_id.replace("-", "").ljust(32, "0")[:32],
                "spanId": ev.event_id.replace("-", "").ljust(16, "0")[:16],
                "parentSpanId": ev.parent_id.replace("-", "").ljust(16, "0")[:16] if ev.parent_id else "",
                "name": ev.tool_or_model_name or ev.__class__.__name__,
                "kind": 1,  # SPAN_KIND_INTERNAL
                "startTimeUnixNano": str(ts_nano),
                "endTimeUnixNano": str(end_nano),
                "attributes": attributes,
                "status": {
                    "code": 2 if ev.status.value in ["error", "violated"] else 1
                }
            }
            spans_otlp.append(span_data)

        return {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": agent_name}},
                            {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                            {"key": "telemetry.sdk.name", "value": {"stringValue": "agentops-observatory"}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {
                                "name": "io.agentops.observatory",
                                "version": "1.0.0"
                            },
                            "spans": spans_otlp
                        }
                    ]
                }
            ]
        }
