"""Application exception hierarchy."""

from __future__ import annotations


class AppError(Exception):
    """Base class for application-level errors."""

    code: str = "app_error"

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or self.code
        super().__init__(message)


class ValidationError(AppError):
    code = "validation_error"


class AuthenticationError(AppError):
    code = "authentication_error"


class InvalidCredentialsError(AuthenticationError):
    code = "invalid_credentials"

    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(message)


class ForbiddenError(AppError):
    code = "forbidden"


class InactiveUserError(ForbiddenError):
    code = "inactive_user"

    def __init__(self, message: str = "User account is inactive.") -> None:
        super().__init__(message)


class NotFoundError(AppError):
    code = "not_found"


class ConflictError(AppError):
    code = "conflict"


class ServiceUnavailableError(AppError):
    code = "service_unavailable"
