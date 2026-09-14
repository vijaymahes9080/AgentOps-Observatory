"""
AgentOps Observatory - Time-Travel Deterministic Run Replayer (Phase 5+)
Provides step-by-step deterministic playback of past multi-agent execution traces.
Allows security investigators and developers to step forwards and backwards through span states.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ReplayStep(BaseModel):
    step_number: int
    event_id: str
    event_type: str
    name: str
    status: str
    elapsed_ms: float
    state_delta: Dict[str, Any]


class RunReplayer:
    """Reconstructs ordered sequential state transitions for interactive playback."""

    @classmethod
    def generate_replay_steps(cls, events: List[Dict[str, Any]]) -> List[ReplayStep]:
        # Sort by timestamp
        sorted_evs = sorted(events, key=lambda e: e.get("timestamp", ""))
        steps = []
        cumulative_ms = 0.0

        for idx, ev in enumerate(sorted_evs):
            dur = float(ev.get("duration_ms", 0.0))
            cumulative_ms += dur
            steps.append(ReplayStep(
                step_number=idx + 1,
                event_id=ev.get("event_id", ""),
                event_type=ev.get("event_type", "Span"),
                name=ev.get("tool_or_model_name") or ev.get("name") or "step",
                status=ev.get("status", "success"),
                elapsed_ms=round(cumulative_ms, 2),
                state_delta={
                    "tokens": ev.get("payload", {}).get("total_tokens", 0),
                    "error": ev.get("payload", {}).get("error_details"),
                    "output": ev.get("payload", {}).get("result_redacted")
                }
            ))

        return steps
