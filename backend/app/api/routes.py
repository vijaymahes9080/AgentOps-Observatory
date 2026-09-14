"""
AgentOps Observatory - API Routes (Phase 2, 4, 8, 9, 10)
FastAPI routes for event ingestion, run queries, timeline/DAG visualization,
policy violations, redaction audit logs, and export reporting.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.security import AuthContext, get_current_auth, require_roles
from backend.app.models.db import (
    DBAgentRun,
    DBEvent,
    DBIncident,
    DBPolicyViolation,
    DBRedactionAudit,
    async_session_factory,
)
from backend.app.schemas.events import BaseEvent
from backend.app.services.storage import IngestionService
from backend.app.services.trace import TraceService

router = APIRouter()
ingestion_service = IngestionService()


# 1. Health & Version (Public / Operational)
@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected (sqlite/postgres)",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/version", tags=["System"])
async def get_version():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "schema_version": "1.0.0",
        "redaction_policy_version": "2.1.0",
        "guardrail_spec": "AgentOps-10-Rules"
    }


# 2. Event Ingestion (Collector)
@router.post("/events", status_code=status.HTTP_201_CREATED, tags=["Collector"])
async def ingest_event(
    event: Dict[str, Any],
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    auth: AuthContext = Depends(get_current_auth)
):
    try:
        result = await ingestion_service.ingest_event(
            event_dict=event,
            tenant_id=auth.tenant_id,
            idempotency_key=idempotency_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to ingest event: {str(e)}")


@router.post("/events/batch", status_code=status.HTTP_201_CREATED, tags=["Collector"])
async def ingest_events_batch(
    events: List[Dict[str, Any]],
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    auth: AuthContext = Depends(get_current_auth)
):
    try:
        result = await ingestion_service.ingest_batch(
            events=events,
            tenant_id=auth.tenant_id,
            idempotency_key=idempotency_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to ingest batch: {str(e)}")


# 3. Runs Telemetry & Details
@router.get("/runs", tags=["Observatory"])
async def list_runs(
    status_filter: Optional[str] = Query(None, alias="status"),
    agent_name: Optional[str] = None,
    is_partial: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    auth: AuthContext = Depends(get_current_auth)
):
    async with async_session_factory() as session:
        query = select(DBAgentRun).where(DBAgentRun.tenant_id == auth.tenant_id)
        if status_filter:
            query = query.where(DBAgentRun.status == status_filter)
        if agent_name:
            query = query.where(DBAgentRun.agent_name.ilike(f"%{agent_name}%"))
        if is_partial is not None:
            query = query.where(DBAgentRun.is_partial == is_partial)
            
        query = query.order_by(desc(DBAgentRun.created_at)).offset(offset).limit(limit)
        results = await session.execute(query)
        runs = results.scalars().all()
        
        # Count total
        count_q = select(func.count(DBAgentRun.run_id)).where(DBAgentRun.tenant_id == auth.tenant_id)
        total = (await session.execute(count_q)).scalar() or 0
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "runs": [
                {
                    "run_id": r.run_id,
                    "agent_name": r.agent_name,
                    "goal": r.goal,
                    "status": r.status,
                    "is_partial": r.is_partial,
                    "missing_reasons": json.loads(r.missing_telemetry_reasons or "[]"),
                    "total_events": r.total_events,
                    "total_duration_ms": r.total_duration_ms,
                    "total_tokens": r.total_tokens,
                    "total_cost_usd": r.total_cost_usd,
                    "total_energy_kwh": r.total_energy_kwh,
                    "total_carbon_gco2eq": r.total_carbon_gco2eq,
                    "policy_violation_count": r.policy_violation_count,
                    "redaction_count": r.redaction_count,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in runs
            ]
        }


@router.get("/runs/{run_id}", tags=["Observatory"])
async def get_run_detail(run_id: str, auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        run = await session.get(DBAgentRun, run_id)
        if not run or run.tenant_id != auth.tenant_id:
            raise HTTPException(status_code=404, detail="Run not found or unauthorized")

        # Fetch events for this run
        events_q = select(DBEvent).where(DBEvent.run_id == run_id).order_by(DBEvent.timestamp)
        ev_res = await session.execute(events_q)
        events = ev_res.scalars().all()

        return {
            "run_id": run.run_id,
            "agent_name": run.agent_name,
            "goal": run.goal,
            "status": run.status,
            "is_partial": run.is_partial,
            "missing_telemetry_reasons": json.loads(run.missing_telemetry_reasons or "[]"),
            "total_events": run.total_events,
            "total_duration_ms": run.total_duration_ms,
            "total_tokens": run.total_tokens,
            "total_cost_usd": run.total_cost_usd,
            "total_energy_kwh": run.total_energy_kwh,
            "total_carbon_gco2eq": run.total_carbon_gco2eq,
            "policy_violation_count": run.policy_violation_count,
            "redaction_count": run.redaction_count,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "events": [
                {
                    "event_id": e.event_id,
                    "parent_id": e.parent_id,
                    "event_type": e.event_type,
                    "source": e.source,
                    "actor": e.actor,
                    "name": e.tool_or_model_name,
                    "status": e.status,
                    "duration_ms": e.duration_ms,
                    "payload": json.loads(e.payload_json),
                    "current_hash": e.current_hash,
                    "prev_hash": e.prev_hash,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None
                }
                for e in events
            ]
        }


@router.get("/runs/{run_id}/timeline", tags=["Trace & DAG"])
async def get_run_timeline(run_id: str, auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        events_q = select(DBEvent).where(DBEvent.run_id == run_id).order_by(DBEvent.timestamp)
        ev_res = await session.execute(events_q)
        events = ev_res.scalars().all()
        
        parsed_events = []
        for e in events:
            payload = json.loads(e.payload_json)
            parsed_events.append(ingestion_service._parse_event_object(payload))

        trace_graph = TraceService.build_trace(run_id=run_id, events=parsed_events)
        return trace_graph.model_dump()


# 4. Policy Violations & Incidents
@router.get("/policies/violations", tags=["Governance"])
async def list_policy_violations(
    severity: Optional[str] = None,
    rule_id: Optional[str] = None,
    limit: int = 50,
    auth: AuthContext = Depends(get_current_auth)
):
    async with async_session_factory() as session:
        query = select(DBPolicyViolation).order_by(desc(DBPolicyViolation.timestamp)).limit(limit)
        if severity:
            query = query.where(DBPolicyViolation.severity == severity.upper())
        if rule_id:
            query = query.where(DBPolicyViolation.rule_id == rule_id)
        violations = (await session.execute(query)).scalars().all()
        return [
            {
                "violation_id": v.violation_id,
                "run_id": v.run_id,
                "event_id": v.event_id,
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "severity": v.severity,
                "evidence": v.evidence,
                "remediation": v.remediation,
                "confidence": v.confidence,
                "timestamp": v.timestamp.isoformat() if v.timestamp else None
            }
            for v in violations
        ]


@router.get("/incidents", tags=["Governance"])
async def list_incidents(resolved: Optional[bool] = None, limit: int = 50, auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        query = select(DBIncident).order_by(desc(DBIncident.timestamp)).limit(limit)
        if resolved is not None:
            query = query.where(DBIncident.resolved == resolved)
        incidents = (await session.execute(query)).scalars().all()
        return [
            {
                "incident_id": inc.incident_id,
                "run_id": inc.run_id,
                "title": inc.title,
                "summary": inc.summary,
                "severity": inc.severity,
                "resolved": inc.resolved,
                "resolution_notes": inc.resolution_notes,
                "timestamp": inc.timestamp.isoformat() if inc.timestamp else None
            }
            for inc in incidents
        ]


# 5. Redaction Audit Trail
@router.get("/redactions", tags=["Audit & Privacy"])
async def list_redactions(limit: int = 50, auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        query = select(DBRedactionAudit).order_by(desc(DBRedactionAudit.timestamp)).limit(limit)
        redactions = (await session.execute(query)).scalars().all()
        return [
            {
                "audit_id": r.audit_id,
                "run_id": r.run_id,
                "event_id": r.event_id,
                "redaction_type": r.redaction_type,
                "masked_placeholder": r.masked_placeholder,
                "location": r.location,
                "policy_version": r.policy_version,
                "character_count": r.character_count,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            }
            for r in redactions
        ]


# 6. Overview & Metrics
@router.get("/metrics/overview", tags=["Analytics"])
async def get_overview_metrics(auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        # Aggregations
        runs_count = (await session.execute(select(func.count(DBAgentRun.run_id)).where(DBAgentRun.tenant_id == auth.tenant_id))).scalar() or 0
        violations_count = (await session.execute(select(func.count(DBPolicyViolation.violation_id)))).scalar() or 0
        redactions_count = (await session.execute(select(func.count(DBRedactionAudit.audit_id)))).scalar() or 0
        incidents_count = (await session.execute(select(func.count(DBIncident.incident_id)).where(DBIncident.resolved == False))).scalar() or 0
        
        totals = await session.execute(
            select(
                func.sum(DBAgentRun.total_tokens),
                func.sum(DBAgentRun.total_cost_usd),
                func.sum(DBAgentRun.total_energy_kwh),
                func.sum(DBAgentRun.total_carbon_gco2eq)
            ).where(DBAgentRun.tenant_id == auth.tenant_id)
        )
        total_tokens, total_cost, total_energy, total_carbon = totals.one()

        return {
            "total_runs": runs_count,
            "open_incidents": incidents_count,
            "total_policy_violations": violations_count,
            "total_redactions": redactions_count,
            "total_tokens": total_tokens or 0,
            "total_cost_usd": round(total_cost or 0.0, 4),
            "total_energy_kwh": round(total_energy or 0.0, 6),
            "total_carbon_gco2eq": round(total_carbon or 0.0, 4),
            "compliance_rate_percent": round(max(0.0, 100.0 - ((violations_count / max(runs_count, 1)) * 100.0)), 2)
        }


# 7. Tool Inventory
@router.get("/tools/inventory", tags=["Inventory"])
async def get_tool_inventory(auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        query = (
            select(
                DBEvent.tool_or_model_name,
                DBEvent.source,
                func.count(DBEvent.event_id).label("call_count"),
                func.avg(DBEvent.duration_ms).label("avg_duration_ms")
            )
            .where(DBEvent.tool_or_model_name.is_not(None))
            .group_by(DBEvent.tool_or_model_name, DBEvent.source)
            .order_by(desc("call_count"))
        )
        res = await session.execute(query)
        tools = res.all()
        return [
            {
                "name": t[0],
                "source": t[1],
                "call_count": t[2],
                "avg_duration_ms": round(float(t[3] or 0.0), 2)
            }
            for t in tools
        ]


# 8. Export Telemetry (Sanitized JSON & Audit)
@router.get("/export/runs/{run_id}", tags=["Exports"])
async def export_run_telemetry(run_id: str, auth: AuthContext = Depends(get_current_auth)):
    async with async_session_factory() as session:
        run = await session.get(DBAgentRun, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
            
        events = (await session.execute(
            select(DBEvent).where(DBEvent.run_id == run_id).order_by(DBEvent.timestamp)
        )).scalars().all()
        
        export_payload = {
            "platform": "AgentOps Observatory",
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "exported_by": auth.user_id,
            "run": {
                "run_id": run.run_id,
                "agent_name": run.agent_name,
                "status": run.status,
                "is_partial": run.is_partial,
                "total_events": run.total_events,
                "total_tokens": run.total_tokens,
                "total_cost_usd": run.total_cost_usd,
                "total_energy_kwh": run.total_energy_kwh,
                "total_carbon_gco2eq": run.total_carbon_gco2eq
            },
            "events": [
                {
                    "event_id": e.event_id,
                    "parent_id": e.parent_id,
                    "event_type": e.event_type,
                    "name": e.tool_or_model_name,
                    "status": e.status,
                    "duration_ms": e.duration_ms,
                    "prev_hash": e.prev_hash,
                    "current_hash": e.current_hash,
                    "payload_redacted": json.loads(e.payload_json)
                }
                for e in events
            ]
        }
        return export_payload
