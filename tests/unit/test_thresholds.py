from __future__ import annotations

import os

import pytest

from play_insights.thresholds import (
    CRASH_RATE_THRESHOLD,
    ANR_RATE_THRESHOLD,
    ThresholdViolation,
    TrendVelocity,
    calculate_trend_velocity,
    check_violations,
    detect_regression,
    format_violation_summary,
)


def test_no_violations() -> None:
    vitals = [
        {"metric_set": "crashRateMetricSet", "avg_value": 0.005},
        {"metric_set": "anrRateMetricSet", "avg_value": 0.001},
    ]
    result = check_violations(vitals)
    assert result == []


def test_crash_violation() -> None:
    vitals = [
        {"metric_set": "crashRateMetricSet", "avg_value": 0.241},
    ]
    result = check_violations(vitals)
    assert len(result) == 1
    v = result[0]
    assert v.metric_set == "crashRateMetricSet"
    assert v.multiple == pytest.approx(22.1, abs=0.5)
    assert v.is_critical is True
    assert v.current_value == pytest.approx(0.241)
    assert v.threshold == CRASH_RATE_THRESHOLD


def test_anr_violation() -> None:
    vitals = [
        {"metric_set": "anrRateMetricSet", "avg_value": 0.015},
    ]
    result = check_violations(vitals)
    assert len(result) == 1
    v = result[0]
    assert v.is_critical is False  # 0.015 / 0.0047 ≈ 3.2x < 10


def test_format_summary_critical() -> None:
    violations = [
        ThresholdViolation(
            metric_set="crashRateMetricSet",
            current_value=0.241,
            threshold=CRASH_RATE_THRESHOLD,
            multiple=22.1,
            is_critical=True,
        )
    ]
    summary = format_violation_summary(violations)
    assert "RISCO CRÍTICO" in summary
    assert "22.1x" in summary


def test_format_summary_empty() -> None:
    assert format_violation_summary([]) == ""


def test_unknown_metric_set_ignored() -> None:
    vitals = [{"metric_set": "unknownMetricSet", "avg_value": 99.9}]
    assert check_violations(vitals) == []


# --- TrendVelocity tests ---

def test_trend_worsening() -> None:
    series = [
        {"date": f"2026-01-{i:02d}", "avg_crash": 0.10} for i in range(1, 8)
    ] + [
        {"date": f"2026-01-{i:02d}", "avg_crash": 0.20} for i in range(8, 15)
    ]
    result = calculate_trend_velocity(series)
    assert "piorando" in result.direction
    assert result.delta_pp > 0


def test_trend_improving() -> None:
    series = [
        {"date": f"2026-01-{i:02d}", "avg_crash": 0.20} for i in range(1, 8)
    ] + [
        {"date": f"2026-01-{i:02d}", "avg_crash": 0.10} for i in range(8, 15)
    ]
    result = calculate_trend_velocity(series)
    assert "melhorando" in result.direction
    assert result.delta_pp < 0


def test_trend_stable() -> None:
    series = [
        {"date": f"2026-01-{i:02d}", "avg_crash": 0.15} for i in range(1, 15)
    ]
    result = calculate_trend_velocity(series)
    assert "estável" in result.direction
    assert abs(result.delta_pp) < 0.5


def test_trend_empty() -> None:
    result = calculate_trend_velocity([])
    assert result.direction == "→ estável"
    assert result.delta_pp == 0.0
    assert result.current_7d_avg == 0.0


# --- detect_regression tests ---

def test_regression_detected() -> None:
    versions = [
        {"app_version": "20252", "crash_avg_pct": 24.0, "days_with_data": 10, "first_seen": "2026-02-01", "last_seen": "2026-02-10"},
        {"app_version": "20251", "crash_avg_pct": 15.0, "days_with_data": 12, "first_seen": "2026-01-01", "last_seen": "2026-01-31"},
    ]
    result = detect_regression(versions)
    assert result["has_regression"] is True
    assert result["current_version"] == "20252"
    assert result["delta_pp"] == pytest.approx(9.0, abs=0.1)


def test_no_regression() -> None:
    versions = [
        {"app_version": "20252", "crash_avg_pct": 5.0, "days_with_data": 10, "first_seen": "2026-02-01", "last_seen": "2026-02-10"},
        {"app_version": "20251", "crash_avg_pct": 15.0, "days_with_data": 12, "first_seen": "2026-01-01", "last_seen": "2026-01-31"},
    ]
    result = detect_regression(versions)
    assert result["has_regression"] is False


def test_regression_single_version() -> None:
    versions = [
        {"app_version": "20252", "crash_avg_pct": 24.0, "days_with_data": 10, "first_seen": "2026-02-01", "last_seen": "2026-02-10"},
    ]
    result = detect_regression(versions)
    assert result["has_regression"] is False


def test_regression_empty() -> None:
    assert detect_regression([]) == {"has_regression": False, "details": None}


@pytest.mark.live_api
def test_with_real_db() -> None:
    db_path = os.environ.get("DB_PATH", "play_insights.duckdb")
    from play_insights.duckdb_repo import DuckDBRepository
    repo = DuckDBRepository(db_path=db_path)
    vitals = repo.query("""
        SELECT metric_set, ROUND(AVG(metric_value), 6) AS avg_value
        FROM vitals_daily
        GROUP BY metric_set
    """)
    result = check_violations(vitals)
    print(f"\nThreshold violations in DB: {result}")
    assert isinstance(result, list)


@pytest.mark.live_api
def test_trend_with_real_db() -> None:
    db_path = os.environ.get("DB_PATH", "play_insights.duckdb")
    from play_insights.duckdb_repo import DuckDBRepository
    repo = DuckDBRepository(db_path=db_path)
    crash_series = repo.query("""
        SELECT date, ROUND(AVG(metric_value), 4) AS avg_crash
        FROM vitals_daily
        WHERE metric_set = 'crashRateMetricSet'
        GROUP BY date
        ORDER BY date DESC
        LIMIT 30
    """)
    result = calculate_trend_velocity(crash_series)
    print(f"\nCrash trend: {result}")
    assert isinstance(result, TrendVelocity)


@pytest.mark.live_api
def test_regression_with_real_db() -> None:
    db_path = os.environ.get("DB_PATH", "play_insights.duckdb")
    from play_insights.duckdb_repo import DuckDBRepository
    repo = DuckDBRepository(db_path=db_path)
    crash_by_version = repo.query("""
        SELECT app_version,
               ROUND(AVG(metric_value) * 100, 2) AS crash_avg_pct,
               COUNT(DISTINCT date) AS days_with_data,
               MIN(date) AS first_seen,
               MAX(date) AS last_seen
        FROM vitals_daily
        WHERE metric_set = 'crashRateMetricSet'
          AND app_version IS NOT NULL
        GROUP BY app_version
        ORDER BY MAX(date) DESC
        LIMIT 10
    """)
    result = detect_regression(crash_by_version)
    print(f"\nVersion regression: {result}")
    assert isinstance(result, dict)
    assert "has_regression" in result
