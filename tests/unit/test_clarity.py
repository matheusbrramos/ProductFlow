"""Unit tests for Clarity integration: client, analysis, repo methods."""
from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import requests

from play_insights.clarity_analysis import (
    KPI_THRESHOLDS,
    _is_alert,
    _pct_delta,
    _trend_direction,
    calculate_kpis,
    calculate_trend,
    compute_baseline,
    cross_reference_devices,
    should_recompute_baseline,
)
from play_insights.clarity_client import ClarityClient, MAX_REQUESTS_PER_RUN
from play_insights.duckdb_repo import DuckDBRepository
from play_insights.models import ClarityKPISnapshot, ClarityRow


# ─── Fixtures ────────────────────────────────────────────────────────────────

def _make_row(**kwargs) -> ClarityRow:
    defaults = dict(
        project_id="proj1",
        fetch_date=date.today().isoformat(),
        num_of_days=3,
        dim1_name="Device",
        dim1_value="Mobile",
        dim2_name=None,
        dim2_value=None,
        dim3_name=None,
        dim3_value=None,
        sessions=1000,
        users=800,
        scroll_depth_pct=55.0,
        engagement_time_ms=90_000.0,
        dead_click_count=50,
        rage_click_count=20,
        error_click_count=10,
        script_error_count=5,
        lcp_ms=2_200.0,
        inp_ms=150.0,
        cls=0.05,
    )
    defaults.update(kwargs)
    return ClarityRow(**defaults)


def _make_snapshot(**kwargs) -> ClarityKPISnapshot:
    defaults = dict(
        snapshot_date=date.today().isoformat(),
        snapshot_type="daily",
        period_days=3,
        total_sessions=1000,
        total_users=800,
        dead_click_rate=0.05,
        rage_click_rate=0.02,
        error_click_rate=0.01,
        script_error_rate=0.005,
        avg_scroll_depth_pct=55.0,
        avg_engagement_time_ms=90_000.0,
        avg_lcp_ms=2_200.0,
        avg_inp_ms=150.0,
        avg_cls=0.05,
        computed_at="2026-01-01T00:00:00+00:00",
    )
    defaults.update(kwargs)
    return ClarityKPISnapshot(**defaults)


@pytest.fixture
def repo(tmp_path) -> DuckDBRepository:
    return DuckDBRepository(db_path=str(tmp_path / "test.duckdb"))


# ─── calculate_kpis ──────────────────────────────────────────────────────────

def test_calculate_kpis_basic() -> None:
    rows = [_make_row(sessions=1000, rage_click_count=40)]
    snap = calculate_kpis(rows)
    assert snap.total_sessions == 1000
    assert snap.rage_click_rate == pytest.approx(0.04, rel=1e-4)


def test_calculate_kpis_zero_sessions() -> None:
    rows = [_make_row(sessions=0, rage_click_count=0)]
    snap = calculate_kpis(rows)
    assert snap.rage_click_rate == 0.0


def test_calculate_kpis_multiple_rows() -> None:
    rows = [
        _make_row(sessions=600, rage_click_count=12, lcp_ms=2_000.0),
        _make_row(sessions=400, rage_click_count=8, lcp_ms=3_000.0),
    ]
    snap = calculate_kpis(rows)
    assert snap.total_sessions == 1000
    assert snap.rage_click_rate == pytest.approx(0.02, rel=1e-4)
    # LCP weighted avg: (2000*600 + 3000*400) / 1000 = 2400
    assert snap.avg_lcp_ms == pytest.approx(2400.0, rel=1e-3)


def test_calculate_kpis_none_values_ignored() -> None:
    rows = [_make_row(lcp_ms=None, sessions=500, rage_click_count=10)]
    snap = calculate_kpis(rows)
    assert snap.avg_lcp_ms == 0.0  # no valid lcp values


# ─── calculate_trend ─────────────────────────────────────────────────────────

