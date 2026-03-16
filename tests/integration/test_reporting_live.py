from __future__ import annotations

import os

import pytest

from play_insights.reporting_client import DeveloperReportingClient


@pytest.mark.live_api
def test_query_crash_anr_live(require_live_env: None) -> None:
    package = os.getenv("PLAY_PACKAGE_NAME", "")
    client = DeveloperReportingClient(package_name=package)
    crash_rows = client.query_crash_rate(days=3)
    anr_rows = client.query_anr_rate(days=3)

    assert isinstance(crash_rows, list)
    assert isinstance(anr_rows, list)
    for row in crash_rows + anr_rows:
        assert row.metric_set
        assert row.package_name == package
        assert row.date


@pytest.mark.live_api
def test_query_error_issues_live(require_live_env: None) -> None:
    package = os.getenv("PLAY_PACKAGE_NAME", "")
    client = DeveloperReportingClient(package_name=package)
    rows = client.query_error_issues(days=3)
    assert isinstance(rows, list)

