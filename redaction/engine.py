"""
AgentOps Observatory - Deterministic Redaction Engine (Phase 3)
Provides high-performance, deterministic masking of secrets, API keys, credentials, and PII.
Generates RedactionEvent audit logs without ever logging or storing the raw secret.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from backend.app.schemas.events import EventStatus, RedactionEvent, SensitivityLevel, SourceType


def luhn_checksum(card_number_str: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    digits = [int(d) for d in card_number_str if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


class RedactionEngine:
    """
    Deterministic Redaction Engine supporting recursive payloads,
    pattern matching, Luhn verification for payment cards, and structured audit logs.
    """
    POLICY_VERSION = "2.1.0"

    # Pre-compiled regex patterns for performance
    PATTERNS = {
        "PRIVATE_KEY": re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
            re.IGNORECASE
        ),
        "OPENAI_API_KEY": re.compile(r"\bsk-[a-zA-Z0-9]{20,T3BlbkFJ[a-zA-Z0-9]{20,}\b|\bsk-(?:proj-)?[a-zA-Z0-9\-_]{32,}\b"),
        "ANTHROPIC_API_KEY": re.compile(r"\bsk-ant-[a-zA-Z0-9\-_]{32,}\b"),
        "AWS_ACCESS_KEY": re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16,20}\b"),
        "JWT_TOKEN": re.compile(r"\beyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\b"),
        "BEARER_TOKEN": re.compile(r"\bBearer\s+([a-zA-Z0-9\-_\.]{16,})\b", re.IGNORECASE),
        "GENERIC_API_KEY": re.compile(
            r"(?i)(?:api_key|apikey|access_token|auth_token|secret_key|client_secret)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?"
        ),
        "PASSWORD_INLINE": re.compile(
            r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"\s\r\n]{6,})['\"]?"
        ),
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
        "PHONE": re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "GOVT_ID_SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "CREDIT_CARD_CANDIDATE": re.compile(r"\b(?:\d[ -]*?){13,19}\b")
    }

    # Sensitive key names in JSON / dicts
    SENSITIVE_KEY_NAMES = {
        "password", "passwd", "pwd", "secret", "api_key", "apikey",
        "access_token", "auth_token", "client_secret", "private_key",
        "ssn", "credit_card", "cvv", "token", "authorization"
    }

    def __init__(self, policy_version: Optional[str] = None):
        self.policy_version = policy_version or self.POLICY_VERSION

    def _generate_masked_token(self, secret_type: str, raw_secret: str) -> str:
        """
        Generate a safe, non-reversible surrogate hash token.
        Preserves deterministic grouping for audit analytics without exposing secrets.
        """
        hash_digest = hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()[:8]
        return f"[REDACTED_{secret_type}_{hash_digest}]"

    def redact_text(
        self, text: str, location_prefix: str = "root", run_id: Optional[str] = None
    ) -> Tuple[str, List[RedactionEvent]]:
        """
        Redact a single string value across all regex categories.
        Returns: (sanitized_string, list_of_redaction_events)
        """
        if not text or not isinstance(text, str):
            return text, []

        redaction_events: List[RedactionEvent] = []
        sanitized = text

        # 1. Private keys first (multiline block)
        for match in self.PATTERNS["PRIVATE_KEY"].finditer(text):
            raw = match.group(0)
            placeholder = self._generate_masked_token("PRIVATE_KEY", raw)
            sanitized = sanitized.replace(raw, placeholder)
            redaction_events.append(self._create_event(
                run_id=run_id,
                redaction_type="PRIVATE_KEY",
                placeholder=placeholder,
                location=location_prefix,
                char_count=len(raw)
            ))

        # 2. Specific API keys
        for key_type, pattern in [
            ("OPENAI_KEY", self.PATTERNS["OPENAI_API_KEY"]),
            ("ANTHROPIC_KEY", self.PATTERNS["ANTHROPIC_API_KEY"]),
            ("AWS_ACCESS_KEY", self.PATTERNS["AWS_ACCESS_KEY"]),
            ("JWT_TOKEN", self.PATTERNS["JWT_TOKEN"]),
        ]:
            for match in pattern.finditer(sanitized):
                raw = match.group(0)
                placeholder = self._generate_masked_token(key_type, raw)
                sanitized = sanitized.replace(raw, placeholder)
                redaction_events.append(self._create_event(
                    run_id=run_id,
                    redaction_type=key_type,
                    placeholder=placeholder,
                    location=location_prefix,
                    char_count=len(raw)
                ))

        # 3. Bearer tokens
        for match in self.PATTERNS["BEARER_TOKEN"].finditer(sanitized):
            token_body = match.group(1)
            placeholder = self._generate_masked_token("BEARER_TOKEN", token_body)
            sanitized = sanitized.replace(match.group(0), f"Bearer {placeholder}")
            redaction_events.append(self._create_event(
                run_id=run_id,
                redaction_type="BEARER_TOKEN",
                placeholder=placeholder,
                location=location_prefix,
                char_count=len(token_body)
            ))

        # 4. Inline Generic API Key & Password patterns
        for key_type, pattern in [
            ("GENERIC_API_KEY", self.PATTERNS["GENERIC_API_KEY"]),
            ("PASSWORD", self.PATTERNS["PASSWORD_INLINE"]),
        ]:
            for match in pattern.finditer(sanitized):
                secret_val = match.group(1)
                placeholder = self._generate_masked_token(key_type, secret_val)
                sanitized = sanitized.replace(secret_val, placeholder)
                redaction_events.append(self._create_event(
                    run_id=run_id,
                    redaction_type=key_type,
                    placeholder=placeholder,
                    location=location_prefix,
                    char_count=len(secret_val)
                ))

        # 5. Government IDs (SSN)
        for match in self.PATTERNS["GOVT_ID_SSN"].finditer(sanitized):
            raw = match.group(0)
            placeholder = self._generate_masked_token("GOVT_ID_SSN", raw)
            sanitized = sanitized.replace(raw, placeholder)
            redaction_events.append(self._create_event(
                run_id=run_id,
                redaction_type="GOVT_ID_SSN",
                placeholder=placeholder,
                location=location_prefix,
                char_count=len(raw)
            ))

        # 6. Credit Card Numbers (with Luhn validation)
        for match in self.PATTERNS["CREDIT_CARD_CANDIDATE"].finditer(sanitized):
            raw_candidate = match.group(0)
            digits_only = re.sub(r"\D", "", raw_candidate)
            if 13 <= len(digits_only) <= 19 and luhn_checksum(digits_only):
                placeholder = self._generate_masked_token("CREDIT_CARD", digits_only)
                sanitized = sanitized.replace(raw_candidate, placeholder)
                redaction_events.append(self._create_event(
                    run_id=run_id,
                    redaction_type="CREDIT_CARD",
                    placeholder=placeholder,
                    location=location_prefix,
                    char_count=len(digits_only)
                ))

        # 7. Email addresses
        for match in self.PATTERNS["EMAIL"].finditer(sanitized):
            raw = match.group(0)
            placeholder = self._generate_masked_token("EMAIL", raw)
            sanitized = sanitized.replace(raw, placeholder)
            redaction_events.append(self._create_event(
                run_id=run_id,
                redaction_type="EMAIL",
                placeholder=placeholder,
                location=location_prefix,
                char_count=len(raw)
            ))

        # 8. Phone numbers
        for match in self.PATTERNS["PHONE"].finditer(sanitized):
            raw = match.group(0)
            # Avoid single short numbers
            if len(re.sub(r"\D", "", raw)) >= 10:
                placeholder = self._generate_masked_token("PHONE", raw)
                sanitized = sanitized.replace(raw, placeholder)
                redaction_events.append(self._create_event(
                    run_id=run_id,
                    redaction_type="PHONE",
                    placeholder=placeholder,
                    location=location_prefix,
                    char_count=len(raw)
                ))

        return sanitized, redaction_events

    def redact_payload(
        self, payload: Any, location_path: str = "$", run_id: Optional[str] = None
    ) -> Tuple[Any, List[RedactionEvent]]:
        """
        Recursively redact any nested Python data structure (dict, list, primitive).
        """
        events: List[RedactionEvent] = []

        if isinstance(payload, str):
            sanitized, str_events = self.redact_text(payload, location_prefix=location_path, run_id=run_id)
            return sanitized, str_events

        elif isinstance(payload, dict):
            new_dict: Dict[str, Any] = {}
            for k, v in payload.items():
                curr_path = f"{location_path}.{k}"
                # If key name itself indicates sensitive credential, mask immediately
                if str(k).lower() in self.SENSITIVE_KEY_NAMES and isinstance(v, (str, int, float)):
                    raw_str = str(v)
                    placeholder = self._generate_masked_token("SENSITIVE_FIELD", raw_str)
                    new_dict[k] = placeholder
                    events.append(self._create_event(
                        run_id=run_id,
                        redaction_type="SENSITIVE_FIELD",
                        placeholder=placeholder,
                        location=curr_path,
                        char_count=len(raw_str)
                    ))
                else:
                    sanitized_val, child_events = self.redact_payload(v, location_path=curr_path, run_id=run_id)
                    new_dict[k] = sanitized_val
                    events.extend(child_events)
            return new_dict, events

        elif isinstance(payload, list):
            new_list: List[Any] = []
            for idx, item in enumerate(payload):
                curr_path = f"{location_path}[{idx}]"
                sanitized_val, child_events = self.redact_payload(item, location_path=curr_path, run_id=run_id)
                new_list.append(sanitized_val)
                events.extend(child_events)
            return new_list, events

        else:
            return payload, []

    def _create_event(
        self,
        run_id: Optional[str],
        redaction_type: str,
        placeholder: str,
        location: str,
        char_count: int
    ) -> RedactionEvent:
        """Construct audit event for redaction."""
        return RedactionEvent(
            event_id=str(uuid4()),
            run_id=run_id or "global",
            source=SourceType.SYSTEM,
            actor="redaction-engine",
            status=EventStatus.REDACTED,
            sensitivity=SensitivityLevel.RESTRICTED,
            redaction_type=redaction_type,
            masked_placeholder=placeholder,
            location=location,
            policy_version=self.policy_version,
            character_count=char_count,
            provenance={"engine": "DeterministicRedactionEngine", "version": self.policy_version}
        )
