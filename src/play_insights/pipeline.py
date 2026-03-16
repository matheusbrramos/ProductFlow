from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from time import perf_counter

from play_insights.clarity_analysis import (
    calculate_kpis,
    calculate_trend,
    compute_baseline,
    cross_reference_devices,
    should_recompute_baseline,
)
from play_insights.clarity_client import ClarityClient
from play_insights.config import Settings
from play_insights.duckdb_repo import DuckDBRepository
from play_insights.play_reviews_client import fetch_reviews
from play_insights.prioritization import generate_recommendations
from play_insights.report_daily import generate_daily_report
from play_insights.report_weekly import generate_weekly_report
from play_insights.reporting_client import DeveloperReportingClient
from play_insights.reply_engine import build_dry_run_queue, publish_replies
from play_insights.scoring import infer_intent, sentiment_label, severity_score
from play_insights.stats_client import StatsClient
from play_insights.voc_classifier import classify_voc, detect_event_urgency

logger = logging.getLogger(__name__)


def _repo(settings: Settings) -> DuckDBRepository:
    return DuckDBRepository(
        db_path=settings.db_path,
        memory_limit=settings.duckdb_memory_limit,
        threads=settings.duckdb_threads,
    )


def ingest_reviews(settings: Settings) -> dict:
    start = perf_counter()
    with _repo(settings) as repo:
        reviews = fetch_reviews(settings.play_package_name)
        written = repo.upsert_reviews_raw(reviews)
    elapsed = perf_counter() - start
    summary = {"fetched": len(reviews), "written": written, "elapsed_seconds": round(elapsed, 2)}
    logger.info("reviews ingest summary: %s", summary)
    return summary


def ingest_vitals(settings: Settings, days: int = 7) -> dict:
    start = perf_counter()
    client = DeveloperReportingClient(package_name=settings.play_package_name)
    crash_rows = client.query_crash_rate(days=days)
    anr_rows = client.query_anr_rate(days=days)
    try:
        slow_rendering_rows = client.query_slow_rendering(days=days)
    except Exception as exc:  # noqa: BLE001
        logger.warning("slowRendering not available (403?): %s", exc)
        slow_rendering_rows = []
    try:
        slow_start_rows = client.query_slow_start(days=days)
    except Exception as exc:  # noqa: BLE001
        logger.warning("slowStart not available (403?): %s", exc)
        slow_start_rows = []
    rows = crash_rows + anr_rows + slow_rendering_rows + slow_start_rows
    with _repo(settings) as repo:
        written = repo.upsert_vitals_daily(rows)
    elapsed = perf_counter() - start
    summary = {
        "fetched": len(rows),
        "crash_count": len(crash_rows),
        "anr_count": len(anr_rows),
        "slow_rendering_count": len(slow_rendering_rows),
        "slow_start_count": len(slow_start_rows),
        "written": written,
        "elapsed_seconds": round(elapsed, 2),
    }
    logger.info("vitals ingest summary: %s", summary)
    return summary


def ingest_errors(settings: Settings, days: int = 7) -> dict:
    start = perf_counter()
    client = DeveloperReportingClient(package_name=settings.play_package_name)
    issues = client.query_error_issues(days=days)
    with _repo(settings) as repo:
        written = repo.upsert_error_issues(issues)
    elapsed = perf_counter() - start
    summary = {"fetched": len(issues), "written": written, "elapsed_seconds": round(elapsed, 2)}
    logger.info("errors ingest summary: %s", summary)
    return summary


def ingest_stats(settings: Settings, days: int = 7) -> dict:
    if not settings.play_bq_export_dataset:
        logger.info("PLAY_BQ_EXPORT_DATASET not set — skipping stats ingestion.")
        return {"skipped": True, "reason": "PLAY_BQ_EXPORT_DATASET not configured"}
    if not settings.gcp_project_id:
        logger.warning("GCP_PROJECT_ID not set — cannot query BQ export for stats.")
        return {"skipped": True, "reason": "GCP_PROJECT_ID not configured"}
    start = perf_counter()
    client = StatsClient(project_id=settings.gcp_project_id, export_dataset=settings.play_bq_export_dataset)
    records = client.query_install_stats(days=days)
    with _repo(settings) as repo:
        written = repo.upsert_stats_daily(records)
    elapsed = perf_counter() - start
    summary = {"fetched": len(records), "written": written, "elapsed_seconds": round(elapsed, 2)}
    logger.info("stats ingest summary: %s", summary)
    return summary


