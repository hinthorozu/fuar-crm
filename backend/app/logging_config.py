"""Centralized logging configuration for FAIR CRM."""

from __future__ import annotations

import logging


def setup_logging(app_env: str = "development", app_debug: bool = True) -> None:
    """Configure application-wide logging."""
    level = logging.DEBUG if app_debug else logging.INFO
    if app_env.lower() == "production" and not app_debug:
        level = logging.INFO

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Return a named application logger."""
    return logging.getLogger(name)
