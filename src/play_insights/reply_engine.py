from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from googleapiclient.discovery import build

from play_insights.duckdb_repo import DuckDBRepository
from play_insights.google_auth import get_credentials

BLOCKED_CATEGORIES = {"pagamento_assinatura"}


def _build_reply_text(category: str, comment: str) -> str:
    if category == "estabilidade":
        return "Sentimos muito pela instabilidade. Estamos investigando e vamos liberar uma correcao em breve."
    if category == "performance":
        return "Obrigado pelo relato. Estamos trabalhando para reduzir lentidao e melhorar a experiencia."
    if category == "login_autenticacao":
        return "Entendemos o problema de acesso. Fale com nosso suporte para uma resolucao imediata."
    return "Obrigado pelo feedback. Seu comentario foi registrado e estamos atuando para melhorar o app."


def build_dry_run_queue(
    repo: DuckDBRepository,
    confidence_threshold: float = 0.70,
) -> tuple[list[dict[str, Any]], Path]:
    rows = repo.query(
        """
        SELECT e.review_id, e.complaint_category, e.confidence, r.comment_text
        FROM reviews_enriched e
        JOIN reviews_raw r USING (review_id)
        WHERE e.sentiment_label = 'neg'
        ORDER BY e.ingested_at DESC
        LIMIT 100
        """
    )

    queue: list[dict[str, Any]] = []
    for row in rows:
        category = row.get("complaint_category") or "usabilidade"
        confidence = float(row.get("confidence") or 0.0)
        if category in BLOCKED_CATEGORIES or confidence < confidence_threshold:
            continue
        queue.append(
            {
                "review_id": row["review_id"],
                "complaint_category": category,
                "confidence": confidence,
                "reply_text": _build_reply_text(category, row.get("comment_text", "")),
            }
        )

    today = date.today().isoformat()
    path = Path(".productflow/memory") / f"reply-dryrun-{today}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "date": today,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "items": queue,
    }
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return queue, path


def publish_replies(
    package_name: str,
    queue: list[dict[str, Any]],
    repo: DuckDBRepository,
    approval_token: str | None,
) -> int:
    if not approval_token:
        raise ValueError("Manual approval token is required for publish mode.")

    credentials = get_credentials()
    service = build("androidpublisher", "v3", credentials=credentials, cache_discovery=False)

    audit_rows: list[dict[str, Any]] = []
    published = 0
    now = datetime.now(tz=timezone.utc)
    for item in queue:
        review_id = item["review_id"]
        try:
            service.reviews().reply(
                packageName=package_name,
                reviewId=review_id,
                body={"replyText": item["reply_text"]},
            ).execute()
            published += 1
            status = "success"
            message = "Reply published"
        except Exception as exc:  # noqa: BLE001
            status = "failed"
            message = str(exc)
        audit_rows.append(
            {
                "event_date": now.date().isoformat(),
                "event_time": now.isoformat(),
                "review_id": review_id,
                "mode": "publish",
                "status": status,
                "message": message,
            }
        )

    if audit_rows:
        repo.insert_reply_audit(audit_rows)
    return published