def test_calculate_trend_no_previous_no_baseline() -> None:
    current = _make_snapshot(rage_click_rate=0.03)
    report = calculate_trend(current, None, None)
    rage = next(t for t in report.kpi_trends if t.kpi_name == "rage_click_rate")
    assert rage.previous_value is None
    assert rage.trend_vs_previous == "N/A"


def test_calculate_trend_vs_previous_worsening() -> None:
    current = _make_snapshot(rage_click_rate=0.06)  # above alert threshold 0.04
    previous = _make_snapshot(rage_click_rate=0.02)
    report = calculate_trend(current, previous, None)
    rage = next(t for t in report.kpi_trends if t.kpi_name == "rage_click_rate")
    assert "piorando" in rage.trend_vs_previous
    assert rage.is_alert is True
    assert len(report.alerts) >= 1


def test_calculate_trend_stable_within_threshold() -> None:
    current = _make_snapshot(rage_click_rate=0.021)
    previous = _make_snapshot(rage_click_rate=0.020)
    report = calculate_trend(current, previous, None)
    rage = next(t for t in report.kpi_trends if t.kpi_name == "rage_click_rate")
    assert rage.trend_vs_previous == "→"


def test_calculate_trend_with_baseline() -> None:
    current = _make_snapshot(rage_click_rate=0.03)
    baseline_rows = [{"kpi_name": "rage_click_rate", "baseline_value": 0.025}]
    report = calculate_trend(current, None, baseline_rows)
    assert report.baseline_available is True
    rage = next(t for t in report.kpi_trends if t.kpi_name == "rage_click_rate")
    assert rage.baseline_value == pytest.approx(0.025)


# ─── _pct_delta ──────────────────────────────────────────────────────────────

def test_pct_delta_basic() -> None:
    assert _pct_delta(0.03, 0.02) == pytest.approx(50.0)


def test_pct_delta_zero_reference() -> None:
    assert _pct_delta(0.03, 0.0) is None


# ─── _is_alert ────────────────────────────────────────────────────────────────

def test_is_alert_lower_is_better_over_threshold() -> None:
    assert _is_alert("rage_click_rate", 0.05) is True


def test_is_alert_lower_is_better_under_threshold() -> None:
    assert _is_alert("rage_click_rate", 0.01) is False


def test_is_alert_higher_is_better_under_threshold() -> None:
    assert _is_alert("avg_scroll_depth_pct", 25.0) is True  # alert < 30%


def test_is_alert_higher_is_better_over_threshold() -> None:
    assert _is_alert("avg_scroll_depth_pct", 60.0) is False


# ─── compute_baseline ────────────────────────────────────────────────────────

def test_compute_baseline_median() -> None:
    rows = [
        {"rage_click_rate": 0.01},
        {"rage_click_rate": 0.02},
        {"rage_click_rate": 0.03},
        {"rage_click_rate": 0.10},  # outlier
        {"rage_click_rate": 0.03},
    ]
    result = compute_baseline(rows)
    rage = next(r for r in result if r["kpi_name"] == "rage_click_rate")
    # Sorted: 0.01, 0.02, 0.03, 0.03, 0.10 → median = 0.03
    assert rage["baseline_value"] == pytest.approx(0.03)
    assert rage["computed_from_days"] == 5


def test_compute_baseline_empty() -> None:
    assert compute_baseline([]) == []


# ─── should_recompute_baseline ───────────────────────────────────────────────

def test_should_recompute_no_baseline_enough_days() -> None:
    assert should_recompute_baseline([], available_days=7) is True


def test_should_recompute_no_baseline_not_enough_days() -> None:
    assert should_recompute_baseline([], available_days=5) is False


def test_should_not_recompute_baseline_exists() -> None:
    existing = [{"kpi_name": "rage_click_rate", "baseline_value": 0.02}]
    assert should_recompute_baseline(existing, available_days=30) is False


