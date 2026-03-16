"""
One-time baseline report generator.

Generates baseline reports covering the maximum available historical window (90 days).
Output files are saved with the suffix '-baseline' to distinguish from daily/weekly runs.

Usage:
    python scripts/generate_baseline.py

Prerequisites:
    python -m play_insights ingest --days 90
    python -m play_insights analyze --window 90d
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from the project root without installing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from play_insights.config import Settings  # noqa: E402
from play_insights.duckdb_repo import DuckDBRepository
from play_insights.report_daily import generate_daily_report
from play_insights.report_weekly import generate_weekly_report

BASELINE_WINDOW = 90  # days — max practical window for Play Developer Reporting API


def main() -> None:
    settings = Settings.from_env()
    repo = DuckDBRepository(db_path=settings.db_path)

    # Fetch recommendations already computed for today (from analyze --window 90d)
    recommendations = repo.query("""
        SELECT *
        FROM recommendations
        WHERE date = CURRENT_DATE
        ORDER BY expected_impact_score DESC
    """)

    print(f"Generating baseline reports — window: {BASELINE_WINDOW} days")
    print(f"Recommendations found: {len(recommendations)}")

    daily_path, json_path = generate_daily_report(
        repo=repo,
        recommendations=recommendations,
        window=BASELINE_WINDOW,
        output_suffix="-baseline",
    )
    print(f"Daily baseline:  {daily_path}")
    print(f"JSON baseline:   {json_path}")

    weekly_path = generate_weekly_report(
        repo=repo,
        window=BASELINE_WINDOW,
        output_suffix="-baseline",
    )
    print(f"Weekly baseline: {weekly_path}")
    print("\nDone. These files represent the historical baseline of the app.")


if __name__ == "__main__":
    main()
