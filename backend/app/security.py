"""Security helpers for authentication."""

from __future__ import annotations

from passlib.context import CryptContext

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