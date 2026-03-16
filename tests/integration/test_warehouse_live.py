from __future__ import annotations

import os

import pytest

from play_insights.duckdb_repo import DuckDBRepository
from play_insights.play_reviews_client import fetch_reviews
from play_insights.reporting_client import DeveloperReportingClient


@pytest.mark.warehouse
def test_reviews_upsert_idempotent(require_live_env: None, tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "test.duckdb"))
    package = os.getenv("PLAY_PACKAGE_NAME", "")
    reviews = fetch_reviews(package_name=package, max_results=5)
    first = repo.upsert_reviews_raw(reviews)
    second = repo.upsert_reviews_raw(reviews)
    assert first == second


@pytest.mark.warehouse
def test_vitals_write_live(require_live_env: None, tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "test.duckdb"))
    package = os.getenv("PLAY_PACKAGE_NAME", "")
    client = DeveloperReportingClient(package_name=package)
    rows = client.query_crash_rate(days=2) + client.query_anr_rate(days=2)
    written = repo.upsert_vitals_daily(rows)
    assert written == len(rows)
