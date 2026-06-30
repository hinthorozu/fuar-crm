"""Authentication business logic."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.base import (
    AuthenticationError,
    InactiveUserError,
    InvalidCredentialsError,
    NotFoundError,
    ServiceUnavailableError,
)
from app.logging_config import get_logger
from app.models.models import User
from app.repositories.user_repository import UserRepository
from app.security import create_access_token, decode_access_token, verify_password

logger = get_logger(__name__)


class AuthService:
    """Authentication and current-user resolution."""

    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    @staticmethod
    def resolve_user_role(user: User) -> str:
        if user.role_ref is not None and user.role_ref.name:
            return user.role_ref.name
        return user.role

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user by email and password."""
        user = self.user_repository.find_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            logger.warning("Failed login attempt for email=%s", UserRepository.normalize_email(email))
            raise InvalidCredentialsError()

        if not user.is_active:
            logger.warning("Inactive user login attempt for user_id=%s", user.id)
            raise InactiveUserError()

        updated_user = self.user_repository.update_last_login(user)
        logger.info("Successful login for user_id=%s", updated_user.id)
        return updated_user

    def build_access_token_for_user(self, user: User) -> str:
        """Create a JWT access token for an authenticated user."""
        claims = {
            "sub": str(user.id),
            "user_id": user.id,
            "organization_id": user.organization_id,
            "email": user.email,
            "role": self.resolve_user_role(user),
            "type": "access",
        }
        try:
            return create_access_token(claims)
        except RuntimeError as exc:
            raise ServiceUnavailableError(str(exc)) from exc

    def get_user_from_token(self, token: str) -> User:
        """Load the authenticated user referenced by a JWT access token."""
        try:
            payload = decode_access_token(token)
        except ValueError as exc:
            raise AuthenticationError(str(exc)) from exc
        except RuntimeError as exc:
            raise ServiceUnavailableError(str(exc)) from exc

        user_id = payload.get("user_id") or payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Token payload is missing user_id.")

        user = self.user_repository.find_by_id(int(user_id))
        if user is None:
            raise NotFoundError("User not found.")

        return user


def get_auth_service(db: Session) -> AuthService:
    """Factory helper for auth service construction."""
    return AuthService(db)
