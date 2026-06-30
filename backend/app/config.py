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


UNSAFE_JWT_SECRETS = frozenset(
    {
        "",
        "change_me",
        "change_me_in_env",
        "changeme",
        "secret",
        "your_secret_key_here",
        "replace_with_a_long_random_secret_key",
    }
)


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings for FAIR CRM backend."""

    app_env: str
    app_debug: bool
    auth_enabled: bool
    secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    database_url_override: str | None
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str | None
    db_allow_empty_password: bool

    @classmethod
    def from_env(cls) -> "AppSettings":
        expire_raw = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30").strip()
        try:
            jwt_access_token_expire_minutes = max(1, int(expire_raw))
        except ValueError:
            jwt_access_token_expire_minutes = 30

        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            app_debug=_env_bool("APP_DEBUG", True),
            auth_enabled=_env_bool("AUTH_ENABLED", False),
            secret_key=(os.getenv("SECRET_KEY") or "").strip(),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256").strip() or "HS256",
            jwt_access_token_expire_minutes=jwt_access_token_expire_minutes,
            database_url_override=os.getenv("DATABASE_URL") or None,
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=os.getenv("DB_PORT", "3306"),
            db_name=os.getenv("DB_NAME", "fair_crm"),
            db_user=os.getenv("DB_USER", "root"),
            db_password=os.getenv("DB_PASSWORD"),
            db_allow_empty_password=_env_bool("DB_ALLOW_EMPTY_PASSWORD", False),
        )

    def ensure_jwt_ready(self) -> None:
        """Validate JWT settings before issuing or verifying tokens."""
        if not self.secret_key:
            raise RuntimeError(
                "SECRET_KEY is missing. Create backend/.env from backend/.env.example "
                "and set SECRET_KEY to a long random value."
            )
        if self.secret_key.lower() in UNSAFE_JWT_SECRETS or len(self.secret_key) < 16:
            raise RuntimeError(
                "SECRET_KEY is missing or unsafe. Set a random SECRET_KEY with at least "
                "16 characters in backend/.env before using authentication."
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
