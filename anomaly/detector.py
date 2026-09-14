"""
AgentOps Observatory - Anomaly Detection Engine (Phase 8)
Deterministic anomaly rules and behavioral sequence analysis for AI agents.
Detects tool sequence deviations, retry bursts, oversized responses, unknown tools, and novel destinations.
"""

from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel
from backend.app.schemas.events import BaseEvent, ModelCall, PolicySeverity, ToolCall


class AnomalyReport(BaseModel):
    anomaly_id: str
    run_id: str
    anomaly_type: str
    severity: PolicySeverity
    description: str
    confidence: float
    affected_event_id: Optional[str] = None
    baseline_value: Optional[str] = None
    observed_value: Optional[str] = None


class AnomalyDetector:
    """
    Stateful anomaly detection engine with deterministic rule evaluations
    and Markov sequence transition baselines.
    """

    KNOWN_TOOL_REGISTRY: Set[str] = {
        "read_file", "view_file", "search_web", "list_dir", "grep_search",
        "calculate", "format_json", "http_get", "database_query_readonly",
        "mcp_fetch_weather", "mcp_read_resource", "n8n_notify_slack", "write_to_file"
    }

    # Prohibited or highly suspicious transitions (Markov penalty)
    SUSPICIOUS_TRANSITIONS = {
        ("write_to_file", "write_to_file"): "Rapid successive write bursts without inspection",
        ("calculate", "destructive_action"): "Abrupt transition from compute to dangerous action",
        ("search_web", "external_network_call"): "Potential exfiltration following web search",
    }

    def __init__(self, baseline_max_chars: int = 25000, max_retry_threshold: int = 3):
        self.baseline_max_chars = baseline_max_chars
        self.max_retry_threshold = max_retry_threshold
        self.seen_destinations: Set[str] = {"api.github.com", "api.openai.com", "api.anthropic.com", "localhost"}
        self.known_tools: Set[str] = set(self.KNOWN_TOOL_REGISTRY)
        self._run_tool_histories: Dict[str, List[str]] = {}

    def analyze_event(
        self, event: BaseEvent, run_events: Optional[List[BaseEvent]] = None
    ) -> List[AnomalyReport]:
        """Inspect event against deterministic anomaly checks."""
        anomalies: List[AnomalyReport] = []
        run_events = run_events or []

        # 1. Unknown Tool Check
        if isinstance(event, ToolCall):
            if event.tool_name not in self.known_tools:
                anomalies.append(AnomalyReport(
                    anomaly_id=f"ANOM-UNKNOWN-TOOL-{event.event_id[:8]}",
                    run_id=event.run_id,
                    anomaly_type="unknown_tool",
                    severity=PolicySeverity.MEDIUM,
                    description=f"Invocation of tool '{event.tool_name}' not present in verified baseline registry.",
                    confidence=0.88,
                    affected_event_id=event.event_id,
                    baseline_value="verified_tools_list",
                    observed_value=event.tool_name
                ))

        # 2. Sudden Retry Spike
        if isinstance(event, ToolCall) and (event.retry_count >= self.max_retry_threshold):
            anomalies.append(AnomalyReport(
                anomaly_id=f"ANOM-RETRY-SPIKE-{event.event_id[:8]}",
                run_id=event.run_id,
                anomaly_type="sudden_retry_spike",
                severity=PolicySeverity.HIGH,
                description=f"Tool '{event.tool_name}' triggered a sudden retry spike ({event.retry_count} retries).",
                confidence=0.95,
                affected_event_id=event.event_id,
                baseline_value=f"< {self.max_retry_threshold}",
                observed_value=str(event.retry_count)
            ))

        # 3. Unusually Large Output Check
        if isinstance(event, ModelCall):
            out_len = len(event.response_redacted or "")
            if out_len > self.baseline_max_chars or event.completion_tokens > 4096:
                anomalies.append(AnomalyReport(
                    anomaly_id=f"ANOM-LARGE-OUTPUT-{event.event_id[:8]}",
                    run_id=event.run_id,
                    anomaly_type="unusually_large_output",
                    severity=PolicySeverity.MEDIUM,
                    description=f"Model completion payload unusually large ({out_len} chars, {event.completion_tokens} tokens).",
                    confidence=0.90,
                    affected_event_id=event.event_id,
                    baseline_value=f"< {self.baseline_max_chars} chars",
                    observed_value=f"{out_len} chars"
                ))

        # 4. Unusual Tool Sequence (Markov Transition Check)
        if isinstance(event, ToolCall):
            history = self._run_tool_histories.setdefault(event.run_id, [])
            if history:
                prev_tool = history[-1]
                transition = (prev_tool, event.tool_name)
                if transition in self.SUSPICIOUS_TRANSITIONS:
                    anomalies.append(AnomalyReport(
                        anomaly_id=f"ANOM-UNUSUAL-SEQ-{event.event_id[:8]}",
                        run_id=event.run_id,
                        anomaly_type="unusual_tool_sequence",
                        severity=PolicySeverity.MEDIUM,
                        description=f"Unusual tool transition from '{prev_tool}' to '{event.tool_name}': {self.SUSPICIOUS_TRANSITIONS[transition]}",
                        confidence=0.85,
                        affected_event_id=event.event_id,
                        baseline_value=f"Allowed transitions from {prev_tool}",
                        observed_value=f"{prev_tool} -> {event.tool_name}"
                    ))
            history.append(event.tool_name)

        # 5. New Destination Check
        if isinstance(event, ToolCall) and "destination" in event.arguments_redacted:
            dest = str(event.arguments_redacted["destination"])
            if dest not in self.seen_destinations:
                anomalies.append(AnomalyReport(
                    anomaly_id=f"ANOM-NEW-DEST-{event.event_id[:8]}",
                    run_id=event.run_id,
                    anomaly_type="new_destination",
                    severity=PolicySeverity.LOW,
                    description=f"Outbound network call to novel, unseen destination '{dest}'.",
                    confidence=0.80,
                    affected_event_id=event.event_id,
                    baseline_value="known_destinations",
                    observed_value=dest
                ))
                self.seen_destinations.add(dest)

        return anomalies
