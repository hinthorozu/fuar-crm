"""FAIR CRM comprehensive quality check.

Run from project root:
    python scripts/quality_check.py

Orchestrates dev_check and health_check, then runs static project validations.
"""

from __future__ import annotations

import ast
import importlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ENV_FILE = BACKEND_DIR / ".env"
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"

# Align sys.path with health_check.py for deterministic backend imports.
backend_path = str(BACKEND_DIR)
if backend_path in sys.path:
    sys.path.remove(backend_path)
sys.path.insert(0, backend_path)

loaded_app = sys.modules.get("app")
if loaded_app is not None:
    loaded_file = getattr(loaded_app, "__file__", "") or ""
    if str(BACKEND_DIR) not in loaded_file:
        for module_name in list(sys.modules):
            if module_name == "app" or module_name.startswith("app."):
                sys.modules.pop(module_name, None)

EXPECTED_MODELS = {
    "Organization",
    "Role",
    "Permission",
    "RolePermission",
    "User",
    "Customer",
    "Contact",
    "CustomerPhone",
    "CustomerEmail",
    "Note",
    "Fair",
    "FairParticipation",
    "ImportBatch",
    "ImportRow",
    "ScraperSource",
    "ScraperRun",
    "AuditLog",
}

EXPECTED_TABLES = {
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

EXPECTED_ROUTER_PREFIXES = {
    "/dashboard",
    "/fairs",
    "/customers",
    "/contacts",
    "/customer-phones",
    "/customer-emails",
    "/notes",
    "/fair-participations",
    "/auth",
}

EXPECTED_PROJECT_DIRS = (
    "backend",
    "frontend",
    "docs",
    "resources",
    "scripts",
)

EXPECTED_PROJECT_FILES = (
    "README.md",
    "MASTER_CONTEXT.md",
    "CHANGELOG.md",
    "FAIR_CRM_PROJECT.xlsx",
    "docker-compose.yml",
    ".gitignore",
    "LICENSE",
)

REQUIRED_PROJECT_DOCS = (
    "README.md",
    "MASTER_CONTEXT.md",
    "CHANGELOG.md",
    "FAIR_CRM_PROJECT.xlsx",
)

IMPORT_TO_REQUIREMENT = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "sqlalchemy": "sqlalchemy",
    "pymysql": "pymysql",
    "dotenv": "python-dotenv",
    "pydantic": "pydantic",
    "openpyxl": "openpyxl",
    "passlib": "passlib",
    "bcrypt": "bcrypt",
    "jose": "python-jose",
}

SCAN_MARKERS_DIRS = (BACKEND_DIR, SCRIPTS_DIR)
MARKER_PATTERN = re.compile(r"#\s*(TODO|FIXME)\b")

CHECK_POINTS = {
    "Python Compile": 8,
    "Imports": 8,
    "FastAPI": 8,
    "Models": 8,
    "Routers": 8,
    "Requirements": 8,
    "Environment": 8,
    "Project Structure": 4,
    "Project Files": 4,
    "Circular Imports": 8,
    "Health Check": 8,
    "Dev Check": 8,
    "Code Markers": 12,
}


@dataclass
class CheckOutcome:
    name: str
    status: str
    points: int
    max_points: int
    hard_fail: bool = False
    details: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    outcomes: list[CheckOutcome] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    git_status: str = "UNKNOWN"

    @property
    def score(self) -> int:
        return sum(item.points for item in self.outcomes)

    @property
    def hard_failures(self) -> list[CheckOutcome]:
        return [item for item in self.outcomes if item.hard_fail]

    @property
    def ready(self) -> bool:
        return not self.hard_failures


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


