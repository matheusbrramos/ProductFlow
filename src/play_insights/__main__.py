from __future__ import annotations

import argparse
import json
import logging
import sys

from play_insights.config import ConfigError, Settings
from play_insights.logging_utils import setup_logging
from play_insights.duckdb_repo import DuckDBRepository
from play_insights.pipeline import (
    analyze,
    analyze_clarity,
    compute_clarity_baseline,
    generate_report,
    handle_reply,
    ingest_all,
    ingest_clarity,
    ingest_errors,
    ingest_reviews,
    ingest_stats,
    ingest_vitals,
)


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="play_insights", description="Google Play intelligence pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest-reviews")
    vitals_parser = sub.add_parser("ingest-vitals")
    vitals_parser.add_argument("--days", type=int, default=7)
    errors_parser = sub.add_parser("ingest-errors")
    errors_parser.add_argument("--days", type=int, default=7)
    stats_parser = sub.add_parser("ingest-stats")
    stats_parser.add_argument("--days", type=int, default=7)
    ingest_parser = sub.add_parser("ingest")
    ingest_parser.add_argument("--days", type=int, default=7)

    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("--window", default="7d")

    report_parser = sub.add_parser("report")
    report_parser.add_argument("--mode", choices=["daily", "weekly"], required=True)

    reply_parser = sub.add_parser("reply")
    reply_parser.add_argument("--mode", choices=["dry-run", "publish"], required=True)

    sub.add_parser("ingest-clarity")

    analyze_clarity_parser = sub.add_parser("analyze-clarity")
    analyze_clarity_parser.add_argument("--window", default="7d")

    baseline_parser = sub.add_parser("clarity-baseline")
    baseline_parser.add_argument("--force", action="store_true")

    sub.add_parser("maintenance")

    return parser


def _parse_window_days(window: str) -> int:
    normalized = window.strip().lower()
    if normalized.endswith("d"):
        return int(normalized[:-1])
    return int(normalized)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2

    setup_logging(settings.log_level)
    logger = logging.getLogger("play_insights")

    try:
        if args.command == "ingest-reviews":
            _print_json(ingest_reviews(settings))
            return 0
        if args.command == "ingest-vitals":
            _print_json(ingest_vitals(settings, days=args.days))
            return 0
        if args.command == "ingest-errors":
            _print_json(ingest_errors(settings, days=args.days))
            return 0
        if args.command == "ingest-stats":
            _print_json(ingest_stats(settings, days=args.days))
            return 0
        if args.command == "ingest":
            _print_json(ingest_all(settings, days=args.days))
            return 0
        if args.command == "analyze":
            days = _parse_window_days(args.window)
            _print_json(analyze(settings, window_days=days))
            return 0
        if args.command == "report":
            _print_json(generate_report(settings, mode=args.mode))
            return 0
        if args.command == "reply":
            _print_json(handle_reply(settings, mode=args.mode))
            return 0
        if args.command == "ingest-clarity":
            _print_json(ingest_clarity(settings))
            return 0
        if args.command == "analyze-clarity":
            days = _parse_window_days(args.window)
            _print_json(analyze_clarity(settings, window_days=days))
            return 0
        if args.command == "clarity-baseline":
            _print_json(compute_clarity_baseline(settings, force=args.force))
            return 0
        if args.command == "maintenance":
            with DuckDBRepository(
                db_path=settings.db_path,
                memory_limit=settings.duckdb_memory_limit,
                threads=settings.duckdb_threads,
            ) as repo:
                result = repo.maintenance()
            _print_json(result)
            return 0
        parser.print_help()
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.exception("command failed")
        print(f"Command failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

