"""
AgentOps Observatory - Multi-Channel Alerting Engine
Dispatches real-time security alerts and incident notices to Slack, Discord, and PagerDuty webhooks.
"""

from typing import Any, Dict, Optional
import httpx
from backend.app.schemas.events import PolicyEvent, PolicySeverity


class AlertDispatcher:
    """Dispatches webhook notifications when high-severity policy events trigger."""

    @classmethod
    async def dispatch_slack_alert(
        cls,
        webhook_url: str,
        policy_event: PolicyEvent,
        run_id: str
    ) -> bool:
        if not webhook_url:
            return False

        payload = {
            "text": f":warning: *AgentOps Security Alert: {policy_event.rule_name}*",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"AgentOps Guardrail Breach [{policy_event.severity.value}]"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Run ID:*\n`{run_id}`"},
                        {"type": "mrkdwn", "text": f"*Rule:*\n{policy_event.rule_id}"},
                        {"type": "mrkdwn", "text": f"*Confidence:*\n{(policy_event.confidence * 100):.0f}%"},
                        {"type": "mrkdwn", "text": f"*Severity:*\n{policy_event.severity.value}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Evidence:*\n```{policy_event.evidence}```"}
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"*Remediation:* {policy_event.remediation}"}
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.post(webhook_url, json=payload)
                return res.status_code in [200, 204]
        except Exception:
            return False

    @classmethod
    async def dispatch_discord_alert(
        cls,
        webhook_url: str,
        policy_event: PolicyEvent,
        run_id: str
    ) -> bool:
        if not webhook_url:
            return False

        color = 0xF43F5E if policy_event.severity == PolicySeverity.CRITICAL else 0xF59E0B

        payload = {
            "embeds": [
                {
                    "title": f"AgentOps Alert: {policy_event.rule_name}",
                    "description": policy_event.evidence,
                    "color": color,
                    "fields": [
                        {"name": "Run ID", "value": run_id, "inline": True},
                        {"name": "Severity", "value": policy_event.severity.value, "inline": True},
                        {"name": "Remediation", "value": policy_event.remediation}
                    ],
                    "footer": {"text": "AgentOps Observatory Security Engine"}
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.post(webhook_url, json=payload)
                return res.status_code in [200, 204]
        except Exception:
            return False
