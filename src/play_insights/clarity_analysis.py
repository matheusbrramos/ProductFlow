"""Clarity analytics: KPI calculation, trend detection, baseline management, and cross-reference with Play vitals."""
from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from play_insights.models import ClarityKPISnapshot, ClarityRow

logger = logging.getLogger(__name__)

# KPI thresholds for alert generation
KPI_THRESHOLDS: dict[str, dict[str, float]] = {
    "rage_click_rate":      {"target": 0.02, "alert": 0.04},
    "dead_click_rate":      {"target": 0.05, "alert": 0.10},
    "error_click_rate":     {"target": 0.01, "alert": 0.03},
    "script_error_rate":    {"target": 0.005, "alert": 0.02},
    "avg_scroll_depth_pct": {"target": 50.0, "alert": 30.0},   # alert if BELOW
    "avg_engagement_time_ms": {"target": 60_000, "alert": 20_000},  # alert if BELOW
    "avg_lcp_ms":  {"target": 2_500, "alert": 4_000},
    "avg_inp_ms":  {"target": 200,   "alert": 500},
    "avg_cls":     {"target": 0.10,  "alert": 0.25},
}

# KPIs where LOWER is better (alert fires when value is ABOVE threshold)
_LOWER_IS_BETTER = {
    "rage_click_rate", "dead_click_rate", "error_click_rate", "script_error_rate",
    "avg_lcp_ms", "avg_inp_ms", "avg_cls",
}
# KPIs where HIGHER is better (alert fires when value is BELOW threshold)
_HIGHER_IS_BETTER = {"avg_scroll_depth_pct", "avg_engagement_time_ms"}

# Trend stability threshold: changes <= ±10% are considered stable
_STABLE_PCT_THRESHOLD = 10.0


@dataclass
class KPITrendItem:
    kpi_name: str
    current_value: float
    previous_value: float | None       # same KPI last week
    baseline_value: float | None       # long-run median
    delta_vs_previous_pct: float | None
    delta_vs_baseline_pct: float | None
    trend_vs_previous: str             # "↑" | "↓" | "→" | "N/A"
    trend_vs_baseline: str
    is_alert: bool                     # current value violates alert threshold


@dataclass
class DeviceCrossRef:
    device_name: str
    crash_rate_play: float | None       # crash_rate from Play vitals
    rage_click_rate_clarity: float | None
    combined_risk_score: float          # crash_rate * rage_click_rate * 100
    sessions_clarity: int | None


@dataclass
class ClarityTrendReport:
    generated_at: str
    period_label: str
    kpi_trends: list[KPITrendItem] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)    # human-readable alert messages
    baseline_available: bool = False
    baseline_days: int = 0


def calculate_kpis(rows: list[ClarityRow], snapshot_date: str | None = None) -> ClarityKPISnapshot:
    """Aggregate list[ClarityRow] → ClarityKPISnapshot for the given period."""
    if not snapshot_date:
        snapshot_date = date.today().isoformat()

    total_sessions = sum(r.sessions or 0 for r in rows)
    total_users = sum(r.users or 0 for r in rows)

    def _rate(count_attr: str) -> float:
        if total_sessions == 0:
            return 0.0
        total = sum(getattr(r, count_attr) or 0 for r in rows)
        return round(total / total_sessions, 6)

    def _weighted_avg(value_attr: str) -> float:
        """Sessions-weighted average, ignoring rows with None value."""
        pairs = [(getattr(r, value_attr), r.sessions or 0) for r in rows if getattr(r, value_attr) is not None]
        total_w = sum(s for _, s in pairs)
        if not total_w:
            return 0.0
        return round(sum(v * s for v, s in pairs) / total_w, 4)

    return ClarityKPISnapshot(
        snapshot_date=snapshot_date,
        snapshot_type="daily",
        period_days=rows[0].num_of_days if rows else 0,
        total_sessions=total_sessions,
        total_users=total_users,
        dead_click_rate=_rate("dead_click_count"),
        rage_click_rate=_rate("rage_click_count"),
        error_click_rate=_rate("error_click_count"),
        script_error_rate=_rate("script_error_count"),
        avg_scroll_depth_pct=_weighted_avg("scroll_depth_pct"),
        avg_engagement_time_ms=_weighted_avg("engagement_time_ms"),
        avg_lcp_ms=_weighted_avg("lcp_ms"),
        avg_inp_ms=_weighted_avg("inp_ms"),
        avg_cls=_weighted_avg("cls"),
        computed_at=datetime.now(tz=timezone.utc).isoformat(),
    )


