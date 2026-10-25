"""Run the repeatable Phase 1 quality and security gate."""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NPM = "npm.cmd" if os.name == "nt" else "npm"


def run(command: list[str], *, environment: dict[str, str] | None = None) -> None:
    """Run one gate command and propagate every non-zero result."""
    print(f"\n> {' '.join(command)}", flush=True)
    subprocess.run(
        command,
        check=True,
        cwd=PROJECT_ROOT,
        env=environment,
    )


def main() -> None:
    run([NPM, "ci", "--ignore-scripts"])
    run([NPM, "exec", "playwright", "--", "install", "chromium"])
    run([NPM, "run", "static:build"])
    run([NPM, "run", "assets:check"])
    run([NPM, "run", "css:watch:smoke"])

    run([sys.executable, "-m", "ruff", "check", "."])
    run([sys.executable, "-m", "ruff", "format", "--check", "."])
    run(
        [
            sys.executable,
            "manage.py",
            "makemigrations",
            "--check",
            "--dry-run",
        ]
    )
    run([sys.executable, "manage.py", "check"])

    run([sys.executable, "-m", "coverage", "erase"])
    run(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-m",
            "pytest",
            "--create-db",
        ]
    )
    run([sys.executable, "-m", "coverage", "report"])

    production_environment = os.environ.copy()
    production_environment["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    production_environment["DJANGO_SECRET_KEY"] = (
        "phase-1-deploy-check-only-7vQ2!kP9#xM4@cR8$zT6&wN3"
    )
    run(
        [
            sys.executable,
            "manage.py",
            "check",
            "--deploy",
            "--fail-level",
            "WARNING",
        ],
        environment=production_environment,
    )
    run(
        [sys.executable, "manage.py", "collectstatic", "--noinput", "--verbosity", "0"],
        environment=production_environment,
    )

    print("\nPhase 1 quality and security gate passed.", flush=True)


if __name__ == "__main__":
    main()
