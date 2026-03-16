from __future__ import annotations

import pytest

from play_insights.config import ConfigError, Settings


def test_settings_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAY_PACKAGE_NAME", "com.app")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/creds.json")
    monkeypatch.setenv("DB_PATH", "/tmp/test.duckdb")
    monkeypatch.setenv("REPLY_PUBLISH_ENABLED", "false")

    settings = Settings.from_env()
    assert settings.play_package_name == "com.app"
    assert settings.db_path == "/tmp/test.duckdb"
    assert settings.reply_publish_enabled is False
    assert settings.gcp_project_id is None


def test_settings_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ["PLAY_PACKAGE_NAME", "GOOGLE_APPLICATION_CREDENTIALS"]:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ConfigError):
        Settings.from_env()


def test_settings_db_path_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAY_PACKAGE_NAME", "com.app")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/creds.json")
    monkeypatch.delenv("DB_PATH", raising=False)
    settings = Settings.from_env()
    assert settings.db_path == "play_insights.duckdb"


def test_settings_gcp_project_id_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAY_PACKAGE_NAME", "com.app")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/creds.json")
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    settings = Settings.from_env()
    assert settings.gcp_project_id is None


def test_publish_mode_requires_approval_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAY_PACKAGE_NAME", "com.app")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/creds.json")
    monkeypatch.setenv("REPLY_PUBLISH_ENABLED", "true")
    monkeypatch.delenv("REPLY_PUBLISH_APPROVAL_TOKEN", raising=False)
    settings = Settings.from_env()
    with pytest.raises(ConfigError):
        settings.validate_publish_mode()
