"""
AgentOps Observatory - Model Context Protocol (MCP) Adapter (Phase 6)
Observes MCP messages, tool invocations, and resource readings.
Translates MCP JSON-RPC payloads into standard AgentOps ToolCall and Span events.
Does NOT execute mutations; purely observes and standardizes telemetry.
"""

from typing import Any, Dict, Optional
from uuid import uuid4
from backend.app.schemas.events import EventStatus, SensitivityLevel, SourceType, ToolCall


class MCPAdapter:
    """
    Adapter for observing Model Context Protocol tool requests, notifications, and responses.
    """

    def __init__(self, server_name: str = "mcp-server-default"):
        self.server_name = server_name

    def transform_tool_call(
        self,
        run_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[Any] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
        parent_id: Optional[str] = None
    ) -> ToolCall:
        """
        Transforms an MCP tools/call JSON-RPC operation into an AgentOps ToolCall event.
        """
        status = EventStatus.ERROR if error else EventStatus.SUCCESS
        
        return ToolCall(
            event_id=str(uuid4()),
            run_id=run_id,
            parent_id=parent_id,
            source=SourceType.MCP,
            actor=f"mcp:{self.server_name}",
            tool_or_model_name=tool_name,
            tool_name=tool_name,
            mcp_server=self.server_name,
            arguments_redacted=arguments,
            result_redacted=str(result) if result is not None else None,
            is_mcp=True,
            status=status,
            duration_ms=duration_ms,
            error_details=error,
            sensitivity=SensitivityLevel.INTERNAL,
            provenance={"mcp_protocol_version": "2024-11-05", "server": self.server_name}
        )

    def parse_jsonrpc_request(
        self,
        run_id: str,
        jsonrpc_payload: Dict[str, Any],
        parent_id: Optional[str] = None
    ) -> Optional[ToolCall]:
        """Parse raw MCP JSON-RPC 2.0 request frame."""
        method = jsonrpc_payload.get("method")
        params = jsonrpc_payload.get("params", {})
        
        if method == "tools/call":
            tool_name = params.get("name", "unknown_tool")
            args = params.get("arguments", {})
            return self.transform_tool_call(
                run_id=run_id,
                tool_name=tool_name,
                arguments=args,
                parent_id=parent_id
            )
        return None
