"""Microsoft Clarity Data Export API client.

Endpoint: GET https://www.clarity.ms/export-data/api/v1/project-live-insights
Auth: Bearer JWT token generated in Clarity Settings → Data Export.

Limitations (as of 2026):
- Max 10 requests per project per day.
- numOfDays: 1, 2, or 3 (no historical data beyond 3 days per call).
- Max 1,000 rows per response (no pagination).
- MAX_REQUESTS_PER_RUN = 6 leaves a buffer of 4 for ad-hoc use.
"""
from __future__ import annotations

import logging
import time
from datetime import date
from typing import Any

import requests

from play_insights.models import ClarityRow
from play_insights.retry import retry_call

logger = logging.getLogger(__name__)

BASE_URL = "https://www.clarity.ms/export-data/api/v1/project-live-insights"
MAX_REQUESTS_PER_RUN = 6

# Ordered list of (dim1, dim2, dim3) dimension combos to fetch each run.
# Costs exactly 6 requests — within the 10/day budget.
DEFAULT_DIMENSION_BATCHES: list[tuple[str | None, str | None, str | None]] = [
    ("Device", "OS", None),           # cross-ref with Play vitals
    ("Device", "Country", None),       # filter BR vs. others
    ("URL", None, None),               # pages with most problems (checkout)
    ("Channel", None, None),           # rage clicks by acquisition channel
    ("OS", None, None),                # trend by OS (iOS vs. Android web)
    ("Source", "Medium", None),        # traffic quality by campaign
]

# Keys that appear in every information row but are NOT dimension values.
# Any key NOT in this set is treated as a dimension value.
_INFO_METRIC_KEYS: frozenset[str] = frozenset({
    "sessionsCount", "totalSessionCount", "totalBotSessionCount",
    "distantUserCount", "PagesPerSessionPercentage",
    "sessionsWithMetricPercentage", "sessionsWithoutMetricPercentage",
    "pagesViews", "subTotal",
})

# metricName → ClarityRow field for click-count metrics (value = subTotal)
_CLICK_METRIC_MAP: dict[str, str] = {
    "DeadClickCount": "dead_click_count",
    "RageClickCount": "rage_click_count",
    "ErrorClickCount": "error_click_count",
    "ScriptErrorCount": "script_error_count",
}