def ingest_clarity(settings: Settings) -> dict:
    """Fetch data from Microsoft Clarity API and persist to DuckDB.

    Returns {"skipped": True} if clarity_enabled=False or token missing.
    The quota guard prevents double-fetching on the same calendar day.
    """
    if not settings.clarity_enabled:
        logger.info("CLARITY_ENABLED=false — skipping Clarity ingestion.")
        return {"skipped": True, "reason": "CLARITY_ENABLED not configured"}
    if not settings.clarity_project_id or not settings.clarity_api_token:
        logger.warning("CLARITY_PROJECT_ID or CLARITY_API_TOKEN not set — skipping.")
        return {"skipped": True, "reason": "Clarity credentials not configured"}

    with _repo(settings) as repo:
        if repo.clarity_already_ingested_today():
            logger.info("Clarity data already ingested today — skipping (quota guard).")
            return {"skipped": True, "reason": "already ingested today"}

    start = perf_counter()
    client = ClarityClient(
        project_id=settings.clarity_project_id,
        api_token=settings.clarity_api_token,
    )
    rows = client.fetch_all_batches(num_of_days=settings.clarity_num_days)

    with _repo(settings) as repo:
        written_raw = repo.upsert_clarity_raw(rows)
        if rows:
            snapshot = calculate_kpis(rows)
            repo.upsert_clarity_kpis_daily(snapshot)
            written_kpis = 1
        else:
            written_kpis = 0

    elapsed = perf_counter() - start
    summary = {
        "fetched": len(rows),
        "requests_made": client._requests_made,
        "written_raw": written_raw,
        "written_kpis": written_kpis,
        "elapsed_seconds": round(elapsed, 2),
    }
    logger.info("Clarity ingest summary: %s", summary)
    return summary


