from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from play_insights.models import VitalsRecord


def _make_api_row(metric_value: float = 0.35, version: str = "20252") -> dict:
    return {
        "startTime": {"year": 2026, "month": 3, "day": 1},
        "metrics": [{"decimalValue": {"value": str(metric_value)}}],
        "dimensions": [
            {"dimension": "versionCode", "int64Value": version},
            {"dimension": "countryCode", "stringValue": "BR"},
            {"dimension": "deviceModel", "stringValue": "samsung/a25x"},
            {"dimension": "apiLevel", "int64Value": "35"},
        ],
    }


@patch("play_insights.reporting_client.refresh_access_token")
@patch("play_insights.reporting_client.DeveloperReportingClient._post_query")
def test_query_slow_rendering_structure(mock_post, mock_auth) -> None:
    mock_auth.return_value = MagicMock(token="fake-token")
    mock_post.return_value = {"rows": [_make_api_row(0.40), _make_api_row(0.35)]}

    from play_insights.reporting_client import DeveloperReportingClient
    client = DeveloperReportingClient.__new__(DeveloperReportingClient)
    client.package_name = "com.test.app"
    client.timeout_seconds = 30
    client._token = "fake-token"

    result = client.query_slow_rendering(days=7)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(r, VitalsRecord) for r in result)
    assert all(r.metric_set == "slowRenderingRateMetricSet" for r in result)


@patch("play_insights.reporting_client.refresh_access_token")
@patch("play_insights.reporting_client.DeveloperReportingClient._post_query")
def test_slow_rendering_zero_rows(mock_post, mock_auth) -> None:
    mock_auth.return_value = MagicMock(token="fake-token")
    mock_post.return_value = {"rows": []}

    from play_insights.reporting_client import DeveloperReportingClient
    client = DeveloperReportingClient.__new__(DeveloperReportingClient)
    client.package_name = "com.test.app"
    client.timeout_seconds = 30
    client._token = "fake-token"

    result = client.query_slow_rendering(days=7)
    assert result == []


@patch("play_insights.reporting_client.refresh_access_token")
@patch("play_insights.reporting_client.DeveloperReportingClient._post_query")
def test_query_slow_start_structure(mock_post, mock_auth) -> None:
    mock_auth.return_value = MagicMock(token="fake-token")
    mock_post.return_value = {"rows": [_make_api_row(0.25)]}

    from play_insights.reporting_client import DeveloperReportingClient
    client = DeveloperReportingClient.__new__(DeveloperReportingClient)
    client.package_name = "com.test.app"
    client.timeout_seconds = 30
    client._token = "fake-token"

    result = client.query_slow_start(days=7)
    assert len(result) == 1
    assert result[0].metric_set == "slowStartRateMetricSet"


@pytest.mark.live_api
def test_slow_rendering_live() -> None:
    from play_insights.reporting_client import DeveloperReportingClient
    pkg = os.environ.get("PLAY_PACKAGE_NAME", "br.com.quero2ingressos")
    client = DeveloperReportingClient(package_name=pkg)
    result = client.query_slow_rendering(days=7)
    print(f"\nSlow rendering records: {len(result)}")
    assert isinstance(result, list)


@pytest.mark.live_api
def test_slow_start_live() -> None:
    from play_insights.reporting_client import DeveloperReportingClient
    pkg = os.environ.get("PLAY_PACKAGE_NAME", "br.com.quero2ingressos")
    client = DeveloperReportingClient(package_name=pkg)
    result = client.query_slow_start(days=7)
    print(f"\nSlow start records: {len(result)}")
    assert isinstance(result, list)
