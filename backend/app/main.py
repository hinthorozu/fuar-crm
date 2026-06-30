"""Fair CRM API application."""

from fastapi import FastAPI

from app.database import AUTH_ENABLED
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
    app = FastAPI(
        title="Fair CRM API",
        description="Backend API for fair, customer and participation management.",
        version=APP_VERSION,
    )

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