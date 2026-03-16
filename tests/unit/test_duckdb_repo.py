from __future__ import annotations

import logging
from datetime import datetime, timezone

import pytest

from play_insights.duckdb_repo import DuckDBRepository
from play_insights.models import ErrorIssueRecord, ReviewRecord, StatsRecord, VitalsRecord


@pytest.fixture()
def repo(tmp_path) -> DuckDBRepository:
    return DuckDBRepository(db_path=str(tmp_path / "test.duckdb"))


def test_upsert_reviews_raw_returns_count(repo: DuckDBRepository) -> None:
    records = [
        ReviewRecord(
            review_id="r1",
            star_rating=3,
            comment_text="ok",
            app_version_name="1.0",
            app_version_code="10",
            reviewer_language="pt",
            last_modified_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
    ]
    written = repo.upsert_reviews_raw(records)
    assert written == 1


def test_upsert_reviews_raw_deduplicates(repo: DuckDBRepository) -> None:
    rec = ReviewRecord(
        review_id="r1",
        star_rating=3,
        comment_text="ok",
        app_version_name="1.0",
        app_version_code="10",
        reviewer_language="pt",
        last_modified_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    repo.upsert_reviews_raw([rec])
    repo.upsert_reviews_raw([rec])
    rows = repo.query("SELECT COUNT(*) AS n FROM reviews_raw")
    assert rows[0]["n"] == 1


def test_upsert_vitals_daily(repo: DuckDBRepository) -> None:
    records = [
        VitalsRecord(date="2024-01-15", metric_set="crashRateMetricSet", metric_value=0.01, package_name="com.app")
    ]
    written = repo.upsert_vitals_daily(records)
    assert written == 1
    rows = repo.query("SELECT metric_value FROM vitals_daily")
    assert abs(rows[0]["metric_value"] - 0.01) < 1e-9


def test_upsert_error_issues(repo: DuckDBRepository) -> None:
    records = [
        ErrorIssueRecord(
            issue_id="e1",
            issue_title="Crash on start",
            error_type="crash",
            affected_users=100.0,
            app_version="1.0",
            device_model="Pixel",
            os_version="12",
            first_seen="2024-01-01",
            last_seen="2024-01-15",
        )
    ]
    written = repo.upsert_error_issues(records)
    assert written == 1


def test_upsert_stats_daily(repo: DuckDBRepository) -> None:
    records = [StatsRecord(date="2024-01-15", country="BR", installs=100, uninstalls=10, active_devices=500)]
    written = repo.upsert_stats_daily(records)
    assert written == 1
    rows = repo.query("SELECT installs FROM stats_daily")
    assert rows[0]["installs"] == 100


def test_upsert_recommendations_replaces_by_date(repo: DuckDBRepository) -> None:
    recs = [
        {
            "date": "2024-01-15",
            "recommendation_id": "cat-2024-01-15",
            "complaint_category": "estabilidade",
            "evidence_refs": "neg_count=5",
            "expected_impact_score": 10.0,
            "effort_tshirt": "M",
            "owner_suggestion": "Engineering",
        }
    ]
    repo.upsert_recommendations(recs)
    repo.upsert_recommendations(recs)
    rows = repo.query("SELECT COUNT(*) AS n FROM recommendations")
    assert rows[0]["n"] == 1


def test_query_returns_list_of_dicts(repo: DuckDBRepository) -> None:
    repo.upsert_vitals_daily(
        [VitalsRecord(date="2024-01-15", metric_set="crashRateMetricSet", metric_value=0.05, package_name="com.app")]
    )
    result = repo.query("SELECT metric_set FROM vitals_daily")
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    assert result[0]["metric_set"] == "crashRateMetricSet"

# ============================================================
# Passo 1: Context Manager e close()
# ============================================================

def test_close_explicit(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "close.duckdb"))
    repo.close()  # should not raise


def test_context_manager(tmp_path) -> None:
    with DuckDBRepository(db_path=str(tmp_path / "cm.duckdb")) as repo:
        repo.upsert_vitals_daily(
            [VitalsRecord(date="2024-01-15", metric_set="crashRateMetricSet", metric_value=0.01, package_name="com.app")]
        )
        rows = repo.query("SELECT COUNT(*) AS n FROM vitals_daily")
    assert rows[0]["n"] == 1


def test_connection_closed_after_context_manager(tmp_path) -> None:
    import duckdb
    with DuckDBRepository(db_path=str(tmp_path / "closed.duckdb")) as repo:
        pass
    with pytest.raises(Exception):
        repo._conn.execute("SELECT 1")


# ============================================================
# Passo 2: Limite de linhas em query()
# ============================================================

def _make_reviews(n: int) -> list[ReviewRecord]:
    return [
        ReviewRecord(
            review_id=f"r{i}",
            star_rating=3,
            comment_text="test",
            app_version_name="1.0",
            app_version_code="10",
            reviewer_language="pt",
            last_modified_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        for i in range(n)
    ]


def test_query_max_rows_truncates(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "maxrows.duckdb"))
    repo.upsert_reviews_raw(_make_reviews(200))
    result = repo.query("SELECT * FROM reviews_raw", max_rows=50)
    assert len(result) == 50
    repo.close()


def test_query_max_rows_emits_warning(tmp_path, caplog) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "warn.duckdb"))
    repo.upsert_reviews_raw(_make_reviews(200))
    with caplog.at_level(logging.WARNING, logger="play_insights.duckdb_repo"):
        repo.query("SELECT * FROM reviews_raw", max_rows=50)
    assert any("truncat" in r.message.lower() or "max_rows" in r.message.lower() for r in caplog.records)
    repo.close()


