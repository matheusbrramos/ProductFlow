from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from play_insights.duckdb_repo import DuckDBRepository


def _effort_tshirt(category: str) -> str:
    mapping = {
        "estabilidade": "M",
        "performance": "M",
        "login_autenticacao": "S",
        "pagamento_assinatura": "L",
        "funcionalidade_quebrada": "M",
        "usabilidade": "S",
        "conteudo_confiabilidade": "S",
        "suporte_comunicacao": "S",
    }
    return mapping.get(category, "M")


def _owner_suggestion(category: str) -> str:
    if category in {"estabilidade", "performance", "funcionalidade_quebrada"}:
        return "Engineering"
    if category in {"usabilidade", "conteudo_confiabilidade"}:
        return "Product Design"
    return "Product + Support"


def generate_recommendations(repo: DuckDBRepository, window_days: int = 7) -> list[dict]:
    start_date = (date.today() - timedelta(days=window_days)).isoformat()

    review_sql = f"""
    SELECT complaint_category, COUNT(*) AS negative_count, AVG(CAST(severity AS DOUBLE)) AS severity_avg
    FROM reviews_enriched
    WHERE ingest_date >= '{start_date}'::DATE AND sentiment_label = 'neg'
    GROUP BY complaint_category
    """
    reviews_rows = repo.query(review_sql)

    vitals_sql = f"""
    SELECT AVG(metric_value) AS vitals_avg
    FROM vitals_daily
    WHERE date >= '{start_date}'::DATE
    """
    vitals_rows = repo.query(vitals_sql)
    vitals_avg = float(vitals_rows[0]["vitals_avg"] or 0.0) if vitals_rows else 0.0

    issues_sql = f"""
    SELECT COALESCE(SUM(affected_users), 0) AS affected_users
    FROM error_issues
    WHERE ingest_date >= '{start_date}'::DATE
    """
    issues_rows = repo.query(issues_sql)
    affected_users = float(issues_rows[0]["affected_users"] or 0.0) if issues_rows else 0.0

    recs: list[dict] = []
    for row in reviews_rows:
        category = row["complaint_category"] or "usabilidade"
        negative_count = int(row["negative_count"] or 0)
        severity_avg = float(row["severity_avg"] or 3.0)
        impact_score = negative_count * severity_avg * (1 + vitals_avg) * (1 + min(affected_users, 1000) / 1000)
        recs.append(
            {
                "date": date.today().isoformat(),
                "recommendation_id": f"{category}-{date.today().isoformat()}",
                "complaint_category": category,
                "evidence_refs": f"neg_count={negative_count};severity_avg={severity_avg:.2f};vitals_avg={vitals_avg:.4f};affected_users={affected_users:.1f}",
                "expected_impact_score": round(impact_score, 3),
                "effort_tshirt": _effort_tshirt(category),
                "owner_suggestion": _owner_suggestion(category),
            }
        )

    recs.sort(key=lambda item: item["expected_impact_score"], reverse=True)
    return recs


def summarize_top_categories(repo: DuckDBRepository, top_n: int = 5) -> list[dict]:
    sql = f"""
    SELECT complaint_category, COUNT(*) AS total
    FROM reviews_enriched
    WHERE sentiment_label = 'neg'
    GROUP BY complaint_category
    ORDER BY total DESC
    LIMIT {top_n}
    """
    return repo.query(sql)


def summarize_impacted_segments(repo: DuckDBRepository, top_n: int = 5) -> list[dict]:
    sql = f"""
    SELECT app_version, device_model, os_version, AVG(metric_value) AS metric_avg
    FROM vitals_daily
    GROUP BY app_version, device_model, os_version
    ORDER BY metric_avg DESC
    LIMIT {top_n}
    """
    return repo.query(sql)


def summarize_recommendations(recommendations: list[dict], top_n: int = 5) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for rec in recommendations:
        grouped[rec["complaint_category"]].append(rec)
    flattened = sorted(recommendations, key=lambda item: item["expected_impact_score"], reverse=True)
    return flattened[:top_n]
