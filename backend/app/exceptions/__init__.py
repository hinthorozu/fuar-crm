"""Centralized application exceptions."""

from app.exceptions.base import (
    AppError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    InactiveUserError,
    InvalidCredentialsError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)

__all__ = [
    "AppError",
    "AuthenticationError",
    "ConflictError",
    "ForbiddenError",
    "InactiveUserError",
    "InvalidCredentialsError",
    "NotFoundError",
    "ServiceUnavailableError",
    "ValidationError",
]