# ─── cross_reference_devices ─────────────────────────────────────────────────

def test_cross_reference_basic() -> None:
    clarity_rows = [
        {"dim1_value": "Samsung Galaxy A25", "sessions": 1000, "rage_click_count": 80},
    ]
    play_vitals = [
        {"device_model": "samsung/a25x", "metric_value": 0.57},
    ]
    refs = cross_reference_devices(clarity_rows, play_vitals)
    assert len(refs) == 1
    assert refs[0].device_name == "Samsung Galaxy A25"
    assert refs[0].crash_rate_play is not None
    assert refs[0].rage_click_rate_clarity == pytest.approx(0.08)
    assert refs[0].combined_risk_score > 0


def test_cross_reference_no_match() -> None:
    clarity_rows = [{"dim1_value": "iPhone", "sessions": 500, "rage_click_count": 10}]
    play_vitals = [{"device_model": "samsung/a25x", "metric_value": 0.57}]
    refs = cross_reference_devices(clarity_rows, play_vitals)
    # iPhone won't match samsung — crash_rate_play should be None
    assert refs[0].crash_rate_play is None


def test_cross_reference_empty() -> None:
    assert cross_reference_devices([], []) == []


# ─── DuckDB repo: Clarity tables ─────────────────────────────────────────────

def test_upsert_clarity_raw(repo: DuckDBRepository) -> None:
    rows = [_make_row()]
    written = repo.upsert_clarity_raw(rows)
    assert written == 1


def test_upsert_clarity_raw_deduplicates(repo: DuckDBRepository) -> None:
    row = _make_row()
    repo.upsert_clarity_raw([row])
    repo.upsert_clarity_raw([row])  # same row again
    result = repo.query("SELECT COUNT(*) AS cnt FROM clarity_raw")
    assert result[0]["cnt"] == 1


def test_upsert_clarity_kpis_daily(repo: DuckDBRepository) -> None:
    snap = _make_snapshot()
    written = repo.upsert_clarity_kpis_daily(snap)
    assert written == 1
    rows = repo.query("SELECT * FROM clarity_kpis_daily")
    assert len(rows) == 1
    assert rows[0]["rage_click_rate"] == pytest.approx(0.02)


def test_upsert_clarity_kpis_daily_deduplicates(repo: DuckDBRepository) -> None:
    snap = _make_snapshot()
    repo.upsert_clarity_kpis_daily(snap)
    snap2 = _make_snapshot(rage_click_rate=0.05)  # same date/type, updated value
    repo.upsert_clarity_kpis_daily(snap2)
    rows = repo.query("SELECT * FROM clarity_kpis_daily")
    assert len(rows) == 1
    assert rows[0]["rage_click_rate"] == pytest.approx(0.05)


def test_upsert_clarity_baseline(repo: DuckDBRepository) -> None:
    baseline = [{"kpi_name": "rage_click_rate", "baseline_value": 0.025, "computed_from_days": 14}]
    written = repo.upsert_clarity_baseline(baseline)
    assert written == 1
    current = repo.query_clarity_baseline_current()
    assert len(current) == 1
    assert current[0]["kpi_name"] == "rage_click_rate"


def test_upsert_clarity_baseline_invalidates_previous(repo: DuckDBRepository) -> None:
    b1 = [{"kpi_name": "rage_click_rate", "baseline_value": 0.02, "computed_from_days": 7}]
    repo.upsert_clarity_baseline(b1)
    b2 = [{"kpi_name": "rage_click_rate", "baseline_value": 0.025, "computed_from_days": 14}]
    repo.upsert_clarity_baseline(b2)
    current = repo.query_clarity_baseline_current()
    # Only most recent should have valid_until = NULL
    assert len(current) == 1
    assert current[0]["baseline_value"] == pytest.approx(0.025)


def test_clarity_already_ingested_today_false(repo: DuckDBRepository) -> None:
    assert repo.clarity_already_ingested_today() is False


