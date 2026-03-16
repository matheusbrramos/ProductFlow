from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import logging

import duckdb

from play_insights.models import ClarityKPISnapshot, ClarityRow, ErrorIssueRecord, ReviewRecord, StatsRecord, VitalsRecord

logger = logging.getLogger(__name__)


def _iso_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


_SCHEMA: dict[str, str] = {
    "reviews_raw": """
        CREATE TABLE IF NOT EXISTS reviews_raw (
            review_id VARCHAR NOT NULL,
            star_rating INTEGER,
            comment_text VARCHAR,
            app_version_name VARCHAR,
            app_version_code VARCHAR,
            reviewer_language VARCHAR,
            last_modified_at TIMESTAMP,
            ingested_at TIMESTAMP NOT NULL,
            ingest_date DATE NOT NULL,
            dedupe_id VARCHAR NOT NULL
        )
    """,
    "vitals_daily": """
        CREATE TABLE IF NOT EXISTS vitals_daily (
            date DATE NOT NULL,
            metric_set VARCHAR NOT NULL,
            metric_value DOUBLE NOT NULL,
            package_name VARCHAR NOT NULL,
            app_version VARCHAR,
            country VARCHAR,
            device_model VARCHAR,
            os_version VARCHAR,
            ingested_at TIMESTAMP NOT NULL,
            dedupe_id VARCHAR NOT NULL
        )
    """,
    "error_issues": """
        CREATE TABLE IF NOT EXISTS error_issues (
            issue_id VARCHAR NOT NULL,
            issue_title VARCHAR NOT NULL,
            error_type VARCHAR,
            affected_users DOUBLE,
            app_version VARCHAR,
            device_model VARCHAR,
            os_version VARCHAR,
            first_seen DATE,
            last_seen DATE,
            ingested_at TIMESTAMP NOT NULL,
            ingest_date DATE NOT NULL,
            dedupe_id VARCHAR NOT NULL
        )
    """,
    "reviews_enriched": """
        CREATE TABLE IF NOT EXISTS reviews_enriched (
            review_id VARCHAR NOT NULL,
            sentiment_label VARCHAR,
            complaint_category VARCHAR,
            severity INTEGER,
            intent VARCHAR,
            topic_keywords VARCHAR,
            confidence DOUBLE,
            source_comment_text VARCHAR,
            event_urgency BOOLEAN DEFAULT FALSE,
            ingested_at TIMESTAMP NOT NULL,
            ingest_date DATE NOT NULL,
            dedupe_id VARCHAR NOT NULL
        )
    """,
    "recommendations": """
        CREATE TABLE IF NOT EXISTS recommendations (
            date DATE NOT NULL,
            recommendation_id VARCHAR NOT NULL,
            complaint_category VARCHAR NOT NULL,
            evidence_refs VARCHAR,
            expected_impact_score DOUBLE NOT NULL,
            effort_tshirt VARCHAR,
            owner_suggestion VARCHAR,
            created_at TIMESTAMP NOT NULL
        )
    """,
    "reply_audit": """
        CREATE TABLE IF NOT EXISTS reply_audit (
            event_date DATE NOT NULL,
            event_time TIMESTAMP NOT NULL,
            review_id VARCHAR NOT NULL,
            mode VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            message VARCHAR
        )
    """,
    "stats_daily": """
        CREATE TABLE IF NOT EXISTS stats_daily (
            date DATE NOT NULL,
            country VARCHAR,
            installs INTEGER,
            uninstalls INTEGER,
            active_devices INTEGER,
            ingested_at TIMESTAMP NOT NULL,
            dedupe_id VARCHAR NOT NULL
        )
    """,
    "clarity_raw": """
        CREATE TABLE IF NOT EXISTS clarity_raw (
            project_id      VARCHAR NOT NULL,
            fetch_date      DATE NOT NULL,
            num_of_days     INTEGER NOT NULL,
            dim1_name       VARCHAR,
            dim1_value      VARCHAR,
            dim2_name       VARCHAR,
            dim2_value      VARCHAR,
            dim3_name       VARCHAR,
            dim3_value      VARCHAR,
            sessions        INTEGER,
            users           INTEGER,
            scroll_depth_pct  DOUBLE,
            engagement_time_ms DOUBLE,
            dead_click_count   INTEGER,
            rage_click_count   INTEGER,
            error_click_count  INTEGER,
            script_error_count INTEGER,
            lcp_ms          DOUBLE,
            inp_ms          DOUBLE,
            cls             DOUBLE,
            ingested_at     TIMESTAMP NOT NULL,
            dedupe_id       VARCHAR NOT NULL
        )
    """,
    "clarity_kpis_daily": """
        CREATE TABLE IF NOT EXISTS clarity_kpis_daily (
            snapshot_date         DATE NOT NULL,
            snapshot_type         VARCHAR NOT NULL,
            period_days           INTEGER NOT NULL,
            total_sessions        INTEGER,
            total_users           INTEGER,
            dead_click_rate       DOUBLE,
            rage_click_rate       DOUBLE,
            error_click_rate      DOUBLE,
            script_error_rate     DOUBLE,
            avg_scroll_depth_pct  DOUBLE,
            avg_engagement_time_ms DOUBLE,
            avg_lcp_ms            DOUBLE,
            avg_inp_ms            DOUBLE,
            avg_cls               DOUBLE,
            computed_at           TIMESTAMP NOT NULL,
            dedupe_id             VARCHAR NOT NULL
        )
    """,
    "clarity_baseline": """
        CREATE TABLE IF NOT EXISTS clarity_baseline (
            kpi_name        VARCHAR NOT NULL,
            baseline_value  DOUBLE NOT NULL,
            computed_from_days INTEGER NOT NULL,
            computed_at     TIMESTAMP NOT NULL,
            valid_from      DATE NOT NULL,
            valid_until     DATE,
            dedupe_id       VARCHAR NOT NULL
        )
    """,
}


