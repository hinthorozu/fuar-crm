"""FAIR CRM local health check.

Run from project root:
    python scripts/health_check.py

This script checks local configuration, database connectivity, schema tables,
seed counts, FastAPI importability and key route registration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
ENV_FILE = BACKEND_DIR / ".env"
EXCEL_FILE = PROJECT_ROOT / "FAIR_CRM_PROJECT.xlsx"

# Make backend/app imports deterministic when this script is run from any folder.
backend_path = str(BACKEND_DIR)
if backend_path in sys.path:
    sys.path.remove(backend_path)
sys.path.insert(0, backend_path)

# Avoid accidentally reusing a stale/imported package named "app" from another
# location when the health check is run inside IDEs, notebooks or shells.
loaded_app = sys.modules.get("app")
if loaded_app is not None:
    loaded_file = getattr(loaded_app, "__file__", "") or ""
    if str(BACKEND_DIR) not in loaded_file:
        for module_name in list(sys.modules):
            if module_name == "app" or module_name.startswith("app."):
                sys.modules.pop(module_name, None)


class CheckResult:
    def __init__(self, name: str, ok: bool, detail: str = "") -> None:
        self.name = name
        self.ok = ok
        self.detail = detail


def print_result(result: CheckResult) -> None:
    status = "[OK]" if result.ok else "[FAIL]"
    print(f"{result.name:<32} {status} {result.detail}")


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def add(results: list[CheckResult], name: str, ok: bool, detail: str = "") -> bool:
    result = CheckResult(name, ok, detail)
    results.append(result)
    print_result(result)
    return ok


def safe_count(connection: Any, table_name: str) -> int | None:
    from sqlalchemy import text

    try:
        return int(connection.execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).scalar() or 0)
    except Exception:
        return None


def main() -> int:
    print("FAIR CRM Health Check")
    print("=" * 42)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    results: list[CheckResult] = []

    add(results, "Project root", PROJECT_ROOT.exists(), str(PROJECT_ROOT))
    add(results, "Backend directory", BACKEND_DIR.exists(), str(BACKEND_DIR))
    add(results, "Project Excel hub", EXCEL_FILE.exists(), "FAIR_CRM_PROJECT.xlsx")

    env_exists = add(results, ".env file", ENV_FILE.exists(), str(ENV_FILE))
    env_values = read_env_file(ENV_FILE)

    if env_exists:
        required_keys = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER"]
        for key in required_keys:
            add(results, f".env {key}", bool(env_values.get(key)), env_values.get(key, "missing"))

        allow_empty = env_values.get("DB_ALLOW_EMPTY_PASSWORD", "false").lower() in {"1", "true", "yes", "on"}
        has_password = bool(env_values.get("DB_PASSWORD"))
        add(
            results,
            ".env DB_PASSWORD",
            has_password or allow_empty,
            "set" if has_password else "empty allowed" if allow_empty else "missing",
        )
    else:
        add(results, ".env required keys", False, "copy backend/.env.example to backend/.env")

    settings = None
    try:
        from app.config import settings as loaded_settings

        settings = loaded_settings
        add(results, "Config import", True, "app.config")
    except Exception as exc:
        add(results, "Config import", False, str(exc))

    db_url_ready = False
    if settings is not None:
        try:
            _ = settings.database_url
            db_url_ready = add(results, "Database URL build", True, "credentials loaded")
        except Exception as exc:
            add(results, "Database URL build", False, str(exc))

    engine = None
    if db_url_ready:
        try:
            from app.database import engine as loaded_engine

            engine = loaded_engine
            add(results, "Database engine", True, "SQLAlchemy engine created")
        except Exception as exc:
            add(results, "Database engine", False, str(exc))

    connection = None
    if engine is not None:
        try:
            from sqlalchemy import text

            connection = engine.connect()
            connection.execute(text("SELECT 1"))
            add(results, "Database connection", True, "SELECT 1 OK")
        except Exception as exc:
            add(results, "Database connection", False, str(exc))

    if connection is not None:
        try:
            from sqlalchemy import inspect

            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())
            expected_tables = {
                "organizations",
                "roles",
                "permissions",
                "role_permissions",
                "users",
                "customers",
                "contacts",
                "customer_phones",
                "customer_emails",
                "fairs",
                "fair_participations",
                "notes",
                "import_batches",
                "import_rows",
                "scraper_sources",
                "scraper_runs",
                "audit_logs",
            }
            missing = sorted(expected_tables - existing_tables)
            add(
                results,
                "Required tables",
                not missing,
                "all required tables exist" if not missing else "missing: " + ", ".join(missing),
            )

            seed_tables = [
                "organizations",
                "roles",
                "permissions",
                "role_permissions",
                "users",
                "customers",
                "contacts",
                "customer_phones",
                "customer_emails",
                "fairs",
                "fair_participations",
                "notes",
                "import_batches",
                "import_rows",
                "scraper_sources",
                "scraper_runs",
                "audit_logs",
            ]
            for table in seed_tables:
                if table in existing_tables:
                    count = safe_count(connection, table)
                    add(results, f"Rows: {table}", count is not None, str(count) if count is not None else "count failed")
                else:
                    add(results, f"Rows: {table}", False, "table missing")
        except Exception as exc:
            add(results, "Schema/seed checks", False, str(exc))
        finally:
            connection.close()

    try:
        import app.main as app_main
        from app.main import app

        add(results, "FastAPI app import", True, f"app.main:app from {Path(app_main.__file__).resolve()}")
        
        route_paths = set(app.openapi()["paths"].keys())

        def normalize_route_path(path: str) -> str:
            """Normalize FastAPI route paths for health-check comparison.

            FastAPI registers list routes declared as @router.get("/") with a
            trailing slash, for example /customers/. For daily testing we want
            /customers and /customers/ to be treated as the same endpoint.
            """
            if path != "/" and path.endswith("/"):
                return path.rstrip("/")
            return path

        normalized_route_paths = {normalize_route_path(path) for path in route_paths}
        
        required_routes = {
            "/",
            "/health-check",
            "/dashboard/summary",
            "/customers",
            "/customers/{customer_id}/profile",
            "/fair-participations"
        }
        missing_routes = sorted(required_routes - normalized_route_paths)
        
        add(
            results,
            "Key API routes",
            not missing_routes,
            f"all key routes registered; total routes: {len(normalized_route_paths)}"
            if not missing_routes
            else "missing: " + ", ".join(missing_routes) + "; found: " + ", ".join(sorted(normalized_route_paths)),
        )
    except Exception as exc:
        add(results, "FastAPI app import", False, str(exc))

    print()
    failed = [r for r in results if not r.ok]
    if failed:
        print("Result: SYSTEM NOT READY")
        print("Fix the [FAIL] items above, then run this command again:")
        print("    python scripts/health_check.py")
        return 1

    print("Result: SYSTEM READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