def _kpi_fields() -> list[str]:
    return [
        "dead_click_rate", "rage_click_rate", "error_click_rate", "script_error_rate",
        "avg_scroll_depth_pct", "avg_engagement_time_ms",
        "avg_lcp_ms", "avg_inp_ms", "avg_cls",
    ]


def _pct_delta(current: float, reference: float) -> float | None:
    if reference == 0:
        return None
    return round((current - reference) / reference * 100, 2)


def _trend_direction(pct_delta: float | None, kpi_name: str) -> str:
    if pct_delta is None:
        return "N/A"
    if abs(pct_delta) <= _STABLE_PCT_THRESHOLD:
        return "→"
    if kpi_name in _LOWER_IS_BETTER:
        return "↑ piorando" if pct_delta > 0 else "↓ melhorando"
    return "↑ melhorando" if pct_delta > 0 else "↓ piorando"


def _is_alert(kpi_name: str, value: float) -> bool:
    thresholds = KPI_THRESHOLDS.get(kpi_name)
    if not thresholds:
        return False
    alert_threshold = thresholds["alert"]
    if kpi_name in _LOWER_IS_BETTER:
        return value > alert_threshold
    return value < alert_threshold


def calculate_trend(
    current: ClarityKPISnapshot,
    previous: ClarityKPISnapshot | None,
    baseline_rows: list[dict[str, Any]] | None,
) -> ClarityTrendReport:
    """Calculate trend deltas vs. previous week and vs. baseline."""
    now = datetime.now(tz=timezone.utc).isoformat()
    baseline_map = {r["kpi_name"]: float(r["baseline_value"]) for r in (baseline_rows or [])}
    baseline_available = bool(baseline_map)

    trends: list[KPITrendItem] = []
    alerts: list[str] = []

    for kpi in _kpi_fields():
        cur_val = getattr(current, kpi, 0.0) or 0.0
        prev_val = getattr(previous, kpi, None) if previous else None
        base_val = baseline_map.get(kpi)

        d_prev = _pct_delta(cur_val, prev_val) if prev_val is not None else None
        d_base = _pct_delta(cur_val, base_val) if base_val is not None else None

        alert = _is_alert(kpi, cur_val)
        if alert:
            threshold = KPI_THRESHOLDS[kpi]["alert"]
            direction = "acima" if kpi in _LOWER_IS_BETTER else "abaixo"
            alerts.append(
                f"{kpi} em {cur_val:.4f} — {direction} do threshold de alerta ({threshold})"
            )

        trends.append(KPITrendItem(
            kpi_name=kpi,
            current_value=cur_val,
            previous_value=prev_val,
            baseline_value=base_val,
            delta_vs_previous_pct=d_prev,
            delta_vs_baseline_pct=d_base,
            trend_vs_previous=_trend_direction(d_prev, kpi),
            trend_vs_baseline=_trend_direction(d_base, kpi),
            is_alert=alert,
        ))

    return ClarityTrendReport(
        generated_at=now,
        period_label=f"{current.snapshot_date} (janela {current.period_days}d)",
        kpi_trends=trends,
        alerts=alerts,
        baseline_available=baseline_available,
        baseline_days=len(baseline_rows) if baseline_rows else 0,
    )


# Rough device name normalization for cross-reference matching
def _normalize_device(name: str) -> str:
    return name.lower().replace("-", " ").replace("_", " ").replace("/", " ").strip()


