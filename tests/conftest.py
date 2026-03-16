from __future__ import annotations

import os

import pytest


REQUIRED_ENV = [
    "PLAY_PACKAGE_NAME",
    "GOOGLE_APPLICATION_CREDENTIALS",
]


def has_live_env() -> bool:
    return all(bool(os.getenv(key)) for key in REQUIRED_ENV)


@pytest.fixture
def require_live_env() -> None:
    if not has_live_env():
        pytest.skip("Live environment variables are required for this test.")
