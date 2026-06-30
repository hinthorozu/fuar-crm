"""Fair CRM API application."""

from fastapi import FastAPI

from app.config import settings
from app.database import AUTH_ENABLED
from app.exception_handlers import register_exception_handlers
from app.logging_config import setup_logging
from app.routers import (
    auth,
    contacts,
    customer_emails,
    customer_phones,
    customers,
    dashboard,
    fair_participations,
    fairs,
    notes,
)

APP_VERSION = "0.1.9"


def create_app() -> FastAPI:
    setup_logging(settings.app_env, settings.app_debug)

    app = FastAPI(
        title="Fair CRM API",
        description="Backend API for fair, customer and participation management.",
        version=APP_VERSION,
    )

    register_exception_handlers(app)

    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(fairs.router)
    app.include_router(customers.router)
    app.include_router(contacts.router)
    app.include_router(customer_phones.router)
    app.include_router(customer_emails.router)
    app.include_router(notes.router)
    app.include_router(fair_participations.router)

    @app.get("/")
    def root():
        return {
            "status": "running",
            "message": "Fair CRM API is running",
            "version": APP_VERSION,
            "auth_enabled": AUTH_ENABLED,
        }

    @app.get("/health-check")
    def health_check():
        from app.database import engine

        try:
            with engine.connect():
                return {
                    "database": "connected",
                    "status": "healthy",
                    "version": APP_VERSION,
                }
        except Exception as exc:
            return {
                "database": "not_connected",
                "status": "unhealthy",
                "error": str(exc),
                "version": APP_VERSION,
            }

    return app


app = create_app()