def test_clarity_already_ingested_today_true(repo: DuckDBRepository) -> None:
    repo.upsert_clarity_raw([_make_row(fetch_date=date.today().isoformat())])
    assert repo.clarity_already_ingested_today() is True


def test_query_clarity_kpis_window(repo: DuckDBRepository) -> None:
    snap = _make_snapshot()
    repo.upsert_clarity_kpis_daily(snap)
    rows = repo.query_clarity_kpis_window(days=7)
    assert len(rows) == 1


# ─── ClarityClient ───────────────────────────────────────────────────────────

def _make_clarity_api_response(n: int = 2) -> list:
    """Build a realistic Clarity API response matching the actual API format.

    The real API returns a list of metric objects, each with metricName and
    information (list of dimension-value rows with metric data).
    """
    devices = [f"Device{i}" for i in range(n)]
    info_base = lambda device: {  # noqa: E731
        "sessionsCount": "500",
        "sessionsWithMetricPercentage": 2.0,
        "sessionsWithoutMetricPercentage": 98.0,
        "pagesViews": "100",
        "Device": device,
        "OS": "Android",
    }
    return [
        {
            "metricName": "Traffic",
            "information": [
                {
                    "totalSessionCount": "500",
                    "totalBotSessionCount": "10",
                    "distantUserCount": "400",
                    "PagesPerSessionPercentage": 2.5,
                    "Device": devices[i],
                    "OS": "Android",
                }
                for i in range(n)
            ],
        },
        {
            "metricName": "DeadClickCount",
            "information": [{**info_base(devices[i]), "subTotal": "20"} for i in range(n)],
        },
        {
            "metricName": "RageClickCount",
            "information": [{**info_base(devices[i]), "subTotal": "10"} for i in range(n)],
        },
        {
            "metricName": "ErrorClickCount",
            "information": [{**info_base(devices[i]), "subTotal": "5"} for i in range(n)],
        },
        {
            "metricName": "ScriptErrorCount",
            "information": [{**info_base(devices[i]), "subTotal": "2"} for i in range(n)],
        },
    ]


def test_clarity_client_fetch_parses_rows() -> None:
    client = ClarityClient(project_id="proj1", api_token="token123")
    with patch("play_insights.clarity_client.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = _make_clarity_api_response(3)
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        rows = client.fetch(num_of_days=3, dimension1="Device", dimension2="OS")
        assert len(rows) == 3
        assert rows[0].project_id == "proj1"
        assert rows[0].sessions == 500
        assert rows[0].dead_click_count == 20
        assert rows[0].rage_click_count == 10
        assert rows[0].lcp_ms is None  # not available in Clarity Data Export API


def test_clarity_client_handles_401_gracefully() -> None:
    client = ClarityClient(project_id="proj1", api_token="bad_token")
    with patch("play_insights.clarity_client.requests.get") as mock_get:
        mock_resp = MagicMock()
        http_err = requests.HTTPError(response=MagicMock(status_code=401))
        mock_resp.raise_for_status.side_effect = http_err
        mock_get.return_value = mock_resp

        rows = client.fetch(num_of_days=3)
        assert rows == []


def test_clarity_client_respects_max_requests() -> None:
    client = ClarityClient(project_id="proj1", api_token="token")
    client._requests_made = MAX_REQUESTS_PER_RUN  # simulate budget exhausted
    with patch("play_insights.clarity_client.requests.get") as mock_get:
        rows = client.fetch(num_of_days=3)
        assert rows == []
        mock_get.assert_not_called()


def test_clarity_client_clamps_num_of_days() -> None:
    client = ClarityClient(project_id="proj1", api_token="token")
    with patch("play_insights.clarity_client.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        client.fetch(num_of_days=99)  # should be clamped to 3
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]["params"] if "params" in call_kwargs[1] else call_kwargs[0][1]
        assert params["numOfDays"] == 3
