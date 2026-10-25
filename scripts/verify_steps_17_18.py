"""Run the atomic Step 17–18 acceptance gate."""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NPM = "npm.cmd" if os.name == "nt" else "npm"
FORMAT_TARGETS = [
    "apps/accounts/forms.py",
    "config/settings/base.py",
    "config/settings/production.py",
    "scripts/verify_steps_17_18.py",
    "tests/test_authentication_browser.py",
    "tests/test_authentication_templates.py",
    "tests/test_environment_settings.py",
    "tests/test_global_templates.py",
    "tests/test_static_assets.py",
]


def run(command: list[str], *, environment: dict[str, str] | None = None) -> None:
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
    run([sys.executable, "-m", "pytest"])
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
    run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "manage.py",
            "config",
            "apps",
            "tests",
            "scripts",
        ]
    )
    run(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--check",
            *FORMAT_TARGETS,
        ]
    )

    production_environment = os.environ.copy()
    production_environment["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    run(
        [sys.executable, "manage.py", "collectstatic", "--noinput", "--verbosity", "0"],
        environment=production_environment,
    )

    print("\nStep 17–18 acceptance gate passed.", flush=True)


if __name__ == "__main__":
    main()