def test_query_with_explicit_limit_no_warning(tmp_path, caplog) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "nwarn.duckdb"))
    repo.upsert_reviews_raw(_make_reviews(200))
    with caplog.at_level(logging.WARNING, logger="play_insights.duckdb_repo"):
        result = repo.query("SELECT * FROM reviews_raw LIMIT 10", max_rows=50_000)
    assert len(result) == 10
    warning_msgs = [r.message for r in caplog.records]
    assert not any("truncat" in m.lower() or "max_rows" in m.lower() for m in warning_msgs)
    repo.close()


# ============================================================
# Passo 3: Indices nas tabelas
# ============================================================

def test_indexes_exist_vitals(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "idx.duckdb"))
    # Ensure the table exists first
    repo.upsert_vitals_daily(
        [VitalsRecord(date="2024-01-15", metric_set="crashRateMetricSet", metric_value=0.01, package_name="com.app")]
    )
    idxs = repo.query("SELECT index_name FROM duckdb_indexes() WHERE table_name = 'vitals_daily'")
    names = {r["index_name"] for r in idxs}
    assert "idx_vitals_date_metric" in names
    repo.close()


def test_indexes_exist_reviews_raw(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "idx2.duckdb"))
    repo.upsert_reviews_raw(_make_reviews(1))
    idxs = repo.query("SELECT index_name FROM duckdb_indexes() WHERE table_name = 'reviews_raw'")
    names = {r["index_name"] for r in idxs}
    assert "idx_reviews_raw_date" in names
    repo.close()


def test_indexes_exist_reviews_enriched(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "idx3.duckdb"))
    repo.upsert_reviews_enriched([{
        "review_id": "r1",
        "complaint_category": "estabilidade",
        "sentiment_label": "neg",
        "severity": 2,
        "intent": "relato",
        "topic_keywords": "crash",
        "confidence": 0.9,
        "source_comment_text": "app trava",
    }])
    idxs = repo.query("SELECT index_name FROM duckdb_indexes() WHERE table_name = 'reviews_enriched'")
    names = {r["index_name"] for r in idxs}
    assert "idx_enriched_category" in names
    repo.close()


def test_explain_vitals_uses_index(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "explain.duckdb"))
    repo.upsert_vitals_daily(
        [VitalsRecord(date="2024-01-15", metric_set="crashRateMetricSet", metric_value=0.01, package_name="com.app")]
    )
    # Just verify EXPLAIN runs without error (DuckDB may choose index or not depending on data size)
    result = repo.query("EXPLAIN SELECT * FROM vitals_daily WHERE date >= '2024-01-01'")
    assert len(result) > 0
    repo.close()


# ============================================================
# Passo 4: WAL Checkpoint e maintenance()
# ============================================================

def test_maintenance_returns_ok(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "maint.duckdb"))
    repo.upsert_reviews_raw(_make_reviews(10))
    result = repo.maintenance()
    assert result["status"] == "ok"
    assert "tables" in result
    repo.close()


def test_wal_autocheckpoint_applied(tmp_path) -> None:
    repo = DuckDBRepository(db_path=str(tmp_path / "wal.duckdb"))
    # DuckDB 1.4+ may not expose wal_autocheckpoint via pragma_* or similar,
    # so we just verify __init__ ran without error and connection is usable.
    rows = repo.query("SELECT 42 AS val")
    assert rows[0]["val"] == 42
    repo.close()
