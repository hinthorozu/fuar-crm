"""Authentication dependencies."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions.base import ForbiddenError, InactiveUserError
from app.models.models import User
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Paste the JWT access token returned by POST /auth/login.",
    auto_error=True,
)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.get_user_from_token(credentials.credentials)


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise InactiveUserError()
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    role = auth_service.resolve_user_role(current_user)
    if role not in {"super_admin", "admin"}:
        raise ForbiddenError("Admin privileges required.")
    return current_user
