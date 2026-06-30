"""FAIR CRM development check.

Run from project root:
    python scripts/dev_check.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_check(name: str, command: list[str]) -> bool:
    print(f"\n{name}")
    print("-" * 42)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
    )

    if result.returncode == 0:
        print(f"[OK] {name}")
        return True

    print(f"[FAIL] {name}")
    return False


def main() -> int:
    print("FAIR CRM DEV CHECK")
    print("=" * 42)
    print(f"Project root: {PROJECT_ROOT}")

    checks = [
        (
            "Python syntax compile",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "backend",
                "scripts",
            ],
        ),
        (
            "Health check",
            [
                sys.executable,
                "scripts/health_check.py",
            ],
        ),
    ]

    results = [run_check(name, command) for name, command in checks]

    print()
    if all(results):
        print("Result: READY")
        return 0

    print("Result: NOT READY")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())