"""Security helpers for authentication."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a secure password hash."""
    if not password or len(password.strip()) < 6:
        raise ValueError("Password must be at least 6 characters.")
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain password against a stored hash."""
    if not plain_password or not password_hash:
        return False
    return password_context.verify(plain_password, password_hash)


def create_access_token(claims: dict[str, Any]) -> str:
    """Create a JWT access token with the provided claims."""
    settings.ensure_jwt_ready()
    payload = claims.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload.setdefault("type", "access")
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    settings.ensure_jwt_ready()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired access token.") from exc

    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")

    return payload
