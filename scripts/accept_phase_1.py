"""Run Phase 1 acceptance from a temporary clean Python environment."""

try:
    from scripts._acceptance import run_acceptance
except ModuleNotFoundError:  # Direct execution places scripts/ first on sys.path.
    from _acceptance import run_acceptance

GATE_SCRIPT = "scripts/verify_phase_1.py"
SMOKE_SCRIPTS = ("tests/browser/development-server-smoke.mjs",)


def main() -> None:
    run_acceptance(1, gate_script=GATE_SCRIPT, smoke_scripts=SMOKE_SCRIPTS)


if __name__ == "__main__":
    main()
