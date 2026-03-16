from __future__ import annotations

import os

import pytest

from play_insights.play_reviews_client import fetch_reviews


@pytest.mark.live_api
def test_fetch_reviews_live_schema(require_live_env: None) -> None:
    package = os.getenv("PLAY_PACKAGE_NAME", "")
    reviews = fetch_reviews(package_name=package, max_results=10)
    for review in reviews:
        assert review.review_id
        assert hasattr(review, "star_rating")
        assert hasattr(review, "comment_text")
        assert hasattr(review, "reviewer_language")

