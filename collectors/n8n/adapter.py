"""
AgentOps Observatory - n8n Workflow Adapter (Phase 6)
Transforms n8n node execution events, trigger webhooks, and execution states
into standardized AgentOps WorkflowEvent schemas.
"""

from typing import Any, Dict, Optional
from uuid import uuid4
from backend.app.core.security import verify_webhook_signature
from backend.app.schemas.events import EventStatus, SensitivityLevel, SourceType, WorkflowEvent


class N8nAdapter:
    """
    Adapter for n8n automation workflows, verifying webhook signatures and mapping node telemetry.
    """

    def __init__(self, signing_secret: Optional[str] = None):
        self.signing_secret = signing_secret

    def transform_node_event(
        self,
        run_id: str,
        workflow_id: str,
        workflow_name: str,
        execution_id: str,
        node_name: str,
        node_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
        parent_id: Optional[str] = None,
        raw_payload_bytes: Optional[bytes] = None,
        signature: Optional[str] = None
    ) -> WorkflowEvent:
        """
        Transform an n8n node execution payload into a WorkflowEvent.
        """
        # Webhook signature verification
        is_verified = True
        if self.signing_secret and raw_payload_bytes and signature:
            is_verified = verify_webhook_signature(
                payload_bytes=raw_payload_bytes,
                received_signature=signature,
                secret=self.signing_secret
            )
        elif self.signing_secret and not signature:
            is_verified = False

        status = EventStatus.ERROR if error else EventStatus.SUCCESS

        return WorkflowEvent(
            event_id=str(uuid4()),
            run_id=run_id,
            parent_id=parent_id,
            source=SourceType.N8N,
            actor=f"n8n:{workflow_name}",
            tool_or_model_name=f"{node_name} ({node_type})",
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            execution_id=execution_id,
            node_name=node_name,
            node_type=node_type,
            input_redacted=input_data,
            output_redacted=output_data,
            webhook_verified=is_verified,
            status=status,
            duration_ms=duration_ms,
            sensitivity=SensitivityLevel.INTERNAL,
            provenance={"n8n_version": "1.45.0", "execution_id": execution_id}
        )
