from __future__ import annotations

import os

import pytest

from play_insights.report_weekly import (
    _build_category_persistence,
    _build_crash_vs_reviews_correlation,
)


def _make_weekly_data(
    category_persistence: list | None = None,
    weekly_crash_vs_reviews: list | None = None,
) -> dict:
    return {
        "rating_trend": [],
        "overall_rating": {"avg_rating": 3.5, "total": 10, "negative": 3},
        "categories": [],
        "reviews_with_text": [],
        "vitals_by_metric": [],
        "vitals_trend": [],
        "error_issues": [],
        "recommendations": [],
        "severity_dist": [],
        "install_rows": [],
        "crash_series": [],
        "crash_by_device": [],
        "crash_by_version": [],
        "vitals_dim_gap": {},
        "performance_vitals": [],
        "category_persistence": category_persistence or [],
        "weekly_crash_vs_reviews": weekly_crash_vs_reviews or [],
        "urgent_reviews": [],
        "threshold_violations": [],
        "crash_trend": None,
    }


# --- Category Persistence ---

def test_persistence_empty() -> None:
    data = _make_weekly_data(category_persistence=[])
    assert _build_category_persistence(data) == []


def test_persistence_chronic() -> None:
    data = _make_weekly_data(category_persistence=[
        {"complaint_category": "estabilidade", "first_seen": "2026-01-01", "last_seen": "2026-03-01",
         "weeks_present": 5, "total_reviews": 47},
    ])
    lines = _build_category_persistence(data)
    text = "\n".join(lines)
    assert "Crônico" in text
    assert "Estabilidade" in text


def test_persistence_recurrent() -> None:
    data = _make_weekly_data(category_persistence=[
        {"complaint_category": "performance", "first_seen": "2026-02-01", "last_seen": "2026-03-01",
         "weeks_present": 2, "total_reviews": 8},
    ])
    lines = _build_category_persistence(data)
    text = "\n".join(lines)
    assert "Recorrente" in text


def test_persistence_new() -> None:
    data = _make_weekly_data(category_persistence=[
        {"complaint_category": "usabilidade", "first_seen": "2026-03-01", "last_seen": "2026-03-04",
         "weeks_present": 1, "total_reviews": 3},
    ])
    lines = _build_category_persistence(data)
    text = "\n".join(lines)
    assert "Novo" in text


# --- Crash vs Reviews Correlation ---

def test_correlation_empty() -> None:
    data = _make_weekly_data(weekly_crash_vs_reviews=[])
    assert _build_crash_vs_reviews_correlation(data) == []


def test_correlation_table() -> None:
    data = _make_weekly_data(weekly_crash_vs_reviews=[
        {"week": "2026-01-01", "crash_avg_pct": 24.0, "neg_reviews": 7},
        {"week": "2025-12-25", "crash_avg_pct": 15.0, "neg_reviews": 3},
        {"week": "2025-12-18", "crash_avg_pct": 12.0, "neg_reviews": 2},
        {"week": "2025-12-11", "crash_avg_pct": 10.0, "neg_reviews": 1},
    ])
    lines = _build_crash_vs_reviews_correlation(data)
    text = "\n".join(lines)
    assert "Correlação" in text
    # All 4 rows in the table
    assert "2026-01-01" in text
    assert "2025-12-11" in text


@pytest.mark.live_api
def test_weekly_full_real_db() -> None:
    import os
    db_path = os.environ.get("DB_PATH", "play_insights.duckdb")
    from play_insights.duckdb_repo import DuckDBRepository
    from play_insights.report_weekly import _fetch_weekly_data
    repo = DuckDBRepository(db_path=db_path)
    data = _fetch_weekly_data(repo, window=30)
    assert isinstance(data, dict)
    assert "categories" in data
    assert "threshold_violations" in data
    assert "category_persistence" in data
    assert "weekly_crash_vs_reviews" in data
