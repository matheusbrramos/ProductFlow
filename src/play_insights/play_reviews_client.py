from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterator

from dateutil import parser as date_parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from play_insights.google_auth import get_credentials
from play_insights.models import ReviewRecord
from play_insights.retry import retry_call


def _parse_last_modified(comment_payload: dict) -> datetime | None:
    timestamp = comment_payload.get("lastModified")
    if not timestamp:
        return None

    # The API can return either epoch milliseconds or date map.
    millis = timestamp.get("seconds")
    if millis is not None:
        try:
            return datetime.fromtimestamp(int(millis), tz=timezone.utc)
        except (TypeError, ValueError):
            return None

    raw = timestamp.get("value")
    if raw:
        try:
            return date_parser.isoparse(raw)
        except (TypeError, ValueError):
            return None
    return None


def _normalize_review(review: dict) -> ReviewRecord:
    review_id = review.get("reviewId", "")
    comments = review.get("comments", [])
    user_comment = {}
    for comment in comments:
        if "userComment" in comment:
            user_comment = comment["userComment"]
            break

    app_version_code = user_comment.get("appVersionCode")
    app_version_name = user_comment.get("appVersionName")
    star_rating = user_comment.get("starRating")
    comment_text = user_comment.get("text", "")
    reviewer_language = user_comment.get("reviewerLanguage")
    last_modified_at = _parse_last_modified(user_comment)

    return ReviewRecord(
        review_id=review_id,
        star_rating=int(star_rating) if star_rating is not None else None,
        comment_text=comment_text,
        app_version_name=app_version_name,
        app_version_code=str(app_version_code) if app_version_code is not None else None,
        reviewer_language=reviewer_language,
        last_modified_at=last_modified_at,
    )


def iter_reviews(package_name: str, max_results: int = 100) -> Iterator[ReviewRecord]:
    credentials = get_credentials()
    service = build("androidpublisher", "v3", credentials=credentials, cache_discovery=False)

    token: str | None = None
    while True:
        req = service.reviews().list(
            packageName=package_name,
            maxResults=max_results,
            token=token,
        )
        response = retry_call(
            req.execute,
            retries=3,
            base_delay_seconds=1.0,
            retryable=lambda exc: isinstance(exc, HttpError)
            and exc.resp is not None
            and exc.resp.status in {429, 500, 502, 503, 504},
        )
        for review in response.get("reviews", []):
            yield _normalize_review(review)

        token = response.get("tokenPagination", {}).get("nextPageToken")
        if not token:
            break


def fetch_reviews(package_name: str, max_results: int = 100) -> list[ReviewRecord]:
    return list(iter_reviews(package_name=package_name, max_results=max_results))