class DuckDBRepository:
    def __init__(self, db_path: str, memory_limit: str = "512MB", threads: int = 2):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(db_path)
        self._conn.execute(f"SET memory_limit='{memory_limit}'")
        self._conn.execute(f"SET threads={threads}")
        self._conn.execute("PRAGMA checkpoint_threshold='16MB'")

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "DuckDBRepository":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @property
    def dataset_id(self) -> str:
        return self.db_path

    def ensure_dataset(self) -> None:
        pass  # No-op: DuckDB file is created on connect

    def _ensure_indexes(self) -> None:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_vitals_date_metric ON vitals_daily(date, metric_set)",
            "CREATE INDEX IF NOT EXISTS idx_vitals_package ON vitals_daily(package_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_reviews_raw_date ON reviews_raw(ingest_date)",
            "CREATE INDEX IF NOT EXISTS idx_reviews_raw_id ON reviews_raw(review_id)",
            "CREATE INDEX IF NOT EXISTS idx_enriched_category ON reviews_enriched(complaint_category)",
            "CREATE INDEX IF NOT EXISTS idx_enriched_date ON reviews_enriched(ingest_date)",
            "CREATE INDEX IF NOT EXISTS idx_clarity_raw_date ON clarity_raw(fetch_date)",
            "CREATE INDEX IF NOT EXISTS idx_clarity_kpis_date ON clarity_kpis_daily(snapshot_date, snapshot_type)",
            "CREATE INDEX IF NOT EXISTS idx_clarity_baseline_valid ON clarity_baseline(valid_until)",
        ]
        for ddl in indexes:
            try:
                self._conn.execute(ddl)
            except Exception:  # noqa: BLE001
                pass  # Table does not exist yet; index will be created on first upsert

    def _ensure_table(self, table_name: str) -> None:
        self._conn.execute(_SCHEMA[table_name])
        self._ensure_indexes()
        # Apply schema migrations for tables that may already exist
        if table_name == "reviews_enriched":
            try:
                self._conn.execute(
                    "ALTER TABLE reviews_enriched ADD COLUMN IF NOT EXISTS event_urgency BOOLEAN DEFAULT FALSE"
                )
            except Exception:  # noqa: BLE001
                pass  # Column already exists or DuckDB version doesn't support IF NOT EXISTS

    @staticmethod
    def _hash_key(values: list[str | None]) -> str:
        payload = json.dumps(values, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _delete_keys(self, table_name: str, keys: list[str]) -> None:
        if not keys:
            return
        placeholders = ", ".join("?" * len(keys))
        self._conn.execute(f"DELETE FROM {table_name} WHERE dedupe_id IN ({placeholders})", keys)

    def _insert_rows(self, table_name: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        cols = list(rows[0].keys())
        col_list = ", ".join(cols)
        placeholders = ", ".join("?" * len(cols))
        data = [[row[col] for col in cols] for row in rows]
        self._conn.executemany(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})", data)

    def upsert_reviews_raw(self, records: list[ReviewRecord]) -> int:
        self._ensure_table("reviews_raw")
        now = _iso_now()
        ingest_date = date.today().isoformat()
        rows: list[dict[str, Any]] = []
        keys: list[str] = []
        for rec in records:
            dedupe_id = self._hash_key([rec.review_id, rec.last_modified_at.isoformat() if rec.last_modified_at else ""])
            keys.append(dedupe_id)
            rows.append(
                {
                    "review_id": rec.review_id,
                    "star_rating": rec.star_rating,
                    "comment_text": rec.comment_text,
                    "app_version_name": rec.app_version_name,
                    "app_version_code": rec.app_version_code,
                    "reviewer_language": rec.reviewer_language,
                    "last_modified_at": rec.last_modified_at.isoformat() if rec.last_modified_at else None,
                    "ingested_at": now,
                    "ingest_date": ingest_date,
                    "dedupe_id": dedupe_id,
                }
            )
        self._delete_keys("reviews_raw", keys)
        self._insert_rows("reviews_raw", rows)
        return len(rows)

    def upsert_vitals_daily(self, records: list[VitalsRecord]) -> int:
        self._ensure_table("vitals_daily")
        now = _iso_now()
        rows: list[dict[str, Any]] = []
        keys: list[str] = []
        for rec in records:
            dedupe_id = self._hash_key(
                [rec.date, rec.metric_set, rec.package_name, rec.app_version, rec.country, rec.device_model, rec.os_version]
            )
            keys.append(dedupe_id)
            row = asdict(rec)
            row["ingested_at"] = now
            row["dedupe_id"] = dedupe_id
            rows.append(row)
        self._delete_keys("vitals_daily", keys)
        self._insert_rows("vitals_daily", rows)
        return len(rows)

    def upsert_error_issues(self, records: list[ErrorIssueRecord]) -> int:
        self._ensure_table("error_issues")
        now = _iso_now()
        ingest_date = date.today().isoformat()
        rows: list[dict[str, Any]] = []
        keys: list[str] = []
        for rec in records:
            dedupe_id = self._hash_key([rec.issue_id, rec.last_seen, rec.app_version, rec.device_model, rec.os_version])
            keys.append(dedupe_id)
            row = asdict(rec)
            row["ingested_at"] = now
            row["ingest_date"] = ingest_date
            row["dedupe_id"] = dedupe_id
            rows.append(row)
        self._delete_keys("error_issues", keys)
        self._insert_rows("error_issues", rows)
        return len(rows)

    def upsert_reviews_enriched(self, rows: list[dict[str, Any]]) -> int:
        self._ensure_table("reviews_enriched")
        now = _iso_now()
        ingest_date = date.today().isoformat()
        normalized: list[dict[str, Any]] = []
        keys: list[str] = []
        for row in rows:
            dedupe_id = self._hash_key([row["review_id"], row.get("complaint_category"), row.get("sentiment_label")])
            payload = {
                "review_id": row["review_id"],
                "sentiment_label": row.get("sentiment_label"),
                "complaint_category": row.get("complaint_category"),
                "severity": row.get("severity"),
                "intent": row.get("intent"),
                "topic_keywords": row.get("topic_keywords"),
                "confidence": row.get("confidence"),
                "source_comment_text": row.get("source_comment_text"),
                "event_urgency": bool(row.get("event_urgency", False)),
                "ingested_at": now,
                "ingest_date": ingest_date,
                "dedupe_id": dedupe_id,
            }
            keys.append(dedupe_id)
            normalized.append(payload)
        self._delete_keys("reviews_enriched", keys)
        self._insert_rows("reviews_enriched", normalized)
        return len(normalized)

    def upsert_recommendations(self, rows: list[dict[str, Any]]) -> int:
        self._ensure_table("recommendations")
        for row in rows:
            if "created_at" not in row:
                row["created_at"] = _iso_now()
        if rows:
            target_date = rows[0]["date"]
            self._conn.execute("DELETE FROM recommendations WHERE date = ?", [target_date])
        self._insert_rows("recommendations", rows)
        return len(rows)

    def upsert_stats_daily(self, records: list[StatsRecord]) -> int:
        self._ensure_table("stats_daily")
        now = _iso_now()
        rows: list[dict[str, Any]] = []
        keys: list[str] = []
        for rec in records:
            dedupe_id = self._hash_key([rec.date, rec.country])
            keys.append(dedupe_id)
            rows.append(
                {
                    "date": rec.date,
                    "country": rec.country,
                    "installs": rec.installs,
                    "uninstalls": rec.uninstalls,
                    "active_devices": rec.active_devices,
                    "ingested_at": now,
                    "dedupe_id": dedupe_id,
                }
            )
        self._delete_keys("stats_daily", keys)
        self._insert_rows("stats_daily", rows)
        return len(rows)

    def insert_reply_audit(self, rows: list[dict[str, Any]]) -> int:
        self._ensure_table("reply_audit")
        self._insert_rows("reply_audit", rows)
        return len(rows)

    def query(self, sql: str, max_rows: int = 50_000) -> list[dict[str, Any]]:
        result = self._conn.execute(sql)
        cols = [desc[0] for desc in result.description]
        rows = result.fetchmany(max_rows)
        if len(rows) == max_rows:
            logger.warning(
                "query() returned max_rows=%d rows — result may be truncated. Add LIMIT or increase max_rows.",
                max_rows,
            )
        return [dict(zip(cols, row)) for row in rows]

    def upsert_clarity_raw(self, records: list[ClarityRow]) -> int:
        self._ensure_table("clarity_raw")
        now = _iso_now()
        rows: list[dict[str, Any]] = []
        keys: list[str] = []
        for rec in records:
            dedupe_id = self._hash_key(
                [rec.project_id, rec.fetch_date, str(rec.num_of_days),
                 rec.dim1_name, rec.dim1_value, rec.dim2_name, rec.dim2_value]
            )
            keys.append(dedupe_id)
            rows.append({
                "project_id": rec.project_id,
                "fetch_date": rec.fetch_date,
                "num_of_days": rec.num_of_days,
                "dim1_name": rec.dim1_name,
                "dim1_value": rec.dim1_value,
                "dim2_name": rec.dim2_name,
                "dim2_value": rec.dim2_value,
                "dim3_name": rec.dim3_name,
                "dim3_value": rec.dim3_value,
                "sessions": rec.sessions,
                "users": rec.users,
                "scroll_depth_pct": rec.scroll_depth_pct,
                "engagement_time_ms": rec.engagement_time_ms,
                "dead_click_count": rec.dead_click_count,
                "rage_click_count": rec.rage_click_count,
                "error_click_count": rec.error_click_count,
                "script_error_count": rec.script_error_count,
                "lcp_ms": rec.lcp_ms,
                "inp_ms": rec.inp_ms,
                "cls": rec.cls,
                "ingested_at": now,
                "dedupe_id": dedupe_id,
            })
        self._delete_keys("clarity_raw", keys)
        self._insert_rows("clarity_raw", rows)
        return len(rows)

    def upsert_clarity_kpis_daily(self, snapshot: ClarityKPISnapshot) -> int:
        self._ensure_table("clarity_kpis_daily")
        dedupe_id = self._hash_key([snapshot.snapshot_date, snapshot.snapshot_type])
        self._delete_keys("clarity_kpis_daily", [dedupe_id])
        self._insert_rows("clarity_kpis_daily", [{
            "snapshot_date": snapshot.snapshot_date,
            "snapshot_type": snapshot.snapshot_type,
            "period_days": snapshot.period_days,
            "total_sessions": snapshot.total_sessions,
            "total_users": snapshot.total_users,
            "dead_click_rate": snapshot.dead_click_rate,
            "rage_click_rate": snapshot.rage_click_rate,
            "error_click_rate": snapshot.error_click_rate,
            "script_error_rate": snapshot.script_error_rate,
            "avg_scroll_depth_pct": snapshot.avg_scroll_depth_pct,
            "avg_engagement_time_ms": snapshot.avg_engagement_time_ms,
            "avg_lcp_ms": snapshot.avg_lcp_ms,
            "avg_inp_ms": snapshot.avg_inp_ms,
            "avg_cls": snapshot.avg_cls,
            "computed_at": snapshot.computed_at,
            "dedupe_id": dedupe_id,
        }])
        return 1

    def upsert_clarity_baseline(self, baseline_rows: list[dict[str, Any]]) -> int:
        """Invalidate current baseline before inserting new one."""
        self._ensure_table("clarity_baseline")
        today = date.today().isoformat()
        self._conn.execute(
            "UPDATE clarity_baseline SET valid_until = ? WHERE valid_until IS NULL",
            [today],
        )
        now = _iso_now()
        rows = []
        keys = []
        for row in baseline_rows:
            dedupe_id = self._hash_key([row["kpi_name"], now])
            keys.append(dedupe_id)
            rows.append({
                "kpi_name": row["kpi_name"],
                "baseline_value": float(row["baseline_value"]),
                "computed_from_days": int(row["computed_from_days"]),
                "computed_at": now,
                "valid_from": today,
                "valid_until": None,
                "dedupe_id": dedupe_id,
            })
        self._insert_rows("clarity_baseline", rows)
        return len(rows)

    def query_clarity_kpis_window(self, days: int) -> list[dict[str, Any]]:
        self._ensure_table("clarity_kpis_daily")
        return self.query(f"""
            SELECT * FROM clarity_kpis_daily
            WHERE snapshot_type = 'daily'
              AND snapshot_date >= CURRENT_DATE - {int(days)}
            ORDER BY snapshot_date ASC
        """)

    def query_clarity_baseline_current(self) -> list[dict[str, Any]]:
        self._ensure_table("clarity_baseline")
        return self.query("SELECT * FROM clarity_baseline WHERE valid_until IS NULL")

    def query_clarity_raw_by_dimension(self, dim_name: str, days: int = 7) -> list[dict[str, Any]]:
        self._ensure_table("clarity_raw")
        return self.query(f"""
            SELECT * FROM clarity_raw
            WHERE dim1_name = '{dim_name}'
              AND fetch_date >= CURRENT_DATE - {int(days)}
            ORDER BY fetch_date DESC
        """)

    def clarity_already_ingested_today(self) -> bool:
        """Return True if Clarity data was already fetched today (quota guard)."""
        self._ensure_table("clarity_raw")
        result = self.query("SELECT COUNT(*) AS cnt FROM clarity_raw WHERE fetch_date = CURRENT_DATE")
        return (result[0]["cnt"] if result else 0) > 0

    def maintenance(self) -> dict:
        self._conn.execute("CHECKPOINT")
        self._conn.execute("VACUUM")
        tables = self.query("SELECT table_name, estimated_size FROM duckdb_tables()")
        return {"status": "ok", "tables": tables}
