from __future__ import annotations

import os
import subprocess
import sys

import pytest


@pytest.mark.live_api
@pytest.mark.warehouse
def test_cli_ingest_and_analyze_live(require_live_env: None) -> None:
    if os.getenv("RUN_E2E_LIVE", "false").lower() != "true":
        pytest.skip("Set RUN_E2E_LIVE=true to run end-to-end CLI test.")

    ingest = subprocess.run(
        [sys.executable, "-m", "play_insights", "ingest", "--days", "3"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert ingest.returncode == 0, ingest.stderr or ingest.stdout

    analyze = subprocess.run(
        [sys.executable, "-m", "play_insights", "analyze", "--window", "7d"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert analyze.returncode == 0, analyze.stderr or analyze.stdout

