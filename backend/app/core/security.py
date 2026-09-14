"""
AgentOps Observatory - Security, RBAC, Cryptographic Chaining & Redacted Logging (Phase 10)
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import jwt
from fastapi import Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from backend.app.core.config import settings

# Security Bearer Scheme
bearer_scheme = HTTPBearer(auto_error=False)


# Cryptographic Hash Chaining for Append-Only Audit Integrity
def compute_event_hash(prev_hash: str, event_data: Dict[str, Any]) -> str:
    """
    Compute deterministic SHA-256 hash chaining for tamper-evident audit logs.
    current_hash = SHA256(prev_hash + canonical_json(event_data))
    """
    canonical_json = json.dumps(event_data, sort_keys=True, default=str)
    hasher = hashlib.sha256()
    hasher.update(prev_hash.encode("utf-8"))
    hasher.update(canonical_json.encode("utf-8"))
    return hasher.hexdigest()


# HMAC Webhook Verification
def verify_webhook_signature(payload_bytes: bytes, received_signature: str, secret: Optional[str] = None) -> bool:
    """Verify HMAC SHA-256 signature for incoming n8n or collector webhooks."""
    if not received_signature:
        return False
    signing_secret = (secret or settings.WEBHOOK_SIGNING_SECRET).encode("utf-8")
    expected = hmac.new(signing_secret, payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_signature.replace("sha256=", ""))


# JWT Authentication & RBAC
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthContext:
    def __init__(self, user_id: str, role: str, tenant_id: str = "default"):
        self.user_id = user_id
        self.role = role  # "admin", "auditor", "developer", "viewer"
        self.tenant_id = tenant_id

    def has_role(self, allowed_roles: List[str]) -> bool:
        return self.role in allowed_roles


async def get_current_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Header(None, alias=settings.API_KEY_HEADER)
) -> AuthContext:
    """
    Authenticate via either Bearer JWT or Service API Key.
    Provides local-first developer fallback if debug/dev mode.
    """
    # 1. Check API Key Header (Collector & Service Agents)
    if api_key:
        if api_key == settings.ADMIN_API_KEY:
            return AuthContext(user_id="admin-service", role="admin", tenant_id="default")
        # Support agent keys
        if api_key.startswith("agy-"):
            return AuthContext(user_id="agent-service", role="developer", tenant_id="default")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")

    # 2. Check Bearer JWT Token
    if credentials:
        payload = decode_access_token(credentials.credentials)
        return AuthContext(
            user_id=payload.get("sub", "user"),
            role=payload.get("role", "viewer"),
            tenant_id=payload.get("tenant_id", "default")
        )

    # 3. Development / Local-first permissive fallback
    if settings.DEBUG:
        return AuthContext(user_id="dev-user", role="admin", tenant_id="default")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials missing")


def require_roles(allowed_roles: List[str]):
    """FastAPI dependency for RBAC."""
    async def role_checker(auth: AuthContext = Security(get_current_auth)) -> AuthContext:
        if not auth.has_role(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}"
            )
        return auth
    return role_checker


# Redacted Logging Filter to prevent credentials from ever leaking into logger stdout
class RedactedLogFilter(logging.Filter):
    REDACT_WORDS = ["sk-", "Bearer ", "password=", "secret=", "AKIA"]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.msg)
        for w in self.REDACT_WORDS:
            if w in msg:
                # Mask out potential secret
                record.msg = "[LOG FILTERED: CONTAINS CREDENTIAL FRAGMENT]"
                break
        return True
