import subprocess
from pathlib import Path

import pytest

from scripts.accept_phase_2 import run, stop_process

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase2_acceptance_runner_propagates_command_failures(monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(11, ["synthetic-failure"])

    monkeypatch.setattr(subprocess, "run", fail)

    with pytest.raises(subprocess.CalledProcessError) as error:
        run(["synthetic-failure"])

    assert error.value.returncode == 11


def test_phase2_acceptance_stops_a_running_server():
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


def test_readme_documents_phase2_acceptance_and_manual_review():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    normalized_readme = readme.casefold()

    required_content = (
        "scripts\\accept_phase_2.py",
        "scripts\\verify_project.py",
        "Home",
        "About",
        "Beginners & Safety",
        "Draft Risk Notice",
        "@nuldl_armwrestlingclub",
        "1 December 2026",
        "3:00–7:00 pm",
        "Venue details to be confirmed",
        "University branding remains excluded",
    )
    for content in required_content:
        assert content.casefold() in normalized_readme
