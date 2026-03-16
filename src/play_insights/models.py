from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReviewRecord:
    review_id: str
    star_rating: int | None
    comment_text: str
    app_version_name: str | None
    app_version_code: str | None
    reviewer_language: str | None
    last_modified_at: datetime | None


@dataclass
class VitalsRecord:
    date: str
    metric_set: str
    metric_value: float
    package_name: str
    app_version: str | None = None
    country: str | None = None
    device_model: str | None = None
    os_version: str | None = None


@dataclass
class ErrorIssueRecord:
    issue_id: str
    issue_title: str
    error_type: str | None
    affected_users: float | None
    app_version: str | None
    device_model: str | None
    os_version: str | None
    first_seen: str | None
    last_seen: str | None


@dataclass
class StatsRecord:
    date: str
    country: str | None
    installs: int | None
    uninstalls: int | None
    active_devices: int | None


@dataclass
class ClarityRow:
    """Raw row returned by the Microsoft Clarity Data Export API (one row per dimension combination)."""

    project_id: str
    fetch_date: str                    # YYYY-MM-DD — date of ingest
    num_of_days: int                   # window requested (1, 2, or 3)
    dim1_name: str | None
    dim1_value: str | None
    dim2_name: str | None
    dim2_value: str | None
    dim3_name: str | None
    dim3_value: str | None
    sessions: int | None
    users: int | None
    scroll_depth_pct: float | None
    engagement_time_ms: float | None
    dead_click_count: int | None
    rage_click_count: int | None
    error_click_count: int | None
    script_error_count: int | None
    lcp_ms: float | None               # Largest Contentful Paint
    inp_ms: float | None               # Interaction to Next Paint
    cls: float | None                  # Cumulative Layout Shift


@dataclass
class ClarityKPISnapshot:
    """Calculated KPIs for a period — may be daily, weekly, or baseline."""

    snapshot_date: str                 # YYYY-MM-DD
    snapshot_type: str                 # "daily" | "baseline"
    period_days: int
    total_sessions: int
    total_users: int
    dead_click_rate: float             # dead_clicks / sessions
    rage_click_rate: float
    error_click_rate: float
    script_error_rate: float
    avg_scroll_depth_pct: float
    avg_engagement_time_ms: float
    avg_lcp_ms: float
    avg_inp_ms: float
    avg_cls: float
    computed_at: str                   # ISO timestamp

