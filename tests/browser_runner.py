"""Run a Node Playwright scenario against a Django live server."""

import os
import subprocess
from pathlib import Path

BROWSER_SCRIPTS = Path(__file__).parent / "browser"


def run_node_scenario(
    script: str,
    live_server_url: str,
    *,
    extra_env: dict[str, object] | None = None,
    timeout: int = 90,
) -> None:
    """Run ``tests/browser/<script>`` and fail with its full output on error.

    Output is decoded as UTF-8 explicitly so a Windows locale cannot hide the
    real browser diagnostics.
    """
    environment = os.environ.copy()
    environment["NULDL_LIVE_SERVER_URL"] = live_server_url
    environment.update({key: str(value) for key, value in (extra_env or {}).items()})
    result = subprocess.run(
        ["node", str(BROWSER_SCRIPTS / script)],
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=timeout,
    )
    output = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, output
