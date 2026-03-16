# Play Insights - Developer Guide

This project implements a Google Play intelligence pipeline using real Google APIs.

## 1. Local Setup

1. Install dependencies:
   `python -m pip install -e .[dev]`
2. Set environment variables:
   - `GCP_PROJECT_ID`
   - `BQ_DATASET`
   - `PLAY_PACKAGE_NAME`
   - `GOOGLE_APPLICATION_CREDENTIALS`
3. Validate auth:
   `pytest -m live_api -k auth`

## 2. Test Commands

- Unit tests only:
  `pytest -m "not live_api and not warehouse"`
- Real API tests:
  `pytest -m live_api`
- BigQuery tests:
  `pytest -m warehouse`

Notes:
- Integration tests in this project are designed for real API/warehouse calls.
- If required environment variables are missing, live tests are skipped by design.

## 3. Pipeline Commands

- Ingest all:
  `python -m play_insights ingest`
- Analyze last 7 days:
  `python -m play_insights analyze --window 7d`
- Daily report:
  `python -m play_insights report --mode daily`
- Weekly report:
  `python -m play_insights report --mode weekly`
- Reply dry-run:
  `python -m play_insights reply --mode dry-run`
- Reply publish (guarded):
  `python -m play_insights reply --mode publish`

## 4. Safety Defaults

- `REPLY_PUBLISH_ENABLED` defaults to `false`.
- Publish mode also requires `REPLY_PUBLISH_APPROVAL_TOKEN`.
- For production rollout, start with dry-run only.
