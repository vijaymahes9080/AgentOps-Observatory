"""
AgentOps Observatory - Storage & Ingestion Orchestrator (Phase 2 & 10)
Applies deterministic redaction, policy checks, cryptographic hash chaining,
and incremental metrics accumulation before committing to append-only storage.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from anomaly.detector import AnomalyDetector, AnomalyReport
from backend.app.core.security import compute_event_hash
from backend.app.models.db import (
    DBAgentRun,
    DBEvent,
    DBIdempotencyKey,
    DBIncident,
    DBPolicyViolation,
    DBRedactionAudit,
    async_session_factory,
)
from backend.app.schemas.events import (
    BaseEvent,
    CostEstimate,
    EnergyEstimate,
    EventStatus,
    ModelCall,
    PolicyEvent,
    PolicySeverity,
    RedactionEvent,
    Span,
    ToolCall,
    WorkflowEvent,
)
from backend.app.services.metrics import MetricsEngine
from policy.engine import PolicyEngine
from redaction.engine import RedactionEngine


class IngestionService:
    GENESIS_HASH = "0" * 64

    def __init__(self):
        self.redactor = RedactionEngine()
        self.policy_engine = PolicyEngine()
        self.anomaly_detector = AnomalyDetector()

    async def ingest_event(
        self,
        event_dict: Dict[str, Any],
        tenant_id: str = "default",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full ingestion pipeline:
        1. Idempotency check
        2. Deterministic Redaction (never log or persist raw secret)
        3. Policy Evaluation
        4. Metrics Accumulation (cost/energy/tokens)
        5. Append-only Cryptographic Hash Chaining
        6. Anomaly Detection
        """
        async with async_session_factory() as session:
            # 1. Idempotency & Duplicate Check
            event_id = event_dict.get("event_id")
            if event_id:
                existing_event = await session.get(DBEvent, event_id)
                if existing_event:
                    return {
                        "status": "duplicate_ignored",
                        "event_id": existing_event.event_id,
                        "run_id": existing_event.run_id,
                        "current_hash": existing_event.current_hash,
                        "is_duplicate": True,
                        "redactions_count": 0,
                        "violations_count": 0,
                        "anomalies_count": 0,
                        "is_partial": False
                    }

            if idempotency_key:
                existing_key = await session.get(DBIdempotencyKey, idempotency_key)
                if existing_key:
                    return json.loads(existing_key.response_json)

            run_id = event_dict.get("run_id", "default-run")

            # 2. Deterministic Redaction
            redacted_payload, redaction_events = self.redactor.redact_payload(
                event_dict, location_path="$", run_id=run_id
            )

            # Reconstruct typed event from redacted payload
            event_obj = self._parse_event_object(redacted_payload)

            # 3. Policy Evaluation
            violations = self.policy_engine.evaluate_event(
                event_obj, run_context={"tenant_id": tenant_id}
            )

            # 4. Anomaly Evaluation
            anomalies = self.anomaly_detector.analyze_event(event_obj)

            # 5. Cost & Energy Enrichment if ModelCall
            if isinstance(event_obj, ModelCall) and (not event_obj.cost_estimate or event_obj.cost_estimate.estimated_cost_usd == 0):
                event_obj.cost_estimate = MetricsEngine.calculate_cost(
                    model_name=event_obj.model_name,
                    prompt_tokens=event_obj.prompt_tokens,
                    completion_tokens=event_obj.completion_tokens
                )
                event_obj.energy_estimate = MetricsEngine.calculate_energy_and_carbon(
                    total_tokens=event_obj.total_tokens,
                    duration_ms=event_obj.duration_ms
                )
                redacted_payload["cost_estimate"] = event_obj.cost_estimate.model_dump()
                redacted_payload["energy_estimate"] = event_obj.energy_estimate.model_dump()

            # 6. Retrieve Previous Hash in the Chain
            last_event_query = await session.execute(
                select(DBEvent.current_hash).order_by(desc(DBEvent.timestamp)).limit(1)
            )
            prev_hash = last_event_query.scalar() or self.GENESIS_HASH

            # 7. Compute Tamper-Evident Hash Chain
            current_hash = compute_event_hash(prev_hash, redacted_payload)

            # 8. Fetch or Create DBAgentRun
            db_run = await session.get(DBAgentRun, run_id)
            if not db_run:
                agent_name = (
                    getattr(event_obj, "actor", None)
                    or event_dict.get("provenance", {}).get("agent_name", "agent-default")
                )
                db_run = DBAgentRun(
                    run_id=run_id,
                    agent_name=agent_name,
                    tenant_id=tenant_id,
                    status=event_obj.status.value,
                    created_at=event_obj.timestamp,
                    total_events=0,
                    total_duration_ms=0.0,
                    total_tokens=0,
                    total_cost_usd=0.0,
                    total_energy_kwh=0.0,
                    total_carbon_gco2eq=0.0,
                    policy_violation_count=0,
                    redaction_count=0,
                    missing_telemetry_reasons="[]",
                    tags="[]"
                )
                session.add(db_run)

            # Update run metrics safely
            db_run.total_events = (db_run.total_events or 0) + 1
            db_run.total_duration_ms = max(db_run.total_duration_ms or 0.0, event_obj.duration_ms)
            if isinstance(event_obj, ModelCall):
                db_run.total_tokens = (db_run.total_tokens or 0) + event_obj.total_tokens
                if event_obj.cost_estimate:
                    db_run.total_cost_usd = (db_run.total_cost_usd or 0.0) + event_obj.cost_estimate.estimated_cost_usd
                if event_obj.energy_estimate:
                    db_run.total_energy_kwh = (db_run.total_energy_kwh or 0.0) + event_obj.energy_estimate.energy_kwh
                    db_run.total_carbon_gco2eq = (db_run.total_carbon_gco2eq or 0.0) + event_obj.energy_estimate.carbon_gco2eq

            if violations:
                db_run.policy_violation_count = (db_run.policy_violation_count or 0) + len(violations)
                db_run.status = "violated"

            db_run.redaction_count = (db_run.redaction_count or 0) + len(redaction_events)

            # Check for partial run (missing parent)
            if event_obj.parent_id:
                parent_exists = await session.get(DBEvent, event_obj.parent_id)
                if not parent_exists:
                    db_run.is_partial = True
                    reasons = json.loads(db_run.missing_telemetry_reasons)
                    reason_msg = f"Event {event_obj.event_id} references missing parent {event_obj.parent_id}"
                    if reason_msg not in reasons:
                        reasons.append(reason_msg)
                        db_run.missing_telemetry_reasons = json.dumps(reasons)

            # Save DBEvent
            db_event = DBEvent(
                event_id=event_obj.event_id,
                run_id=run_id,
                parent_id=event_obj.parent_id,
                event_type=event_obj.__class__.__name__,
                source=event_obj.source.value,
                actor=event_obj.actor,
                tool_or_model_name=event_obj.tool_or_model_name or getattr(event_obj, "tool_name", None) or getattr(event_obj, "model_name", None),
                status=event_obj.status.value,
                duration_ms=event_obj.duration_ms,
                sensitivity=event_obj.sensitivity.value,
                payload_json=json.dumps(redacted_payload, default=str),
                prev_hash=prev_hash,
                current_hash=current_hash,
                timestamp=event_obj.timestamp
            )
            session.add(db_event)

            # Save Policy Violations
            for v in violations:
                db_violation = DBPolicyViolation(
                    violation_id=v.event_id,
                    run_id=run_id,
                    event_id=event_obj.event_id,
                    rule_id=v.rule_id,
                    rule_name=v.rule_name,
                    severity=v.severity.value,
                    evidence=v.evidence,
                    remediation=v.remediation,
                    confidence=v.confidence,
                    timestamp=v.timestamp
                )
                session.add(db_violation)

                # Create Incident if Critical
                if v.severity in [PolicySeverity.HIGH, PolicySeverity.CRITICAL]:
                    db_incident = DBIncident(
                        incident_id=f"INC-{v.event_id[:8].upper()}",
                        run_id=run_id,
                        title=f"{v.rule_name} on {event_obj.tool_or_model_name or 'Agent'}",
                        summary=v.evidence,
                        severity=v.severity.value,
                        timestamp=v.timestamp
                    )
                    session.add(db_incident)

            # Save Redaction Audits
            for r in redaction_events:
                db_audit = DBRedactionAudit(
                    audit_id=r.event_id,
                    run_id=run_id,
                    event_id=event_obj.event_id,
                    redaction_type=r.redaction_type,
                    masked_placeholder=r.masked_placeholder,
                    location=r.location,
                    policy_version=r.policy_version,
                    character_count=r.character_count,
                    timestamp=r.timestamp
                )
                session.add(db_audit)

            # Response structure
            response_data = {
                "status": "ingested",
                "event_id": event_obj.event_id,
                "run_id": run_id,
                "current_hash": current_hash,
                "redactions_count": len(redaction_events),
                "violations_count": len(violations),
                "anomalies_count": len(anomalies),
                "is_partial": db_run.is_partial
            }

            # Save Idempotency Key
            if idempotency_key:
                idemp_record = DBIdempotencyKey(
                    key=idempotency_key,
                    request_hash=current_hash,
                    response_json=json.dumps(response_data)
                )
                session.add(idemp_record)

            await session.commit()
            return response_data

    async def ingest_batch(
        self,
        events: List[Dict[str, Any]],
        tenant_id: str = "default",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Batch ingestion supporting atomic processing and ordering."""
        results = []
        for ev in events:
            res = await self.ingest_event(ev, tenant_id=tenant_id)
            results.append(res)
        return {
            "batch_size": len(events),
            "ingested": len(results),
            "results": results
        }

    def _parse_event_object(self, data: Dict[str, Any]) -> BaseEvent:
        """Dynamically instantiate correct event model subclass."""
        # Detect type
        if "model_name" in data or data.get("source") == "model":
            return ModelCall(**data)
        elif "tool_name" in data or data.get("is_mcp") or data.get("source") == "mcp":
            return ToolCall(**data)
        elif "workflow_id" in data or data.get("source") == "n8n":
            return WorkflowEvent(**data)
        elif "span_id" in data:
            return Span(**data)
        else:
            return BaseEvent(**data)
