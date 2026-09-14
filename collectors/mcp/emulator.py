"""
AgentOps Observatory - MCP Protocol Server Mock Emulator (Phase 6+)
Emulates a Model Context Protocol (MCP) server responding to JSON-RPC 2.0 methods:
- tools/list
- tools/call
- resources/list
Allows developers to test MCP clients and capture telemetry safely.
"""

from typing import Any, Dict, List


class MCPServerEmulator:
    """Mock in-memory MCP server protocol emulator."""

    REGISTERED_TOOLS = [
        {
            "name": "calculate_hash",
            "description": "Calculates cryptographic hash of string",
            "inputSchema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        },
        {
            "name": "get_system_time",
            "description": "Returns current UTC timestamp",
            "inputSchema": {"type": "object"}
        }
    ]

    def handle_request(self, jsonrpc_request: Dict[str, Any]) -> Dict[str, Any]:
        req_id = jsonrpc_request.get("id", 1)
        method = jsonrpc_request.get("method")
        params = jsonrpc_request.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.REGISTERED_TOOLS}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})

            if tool_name == "calculate_hash":
                import hashlib
                text = args.get("text", "")
                h = hashlib.sha256(text.encode("utf-8")).hexdigest()
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": h}]}
                }

            elif tool_name == "get_system_time":
                from datetime import datetime, timezone
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": datetime.now(timezone.utc).isoformat()}]}
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32600, "message": f"Unsupported method '{method}'"}
        }
