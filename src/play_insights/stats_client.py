from __future__ import annotations

import logging
from datetime import date, timedelta

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from play_insights.models import StatsRecord

logger = logging.getLogger(__name__)


class StatsClient:
    """Reads install/uninstall/active-device metrics from Play Console BQ export tables."""

    def __init__(self, project_id: str, export_dataset: str):
        self.project_id = project_id
        self.export_dataset = export_dataset
        self.client = bigquery.Client(project=project_id)

    @property
    def dataset_ref(self) -> str:
        return f"{self.project_id}.{self.export_dataset}"

    def _table_exists(self, table_name: str) -> bool:
        try:
            self.client.get_table(f"{self.dataset_ref}.{table_name}")
            return True
        except NotFound:
            return False

    def query_install_stats(self, days: int = 7) -> list[StatsRecord]:
        end = date.today()
        start = end - timedelta(days=days)

        overview_table = "installs_overview_v1"
        country_table = "installs_country_v1"

        if self._table_exists(overview_table):
            return self._query_overview(overview_table, start.isoformat(), end.isoformat())

        if self._table_exists(country_table):
            return self._query_country(country_table, start.isoformat(), end.isoformat())

        logger.warning(
            "Play Console BQ export tables not found in dataset %s. "
            "Enable BigQuery export in Play Console > Setup > BigQuery.",
            self.dataset_ref,
        )
        return []

    def _query_overview(self, table_name: str, start_date: str, end_date: str) -> list[StatsRecord]:
        query = f"""
        SELECT
            DATE(date) AS date,
            NULL AS country,
            daily_device_installs AS installs,
            daily_device_uninstalls AS uninstalls,
            active_device_installs AS active_devices
        FROM `{self.dataset_ref}.{table_name}`
        WHERE DATE(date) BETWEEN @start_date AND @end_date
        ORDER BY date DESC
        """
        cfg = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
        rows = self.client.query(query, job_config=cfg).result()
        return [
            StatsRecord(
                date=str(row["date"]),
                country=row.get("country"),
                installs=row.get("installs"),
                uninstalls=row.get("uninstalls"),
                active_devices=row.get("active_devices"),
            )
            for row in rows
        ]

    def _query_country(self, table_name: str, start_date: str, end_date: str) -> list[StatsRecord]:
        query = f"""
        SELECT
            DATE(date) AS date,
            country_id AS country,
            daily_device_installs AS installs,
            daily_device_uninstalls AS uninstalls,
            active_device_installs AS active_devices
        FROM `{self.dataset_ref}.{table_name}`
        WHERE DATE(date) BETWEEN @start_date AND @end_date
        ORDER BY date DESC, installs DESC
        """
        cfg = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
        rows = self.client.query(query, job_config=cfg).result()
        return [
            StatsRecord(
                date=str(row["date"]),
                country=row.get("country"),
                installs=row.get("installs"),
                uninstalls=row.get("uninstalls"),
                active_devices=row.get("active_devices"),
            )
            for row in rows
        ]
