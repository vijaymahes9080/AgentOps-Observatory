"""
AgentOps Observatory - Python Agent SDK & Observer Decorators (Phase 6)
Lightweight instrumentation client for AI agents, LangChain, CrewAI, AutoGen, or vanilla Python agents.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional
from uuid import uuid4
import httpx

from backend.app.schemas.events import EventStatus, ModelCall, SensitivityLevel, SourceType, Span, ToolCall


class ObservatoryClient:
    """AgentOps client for streaming trace telemetry to the observatory server."""

    def __init__(self, endpoint: str = "http://localhost:8000/api/v1", api_key: Optional[str] = None):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key or "agy-agent-client-key"

    def record_event(self, event_dict: Dict[str, Any]) -> bool:
        """Sends an event payload synchronously or asynchronously."""
        try:
            headers = {"X-AgentOps-API-Key": self.api_key, "Content-Type": "application/json"}
            with httpx.Client(timeout=2.0) as client:
                res = client.post(f"{self.endpoint}/events", json=event_dict, headers=headers)
                return res.status_code in [200, 201]
        except Exception:
            return False


class AgentObserver:
    """Decorator and context helper for monitoring tool executions and model calls."""

    def __init__(self, run_id: Optional[str] = None, client: Optional[ObservatoryClient] = None):
        self.run_id = run_id or f"run-{uuid4().hex[:8]}"
        self.client = client or ObservatoryClient()

    def observe_tool(self, tool_name: Optional[str] = None):
        """Decorator to monitor tool executions, latency, arguments, and outcomes."""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                effective_name = tool_name or func.__name__
                start = time.time()
                error_msg = None
                result = None
                status = EventStatus.SUCCESS
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as ex:
                    error_msg = str(ex)
                    status = EventStatus.ERROR
                    raise
                finally:
                    duration_ms = (time.time() - start) * 1000.0
                    event = ToolCall(
                        event_id=str(uuid4()),
                        run_id=self.run_id,
                        source=SourceType.AGENT,
                        actor="agent-sdk",
                        tool_or_model_name=effective_name,
                        tool_name=effective_name,
                        arguments_redacted={"args": str(args), "kwargs": kwargs},
                        result_redacted=str(result) if result is not None else None,
                        status=status,
                        duration_ms=round(duration_ms, 2),
                        error_details=error_msg,
                        sensitivity=SensitivityLevel.INTERNAL
                    )
                    self.client.record_event(event.model_dump())
            return wrapper
        return decorator
