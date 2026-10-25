import subprocess

import pytest

from scripts.verify_phase_1 import run


def test_quality_gate_propagates_command_failures(monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(7, ["synthetic-failure"])

    monkeypatch.setattr(subprocess, "run", fail)

    with pytest.raises(subprocess.CalledProcessError) as error:
        run(["synthetic-failure"])

    assert error.value.returncode == 7
