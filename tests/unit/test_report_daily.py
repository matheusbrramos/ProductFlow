from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from play_insights.report_daily import (
    _build_executive_kpi_table,
    _build_urgent_alerts,
    _build_version_regression,
    _build_performance_section,
    _build_what_changed,
    load_previous_alerts,
)
from play_insights.thresholds import ThresholdViolation, TrendVelocity


def _make_data(
    crash_avg: float = 0.005,
    anr_avg: float = 0.001,
    violations: list | None = None,
    crash_trend: TrendVelocity | None = None,
    neg: int = 3,
    avg_r: float = 4.0,
    categories: list | None = None,
    urgent_reviews: list | None = None,
    crash_by_version: list | None = None,
    performance_vitals: list | None = None,
) -> dict:
    return {
        "rating": {"avg_rating": avg_r, "total_reviews": 20, "negative": neg, "positive": 15},
        "vitals": [
            {"metric_set": "crashRateMetricSet", "avg_value": crash_avg, "max_value": crash_avg * 1.2, "days_with_data": 14},
            {"metric_set": "anrRateMetricSet", "avg_value": anr_avg, "max_value": anr_avg * 1.2, "days_with_data": 14},
        ],
        "categories": categories or [{"complaint_category": "estabilidade", "total": 5, "avg_severity": 4.0}],
        "threshold_violations": violations or [],
        "crash_trend": crash_trend or TrendVelocity("crashRateMetricSet", crash_avg, crash_avg, 0.0, "→ estável"),
        "urgent_reviews": urgent_reviews or [],
        "crash_by_version": crash_by_version or [],
        "performance_vitals": performance_vitals or [],
        "crash_series": [],
        "reviews_with_text": [],
        "severity_dist": [],
        "intent_dist": [],
        "vitals_dim_gap": {},
        "error_issues_count": 0,
        "crash_by_device": [],
    }


# --- Executive Summary ---

def test_executive_summary_no_violations() -> None:
    data = _make_data(crash_avg=0.005)
    lines = _build_executive_kpi_table(data, "2026-03-04", 30)
    text = "\n".join(lines)
    assert "Resumo Executivo" in text
    assert "ALERTA DE POLÍTICA" not in text
    assert "Crash Rate" in text


def test_executive_summary_with_violation() -> None:
    from play_insights.thresholds import CRASH_RATE_THRESHOLD
    v = ThresholdViolation(
        metric_set="crashRateMetricSet",
        current_value=0.241,
        threshold=CRASH_RATE_THRESHOLD,
        multiple=22.1,
        is_critical=True,
    )
    data = _make_data(crash_avg=0.241, violations=[v])
    lines = _build_executive_kpi_table(data, "2026-03-04", 30)
    text = "\n".join(lines)
    assert "ALERTA DE POLÍTICA GOOGLE PLAY" in text
    assert "22.1x" in text


# --- Urgent Alerts ---

def test_urgent_alerts_empty() -> None:
    data = _make_data(urgent_reviews=[])
    assert _build_urgent_alerts(data) == []


def test_urgent_alerts_with_data() -> None:
    data = _make_data(urgent_reviews=[
        {"comment_text": "show hoje e não consigo entrar", "star_rating": 1, "ingest_date": "2026-03-04",
         "app_version_name": "1.0", "complaint_category": "experiencia_compra", "severity": 5},
        {"comment_text": "urgente preciso do qr code", "star_rating": 1, "ingest_date": "2026-03-04",
         "app_version_name": "1.0", "complaint_category": "experiencia_compra", "severity": 5},
    ])
    lines = _build_urgent_alerts(data)
    text = "\n".join(lines)
    assert "🚨" in text
    assert "show hoje" in text
    assert "urgente" in text


# --- Version Regression ---

def test_version_regression_empty() -> None:
    data = _make_data(crash_by_version=[])
    assert _build_version_regression(data) == []


def test_version_regression_detected() -> None:
    data = _make_data(crash_by_version=[
        {"app_version": "20252", "crash_avg_pct": 24.0, "days_with_data": 10, "first_seen": "2026-02-01", "last_seen": "2026-02-10"},
        {"app_version": "20251", "crash_avg_pct": 15.0, "days_with_data": 12, "first_seen": "2026-01-01", "last_seen": "2026-01-31"},
    ])
    lines = _build_version_regression(data)
    text = "\n".join(lines)
    assert "Regressão detectada" in text
    assert "20252" in text


# --- Performance Section ---

def test_performance_section_empty() -> None:
    data = _make_data(performance_vitals=[])
    lines = _build_performance_section(data)
    text = "\n".join(lines)
    assert "não coletados" in text


def test_performance_section_with_data() -> None:
    data = _make_data(performance_vitals=[
        {"metric_set": "slowRenderingRateMetricSet", "avg_pct": 35.0, "max_pct": 60.0, "days_with_data": 14},
        {"metric_set": "slowStartRateMetricSet", "avg_pct": 20.0, "max_pct": 40.0, "days_with_data": 14},
    ])
    lines = _build_performance_section(data)
    text = "\n".join(lines)
    assert "Slow Rendering" in text
    assert "35.0%" in text
    assert "Slow Start" in text


# --- What Changed ---

def test_what_changed_no_prev() -> None:
    data = _make_data()
    lines = _build_what_changed(data, None, "2026-03-04")
    text = "\n".join(lines)
    assert "Primeiro relatório" in text


def test_what_changed_with_prev() -> None:
    prev = {
        "date": "2026-03-03",
        "health": {"avg_rating": 3.5, "negative_count": 5, "positive_count": 10},
        "vitals_summary": [{"metric_set": "crashRateMetricSet", "avg_value": 0.15}],
    }
    data = _make_data(crash_avg=0.24, avg_r=3.8, neg=8)
    lines = _build_what_changed(data, prev, "2026-03-04")
    text = "\n".join(lines)
    assert "2026-03-03" in text
    assert "Crash Rate" in text


# --- load_previous_alerts ---

def test_load_previous_alerts_none(tmp_path: Path) -> None:
    result = load_previous_alerts("2026-03-04", memory_dir=tmp_path)
    assert result is None


def test_load_previous_alerts_found(tmp_path: Path) -> None:
    payload = {"date": "2026-03-03", "health": {"avg_rating": 3.5}}
    (tmp_path / "alerts-2026-03-03.json").write_text(json.dumps(payload), encoding="utf-8")
    result = load_previous_alerts("2026-03-04", memory_dir=tmp_path)
    assert result is not None
    assert result["date"] == "2026-03-03"


def test_load_previous_alerts_skips_today(tmp_path: Path) -> None:
    payload = {"date": "2026-03-04"}
    (tmp_path / "alerts-2026-03-04.json").write_text(json.dumps(payload), encoding="utf-8")
    result = load_previous_alerts("2026-03-04", memory_dir=tmp_path)
    assert result is None


@pytest.mark.live_api
def test_executive_summary_real_db() -> None:
    db_path = os.environ.get("DB_PATH", "play_insights.duckdb")
    from play_insights.duckdb_repo import DuckDBRepository
    from play_insights.report_daily import _fetch_daily_data
    repo = DuckDBRepository(db_path=db_path)
    data = _fetch_daily_data(repo, window=30)
    lines = _build_executive_kpi_table(data, "2026-03-04", 30)
    assert isinstance(lines, list)
    assert len(lines) > 5
    text = "\n".join(lines)
    assert "Resumo Executivo" in text
