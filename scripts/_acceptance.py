"""Shared clean-environment acceptance flow used by every phase entry point."""

import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path

try:
    from scripts.verify_project import PROJECT_ROOT, run
except ModuleNotFoundError:  # Direct execution places scripts/ first on sys.path.
    from verify_project import PROJECT_ROOT, run

__all__ = [
    "available_loopback_port",
    "environment_python",
    "run",
    "run_acceptance",
    "stop_process",
    "wait_for_server",
]


def environment_python(environment_directory: Path) -> Path:
    if os.name == "nt":
        return environment_directory / "Scripts" / "python.exe"
    return environment_directory / "bin" / "python"


def available_loopback_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def wait_for_server(
    process: subprocess.Popen[str],
    url: str,
    *,
    timeout: float = 30,
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeError(
                f"Django development server exited early with status {return_code}."
            )
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.2)
    raise TimeoutError(f"Django development server did not become ready: {url}")


def stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def run_acceptance(
    phase: int,
    *,
    gate_script: str,
    smoke_scripts: Sequence[str],
) -> None:
    """Build a locked temporary environment, run the gate, then smoke a real server.

    The server log is printed whenever a smoke fails, and the server is always
    stopped before the temporary environment is removed.
    """
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError(
            "The uv command is required for clean-environment acceptance."
        )

    run(["docker", "compose", "up", "-d", "--wait", "postgres"])

    with tempfile.TemporaryDirectory(
        prefix=f"nuldl-phase-{phase}-"
    ) as temporary_directory:
        environment_directory = Path(temporary_directory) / ".venv"
        clean_environment = os.environ.copy()
        clean_environment.pop("VIRTUAL_ENV", None)
        clean_environment["UV_PROJECT_ENVIRONMENT"] = str(environment_directory)

        run([uv, "sync", "--locked"], environment=clean_environment)
        python = str(environment_python(environment_directory))
        run(
            [python, "manage.py", "migrate", "--noinput"],
            environment=clean_environment,
        )
        run([python, gate_script], environment=clean_environment)

        port = available_loopback_port()
        base_url = f"http://127.0.0.1:{port}"
        browser_environment = clean_environment.copy()
        browser_environment["NULDL_LIVE_SERVER_URL"] = base_url

        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as server_log:
            server = subprocess.Popen(
                [
                    python,
                    "manage.py",
                    "runserver",
                    f"127.0.0.1:{port}",
                    "--noreload",
                ],
                cwd=PROJECT_ROOT,
                env=clean_environment,
                stdout=server_log,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            )
            try:
                wait_for_server(server, base_url)
                for smoke_script in smoke_scripts:
                    run(["node", smoke_script], environment=browser_environment)
            except Exception:
                server_log.seek(0)
                print(server_log.read(), flush=True)
                raise
            finally:
                stop_process(server)

    print(f"\nPhase {phase} end-to-end acceptance passed.", flush=True)
