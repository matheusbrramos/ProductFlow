# Data Policy - Play Insights

## Scope
Applies to data ingested from Google Play APIs into BigQuery datasets used by Play Insights.

## Data Minimization
- Store only fields required for VOC analysis, quality diagnostics, and recommendations.
- Avoid storing unrelated reviewer metadata.

## Retention
- Raw tables (`reviews_raw`, `vitals_daily`, `error_issues`): 180 days rolling window.
- Enriched/recommendation tables: 365 days rolling window.
- Reply audit: 365 days minimum for governance traceability.

## Access Control
- Least-privilege IAM on BigQuery dataset.
- Service account access only for scheduled pipeline and controlled local runs.

## Sensitive Data
- Review text can include user-provided personal information.
- Reports must avoid exposing direct PII outside restricted channels.

## Operational Controls
- Publish replies disabled by default.
- Manual approval token required for publish mode.
- All publish attempts logged in `reply_audit`.