def normalize_route_path(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


def parse_requirement_names(path: Path) -> set[str]:
    names: set[str] = set()
    if not path.exists():
        return names
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        package = line.split("==", 1)[0].strip()
        package = package.split("[", 1)[0].strip().lower()
        names.add(package)
    return names


def module_name_for_path(path: Path) -> str:
    relative = path.relative_to(BACKEND_DIR / "app")
    parts = list(relative.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    if not parts:
        return "app"
    return "app." + ".".join(parts)


def collect_backend_python_files() -> list[Path]:
    return sorted((BACKEND_DIR / "app").rglob("*.py"))


def collect_app_imports(path: Path) -> set[str]:
    imports: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "app" or alias.name.startswith("app."):
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "app" or node.module.startswith("app."):
                imports.add(node.module)
    return imports


def find_import_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    stack: list[str] = []
    in_stack: set[str] = set()

    def visit(node: str) -> None:
        if node in in_stack:
            cycle_start = stack.index(node)
            cycles.append(stack[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        stack.append(node)
        for neighbor in sorted(graph.get(node, set())):
            visit(neighbor)
        stack.pop()
        in_stack.remove(node)

    for module_name in sorted(graph):
        visit(module_name)
    return cycles


def run_subprocess_check(script_name: str) -> tuple[bool, list[str]]:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return False, [f"Missing script: {script_path}"]

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, []

    details = [f"{script_name} exited with code {result.returncode}"]
    output = (result.stdout or "").strip()
    errors = (result.stderr or "").strip()
    if output:
        details.append(output)
    if errors:
        details.append(errors)
    return False, details


def add_outcome(
    report: QualityReport,
    name: str,
    passed: bool,
    details: Iterable[str] | None = None,
    *,
    hard_fail: bool = True,
    status: str | None = None,
    points: int | None = None,
) -> None:
    max_points = CHECK_POINTS[name]
    if points is None:
        points = max_points if passed else 0
    if status is None:
        status = "PASS" if passed else "FAIL"
    report.outcomes.append(
        CheckOutcome(
            name=name,
            status=status,
            points=points,
            max_points=max_points,
            hard_fail=hard_fail and not passed,
            details=list(details or ()),
        )
    )


def check_python_compile(report: QualityReport) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "backend", "scripts"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        add_outcome(report, "Python Compile", True)
        return

    details = ["Python compile failed"]
    if result.stderr.strip():
        details.append(result.stderr.strip())
    if result.stdout.strip():
        details.append(result.stdout.strip())
    add_outcome(report, "Python Compile", False, details)


def check_imports(report: QualityReport) -> None:
    modules = [
        "app.config",
        "app.database",
        "app.security",
        "app.main",
        "app.models.models",
        "app.utils.normalization",
        "app.routers.dashboard",
        "app.routers.customers",
        "app.routers.contacts",
        "app.routers.customer_phones",
        "app.routers.customer_emails",
        "app.routers.notes",
        "app.routers.fairs",
        "app.routers.fair_participations",
        "app.routers.auth",
        "app.services.auth_service",
        "app.dependencies.auth",
        "app.schemas.auth",
        "app.schemas.customer",
        "app.schemas.dashboard",
    ]
    failures: list[str] = []
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    add_outcome(report, "Imports", not failures, failures or None)


def check_fastapi(report: QualityReport) -> None:
    failures: list[str] = []
    try:
        from app.main import APP_VERSION, app, create_app

        if not callable(create_app):
            failures.append("create_app is not callable")
        if app is None:
            failures.append("app instance is missing")
        if not hasattr(app, "openapi"):
            failures.append("app.openapi is missing")
        if not APP_VERSION:
            failures.append("APP_VERSION is empty")
    except Exception as exc:
        failures.append(str(exc))

    add_outcome(report, "FastAPI", not failures, failures or None)


def check_models(report: QualityReport) -> None:
    failures: list[str] = []
    try:
        from app.models import models as models_module

        for model_name in sorted(EXPECTED_MODELS):
            if not hasattr(models_module, model_name):
                failures.append(f"Missing model class: {model_name}")

        models_path = Path(models_module.__file__)
        class_names: list[str] = []
        table_names: list[str] = []
        for node in ast.walk(ast.parse(models_path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
                for child in node.body:
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name) and target.id == "__tablename__":
                                if isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                                    table_names.append(child.value.value)

        duplicate_classes = sorted({name for name in class_names if class_names.count(name) > 1})
        duplicate_tables = sorted({name for name in table_names if table_names.count(name) > 1})
        if duplicate_classes:
            failures.append("Duplicate model class names: " + ", ".join(duplicate_classes))
        if duplicate_tables:
            failures.append("Duplicate model table names: " + ", ".join(duplicate_tables))

        from app.database import Base

        missing_tables = sorted(EXPECTED_TABLES - set(Base.metadata.tables.keys()))
        if missing_tables:
            failures.append("Missing SQLAlchemy tables: " + ", ".join(missing_tables))
    except Exception as exc:
        failures.append(str(exc))

    add_outcome(report, "Models", not failures, failures or None)


def check_routers(report: QualityReport) -> None:
    failures: list[str] = []
    try:
        from app.main import app

        openapi_paths = app.openapi()["paths"]
        normalized_paths = [normalize_route_path(path) for path in openapi_paths]

        duplicate_paths = sorted(
            {path for path in normalized_paths if normalized_paths.count(path) > 1}
        )
        if duplicate_paths:
            failures.append("Duplicate normalized routes: " + ", ".join(duplicate_paths))

        duplicate_method_pairs: list[str] = []
        for path, methods in openapi_paths.items():
            method_names = sorted(methods.keys())
            if len(method_names) != len(set(method_names)):
                duplicate_method_pairs.append(f"{path} ({', '.join(method_names)})")
        if duplicate_method_pairs:
            failures.append(
                "Duplicate HTTP methods on routes: " + "; ".join(duplicate_method_pairs)
            )

        route_prefixes = set()
        for path in normalized_paths:
            if path == "/":
                continue
            prefix = "/" + path.strip("/").split("/")[0]
            route_prefixes.add(prefix)

        missing_prefixes = sorted(EXPECTED_ROUTER_PREFIXES - route_prefixes)
        if missing_prefixes:
            failures.append("Missing router prefixes: " + ", ".join(missing_prefixes))
    except Exception as exc:
        failures.append(str(exc))

    add_outcome(report, "Routers", not failures, failures or None)


def check_requirements(report: QualityReport) -> None:
    failures: list[str] = []
    declared = parse_requirement_names(REQUIREMENTS_FILE)
    if not declared:
        failures.append(f"Could not read requirements from {REQUIREMENTS_FILE}")
        add_outcome(report, "Requirements", False, failures)
        return

    used_requirements: set[str] = set()
    for path in collect_backend_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module_name = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".", 1)[0]
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module.split(".", 1)[0]
            if not module_name:
                continue
            requirement_name = IMPORT_TO_REQUIREMENT.get(module_name)
            if requirement_name:
                used_requirements.add(requirement_name)

    missing = sorted(req for req in used_requirements if req.lower() not in declared)
    if missing:
        failures.append("Missing packages in requirements.txt: " + ", ".join(missing))

    add_outcome(report, "Requirements", not failures, failures or None)


def check_environment(report: QualityReport) -> None:
    failures: list[str] = []
    env_values = read_env_file(ENV_FILE)
    if not ENV_FILE.exists():
        failures.append(f"Missing env file: {ENV_FILE}")
    else:
        for key in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER"):
            if not env_values.get(key):
                failures.append(f"Missing .env key: {key}")

        allow_empty = env_values.get("DB_ALLOW_EMPTY_PASSWORD", "false").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        has_password = bool(env_values.get("DB_PASSWORD"))
        if not has_password and not allow_empty:
            failures.append("DB_PASSWORD missing and DB_ALLOW_EMPTY_PASSWORD is not enabled")

    add_outcome(report, "Environment", not failures, failures or None)


def check_project_structure(report: QualityReport) -> None:
    failures: list[str] = []
    for directory in EXPECTED_PROJECT_DIRS:
        path = PROJECT_ROOT / directory
        if not path.is_dir():
            failures.append(f"Missing directory: {directory}/")

    for file_name in EXPECTED_PROJECT_FILES:
        path = PROJECT_ROOT / file_name
        if not path.is_file():
            failures.append(f"Missing file: {file_name}")

    backend_app = BACKEND_DIR / "app"
    if not backend_app.is_dir():
        failures.append("Missing directory: backend/app/")

    add_outcome(report, "Project Structure", not failures, failures or None)


def check_project_files(report: QualityReport) -> None:
    failures: list[str] = []
    for file_name in REQUIRED_PROJECT_DOCS:
        path = PROJECT_ROOT / file_name
        if not path.is_file():
            failures.append(f"Missing required project file: {file_name}")
        elif path.stat().st_size == 0:
            failures.append(f"Empty required project file: {file_name}")

    add_outcome(report, "Project Files", not failures, failures or None)


def check_code_markers(report: QualityReport) -> None:
    markers: list[str] = []
    for root in SCAN_MARKERS_DIRS:
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                match = MARKER_PATTERN.search(line)
                if match:
                    relative = path.relative_to(PROJECT_ROOT)
                    markers.append(f"{relative}:{line_number} {match.group(1)}")

    max_points = CHECK_POINTS["Code Markers"]
    if not markers:
        add_outcome(report, "Code Markers", True, status="PASS", points=max_points)
        return

    deduction = min(max_points, 2 * len(markers))
    points = max(0, max_points - deduction)
    for marker in markers:
        report.warnings.append(f"Code marker found: {marker}")

    add_outcome(
        report,
        "Code Markers",
        True,
        details=[f"Found {len(markers)} TODO/FIXME marker(s)"],
        hard_fail=False,
        status="WARN",
        points=points,
    )


def check_circular_imports(report: QualityReport) -> None:
    failures: list[str] = []
    graph: dict[str, set[str]] = {}

    for path in collect_backend_python_files():
        if path.name == "__init__.py" and path.parent == BACKEND_DIR / "app":
            module_name = "app"
        else:
            module_name = module_name_for_path(path)
        graph.setdefault(module_name, set())
        for imported in collect_app_imports(path):
            graph[module_name].add(imported)

    cycles = find_import_cycles(graph)
    if cycles:
        for cycle in cycles:
            failures.append("Circular import detected: " + " -> ".join(cycle))

    critical_modules = [
        "app.config",
        "app.database",
        "app.security",
        "app.models.models",
        "app.main",
    ]
    for module_name in critical_modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    add_outcome(report, "Circular Imports", not failures, failures or None)


def check_health_check(report: QualityReport) -> None:
    passed, details = run_subprocess_check("health_check.py")
    add_outcome(report, "Health Check", passed, details or None)


def check_dev_check(report: QualityReport) -> None:
    passed, details = run_subprocess_check("dev_check.py")
    add_outcome(report, "Dev Check", passed, details or None)


def check_git_status(report: QualityReport) -> None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        report.git_status = "UNKNOWN"
        report.warnings.append("Git executable not found; git status skipped")
        return

    if result.returncode != 0:
        report.git_status = "UNKNOWN"
        report.warnings.append("Git status command failed")
        if result.stderr.strip():
            report.warnings.append(result.stderr.strip())
        return

    if result.stdout.strip():
        report.git_status = "MODIFIED"
        for line in result.stdout.strip().splitlines():
            report.warnings.append(f"Git change: {line.strip()}")
    else:
        report.git_status = "CLEAN"


def print_summary_line(name: str, status: str) -> None:
    dots = "." * max(1, 22 - len(name))
    print(f"{name} {dots} {status}")


def print_report(report: QualityReport) -> None:
    print("==================================")
    print(" FAIR CRM QUALITY CHECK")
    print("==================================")
    print()

    for outcome in report.outcomes:
        print_summary_line(outcome.name, outcome.status)

    print_summary_line("Git Status", report.git_status)
    print()

    print("Quality Score")
    print()
    print(f"{report.score} / 100")
    print()
    print("Warnings")
    print()
    if report.warnings:
        for warning in report.warnings:
            print(f"- {warning}")
    else:
        print("(none)")
    print()

    if report.ready:
        print("READY FOR COMMIT")
    else:
        print("NOT READY FOR COMMIT")
        print()
        print("Failures")
        print()
        for outcome in report.hard_failures:
            print(f"- {outcome.name}")
            for detail in outcome.details:
                print(f"  {detail}")


def main() -> int:
    report = QualityReport()

    check_python_compile(report)
    check_imports(report)
    check_fastapi(report)
    check_models(report)
    check_routers(report)
    check_requirements(report)
    check_environment(report)
    check_project_structure(report)
    check_project_files(report)
    check_code_markers(report)
    check_circular_imports(report)
    check_health_check(report)
    check_dev_check(report)
    check_git_status(report)

    print_report(report)
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
