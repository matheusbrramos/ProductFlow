from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from play_insights.models import StatsRecord
from play_insights.stats_client import StatsClient


def _make_client(project_id: str = "proj", export_dataset: str = "ds") -> StatsClient:
    with patch("play_insights.stats_client.bigquery.Client"):
        return StatsClient(project_id=project_id, export_dataset=export_dataset)


def test_dataset_ref() -> None:
    client = _make_client(project_id="my-project", export_dataset="my_dataset")
    assert client.dataset_ref == "my-project.my_dataset"


def test_query_install_stats_overview_table(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_client()

    fake_row = {
        "date": "2024-01-15",
        "country": None,
        "installs": 100,
        "uninstalls": 10,
        "active_devices": 500,
    }

    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([fake_row]))
    client.client.get_table = MagicMock(return_value=True)
    client.client.query = MagicMock(return_value=MagicMock(result=MagicMock(return_value=mock_result)))

    records = client._query_overview("installs_overview_v1", "2024-01-08", "2024-01-15")

    assert len(records) == 1
    assert isinstance(records[0], StatsRecord)
    assert records[0].date == "2024-01-15"
    assert records[0].installs == 100
    assert records[0].uninstalls == 10
    assert records[0].active_devices == 500
    assert records[0].country is None


def test_query_install_stats_country_table(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_client()

    fake_rows = [
        {"date": "2024-01-15", "country": "BR", "installs": 80, "uninstalls": 5, "active_devices": 400},
        {"date": "2024-01-15", "country": "US", "installs": 20, "uninstalls": 5, "active_devices": 100},
    ]

    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter(fake_rows))
    client.client.query = MagicMock(return_value=MagicMock(result=MagicMock(return_value=mock_result)))

    records = client._query_country("installs_country_v1", "2024-01-08", "2024-01-15")

    assert len(records) == 2
    assert records[0].country == "BR"
    assert records[1].country == "US"


def test_query_install_stats_no_tables_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    from google.cloud.exceptions import NotFound

    client = _make_client()
    client.client.get_table = MagicMock(side_effect=NotFound("table"))

    records = client.query_install_stats(days=7)

    assert records == []


def test_query_install_stats_prefers_overview_over_country() -> None:
    from google.cloud.exceptions import NotFound

    client = _make_client()

    call_count = {"count": 0}

    def get_table_side_effect(table_ref: str) -> MagicMock:
        call_count["count"] += 1
        if "installs_overview_v1" in str(table_ref):
            return MagicMock()
        raise NotFound("not found")

    client.client.get_table = MagicMock(side_effect=get_table_side_effect)

    fake_result = MagicMock()
    fake_result.__iter__ = MagicMock(return_value=iter([]))
    client.client.query = MagicMock(return_value=MagicMock(result=MagicMock(return_value=fake_result)))

    client.query_install_stats(days=7)

    query_call_args = client.client.query.call_args[0][0]
    assert "installs_overview_v1" in query_call_args
