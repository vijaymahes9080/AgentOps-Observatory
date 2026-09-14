"""
AgentOps Observatory - Database ORM Models (Phase 2 & 10)
Supports SQLite (local-first) and PostgreSQL.
Append-only tamper-evident structure with cryptographic hash chains.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from backend.app.core.config import settings

Base = declarative_base()


class DBAgentRun(Base):
    __tablename__ = "agent_runs"

    run_id = Column(String(64), primary_key=True, index=True)
    agent_name = Column(String(128), default="agent-default", index=True)
    goal = Column(Text, nullable=True)
    root_span_id = Column(String(64), nullable=True)
    status = Column(String(32), default="in_progress", index=True)
    is_partial = Column(Boolean, default=False, index=True)
    missing_telemetry_reasons = Column(Text, default="[]")
    
    total_events = Column(Integer, default=0)
    total_duration_ms = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    total_energy_kwh = Column(Float, default=0.0)
    total_carbon_gco2eq = Column(Float, default=0.0)
    
    policy_violation_count = Column(Integer, default=0)
    redaction_count = Column(Integer, default=0)
    tags = Column(Text, default="[]")
    tenant_id = Column(String(64), default="default", index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    events = relationship("DBEvent", back_populates="run", cascade="all, delete-orphan")


class DBEvent(Base):
    __tablename__ = "events"

    event_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("agent_runs.run_id"), nullable=False, index=True)
    parent_id = Column(String(64), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # Span, ModelCall, ToolCall, WorkflowEvent, etc.
    source = Column(String(32), default="agent", index=True)
    actor = Column(String(128), default="system")
    tool_or_model_name = Column(String(128), nullable=True, index=True)
    status = Column(String(32), default="success", index=True)
    duration_ms = Column(Float, default=0.0)
    sensitivity = Column(String(32), default="internal")
    
    # Strictly redacted payload JSON. Raw secrets are NEVER persisted.
    payload_json = Column(Text, nullable=False)
    
    # Tamper-evident cryptographic hash chain
    prev_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
    
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    run = relationship("DBAgentRun", back_populates="events")


class DBPolicyViolation(Base):
    __tablename__ = "policy_violations"

    violation_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), index=True)
    event_id = Column(String(64), nullable=True, index=True)
    rule_id = Column(String(64), nullable=False, index=True)
    rule_name = Column(String(128), nullable=False)
    severity = Column(String(32), nullable=False, index=True)
    evidence = Column(Text, nullable=False)
    remediation = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DBRedactionAudit(Base):
    __tablename__ = "redaction_audits"

    audit_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), index=True)
    event_id = Column(String(64), nullable=True, index=True)
    redaction_type = Column(String(64), nullable=False, index=True)
    masked_placeholder = Column(String(128), nullable=False)
    location = Column(String(256), nullable=False)
    policy_version = Column(String(32), default="1.0.0")
    character_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DBIncident(Base):
    __tablename__ = "incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), index=True)
    title = Column(String(256), nullable=False)
    summary = Column(Text, nullable=False)
    severity = Column(String(32), default="HIGH", index=True)
    resolved = Column(Boolean, default=False, index=True)
    resolution_notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DBIdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key = Column(String(128), primary_key=True, index=True)
    request_hash = Column(String(64), nullable=False)
    response_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Async engine & session factory
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create tables if not existing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
