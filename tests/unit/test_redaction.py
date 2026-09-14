import pytest
from redaction.engine import RedactionEngine, luhn_checksum


def test_luhn_algorithm():
    assert luhn_checksum("4532015112830366") is True
    assert luhn_checksum("4532015099991234") is False
    assert luhn_checksum("1234") is False


def test_redact_api_keys():
    engine = RedactionEngine()
    text = "Key sk-proj-1234567890abcdef1234567890abcdef and anthropic sk-ant-api03-1234567890abcdef12345678"
    sanitized, events = engine.redact_text(text)
    assert "sk-proj" not in sanitized
    assert "sk-ant" not in sanitized
    assert len(events) >= 2


def test_redact_bearer_tokens():
    engine = RedactionEngine()
    text = "Authorization: Bearer secret_bearer_token_1234567890abcdef"
    sanitized, events = engine.redact_text(text)
    assert "secret_bearer_token" not in sanitized
    assert "[REDACTED_BEARER_TOKEN_" in sanitized


def test_redact_pii_email_and_ssn():
    engine = RedactionEngine()
    text = "User contact is john.doe@company.org with SSN 000-12-3456"
    sanitized, events = engine.redact_text(text)
    assert "john.doe@company.org" not in sanitized
    assert "000-12-3456" not in sanitized
    assert any(e.redaction_type == "EMAIL" for e in events)
    assert any(e.redaction_type == "GOVT_ID_SSN" for e in events)


def test_recursive_payload_redaction():
    engine = RedactionEngine()
    payload = {
        "user": {
            "name": "Alice",
            "email": "alice@corp.com",
            "token": "sensitive_auth_string_12345"
        },
        "items": ["safe_string", "contact +1 (555) 234-5678"]
    }
    sanitized, events = engine.redact_payload(payload)
    assert sanitized["user"]["email"] != "alice@corp.com"
    assert "[REDACTED_SENSITIVE_FIELD_" in sanitized["user"]["token"]
    assert len(events) >= 2
