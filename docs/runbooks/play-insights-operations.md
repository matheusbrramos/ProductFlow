# Runbook - Play Insights Operations

## Purpose
Operational guidance for daily pipeline runs, incident handling, and reply publish safety.

## Required Secrets
- `GCP_PROJECT_ID`
- `BQ_DATASET`
- `PLAY_PACKAGE_NAME`
- `GCP_SERVICE_ACCOUNT_JSON`
- `REPLY_PUBLISH_ENABLED` (default `false`)
- `REPLY_PUBLISH_APPROVAL_TOKEN` (required only for publish)

## Daily Operations
1. Run ingestion:
   `python -m play_insights ingest --days 7`
2. Run analysis:
   `python -m play_insights analyze --window 7d`
3. Run daily report:
   `python -m play_insights report --mode daily`
4. Build dry-run replies:
   `python -m play_insights reply --mode dry-run`

## Weekly Operations
1. Generate weekly report:
   `python -m play_insights report --mode weekly`
2. Review top recommendations and assign owners.

## Incident Handling
### Auth failure
- Confirm service account key and API enablement.
- Re-run auth test:
  `pytest -m live_api -k auth`

### Quota or transient API failures
- Retry pipeline after backoff interval.
- Confirm run logs for `429/5xx` pattern.

### BigQuery write failures
- Check dataset/table existence and IAM permissions.
- Re-run warehouse tests:
  `pytest -m warehouse`

## Emergency Kill Switch
1. Set `REPLY_PUBLISH_ENABLED=false`.
2. Redeploy/restart scheduled workflow.
3. Verify no publish actions in `reply_audit`.

## Publish Governance Checklist
- Manual approval token present.
- High-risk categories blocked.
- Confidence threshold met.
- Dry-run reviewed for quality baseline.

