from __future__ import annotations

from dataclasses import dataclass

# Google Play policy thresholds — exceeding these risks app demotion / reduced visibility
CRASH_RATE_THRESHOLD = 0.0109  # 1.09%
ANR_RATE_THRESHOLD = 0.0047    # 0.47%

_THRESHOLD_MAP = {
    "crashRateMetricSet": CRASH_RATE_THRESHOLD,
    "anrRateMetricSet": ANR_RATE_THRESHOLD,
}


@dataclass
class ThresholdViolation:
    metric_set: str
    current_value: float
    threshold: float
    multiple: float      # current / threshold, rounded to 1 decimal
    is_critical: bool    # multiple > 10.0


@dataclass
class TrendVelocity:
    metric: str
    current_7d_avg: float
    prev_7d_avg: float
    delta_pp: float   # delta in percentage points (not ratio)
    direction: str    # "↗ piorando" | "↘ melhorando" | "→ estável"


def check_violations(vitals: list[dict]) -> list[ThresholdViolation]:
    """Return ThresholdViolation for each metric_set that exceeds its Google Play threshold.

    Args:
        vitals: rows like {"metric_set": "crashRateMetricSet", "avg_value": 0.241}
                as returned by the vitals summary query.
    """
    violations: list[ThresholdViolation] = []
    for row in vitals:
        ms = row.get("metric_set") or ""
        threshold = _THRESHOLD_MAP.get(ms)
        if threshold is None:
            continue
        current = float(row.get("avg_value") or 0.0)
        if current <= threshold:
            continue
        multiple = round(current / threshold, 1)
        violations.append(
            ThresholdViolation(
                metric_set=ms,
                current_value=current,
                threshold=threshold,
                multiple=multiple,
                is_critical=multiple > 10.0,
            )
        )
    return violations


def format_violation_summary(violations: list[ThresholdViolation]) -> str:
    """Return markdown text summarising violations."""
    if not violations:
        return ""
    lines = ["⚠️ **ALERTA DE POLÍTICA GOOGLE PLAY**", ""]
    for v in violations:
        label = "crashRate" if "crash" in v.metric_set.lower() else "ANR rate"
        risk = "RISCO CRÍTICO DE DEMOÇÃO" if v.is_critical else "Atenção"
        lines.append(
            f"- 🚨 **{label}:** {v.current_value:.2%} → **{v.multiple}x** acima do limite "
            f"({v.threshold:.2%}) — {risk}"
        )
    return "\n".join(lines)


def calculate_trend_velocity(crash_series: list[dict]) -> TrendVelocity:
    """Calculate week-over-week trend velocity from crash_series.

    Args:
        crash_series: list of dicts with keys {date: str, avg_crash: float}
                      ordered by date (any order — will be sorted internally).
    """
    if not crash_series:
        return TrendVelocity(
            metric="crashRateMetricSet",
            current_7d_avg=0.0,
            prev_7d_avg=0.0,
            delta_pp=0.0,
            direction="→ estável",
        )

    sorted_series = sorted(crash_series, key=lambda r: str(r.get("date") or ""))
    n = len(sorted_series)
    mid = n // 2

    prev_half = sorted_series[:mid] if mid > 0 else sorted_series
    curr_half = sorted_series[mid:] if mid < n else sorted_series

    def _avg(rows: list[dict]) -> float:
        vals = [float(r.get("avg_crash") or 0.0) for r in rows]
        return sum(vals) / len(vals) if vals else 0.0

    prev_avg = _avg(prev_half)
    curr_avg = _avg(curr_half)

    # Delta in percentage points (multiply by 100 to convert fraction → pp)
    delta_pp = round((curr_avg - prev_avg) * 100, 2)

    if delta_pp > 0.5:
        direction = "↗ piorando"
    elif delta_pp < -0.5:
        direction = "↘ melhorando"
    else:
        direction = "→ estável"

    return TrendVelocity(
        metric="crashRateMetricSet",
        current_7d_avg=curr_avg,
        prev_7d_avg=prev_avg,
        delta_pp=delta_pp,
        direction=direction,
    )


def detect_regression(crash_by_version: list[dict]) -> dict:
    """Detect crash rate regression between the most recent and previous app version.

    Args:
        crash_by_version: list of dicts with keys:
            app_version, crash_avg_pct, days_with_data, first_seen, last_seen
            ordered by last_seen DESC (most recent first).
    """
    if len(crash_by_version) < 2:
        return {"has_regression": False, "details": None}

    # Sort by first_seen DESC — most recent version first
    sorted_vers = sorted(
        crash_by_version,
        key=lambda r: str(r.get("first_seen") or ""),
        reverse=True,
    )

    current = sorted_vers[0]
    previous = sorted_vers[1]

    current_crash = float(current.get("crash_avg_pct") or 0.0)
    prev_crash = float(previous.get("crash_avg_pct") or 0.0)
    delta_pp = round(current_crash - prev_crash, 2)
    pct_change = round((delta_pp / prev_crash * 100) if prev_crash else 0.0, 1)

    has_regression = delta_pp > 0

    return {
        "has_regression": has_regression,
        "current_version": current.get("app_version"),
        "current_crash": current_crash,
        "prev_version": previous.get("app_version"),
        "prev_crash": prev_crash,
        "delta_pp": delta_pp,
        "pct_change": pct_change,
    }
