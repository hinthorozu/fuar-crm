"""Application configuration loaded from backend/.env.

Sensitive values must not be hardcoded in source files. Copy
backend/.env.example to backend/.env and fill local credentials there.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"

# Load backend/.env explicitly so commands work from backend/ or project root.
load_dotenv(dotenv_path=ENV_FILE)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings for FAIR CRM backend."""

    app_env: str
    app_debug: bool
    auth_enabled: bool
    database_url_override: str | None
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str | None
    db_allow_empty_password: bool

    @classmethod
    def from_env(cls) -> "AppSettings":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            app_debug=_env_bool("APP_DEBUG", True),
            auth_enabled=_env_bool("AUTH_ENABLED", False),
            database_url_override=os.getenv("DATABASE_URL") or None,
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=os.getenv("DB_PORT", "3306"),
            db_name=os.getenv("DB_NAME", "fair_crm"),
            db_user=os.getenv("DB_USER", "root"),
            db_password=os.getenv("DB_PASSWORD"),
            db_allow_empty_password=_env_bool("DB_ALLOW_EMPTY_PASSWORD", False),
        )

    @property
    def database_url(self) -> str:
        """Return a SQLAlchemy MySQL URL.

        DATABASE_URL can be used as a full override. Otherwise individual
        DB_* variables are combined safely and password values are URL-escaped.
        """
        if self.database_url_override:
            return self.database_url_override

        if not self.db_password and not self.db_allow_empty_password:
            raise RuntimeError(
                "Database password is missing. Create backend/.env from "
                "backend/.env.example and set DB_PASSWORD. If your local MySQL "
                "user intentionally has no password, set DB_ALLOW_EMPTY_PASSWORD=true."
            )

        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password or "")
        host = self.db_host
        port = self.db_port
        name = self.db_name

        if password:
            credentials = f"{user}:{password}"
        else:
            credentials = user

        return f"mysql+pymysql://{credentials}@{host}:{port}/{name}?charset=utf8mb4"


settings = AppSettings.from_env()
