from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised when runtime configuration is invalid."""


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    db_path: str
    play_package_name: str
    google_application_credentials: str
    gcp_project_id: str | None = None
    timezone: str = "America/Sao_Paulo"
    log_level: str = "INFO"
    reply_publish_enabled: bool = False
    reply_publish_approval_token: str | None = None
    play_bq_export_dataset: str | None = None
    duckdb_memory_limit: str = "512MB"
    duckdb_threads: int = 2
    clarity_project_id: str | None = None
    clarity_api_token: str | None = None
    clarity_num_days: int = 3
    clarity_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        required_map = {
            "PLAY_PACKAGE_NAME": os.getenv("PLAY_PACKAGE_NAME"),
            "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        }
        missing = [key for key, value in required_map.items() if not value]
        if missing:
            missing_joined = ", ".join(sorted(missing))
            raise ConfigError(
                f"Missing required environment variables: {missing_joined}. "
                "Set them before running Play Insights."
            )

        return cls(
            db_path=os.getenv("DB_PATH", "play_insights.duckdb"),
            play_package_name=required_map["PLAY_PACKAGE_NAME"] or "",
            google_application_credentials=required_map["GOOGLE_APPLICATION_CREDENTIALS"] or "",
            gcp_project_id=os.getenv("GCP_PROJECT_ID") or None,
            timezone=os.getenv("TIMEZONE", "America/Sao_Paulo"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            reply_publish_enabled=_to_bool(os.getenv("REPLY_PUBLISH_ENABLED"), default=False),
            reply_publish_approval_token=os.getenv("REPLY_PUBLISH_APPROVAL_TOKEN"),
            play_bq_export_dataset=os.getenv("PLAY_BQ_EXPORT_DATASET") or None,
            duckdb_memory_limit=os.getenv("DUCKDB_MEMORY_LIMIT", "512MB"),
            duckdb_threads=int(os.getenv("DUCKDB_THREADS", "2")),
            clarity_project_id=os.getenv("CLARITY_PROJECT_ID") or None,
            clarity_api_token=os.getenv("CLARITY_API_TOKEN") or None,
            clarity_num_days=int(os.getenv("CLARITY_NUM_DAYS", "3")),
            clarity_enabled=_to_bool(os.getenv("CLARITY_ENABLED"), default=False),
        )

    def validate_publish_mode(self) -> None:
        if self.reply_publish_enabled and not self.reply_publish_approval_token:
            raise ConfigError(
                "REPLY_PUBLISH_ENABLED=true requires REPLY_PUBLISH_APPROVAL_TOKEN."
            )
