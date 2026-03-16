from __future__ import annotations

import pytest

from play_insights.google_auth import refresh_access_token


@pytest.mark.live_api
def test_refresh_access_token_live(require_live_env: None) -> None:
    creds = refresh_access_token()
    assert creds.token
    assert creds.expiry is not None