def analyze_clarity(settings: Settings, window_days: int = 7) -> dict:
    """Calculate Clarity KPI trends and cross-reference with Play vitals."""
    if not settings.clarity_enabled:
        return {"skipped": True, "reason": "CLARITY_ENABLED not configured"}

    with _repo(settings) as repo:
        current_rows = repo.query_clarity_kpis_window(days=window_days)
        previous_rows = repo.query_clarity_kpis_window(days=window_days * 2)
        baseline_rows = repo.query_clarity_baseline_current()
        device_clarity_rows = repo.query_clarity_raw_by_dimension("Device", days=window_days)
        play_vitals = repo.query(f"""
            SELECT device_model, AVG(metric_value) AS metric_value
            FROM vitals_daily
            WHERE metric_set = 'crashRateMetricSet'
              AND date >= CURRENT_DATE - {int(window_days)}
              AND device_model IS NOT NULL
            GROUP BY device_model
            ORDER BY metric_value DESC
            LIMIT 20
        """)

        # Build current and previous KPI snapshots from daily rows
        from play_insights.models import ClarityKPISnapshot

        def _latest_snapshot(rows: list[dict]) -> ClarityKPISnapshot | None:
            if not rows:
                return None
            r = rows[-1]
            return ClarityKPISnapshot(
                snapshot_date=str(r.get("snapshot_date", ""))[:10],
                snapshot_type=str(r.get("snapshot_type", "daily")),
                period_days=int(r.get("period_days") or 0),
                total_sessions=int(r.get("total_sessions") or 0),
                total_users=int(r.get("total_users") or 0),
                dead_click_rate=float(r.get("dead_click_rate") or 0.0),
                rage_click_rate=float(r.get("rage_click_rate") or 0.0),
                error_click_rate=float(r.get("error_click_rate") or 0.0),
                script_error_rate=float(r.get("script_error_rate") or 0.0),
                avg_scroll_depth_pct=float(r.get("avg_scroll_depth_pct") or 0.0),
                avg_engagement_time_ms=float(r.get("avg_engagement_time_ms") or 0.0),
                avg_lcp_ms=float(r.get("avg_lcp_ms") or 0.0),
                avg_inp_ms=float(r.get("avg_inp_ms") or 0.0),
                avg_cls=float(r.get("avg_cls") or 0.0),
                computed_at=datetime.now(tz=timezone.utc).isoformat(),
            )

        current_snapshot = _latest_snapshot(current_rows)
        # Previous = oldest snapshot from the double window (before current window)
        cutoff = window_days
        prev_only = [r for r in previous_rows if r not in current_rows]
        previous_snapshot = _latest_snapshot(prev_only)

        if current_snapshot is None:
            return {"skipped": True, "reason": "No Clarity KPI data available yet"}

        trend_report = calculate_trend(current_snapshot, previous_snapshot, baseline_rows)
        cross_ref = cross_reference_devices(device_clarity_rows, play_vitals)

        # Auto-recompute baseline if needed
        available_days = len(current_rows)
        if should_recompute_baseline(baseline_rows, available_days):
            all_kpi_rows = repo.query_clarity_kpis_window(days=90)
            new_baseline = compute_baseline(all_kpi_rows)
            if new_baseline:
                repo.upsert_clarity_baseline(new_baseline)
                logger.info("Clarity baseline recomputed from %d days.", len(all_kpi_rows))
                baseline_rows = repo.query_clarity_baseline_current()
                trend_report = calculate_trend(current_snapshot, previous_snapshot, baseline_rows)

    return {
        "current_kpis": {
            "snapshot_date": current_snapshot.snapshot_date,
            "total_sessions": current_snapshot.total_sessions,
            "total_users": current_snapshot.total_users,
            "rage_click_rate": current_snapshot.rage_click_rate,
            "dead_click_rate": current_snapshot.dead_click_rate,
            "error_click_rate": current_snapshot.error_click_rate,
            "script_error_rate": current_snapshot.script_error_rate,
            "avg_scroll_depth_pct": current_snapshot.avg_scroll_depth_pct,
            "avg_engagement_time_ms": current_snapshot.avg_engagement_time_ms,
            "avg_lcp_ms": current_snapshot.avg_lcp_ms,
            "avg_inp_ms": current_snapshot.avg_inp_ms,
            "avg_cls": current_snapshot.avg_cls,
        },
        "trend_report": {
            "period_label": trend_report.period_label,
            "baseline_available": trend_report.baseline_available,
            "alerts": trend_report.alerts,
            "kpi_trends": [
                {
                    "kpi": t.kpi_name,
                    "current": t.current_value,
                    "previous": t.previous_value,
                    "baseline": t.baseline_value,
                    "vs_previous": t.trend_vs_previous,
                    "vs_baseline": t.trend_vs_baseline,
                    "is_alert": t.is_alert,
                }
                for t in trend_report.kpi_trends
            ],
        },
        "cross_reference": [
            {
                "device": c.device_name,
                "crash_rate_play": c.crash_rate_play,
                "rage_click_rate_clarity": c.rage_click_rate_clarity,
                "risk_score": c.combined_risk_score,
                "sessions": c.sessions_clarity,
            }
            for c in cross_ref
        ],
    }


def compute_clarity_baseline(settings: Settings, force: bool = False) -> dict:
    """(Re)compute Clarity baseline from all available historical KPI data."""
    if not settings.clarity_enabled:
        return {"skipped": True, "reason": "CLARITY_ENABLED not configured"}

    with _repo(settings) as repo:
        existing = repo.query_clarity_baseline_current()
        available = repo.query_clarity_kpis_window(days=365)
        if not available:
            return {"skipped": True, "reason": "No Clarity KPI history available yet"}
        if existing and not force:
            return {"skipped": True, "reason": "Baseline already exists — use --force to recompute"}
        new_baseline = compute_baseline(available)
        if not new_baseline:
            return {"skipped": True, "reason": "Not enough data to compute baseline"}
        repo.upsert_clarity_baseline(new_baseline)

    return {
        "computed": True,
        "days_used": len(available),
        "kpis_computed": len(new_baseline),
    }


