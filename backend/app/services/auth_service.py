"""Authentication business logic."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.models import User
from app.security import create_access_token, decode_access_token, verify_password


class InvalidCredentialsError(Exception):
    """Raised when email/password authentication fails."""


class InactiveUserError(Exception):
    """Raised when an authenticated user account is inactive."""


def normalize_email(email: str) -> str:
    return email.strip().lower()


def resolve_user_role(user: User) -> str:
    if user.role_ref is not None and user.role_ref.name:
        return user.role_ref.name
    return user.role


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password."""
    normalized_email = normalize_email(email)
    user = (
        db.query(User)
        .options(joinedload(User.role_ref), joinedload(User.organization))
        .filter(User.email == normalized_email)
        .first()
    )

    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Invalid email or password.")

    if not user.is_active:
        raise InactiveUserError("User account is inactive.")

    user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(user)
    return user


def build_access_token_for_user(user: User) -> str:
    """Create a JWT access token for an authenticated user."""
    claims = {
        "sub": str(user.id),
        "user_id": user.id,
        "organization_id": user.organization_id,
        "email": user.email,
        "role": resolve_user_role(user),
        "type": "access",
    }
    return create_access_token(claims)


def get_user_from_token(db: Session, token: str) -> User:
    """Load the authenticated user referenced by a JWT access token."""
    payload = decode_access_token(token)
    user_id = payload.get("user_id") or payload.get("sub")
    if user_id is None:
        raise ValueError("Token payload is missing user_id.")

    user = (
        db.query(User)
        .options(joinedload(User.role_ref), joinedload(User.organization))
        .filter(User.id == int(user_id))
        .first()
    )
    if user is None:
        raise ValueError("User not found.")

    return user
