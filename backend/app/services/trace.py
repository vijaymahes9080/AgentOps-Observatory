"""
AgentOps Observatory - Trace Graph and Timeline Service (Phase 5)
Constructs Directed Acyclic Graph (DAG) traces, parent-child hierarchies,
cascading failure propagation, retry groupings, and missing-telemetry detection.
"""

from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
from backend.app.schemas.events import BaseEvent, EventStatus, ModelCall, Span, ToolCall


class TraceNode(BaseModel):
    id: str
    event_type: str
    name: str
    parent_id: Optional[str] = None
    status: EventStatus
    duration_ms: float
    start_time: str
    offset_ms: float
    children: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    has_error: bool = False
    is_partial_orphan: bool = False


class TraceEdge(BaseModel):
    source: str
    target: str
    relation: str  # "parent_child", "model_to_tool", "retry"


class TraceGraph(BaseModel):
    run_id: str
    root_nodes: List[str] = Field(default_factory=list)
    nodes: Dict[str, TraceNode] = Field(default_factory=dict)
    edges: List[TraceEdge] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    total_duration_ms: float = 0.0
    is_partial: bool = False
    missing_telemetry_warnings: List[str] = Field(default_factory=list)
    failed_node_ids: List[str] = Field(default_factory=list)


class TraceService:
    """Service to assemble trace graphs, timelines, and anomaly flags."""

    @classmethod
    def build_trace(cls, run_id: str, events: List[BaseEvent]) -> TraceGraph:
        if not events:
            return TraceGraph(
                run_id=run_id,
                is_partial=True,
                missing_telemetry_warnings=["No events recorded for this run ID."]
            )

        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        first_time = sorted_events[0].timestamp

        nodes: Dict[str, TraceNode] = {}
        edges: List[TraceEdge] = []
        root_nodes: List[str] = []
        warnings: List[str] = []
        failed_nodes: List[str] = []
        known_ids: Set[str] = {e.event_id for e in sorted_events}

        # 1. Create nodes
        for ev in sorted_events:
            offset_ms = max(0.0, (ev.timestamp - first_time).total_seconds() * 1000.0)
            node_name = ev.tool_or_model_name or getattr(ev, "name", None) or ev.source.value

            is_error = ev.status in [EventStatus.ERROR, EventStatus.VIOLATED]
            if is_error:
                failed_nodes.append(ev.event_id)

            is_orphan = False
            if ev.parent_id and ev.parent_id not in known_ids:
                is_orphan = True
                warnings.append(
                    f"Orphan event detected: Event '{ev.event_id}' ({node_name}) has parent_id '{ev.parent_id}' which is missing from telemetry."
                )

            node = TraceNode(
                id=ev.event_id,
                event_type=ev.__class__.__name__,
                name=node_name,
                parent_id=ev.parent_id,
                status=ev.status,
                duration_ms=ev.duration_ms,
                start_time=ev.timestamp.isoformat(),
                offset_ms=offset_ms,
                attributes={"source": ev.source.value, "actor": ev.actor, "sensitivity": ev.sensitivity.value},
                has_error=is_error,
                is_partial_orphan=is_orphan
            )
            nodes[ev.event_id] = node

        # 2. Build parent-child relationships and edges
        for ev in sorted_events:
            if ev.parent_id and ev.parent_id in nodes:
                nodes[ev.parent_id].children.append(ev.event_id)
                edges.append(TraceEdge(
                    source=ev.parent_id,
                    target=ev.event_id,
                    relation="parent_child"
                ))
            else:
                root_nodes.append(ev.event_id)

        # 3. Model-to-tool and Retry edges
        for i in range(len(sorted_events) - 1):
            curr = sorted_events[i]
            nxt = sorted_events[i + 1]
            # Model calling a tool immediately after
            if isinstance(curr, ModelCall) and isinstance(nxt, ToolCall) and nxt.parent_id == curr.event_id:
                edges.append(TraceEdge(
                    source=curr.event_id,
                    target=nxt.event_id,
                    relation="model_to_tool"
                ))
            # Retry connection
            if isinstance(nxt, ToolCall) and nxt.retry_count > 0 and isinstance(curr, ToolCall) and curr.tool_name == nxt.tool_name:
                edges.append(TraceEdge(
                    source=curr.event_id,
                    target=nxt.event_id,
                    relation="retry"
                ))

        # 4. Check for incomplete / partial run conditions
        is_partial = False
        if warnings:
            is_partial = True

        # Check if root span is unfinished
        has_root_span = any(isinstance(e, Span) and getattr(e, "is_root", False) for e in events)
        if not has_root_span and len(events) > 5:
            warnings.append("Trace root span missing: Run telemetry does not contain an explicit root span.")
            is_partial = True

        # Calculate total run duration
        last_time = sorted_events[-1].timestamp
        total_duration = max(
            (last_time - first_time).total_seconds() * 1000.0,
            max((n.duration_ms for n in nodes.values()), default=0.0)
        )

        timeline_items = [
            {
                "event_id": n.id,
                "name": n.name,
                "type": n.event_type,
                "status": n.status.value,
                "offset_ms": n.offset_ms,
                "duration_ms": n.duration_ms,
                "has_error": n.has_error,
                "is_orphan": n.is_partial_orphan,
                "parent_id": n.parent_id
            }
            for n in nodes.values()
        ]

        return TraceGraph(
            run_id=run_id,
            root_nodes=root_nodes,
            nodes=nodes,
            edges=edges,
            timeline=timeline_items,
            total_duration_ms=round(total_duration, 2),
            is_partial=is_partial,
            missing_telemetry_warnings=warnings,
            failed_node_ids=failed_nodes
        )
