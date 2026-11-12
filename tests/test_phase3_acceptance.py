import subprocess
from pathlib import Path

import pytest

import scripts.accept_phase_3 as acceptance
from scripts.accept_phase_3 import run, stop_process

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase3_acceptance_runner_propagates_command_failures(monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(13, ["synthetic-failure"])

    monkeypatch.setattr(subprocess, "run", fail)

    with pytest.raises(subprocess.CalledProcessError) as error:
        run(["synthetic-failure"])

    assert error.value.returncode == 13


def test_phase3_acceptance_stops_a_running_server():
    class RunningProcess:
        def __init__(self):
            self.terminated = False

        def poll(self):
            return None if not self.terminated else 0

        def terminate(self):
            self.terminated = True

        def wait(self, *, timeout):
            return 0

    process = RunningProcess()

    stop_process(process)

    assert process.terminated is True


def test_phase3_acceptance_runs_clean_gate_and_both_server_smokes(monkeypatch):
    commands = []

    class RunningProcess:
        pass

    monkeypatch.setattr(acceptance.shutil, "which", lambda executable: "uv")
    monkeypatch.setattr(
        acceptance,
        "environment_python",
        lambda environment_directory: Path("phase3-python"),
    )
    monkeypatch.setattr(
        acceptance,
        "run",
        lambda command, *, environment=None: commands.append(command),
    )
    monkeypatch.setattr(
        acceptance.subprocess,
        "Popen",
        lambda *args, **kwargs: RunningProcess(),
    )
    monkeypatch.setattr(acceptance, "wait_for_server", lambda process, url: None)
    monkeypatch.setattr(acceptance, "stop_process", lambda process: None)

    acceptance.main()

    assert commands[0] == [
        "docker",
        "compose",
        "up",
        "-d",
        "--wait",
        "postgres",
    ]
    assert ["uv", "sync", "--locked"] in commands
    assert ["phase3-python", "manage.py", "migrate", "--noinput"] in commands
    assert ["phase3-python", "scripts/verify_project.py"] in commands
    assert ["node", "tests/browser/phase2-development-smoke.mjs"] in commands
    assert ["node", "tests/browser/phase3-development-smoke.mjs"] in commands


def test_readme_documents_phase3_acceptance_and_manual_review():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    normalized_readme = readme.casefold()

    required_content = (
        "scripts\\accept_phase_3.py",
        "scripts\\verify_project.py",
        "Edit profile",
        "Preview profile",
        "Publish profile",
        "Unpublish",
        "Members",
        "Admin hide/unhide",
        "temporary media",
        "synthetic",
        "Production media storage remains unresolved",
    )
    for content in required_content:
        assert content.casefold() in normalized_readme