def ingest_all(settings: Settings, days: int = 7) -> dict:
    started = perf_counter()
    failures: list[str] = []
    results = {}

    for label, fn in [
        ("reviews", lambda: ingest_reviews(settings)),
        ("vitals", lambda: ingest_vitals(settings, days=days)),
        ("errors", lambda: ingest_errors(settings, days=days)),
        ("stats", lambda: ingest_stats(settings, days=days)),
        ("clarity", lambda: ingest_clarity(settings)),
    ]:
        try:
            results[label] = fn()
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: {exc}")
            logger.exception("failed ingestion step: %s", label)

    elapsed = perf_counter() - started
    summary = {
        "results": results,
        "failures": failures,
        "elapsed_seconds": round(elapsed, 2),
    }
    if failures:
        raise RuntimeError(f"Partial ingestion failure: {summary}")
    return summary




def analyze(settings: Settings, window_days: int = 7) -> dict:
    with _repo(settings) as repo:
        reviews = repo.query(
            f"""
            SELECT review_id, star_rating, comment_text
            FROM reviews_raw
            WHERE ingest_date >= CURRENT_DATE - {int(window_days)}
            """
        )
        enriched_rows = []
        for row in reviews:
            text = row.get("comment_text") or ""
            category_result = classify_voc(text)
            sentiment = sentiment_label(text, row.get("star_rating"))
            severity = severity_score(text, row.get("star_rating"), category_result.complaint_category)
            intent = infer_intent(text, category_result.complaint_category, row.get("star_rating"))
            event_urgency = detect_event_urgency(text)
            enriched_rows.append(
                {
                    "review_id": row["review_id"],
                    "sentiment_label": sentiment,
                    "complaint_category": category_result.complaint_category,
                    "severity": severity,
                    "intent": intent,
                    "topic_keywords": category_result.topic_keywords,
                    "confidence": category_result.confidence,
                    "source_comment_text": text,
                    "event_urgency": event_urgency,
                }
            )
        enriched_written = repo.upsert_reviews_enriched(enriched_rows)
        recommendations = generate_recommendations(repo, window_days=window_days)
        rec_written = repo.upsert_recommendations(recommendations)
    return {
        "enriched_written": enriched_written,
        "recommendations_written": rec_written,
        "top_recommendations": recommendations[:5],
    }


def generate_report(settings: Settings, mode: str) -> dict:
    with _repo(settings) as repo:
        if mode == "daily":
            recs = repo.query(
                """
                SELECT *
                FROM recommendations
                WHERE date = CURRENT_DATE
                ORDER BY expected_impact_score DESC
                """
            )
            markdown_path, json_path = generate_daily_report(repo=repo, recommendations=recs)
            return {"mode": mode, "markdown_path": str(markdown_path), "json_path": str(json_path)}

        if mode == "weekly":
            clarity_data = None
            if settings.clarity_enabled:
                try:
                    clarity_data = analyze_clarity(settings)
                    if clarity_data.get("skipped"):
                        clarity_data = None
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Clarity analysis failed — report will proceed without it: %s", exc)
                    clarity_data = None
            markdown_path = generate_weekly_report(repo=repo, clarity_data=clarity_data)
            return {"mode": mode, "markdown_path": str(markdown_path)}

    raise ValueError(f"Unsupported report mode: {mode}")


def handle_reply(settings: Settings, mode: str) -> dict:
    with _repo(settings) as repo:
        queue, queue_path = build_dry_run_queue(repo=repo)
        if mode == "dry-run":
            return {"mode": mode, "queue_size": len(queue), "queue_path": str(queue_path)}

        settings.validate_publish_mode()
        published = publish_replies(
            package_name=settings.play_package_name,
            queue=queue,
            repo=repo,
            approval_token=settings.reply_publish_approval_token,
        )
    return {
        "mode": mode,
        "queue_size": len(queue),
        "published": published,
        "queue_path": str(queue_path),
    }