def cross_reference_devices(
    clarity_rows: list[dict[str, Any]],   # rows from query_clarity_raw_by_dimension("Device")
    play_vitals: list[dict[str, Any]],     # crash_by_device rows from DuckDB
) -> list[DeviceCrossRef]:
    """Cross-reference devices with crashes in Play vs. rage/error clicks in Clarity.

    Returns list ordered by combined_risk_score DESC (top offenders first).
    """
    # Build Clarity device map: device_name → aggregated metrics
    clarity_map: dict[str, dict[str, Any]] = {}
    for row in clarity_rows:
        device = row.get("dim1_value") or ""
        if not device:
            continue
        key = _normalize_device(device)
        if key not in clarity_map:
            clarity_map[key] = {"sessions": 0, "rage_clicks": 0, "original": device}
        clarity_map[key]["sessions"] += int(row.get("sessions") or 0)
        clarity_map[key]["rage_clicks"] += int(row.get("rage_click_count") or 0)

    # Build Play vitals map: device_model → avg crash_rate
    play_map: dict[str, float] = {}
    for row in play_vitals:
        device = row.get("device_model") or ""
        if not device:
            continue
        key = _normalize_device(device)
        val = float(row.get("metric_value") or 0.0)
        if key not in play_map or val > play_map[key]:
            play_map[key] = val

    refs: list[DeviceCrossRef] = []

    # Match Clarity devices with Play devices (substring match for robustness)
    for c_key, c_data in clarity_map.items():
        sessions = c_data["sessions"]
        rage_clicks = c_data["rage_clicks"]
        rage_rate = rage_clicks / sessions if sessions > 0 else 0.0

        # Find best matching Play device
        crash_rate: float | None = None
        for p_key, p_crash in play_map.items():
            if c_key in p_key or p_key in c_key or _tokens_overlap(c_key, p_key):
                if crash_rate is None or p_crash > crash_rate:
                    crash_rate = p_crash

        combined = round((crash_rate or 0.0) * rage_rate * 100, 6)
        refs.append(DeviceCrossRef(
            device_name=c_data["original"],
            crash_rate_play=crash_rate,
            rage_click_rate_clarity=rage_rate,
            combined_risk_score=combined,
            sessions_clarity=sessions,
        ))

    refs.sort(key=lambda x: x.combined_risk_score, reverse=True)
    return refs[:10]  # top 10 only


def _tokens_overlap(a: str, b: str) -> bool:
    ta = set(a.split())
    tb = set(b.split())
    return bool(ta & tb) and len(ta & tb) >= 1


def compute_baseline(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute baseline as median per KPI from historical clarity_kpis_daily rows.

    Uses median (not mean) for robustness against outlier days (e.g., incidents).
    Returns list of {kpi_name, baseline_value, computed_from_days}.
    """
    if not rows:
        return []

    kpi_values: dict[str, list[float]] = {k: [] for k in _kpi_fields()}
    for row in rows:
        for kpi in _kpi_fields():
            v = row.get(kpi)
            if v is not None:
                try:
                    kpi_values[kpi].append(float(v))
                except (TypeError, ValueError):
                    pass

    n_days = len(rows)
    result = []
    for kpi, values in kpi_values.items():
        if not values:
            continue
        baseline_value = statistics.median(values)
        result.append({
            "kpi_name": kpi,
            "baseline_value": round(baseline_value, 6),
            "computed_from_days": n_days,
        })
    logger.info("Baseline computed from %d days for %d KPIs.", n_days, len(result))
    return result


def should_recompute_baseline(
    baseline_rows: list[dict[str, Any]],
    available_days: int,
    min_days_for_baseline: int = 7,
) -> bool:
    """Return True if baseline should be (re)computed.

    Triggers:
    - No baseline exists
    - Available days >= min_days_for_baseline and no baseline yet
    - available_days grew by >= 7 since last baseline (handled externally by pipeline)
    """
    if not baseline_rows:
        return available_days >= min_days_for_baseline
    return False  # auto-recompute logic in pipeline.py via age check
