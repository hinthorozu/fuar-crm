"""Map application exceptions to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import (
    AppError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from app.logging_config import get_logger
from app.schemas.response import ApiErrorResponse, ErrorDetail

logger = get_logger(__name__)


def _error_response(status_code: int, exc: AppError) -> JSONResponse:
    payload = ApiErrorResponse(
        success=False,
        error=ErrorDetail(code=exc.code, message=exc.message),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers for application errors."""

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning("Validation error on %s: %s", request.url.path, exc.message)
        return _error_response(422, exc)

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request,
        exc: AuthenticationError,
    ) -> JSONResponse:
        logger.warning("Authentication error on %s: %s", request.url.path, exc.message)
        response = _error_response(401, exc)
        response.headers["WWW-Authenticate"] = "Bearer"
        return response

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        logger.warning("Forbidden error on %s: %s", request.url.path, exc.message)
        return _error_response(403, exc)

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        logger.info("Not found on %s: %s", request.url.path, exc.message)
        return _error_response(404, exc)

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
        logger.warning("Conflict on %s: %s", request.url.path, exc.message)
        return _error_response(409, exc)

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(
        request: Request,
        exc: ServiceUnavailableError,
    ) -> JSONResponse:
        logger.error("Service unavailable on %s: %s", request.url.path, exc.message)
        return _error_response(503, exc)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error("Application error on %s: %s", request.url.path, exc.message)
        return _error_response(400, exc)

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
        logger.error("Runtime error on %s: %s", request.url.path, exc)
        payload = ApiErrorResponse(
            success=False,
            error=ErrorDetail(code="service_unavailable", message=str(exc)),
        )
        return JSONResponse(status_code=503, content=payload.model_dump())