class ClarityClient:
    def __init__(self, project_id: str, api_token: str, timeout_seconds: int = 30):
        self.project_id = project_id
        self._api_token = api_token
        self.timeout_seconds = timeout_seconds
        self._requests_made = 0

    def fetch(
        self,
        num_of_days: int,
        dimension1: str | None = None,
        dimension2: str | None = None,
        dimension3: str | None = None,
    ) -> list[ClarityRow]:
        """Fetch one batch from the Clarity API and return parsed ClarityRow list."""
        if self._requests_made >= MAX_REQUESTS_PER_RUN:
            logger.warning(
                "ClarityClient: MAX_REQUESTS_PER_RUN=%d reached — skipping additional fetch.",
                MAX_REQUESTS_PER_RUN,
            )
            return []

        num_of_days = max(1, min(3, num_of_days))
        params: dict[str, Any] = {
            "projectId": self.project_id,
            "numOfDays": num_of_days,
        }
        if dimension1:
            params["dimension1"] = dimension1
        if dimension2:
            params["dimension2"] = dimension2
        if dimension3:
            params["dimension3"] = dimension3

        def _do_request() -> dict[str, Any]:
            response = requests.get(
                BASE_URL,
                params=params,
                headers={"Authorization": f"Bearer {self._api_token}"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

        try:
            raw = retry_call(
                _do_request,
                retries=3,
                base_delay_seconds=2.0,
                retryable=lambda exc: isinstance(exc, requests.HTTPError)
                and exc.response is not None
                and exc.response.status_code in {429, 500, 502, 503, 504},
            )
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 401:
                logger.warning(
                    "Clarity token invalid or expired (401). "
                    "Regenerate it at Settings → Data Export in the Clarity dashboard."
                )
                return []
            raise

        self._requests_made += 1
        rows = self._parse_rows(raw, num_of_days, dimension1, dimension2, dimension3)
        if len(rows) >= 1000:
            logger.warning(
                "Clarity fetch returned 1000 rows (API max) — results may be truncated. "
                "Consider narrowing the dimension filter."
            )
        return rows

    def fetch_all_batches(self, num_of_days: int) -> list[ClarityRow]:
        """Execute all DEFAULT_DIMENSION_BATCHES and return combined rows."""
        all_rows: list[ClarityRow] = []
        for dim1, dim2, dim3 in DEFAULT_DIMENSION_BATCHES:
            rows = self.fetch(num_of_days, dimension1=dim1, dimension2=dim2, dimension3=dim3)
            all_rows.extend(rows)
            if rows:
                time.sleep(0.5)  # polite pacing; avoids rate limit bursts
        logger.info(
            "Clarity fetch_all_batches: %d total rows from %d requests.",
            len(all_rows),
            self._requests_made,
        )
        return all_rows

    def _parse_rows(
        self,
        raw: Any,
        num_of_days: int,
        dim1: str | None,
        dim2: str | None,
        dim3: str | None,
    ) -> list[ClarityRow]:
        """Parse the Clarity API response into ClarityRow list.

        The API returns a list of metric objects:
            [{"metricName": "DeadClickCount", "information": [{...}, ...]}, ...]

        Each information row contains metric values (sessionsCount, subTotal, etc.)
        PLUS the dimension values as direct keys (e.g. "Device": "Mobile").

        We pivot from metric-centric to dimension-combination-centric, producing
        one ClarityRow per unique dimension combination per batch.
        """
        fetch_date = date.today().isoformat()
        metric_list = raw if isinstance(raw, list) else raw.get("data", raw.get("rows", []))
        if not metric_list:
            return []

        metric_names_seen = [m.get("metricName") for m in metric_list if isinstance(m, dict)]
        logger.debug("Clarity batch metric names: %s", metric_names_seen)

        # Accumulate per unique dimension combination
        dim_data: dict[frozenset, dict[str, Any]] = {}

        for metric_obj in metric_list:
            if not isinstance(metric_obj, dict):
                continue
            metric_name: str = metric_obj.get("metricName", "")
            information: list = metric_obj.get("information", [])

            for info_row in information:
                if not isinstance(info_row, dict):
                    continue

                # Dimension values = any key not in the known metric-key set
                dim_vals = {k: str(v) for k, v in info_row.items() if k not in _INFO_METRIC_KEYS}
                dim_key = frozenset(dim_vals.items())

                if dim_key not in dim_data:
                    dim_data[dim_key] = {"_dim_vals": dim_vals}
                entry = dim_data[dim_key]

                if metric_name == "Traffic":
                    # Traffic metric carries authoritative session/user counts
                    sessions = self._int(info_row, "totalSessionCount", "sessionsCount")
                    users = self._int(info_row, "distantUserCount", "userCount")
                    if sessions is not None:
                        entry["sessions"] = sessions  # overrides click-metric fallback
                    if users is not None:
                        entry["users"] = users

                elif metric_name in _CLICK_METRIC_MAP:
                    field = _CLICK_METRIC_MAP[metric_name]
                    count = self._int(info_row, "subTotal")
                    if count is not None:
                        entry[field] = count
                    # Sessions fallback from click metrics (if Traffic not yet seen)
                    if entry.get("sessions") is None:
                        s = self._int(info_row, "sessionsCount", "totalSessionCount")
                        if s is not None:
                            entry["sessions"] = s

                elif metric_name in ("ScrollDepth", "Scroll Depth"):
                    val = self._float(info_row, "subTotal", "avgScrollDepth", "scrollDepth")
                    if val is not None:
                        entry["scroll_depth_pct"] = val

                elif metric_name in ("EngagementTime", "Engagement Time"):
                    val = self._float(info_row, "subTotal", "avgEngagementTime", "engagementTime")
                    if val is not None:
                        entry["engagement_time_ms"] = val

                else:
                    logger.debug("Unhandled Clarity metricName=%r (info keys: %s)",
                                 metric_name, list(info_row.keys()))

        def _get_dim(dim_vals: dict[str, str], requested: str | None) -> str | None:
            """Case-insensitive dimension value lookup (handles URL vs Url)."""
            if not requested:
                return None
            if requested in dim_vals:
                return dim_vals[requested]
            lower = requested.lower()
            for k, v in dim_vals.items():
                if k.lower() == lower:
                    return v
            return None

        rows: list[ClarityRow] = []
        for dim_key, data in dim_data.items():
            dv = data["_dim_vals"]
            rows.append(ClarityRow(
                project_id=self.project_id,
                fetch_date=fetch_date,
                num_of_days=num_of_days,
                dim1_name=dim1,
                dim1_value=_get_dim(dv, dim1),
                dim2_name=dim2,
                dim2_value=_get_dim(dv, dim2),
                dim3_name=dim3,
                dim3_value=_get_dim(dv, dim3),
                sessions=data.get("sessions"),
                users=data.get("users"),
                scroll_depth_pct=data.get("scroll_depth_pct"),
                engagement_time_ms=data.get("engagement_time_ms"),
                dead_click_count=data.get("dead_click_count"),
                rage_click_count=data.get("rage_click_count"),
                error_click_count=data.get("error_click_count"),
                script_error_count=data.get("script_error_count"),
                lcp_ms=None,   # Not available in Clarity Data Export API
                inp_ms=None,   # Not available in Clarity Data Export API
                cls=None,      # Not available in Clarity Data Export API
            ))
        return rows

    @staticmethod
    def _int(d: dict[str, Any], *keys: str) -> int | None:
        for k in keys:
            v = d.get(k)
            if v is not None:
                try:
                    return int(v)
                except (ValueError, TypeError):
                    pass
        return None

    @staticmethod
    def _float(d: dict[str, Any], *keys: str) -> float | None:
        for k in keys:
            v = d.get(k)
            if v is not None:
                try:
                    return float(v)
                except (ValueError, TypeError):
                    pass
        return None
