from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta
from typing import Any

import requests

from play_insights.google_auth import refresh_access_token
from play_insights.models import ErrorIssueRecord, VitalsRecord
from play_insights.retry import retry_call

BASE_URL = "https://playdeveloperreporting.googleapis.com/v1beta1"


def _window_dates(days: int) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)  # API freshness limit: max yesterday
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def _build_time_period(start_date: str, end_date: str) -> dict[str, Any]:
    start_y, start_m, start_d = map(int, start_date.split("-"))
    end_y, end_m, end_d = map(int, end_date.split("-"))
    return {
        "startTime": {"year": start_y, "month": start_m, "day": start_d},
        "endTime": {"year": end_y, "month": end_m, "day": end_d},
    }


def _metrics_value(metric_values: list[dict[str, Any]]) -> float:
    if not metric_values:
        return 0.0
    first = metric_values[0]
    decimal_val = first.get("decimalValue")
    if isinstance(decimal_val, dict):
        return float(decimal_val.get("value", 0.0))
    if isinstance(decimal_val, str):
        return float(decimal_val)
    if first.get("integerValue") is not None:
        return float(first.get("integerValue"))
    return 0.0


def _parse_dimension_values(dim_list: list) -> dict[str, str]:
    """Parse Play API DimensionValue array → {dim_name: dim_value}.

    The API returns dimensions as an array of objects like:
    [{"dimension": "versionCode", "int64Value": "340"}, ...]
    """
    out: dict[str, str] = {}
    for dv in dim_list:
        name = dv.get("dimension")
        value = dv.get("stringValue") or (
            str(dv["int64Value"]) if "int64Value" in dv else None
        )
        if name and value:
            out[name] = value
    return out


class DeveloperReportingClient:
    def __init__(self, package_name: str, timeout_seconds: int = 30):
        self.package_name = package_name
        self.timeout_seconds = timeout_seconds
        creds = refresh_access_token()
        self._token = creds.token

    @property
    def app_path(self) -> str:
        return f"apps/{self.package_name}"

    def _post_query(self, metric_set: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{BASE_URL}/{self.app_path}/{metric_set}:query"

        def _do_request() -> dict[str, Any]:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

        return retry_call(
            _do_request,
            retries=3,
            base_delay_seconds=1.0,
            retryable=lambda exc: isinstance(exc, requests.HTTPError)
            and exc.response is not None
            and exc.response.status_code in {429, 500, 502, 503, 504},
        )

    def query_vitals_metric(
        self,
        metric_set: str,
        metric_name: str,
        days: int = 7,
    ) -> list[VitalsRecord]:
        start_date, end_date = _window_dates(days)
        payload: dict[str, Any] = {
            "timelineSpec": {
                "aggregationPeriod": "DAILY",
                **_build_time_period(start_date, end_date),
            },
            "metrics": [metric_name],
            "dimensions": ["versionCode", "countryCode", "deviceModel", "apiLevel"],
            "pageSize": 1000,
            "filter": "",
        }
        response = self._post_query(metric_set=metric_set, payload=payload)
        rows = response.get("rows", [])
        records: list[VitalsRecord] = []
        for row in rows:
            start_time = row.get("startTime") or row.get("start_date") or {}
            date_value = f"{start_time.get('year', 1970):04d}-{start_time.get('month', 1):02d}-{start_time.get('day', 1):02d}"
            metric_values = row.get("metrics", [])
            dimensions = _parse_dimension_values(row.get("dimensions", []))
            metric_value = _metrics_value(metric_values)
            records.append(
                VitalsRecord(
                    date=date_value,
                    metric_set=metric_set,
                    metric_value=metric_value,
                    package_name=self.package_name,
                    app_version=dimensions.get("versionCode"),
                    country=dimensions.get("countryCode"),
                    device_model=dimensions.get("deviceModel"),
                    os_version=dimensions.get("apiLevel"),
                )
            )
        return records

    def query_crash_rate(self, days: int = 7) -> list[VitalsRecord]:
        return self.query_vitals_metric(
            metric_set="crashRateMetricSet",
            metric_name="crashRate",
            days=days,
        )

    def query_anr_rate(self, days: int = 7) -> list[VitalsRecord]:
        return self.query_vitals_metric(
            metric_set="anrRateMetricSet",
            metric_name="anrRate",
            days=days,
        )

    def query_slow_rendering(self, days: int = 7) -> list[VitalsRecord]:
        return self.query_vitals_metric(
            metric_set="slowRenderingRateMetricSet",
            metric_name="slowRenderingRate20thPercentile",
            days=days,
        )

    def query_slow_start(self, days: int = 7) -> list[VitalsRecord]:
        return self.query_vitals_metric(
            metric_set="slowStartRateMetricSet",
            metric_name="slowStartRate",
            days=days,
        )

    def query_error_issues(self, days: int = 7) -> list[ErrorIssueRecord]:
        """Fetch error issues via GET errorIssues:search (grouped crash/ANR issues)."""
        start_date, end_date = _window_dates(days)
        url = f"{BASE_URL}/{self.app_path}/errorIssues:search"
        params: dict[str, Any] = {
            "interval.startTime": f"{start_date}T00:00:00Z",
            "interval.endTime": f"{end_date}T23:59:59Z",
            "pageSize": 100,
        }

        def _do_request() -> dict[str, Any]:
            response = requests.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {self._token}",
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

        try:
            response = retry_call(
                _do_request,
                retries=3,
                base_delay_seconds=1.0,
                retryable=lambda exc: isinstance(exc, requests.HTTPError)
                and exc.response is not None
                and exc.response.status_code in {429, 500, 502, 503, 504},
            )
        except requests.HTTPError:
            return []

        records: list[ErrorIssueRecord] = []
        for issue in response.get("errorIssues", []):
            # appVersion may be {"versionCode": "340"} or absent
            app_ver_obj = issue.get("appVersion") or {}
            app_version = str(app_ver_obj.get("versionCode", "")) or None

            # firstAppVersion holds earliest version that saw this issue
            first_ver_obj = issue.get("firstAppVersion") or {}
            first_seen = first_ver_obj.get("releaseDate") or start_date
            last_seen = (issue.get("lastAppVersion") or {}).get("releaseDate") or end_date

            records.append(
                ErrorIssueRecord(
                    issue_id=issue.get("name", ""),
                    issue_title=issue.get("title", "Unknown error"),
                    error_type=issue.get("type", ""),
                    affected_users=float(issue.get("distinctUsersCount", 0) or 0),
                    app_version=app_version,
                    device_model=None,
                    os_version=None,
                    first_seen=first_seen,
                    last_seen=last_seen,
                )
            )
        return records

    @staticmethod
    def to_dict_records(items: list[VitalsRecord | ErrorIssueRecord]) -> list[dict[str, Any]]:
        return [asdict(item) for item in items]
