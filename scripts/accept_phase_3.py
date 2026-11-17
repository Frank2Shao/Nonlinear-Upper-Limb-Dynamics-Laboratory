"""Run Phase 3 acceptance from a temporary clean Python environment."""

try:
    from scripts._acceptance import run_acceptance
except ModuleNotFoundError:  # Direct execution places scripts/ first on sys.path.
    from _acceptance import run_acceptance

GATE_SCRIPT = "scripts/verify_project.py"
SMOKE_SCRIPTS = (
    "tests/browser/phase2-development-smoke.mjs",
    "tests/browser/phase3-development-smoke.mjs",
)


def main() -> None:
    run_acceptance(3, gate_script=GATE_SCRIPT, smoke_scripts=SMOKE_SCRIPTS)


if __name__ == "__main__":
    main()
