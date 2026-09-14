"""
AgentOps Observatory - Framework Integrations (LangChain & AutoGen) (Phase 6+)
Drop-in callback handlers and hooks for LangChain, LlamaIndex, and AutoGen agent swarms.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4
from collectors.agent.sdk import ObservatoryClient


class AgentOpsLangChainCallback:
    """LangChain callback adapter streaming tool and LLM telemetry to AgentOps."""

    def __init__(self, run_id: Optional[str] = None, client: Optional[ObservatoryClient] = None):
        self.run_id = run_id or f"langchain-run-{uuid4().hex[:8]}"
        self.client = client or ObservatoryClient()

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        model = serialized.get("name", "llm-unknown")
        event = {
            "event_id": str(uuid4()),
            "run_id": self.run_id,
            "source": "model",
            "actor": "langchain-agent",
            "tool_or_model_name": model,
            "model_name": model,
            "prompt_redacted": " ".join(prompts),
            "status": "in_progress"
        }
        self.client.record_event(event)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        tool_name = serialized.get("name", "unknown_tool")
        event = {
            "event_id": str(uuid4()),
            "run_id": self.run_id,
            "source": "agent",
            "actor": "langchain-agent",
            "tool_or_model_name": tool_name,
            "tool_name": tool_name,
            "arguments_redacted": {"input": input_str},
            "status": "in_progress"
        }
        self.client.record_event(event)


class AgentOpsAutoGenHook:
    """AutoGen agent conversation monitor hook."""

    def __init__(self, run_id: Optional[str] = None, client: Optional[ObservatoryClient] = None):
        self.run_id = run_id or f"autogen-run-{uuid4().hex[:8]}"
        self.client = client or ObservatoryClient()

    def on_message_sent(self, sender_name: str, recipient_name: str, message: Dict[str, Any]):
        event = {
            "event_id": str(uuid4()),
            "run_id": self.run_id,
            "source": "agent",
            "actor": sender_name,
            "tool_or_model_name": f"{sender_name}->{recipient_name}",
            "status": "success",
            "arguments_redacted": message
        }
        self.client.record_event(event)
