from __future__ import annotations

from typing import Iterable

import google.auth
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request


ANDROID_PUBLISHER_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
PLAY_REPORTING_SCOPE = "https://www.googleapis.com/auth/playdeveloperreporting"


def get_credentials(scopes: Iterable[str] | None = None) -> Credentials:
    requested_scopes = list(scopes or [ANDROID_PUBLISHER_SCOPE, PLAY_REPORTING_SCOPE])
    credentials, _ = google.auth.default(scopes=requested_scopes)
    return credentials


def refresh_access_token(credentials: Credentials | None = None) -> Credentials:
    creds = credentials or get_credentials()
    creds.refresh(Request())
    return creds

