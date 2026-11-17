import importlib
import subprocess
import sys
from pathlib import Path

import pytest

import scripts._acceptance as acceptance

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKER_UP = ["docker", "compose", "up", "-d", "--wait", "postgres"]
PHASE2_SMOKE = "tests/browser/phase2-development-smoke.mjs"
PHASE3_SMOKE = "tests/browser/phase3-development-smoke.mjs"
PHASE4_SMOKE = "tests/browser/phase4-development-smoke.mjs"

PHASE_EXPECTATIONS = {
    1: ("scripts/verify_phase_1.py", ["tests/browser/development-server-smoke.mjs"]),
    2: ("scripts/verify_project.py", [PHASE2_SMOKE]),
    3: ("scripts/verify_project.py", [PHASE2_SMOKE, PHASE3_SMOKE]),
    4: ("scripts/verify_project.py", [PHASE2_SMOKE, PHASE3_SMOKE, PHASE4_SMOKE]),
}


class FakeServer:
    def __init__(self):
        self.terminated = False
        self.killed = False

    def poll(self):
        return 0 if self.terminated or self.killed else None

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True

    def wait(self, *, timeout):
        return 0


@pytest.fixture
def recorded_acceptance(monkeypatch):
    """Replace every external effect of run_acceptance and record commands."""
    commands = []
    servers = []

    def fake_popen(*args, **kwargs):
        servers.append(FakeServer())
        return servers[-1]

    monkeypatch.setattr(acceptance.shutil, "which", lambda executable: "uv")
    monkeypatch.setattr(
        acceptance,
        "environment_python",
        lambda environment_directory: Path("clean-python"),
    )
    monkeypatch.setattr(
        acceptance,
        "run",
        lambda command, *, environment=None: commands.append(command),
    )
    monkeypatch.setattr(acceptance.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(acceptance, "wait_for_server", lambda process, url: None)
    return commands, servers


@pytest.mark.parametrize("phase", sorted(PHASE_EXPECTATIONS))
def test_phase_acceptance_runs_locked_install_gate_and_server_smokes(
    phase, recorded_acceptance
):
    commands, servers = recorded_acceptance
    gate_script, smoke_scripts = PHASE_EXPECTATIONS[phase]
    module = importlib.import_module(f"scripts.accept_phase_{phase}")

    module.main()

    assert commands == [
        DOCKER_UP,
        ["uv", "sync", "--locked"],
        ["clean-python", "manage.py", "migrate", "--noinput"],
        ["clean-python", gate_script],
        *(["node", smoke] for smoke in smoke_scripts),
    ]
    assert len(servers) == 1
    assert servers[0].terminated is True


def test_acceptance_prints_server_log_and_stops_server_when_a_smoke_fails(
    monkeypatch, recorded_acceptance, capsys
):
    _, servers = recorded_acceptance

    def failing_run(command, *, environment=None):
        if command[0] == "node":
            raise subprocess.CalledProcessError(17, command)

    def popen_with_log(*args, stdout, **kwargs):
        stdout.write("synthetic server log line\n")
        servers.append(FakeServer())
        return servers[-1]

    monkeypatch.setattr(acceptance, "run", failing_run)
    monkeypatch.setattr(acceptance.subprocess, "Popen", popen_with_log)

    with pytest.raises(subprocess.CalledProcessError) as error:
        acceptance.run_acceptance(
            9, gate_script="scripts/verify_project.py", smoke_scripts=["smoke.mjs"]
        )

    assert error.value.returncode == 17
    assert "synthetic server log line" in capsys.readouterr().out
    assert servers[0].terminated is True


def test_acceptance_requires_uv(monkeypatch):
    monkeypatch.setattr(acceptance.shutil, "which", lambda executable: None)

    with pytest.raises(RuntimeError, match="uv command is required"):
        acceptance.run_acceptance(9, gate_script="gate.py", smoke_scripts=[])


def test_stop_process_terminates_a_running_server():
    server = FakeServer()

    acceptance.stop_process(server)

    assert server.terminated is True
    assert server.killed is False


def test_stop_process_kills_a_server_that_ignores_terminate():
    class StubbornServer(FakeServer):
        def poll(self):
            return None

        def wait(self, *, timeout):
            if not self.killed:
                raise subprocess.TimeoutExpired("runserver", timeout)
            return 0

    server = StubbornServer()

    acceptance.stop_process(server)

    assert server.killed is True


@pytest.mark.parametrize("phase", sorted(PHASE_EXPECTATIONS))
def test_phase_script_imports_when_run_directly(phase):
    # README runs `python scripts\accept_phase_N.py`, which puts scripts/ first
    # on sys.path instead of the project root.
    result = subprocess.run(
        [sys.executable, "-c", f"import accept_phase_{phase}"],
        capture_output=True,
        check=False,
        cwd=PROJECT_ROOT / "scripts",
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("phase", sorted(PHASE_EXPECTATIONS))
def test_readme_documents_how_to_run_each_phase_acceptance(phase):
    # Only the runnable entry points are checked; README wording is reviewed by
    # people, not pinned by tests.
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    gate_script, _ = PHASE_EXPECTATIONS[phase]

    for script in (f"scripts/accept_phase_{phase}.py", gate_script):
        windows_path = script.replace("/", "\\")
        assert windows_path in readme, f"README must show how to run {script}."
