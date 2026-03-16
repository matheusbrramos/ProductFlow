from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from play_insights.duckdb_repo import DuckDBRepository
from play_insights.thresholds import (
    calculate_trend_velocity,
    check_violations,
    detect_regression,
    format_violation_summary,
)

_CATEGORY_LABELS = {
    "estabilidade": "Estabilidade (Crashes / ANR)",
    "performance": "Performance (Lentidão / Travamento)",
    "login_autenticacao": "Login & Autenticação",
    "pagamento_assinatura": "Pagamento & Assinatura",
    "usabilidade": "Usabilidade (UX/UI)",
    "funcionalidade_quebrada": "Funcionalidade Quebrada",
    "conteudo_confiabilidade": "Conteúdo & Confiabilidade",
    "suporte_comunicacao": "Suporte & Comunicação",
    "experiencia_compra": "Experiência de Compra (Ingresso/Ticket)",
}

_INTENT_LABELS = {
    "bug_report": "Bug / Problema técnico",
    "frustration": "Frustração / Experiência negativa",
    "support_request": "Pedido de suporte",
    "feature_request": "Solicitação de funcionalidade",
    "praise": "Elogio",
}

_CATEGORY_RISK = {
    "pagamento_assinatura": "ALTA — impacto direto em receita",
    "login_autenticacao": "ALTA — bloqueia acesso ao app",
    "estabilidade": "ALTA — causa desinstalação e reviews negativos",
    "funcionalidade_quebrada": "MÉDIA-ALTA — quebra fluxos core",
    "performance": "MÉDIA — degrada experiência progressivamente",
    "usabilidade": "MÉDIA — gera frustração e abandono",
    "conteudo_confiabilidade": "BAIXA-MÉDIA — afeta percepção de qualidade",
    "suporte_comunicacao": "BAIXA — afeta relacionamento com usuário",
}


def _truncate(text: str, max_chars: int = 280) -> str:
    if not text:
        return ""
    text = text.strip().replace("\n", " ").replace("\r", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text if len(text) <= max_chars else text[:max_chars] + "…"


def _trend_arrow(current: float | None, previous: float | None) -> str:
    if current is None or previous is None:
        return "→"
    if current > previous + 0.1:
        return "↑"
    if current < previous - 0.1:
        return "↓"
    return "→"


def _fetch_weekly_data(repo: DuckDBRepository, window: int = 30) -> dict[str, Any]:
    rating_trend = repo.query(f"""
        SELECT ingest_date,
               ROUND(AVG(CAST(star_rating AS DOUBLE)), 2) AS avg_rating,
               COUNT(*) AS reviews,
               SUM(CASE WHEN star_rating <= 2 THEN 1 ELSE 0 END) AS negative,
               SUM(CASE WHEN star_rating >= 4 THEN 1 ELSE 0 END) AS positive
        FROM reviews_raw
        WHERE ingest_date >= CURRENT_DATE - {window}
        GROUP BY ingest_date
        ORDER BY ingest_date ASC
    """)

    overall_rating = repo.query(f"""
        SELECT ROUND(AVG(CAST(star_rating AS DOUBLE)), 2) AS avg_rating,
               COUNT(*) AS total,
               SUM(CASE WHEN star_rating <= 2 THEN 1 ELSE 0 END) AS negative
        FROM reviews_raw
        WHERE ingest_date >= CURRENT_DATE - {window}
    """)

    categories = repo.query(f"""
        SELECT e.complaint_category,
               COUNT(*) AS total,
               ROUND(AVG(e.severity), 2) AS avg_severity
        FROM reviews_enriched e
        WHERE e.sentiment_label = 'neg'
          AND e.ingest_date >= CURRENT_DATE - {window}
        GROUP BY e.complaint_category
        ORDER BY total DESC
    """)

    reviews_with_text = repo.query(f"""
        SELECT r.star_rating, r.comment_text, r.reviewer_language, r.app_version_name,
               e.complaint_category, e.severity, e.intent, e.topic_keywords
        FROM reviews_raw r
        JOIN reviews_enriched e ON r.review_id = e.review_id
        WHERE e.sentiment_label = 'neg'
          AND r.ingest_date >= CURRENT_DATE - {window}
        ORDER BY e.severity DESC, r.last_modified_at DESC
        LIMIT 50
    """)

    vitals_by_metric = repo.query(f"""
        SELECT metric_set,
               ROUND(AVG(metric_value), 6) AS avg_value,
               ROUND(MAX(metric_value), 6) AS max_value,
               COUNT(DISTINCT date) AS days
        FROM vitals_daily
        WHERE date >= CURRENT_DATE - {window}
        GROUP BY metric_set
        ORDER BY avg_value DESC
    """)

    vitals_trend = repo.query(f"""
        SELECT date, metric_set, ROUND(AVG(metric_value), 6) AS avg_value
        FROM vitals_daily
        WHERE date >= CURRENT_DATE - {window}
        GROUP BY date, metric_set
        ORDER BY date ASC, metric_set
    """)

    error_issues = repo.query(f"""
        SELECT issue_id, issue_title, error_type, affected_users,
               app_version, device_model, os_version, first_seen, last_seen
        FROM error_issues
        WHERE ingest_date >= CURRENT_DATE - {window}
        ORDER BY affected_users DESC
        LIMIT 10
    """)

    recommendations = repo.query("""
        SELECT complaint_category, expected_impact_score, effort_tshirt,
               owner_suggestion, evidence_refs
        FROM recommendations
        WHERE date = CURRENT_DATE
        ORDER BY expected_impact_score DESC
        LIMIT 10
    """)

    severity_dist = repo.query(f"""
        SELECT severity, COUNT(*) AS total
        FROM reviews_enriched
        WHERE ingest_date >= CURRENT_DATE - {window}
          AND sentiment_label = 'neg'
        GROUP BY severity
        ORDER BY severity DESC
    """)

    crash_series = repo.query(f"""
        SELECT date,
               ROUND(AVG(metric_value), 4) AS avg_crash,
               ROUND(MIN(metric_value), 4) AS min_crash,
               ROUND(MAX(metric_value), 4) AS max_crash,
               COUNT(*) AS n_segments
        FROM vitals_daily
        WHERE metric_set = 'crashRateMetricSet'
          AND date >= CURRENT_DATE - {window}
        GROUP BY date
        ORDER BY date DESC
    """)

    vitals_dim_gap = repo.query("""
        SELECT COUNT(*) AS total_rows,
               COUNT(app_version) AS with_app_version,
               COUNT(device_model) AS with_device_model,
               COUNT(country) AS with_country,
               COUNT(os_version) AS with_os_version
        FROM vitals_daily
        WHERE metric_set = 'crashRateMetricSet'
    """)

    crash_by_device = repo.query(f"""
        SELECT device_model, os_version, app_version,
               ROUND(AVG(metric_value) * 100, 1) AS crash_pct,
               COUNT(*) AS days_with_data
        FROM vitals_daily
        WHERE metric_set = 'crashRateMetricSet'
          AND date >= CURRENT_DATE - {window}
          AND device_model IS NOT NULL
        GROUP BY device_model, os_version, app_version
        ORDER BY crash_pct DESC
        LIMIT 10
    """)

    try:
        install_rows = repo.query(f"""
            SELECT date, SUM(installs) AS installs, SUM(uninstalls) AS uninstalls,
                   SUM(active_devices) AS active_devices
            FROM stats_daily
            WHERE date >= CURRENT_DATE - {window}
            GROUP BY date
            ORDER BY date DESC
        """)
    except Exception:  # noqa: BLE001
        install_rows = []

    crash_by_version = repo.query(f"""
        SELECT app_version,
               ROUND(AVG(metric_value) * 100, 2) AS crash_avg_pct,
               COUNT(DISTINCT date) AS days_with_data,
               MIN(date) AS first_seen,
               MAX(date) AS last_seen
        FROM vitals_daily
        WHERE metric_set = 'crashRateMetricSet'
          AND date >= CURRENT_DATE - {window}
          AND app_version IS NOT NULL
        GROUP BY app_version
        ORDER BY MAX(date) DESC
        LIMIT 10
    """)

    performance_vitals = repo.query(f"""
        SELECT metric_set,
               ROUND(AVG(metric_value) * 100, 2) AS avg_pct,
               ROUND(MAX(metric_value) * 100, 2) AS max_pct,
               COUNT(DISTINCT date) AS days_with_data
        FROM vitals_daily
        WHERE metric_set IN ('slowRenderingRateMetricSet', 'slowStartRateMetricSet')
          AND date >= CURRENT_DATE - {window}
        GROUP BY metric_set
    """)

    category_persistence = repo.query(f"""
        SELECT complaint_category,
               MIN(ingest_date) AS first_seen,
               MAX(ingest_date) AS last_seen,
               COUNT(DISTINCT DATE_TRUNC('week', ingest_date::DATE)) AS weeks_present,
               COUNT(*) AS total_reviews
        FROM reviews_enriched
        WHERE sentiment_label = 'neg'
          AND complaint_category IS NOT NULL
          AND ingest_date >= CURRENT_DATE - {max(window, 90)}
        GROUP BY complaint_category
        HAVING COUNT(*) >= 2
        ORDER BY first_seen ASC
    """)

    weekly_crash_vs_reviews = repo.query(f"""
        SELECT DATE_TRUNC('week', v.date::DATE)::DATE AS week,
               ROUND(AVG(v.metric_value) * 100, 1) AS crash_avg_pct,
               COUNT(DISTINCT e.review_id) FILTER (WHERE e.sentiment_label = 'neg') AS neg_reviews
        FROM vitals_daily v
        LEFT JOIN reviews_enriched e ON DATE_TRUNC('week', v.date::DATE) = DATE_TRUNC('week', e.ingest_date::DATE)
        WHERE v.metric_set = 'crashRateMetricSet'
          AND v.date >= CURRENT_DATE - {window}
        GROUP BY DATE_TRUNC('week', v.date::DATE)
        ORDER BY week DESC
        LIMIT 8
    """)

    try:
        urgent_reviews = repo.query(f"""
            SELECT r.comment_text, r.star_rating, r.ingest_date, r.app_version_name,
                   e.complaint_category, e.severity
            FROM reviews_raw r
            JOIN reviews_enriched e ON r.review_id = e.review_id
            WHERE e.event_urgency = TRUE
              AND r.ingest_date >= CURRENT_DATE - {window}
            ORDER BY r.ingest_date DESC
            LIMIT 10
        """)
    except Exception:  # noqa: BLE001
        urgent_reviews = []

    # Derived analytics
    vitals_list = [{"metric_set": v.get("metric_set"), "avg_value": v.get("avg_value")} for v in vitals_by_metric]
    threshold_violations = check_violations(vitals_list)
    crash_trend = calculate_trend_velocity(crash_series)

    return {
        "rating_trend": rating_trend,
        "overall_rating": overall_rating[0] if overall_rating else {},
        "categories": categories,
        "reviews_with_text": reviews_with_text,
        "vitals_by_metric": vitals_by_metric,
        "vitals_trend": vitals_trend,
        "error_issues": error_issues,
        "recommendations": recommendations,
        "severity_dist": severity_dist,
        "install_rows": install_rows,
        "crash_series": crash_series,
        "crash_by_device": crash_by_device,
        "crash_by_version": crash_by_version,
        "vitals_dim_gap": vitals_dim_gap[0] if vitals_dim_gap else {},
        "performance_vitals": performance_vitals,
        "category_persistence": category_persistence,
        "weekly_crash_vs_reviews": weekly_crash_vs_reviews,
        "urgent_reviews": urgent_reviews,
        "threshold_violations": threshold_violations,
        "crash_trend": crash_trend,
    }


def _build_narrative(data: dict[str, Any], window: int) -> list[str]:
    overall = data["overall_rating"]
    categories = data["categories"]
    vitals = data["vitals_by_metric"]
    rating_trend = data["rating_trend"]

    avg_r = overall.get("avg_rating")
    total = overall.get("total", 0) or 0
    neg = overall.get("negative", 0) or 0
    neg_pct = round(neg / total * 100) if total else 0

    crash_avg = next(
        (v["avg_value"] for v in vitals if "crash" in (v.get("metric_set") or "").lower()), 0.0
    ) or 0.0

    # Rating direction
    if len(rating_trend) >= 2:
        first_rating = rating_trend[0].get("avg_rating") or 0
        last_rating = rating_trend[-1].get("avg_rating") or 0
        if last_rating > first_rating + 0.1:
            trend_text = "com sinal de melhoria"
        elif last_rating < first_rating - 0.1:
            trend_text = "com tendência de piora"
        else:
            trend_text = "estável"
    else:
        trend_text = "sem dados de tendência suficientes"

    top_cat = categories[0] if categories else None

    lines = [
        "## Narrativa da Semana",
        "",
    ]

    if total == 0:
        lines.append(
            f"Nos últimos {window} dias, nenhum review foi coletado. "
            "Verifique se a ingestão está funcionando corretamente e se o app tem reviews recentes no Play Console."
        )
    else:
        rating_str = f"⭐ {avg_r:.1f}/5.0" if avg_r else "rating indisponível"
        paragraph = (
            f"O app registrou **{total} review(s)** nos últimos {window} dias, "
            f"com média de {rating_str} e **{neg_pct}% de avaliações negativas** — "
            f"tendência **{trend_text}**. "
        )

        if top_cat:
            cat_label = _CATEGORY_LABELS.get(top_cat["complaint_category"], top_cat["complaint_category"])
            paragraph += (
                f"O tema que mais concentra insatisfação é **{cat_label}** "
                f"({top_cat['total']} relato(s), severidade média {top_cat['avg_severity']}/5). "
            )

        if crash_avg > 0:
            paragraph += (
                f"No lado técnico, o crash rate médio foi de **{crash_avg:.2%}** — "
            )
            if crash_avg < 0.02:
                paragraph += "dentro de parâmetros normais. "
            elif crash_avg < 0.05:
                paragraph += "acima do ideal, requer acompanhamento. "
            else:
                paragraph += "em nível crítico, requer ação imediata. "

        paragraph += (
            "Este relatório consolida o panorama completo para que o time de produto "
            "possa tomar decisões informadas sobre onde investir energia na próxima sprint."
        )

        lines.append(paragraph)

    lines.append("")
    return lines


def _build_rating_trend(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Tendência de Rating",
        "",
    ]

    trend = data["rating_trend"]
    if not trend:
        lines += ["Sem dados de rating no período.", ""]
        return lines

    lines.append("| Data | Avg Rating | Reviews | Negativos | Positivos | Tendência |")
    lines.append("|------|-----------|---------|-----------|-----------|-----------|")

    prev_rating: float | None = None
    for row in trend:
        d = str(row.get("ingest_date") or "?")[:10]
        avg = row.get("avg_rating")
        reviews = row.get("reviews") or 0
        neg = row.get("negative") or 0
        pos = row.get("positive") or 0
        arrow = _trend_arrow(avg, prev_rating)
        rating_str = f"⭐ {avg:.2f}" if avg else "—"
        lines.append(f"| {d} | {rating_str} | {reviews} | {neg} | {pos} | {arrow} |")
        prev_rating = avg

    lines.append("")

    # Interpretation
    if len(trend) >= 3:
        ratings = [r.get("avg_rating") for r in trend if r.get("avg_rating")]
        if ratings:
            first_half = sum(ratings[: len(ratings) // 2]) / max(len(ratings) // 2, 1)
            second_half = sum(ratings[len(ratings) // 2:]) / max(len(ratings) - len(ratings) // 2, 1)
            if second_half > first_half + 0.15:
                lines.append(
                    "> **Interpretação:** Rating mostrando melhoria no período. "
                    "Mudanças recentes no produto ou resolução de bugs pode estar gerando impacto positivo."
                )
            elif second_half < first_half - 0.15:
                lines.append(
                    "> **Alerta:** Rating em queda no período. "
                    "Investigar se houve deploy recente, mudança de funcionalidade ou aumento de bugs."
                )
            else:
                lines.append(
                    "> **Interpretação:** Rating estável no período. "
                    "Nenhuma melhoria ou piora significativa detectada."
                )
        lines.append("")

    return lines


def _build_category_deep_dives(data: dict[str, Any], window: int) -> list[str]:
    lines = [
        "---",
        "",
        "## Deep Dive por Categoria — A História de Cada Problema",
        "",
        "_Cada categoria é analisada com citações reais, padrões observados e correlação técnica._",
        "",
    ]

    categories = data["categories"]
    reviews_all = data["reviews_with_text"]
    vitals = data["vitals_by_metric"]
    recommendations = data["recommendations"]
    error_issues = data["error_issues"]

    if not categories:
        lines += ["Sem categorias de queixa identificadas no período.", ""]
        return lines

    by_cat: dict[str, list[dict]] = {}
    for r in reviews_all:
        cat = r.get("complaint_category") or "outro"
        by_cat.setdefault(cat, []).append(r)

    rec_by_cat: dict[str, dict] = {
        r.get("complaint_category", ""): r for r in recommendations
    }

    crash_avg = next(
        (v["avg_value"] for v in vitals if "crash" in (v.get("metric_set") or "").lower()), None
    )
    anr_avg = next(
        (v["avg_value"] for v in vitals if "anr" in (v.get("metric_set") or "").lower()), None
    )
    total_affected_errors = sum(
        (e.get("affected_users") or 0) for e in error_issues
    )

    for cat_row in categories:
        cat = cat_row["complaint_category"]
        cat_label = _CATEGORY_LABELS.get(cat, cat)
        total = cat_row["total"]
        avg_sev = cat_row["avg_severity"]
        cat_reviews = by_cat.get(cat, [])
        risk = _CATEGORY_RISK.get(cat, "—")

        lines.append(f"### {cat_label}")
        lines.append("")
        lines.append(
            f"**{total} relato(s) negativos** · severidade média **{avg_sev}/5** · risco: {risk}"
        )
        lines.append("")

        # Quotes
        shown = 0
        for r in cat_reviews[:3]:
            text = _truncate(r.get("comment_text") or "", 300)
            if not text:
                continue
            stars = r.get("star_rating", "?")
            lang = r.get("reviewer_language") or "?"
            intent_raw = r.get("intent") or ""
            intent = _INTENT_LABELS.get(intent_raw, intent_raw)
            sev = r.get("severity", "?")
            ver = r.get("app_version_name") or "versão não identificada"

            lines.append(f"> \"{text}\"")
            lines.append(
                f"> _⭐ {stars} · {lang} · {intent} · severidade {sev}/5 · {ver}_"
            )
            lines.append("")
            shown += 1

        if shown == 0:
            lines.append("_Sem texto disponível para esta categoria._")
            lines.append("")

        # Keywords
        keywords: set[str] = set()
        for r in cat_reviews:
            kw = r.get("topic_keywords") or ""
            keywords.update(k.strip() for k in kw.split(",") if k.strip())
        if keywords:
            lines.append(f"**Palavras-chave:** {', '.join(sorted(keywords)[:10])}")
            lines.append("")

        # Technical correlation
        if cat in {"estabilidade", "funcionalidade_quebrada"} and crash_avg is not None:
            lines.append(
                f"**Correlação técnica:** Crash rate de **{crash_avg:.2%}** no período. "
                "Queixas de estabilidade tendem a refletir diretamente os crashes registrados nos vitals. "
                "Verificar crash traces no Firebase/Play Console para identificar o stack trace dominante."
            )
            lines.append("")
        elif cat == "performance" and anr_avg is not None:
            lines.append(
                f"**Correlação técnica:** ANR rate de **{anr_avg:.2%}** no período. "
                "Queixas de lentidão correlacionam com ANR — o app está travando a thread principal."
            )
            lines.append("")
        elif total_affected_errors > 0 and cat in {"funcionalidade_quebrada", "estabilidade"}:
            lines.append(
                f"**Correlação técnica:** {total_affected_errors:.0f} usuários afetados "
                "identificados via error issues. Investigar os erros listados na seção de Hotspots."
            )
            lines.append("")

        # Recommendation
        rec = rec_by_cat.get(cat)
        if rec:
            effort = rec.get("effort_tshirt", "?")
            owner = rec.get("owner_suggestion", "?")
            score = rec.get("expected_impact_score", 0) or 0
            lines.append(
                f"**Recomendação:** Impacto estimado {score:.1f} · Esforço {effort} · Dono: {owner}"
            )
            lines.append("")

    return lines


def _build_technical_hotspots(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Hotspots Técnicos",
        "",
    ]

    vitals = data["vitals_by_metric"]
    error_issues = data["error_issues"]

    if not vitals:
        lines += ["Sem dados de vitals coletados no período.", ""]
        return lines

    lines.append("### Vitals por Métrica")
    lines.append("")
    lines.append("| Métrica | Média | Pico | Dias com dados | Status |")
    lines.append("|---------|-------|------|----------------|--------|")

    for v in vitals:
        ms = v.get("metric_set") or "?"
        avg = v.get("avg_value") or 0.0
        mx = v.get("max_value") or 0.0
        days = v.get("days") or 0

        if "crash" in ms.lower():
            label = "Crash Rate"
            status = "🟢 OK" if avg < 0.02 else "🟡 Atenção" if avg < 0.05 else "🔴 Crítico"
        elif "anr" in ms.lower():
            label = "ANR Rate"
            status = "🟢 OK" if avg < 0.01 else "🟡 Atenção" if avg < 0.03 else "🔴 Crítico"
        else:
            label = ms
            status = "—"

        lines.append(
            f"| {label} | {avg:.4f} ({avg:.2%}) | {mx:.4f} ({mx:.2%}) | {days} dias | {status} |"
        )

    lines.append("")

    # Crash rate time series
    crash_series = data.get("crash_series") or []
    dim_gap = data.get("vitals_dim_gap") or {}
    total_rows = dim_gap.get("total_rows") or 0
    with_ver = dim_gap.get("with_app_version") or 0
    with_dev = dim_gap.get("with_device_model") or 0
    with_country = dim_gap.get("with_country") or 0

    if crash_series:
        lines.append("### Série Temporal do Crash Rate")
        lines.append("")
        lines.append("| Data | Média | Mínimo | Máximo | Segmentos |")
        lines.append("|------|-------|--------|--------|-----------|")
        worst = max(crash_series, key=lambda r: r.get("avg_crash") or 0)
        best = min(crash_series, key=lambda r: r.get("avg_crash") or 0)
        for row in crash_series[:30]:
            d = str(row.get("date") or "?")[:10]
            avg = row.get("avg_crash") or 0.0
            mn = row.get("min_crash") or 0.0
            mx = row.get("max_crash") or 0.0
            n = row.get("n_segments") or 0
            flag = " ⬆️" if row is worst else (" ⬇️" if row is best else "")
            lines.append(f"| {d} | {avg:.2%}{flag} | {mn:.2%} | {mx:.2%} | {n} |")
        lines.append("")
        lines.append(
            f"> **Pior dia:** {str(worst.get('date') or '?')[:10]} — "
            f"média {(worst.get('avg_crash') or 0):.2%}, pico {(worst.get('max_crash') or 0):.2%}"
        )
        lines.append(
            f"> **Melhor dia:** {str(best.get('date') or '?')[:10]} — "
            f"média {(best.get('avg_crash') or 0):.2%}"
        )
        lines.append("")

    # Device breakdown (when available)
    crash_by_device = data.get("crash_by_device") or []
    if crash_by_device:
        lines.append("### Dispositivos Mais Afetados pelos Crashes")
        lines.append("")
        lines.append("| Dispositivo | Android | Versão app | Crash Rate Médio | Dias |")
        lines.append("|-------------|---------|-----------|-----------------|------|")
        for row in crash_by_device[:10]:
            device = row.get("device_model") or "?"
            android = row.get("os_version") or "?"
            ver = row.get("app_version") or "?"
            pct = row.get("crash_pct") or 0.0
            days = row.get("days_with_data") or 0
            lines.append(f"| {device} | API {android} | {ver} | {pct:.1f}% | {days}d |")
        lines.append("")
        worst = crash_by_device[0]
        lines.append(
            f"> **Maior offender:** `{worst.get('device_model')}` "
            f"(Android API {worst.get('os_version')}) — {worst.get('crash_pct'):.1f}% "
            f"de crash rate médio. Priorizar investigação neste dispositivo."
        )
        lines.append("")

    # Dimension availability declaration
    lines.append("### Disponibilidade de Dados de Crash — O Que Temos e O Que Falta")
    lines.append("")
    lines.append(f"**{total_rows} segmentos de crash rate** coletados na base de dados.")
    lines.append("")
    lines.append("| Dimensão | Com dados | Sem dados | Impacto |")
    lines.append("|----------|-----------|-----------|---------|")
    lines.append(
        f"| Versão do app | {with_ver} | {total_rows - with_ver} | "
        f"{'✅ Pode-se ver quais versões crasham mais' if with_ver > 0 else '❌ Não é possível identificar versão afetada'} |"
    )
    lines.append(
        f"| Modelo de dispositivo | {with_dev} | {total_rows - with_dev} | "
        f"{'✅ Pode-se ver quais dispositivos crasham mais' if with_dev > 0 else '❌ Não é possível identificar dispositivo afetado'} |"
    )
    lines.append(
        f"| País | {with_country} | {total_rows - with_country} | "
        f"{'✅ Pode-se ver regiões mais afetadas' if with_country > 0 else '❌ Não é possível identificar região afetada'} |"
    )
    lines.append("")

    if with_ver == 0 and with_dev == 0:
        lines.append(
            "> ⚠️ **A API retorna crash rate global sem segmentação.** "
            "Não é possível, com os dados atuais, determinar qual versão ou dispositivo "
            "é responsável pelo crash rate elevado."
        )
        lines.append(">")
        lines.append("> **Para identificar a causa raiz, acesse diretamente:**")
        lines.append("> - **Play Console** → Android Vitals → Crashes & ANRs → ver por versão/dispositivo")
        lines.append("> - **Firebase Crashlytics** (se integrado) → stack traces detalhados por versão")
        lines.append("> - **Play Console** → Release → Release dashboard → ver se houve deploy recente")
        lines.append("")

    if error_issues:
        lines.append("### Error Issues Identificados pela API")
        lines.append("")
        lines.append("| Título | Tipo | Usuários afetados | Versão | Período |")
        lines.append("|--------|------|-------------------|--------|---------|")
        for e in error_issues[:5]:
            title = (e.get("issue_title") or "?")[:40]
            etype = e.get("error_type") or "?"
            affected = e.get("affected_users") or 0
            ver = e.get("app_version") or "?"
            first = str(e.get("first_seen") or "?")[:10]
            last = str(e.get("last_seen") or "?")[:10]
            lines.append(f"| {title} | {etype} | {affected:.0f} | {ver} | {first} → {last} |")
        lines.append("")
    else:
        lines.append(
            "> **Error Issues API:** 0 registros retornados no período. "
            "Stack traces e erros específicos não estão disponíveis via esta API. "
            "Consultar Firebase Crashlytics ou Play Console diretamente."
        )
        lines.append("")

    return lines


def _build_impact_matrix(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Matriz de Impacto — Onde Focar",
        "",
        "Cada categoria é posicionada por **volume de queixas** (eixo X) "
        "e **severidade média** (eixo Y). Priorize o quadrante superior direito.",
        "",
    ]

    categories = data["categories"]
    if not categories:
        lines += ["Sem dados para construir a matriz.", ""]
        return lines

    # Calculate thresholds
    volumes = [c["total"] for c in categories]
    severities = [c["avg_severity"] for c in categories]
    vol_median = sorted(volumes)[len(volumes) // 2] if volumes else 1
    sev_median = 3.0

    high_high = []  # high volume + high severity
    high_low = []   # high severity + low volume
    low_high = []   # low severity + high volume
    low_low = []    # low volume + low severity

    for c in categories:
        cat_label = _CATEGORY_LABELS.get(c["complaint_category"], c["complaint_category"])
        vol_high = c["total"] >= vol_median
        sev_high = c["avg_severity"] >= sev_median

        entry = f"{cat_label} ({c['total']} · sev {c['avg_severity']})"
        if vol_high and sev_high:
            high_high.append(entry)
        elif sev_high and not vol_high:
            high_low.append(entry)
        elif vol_high and not sev_high:
            low_high.append(entry)
        else:
            low_low.append(entry)

    def _fmt(items: list[str]) -> str:
        return "<br>".join(items) if items else "—"

    lines.append("|  | **Volume Alto** | **Volume Baixo** |")
    lines.append("|--|-----------------|-----------------|")
    lines.append(
        f"| **Severidade Alta** | 🔴 Atacar agora<br>{_fmt(high_high)} | 🟡 Investigar<br>{_fmt(high_low)} |"
    )
    lines.append(
        f"| **Severidade Baixa** | 🟡 Planejar<br>{_fmt(low_high)} | 🟢 Monitorar<br>{_fmt(low_low)} |"
    )
    lines.append("")
    return lines


def _build_strategic_roadmap(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Roadmap Estratégico — Prioridades para a Próxima Sprint",
        "",
        "_Lista curada ordenada por impacto esperado. "
        "Combina evidências de reviews, vitals e issues._",
        "",
    ]

    recommendations = data["recommendations"]
    if not recommendations:
        lines += [
            "Nenhuma recomendação disponível. Execute `python -m play_insights analyze` primeiro.",
            "",
        ]
        return lines

    for i, rec in enumerate(recommendations, 1):
        cat = rec.get("complaint_category") or "?"
        cat_label = _CATEGORY_LABELS.get(cat, cat)
        score = rec.get("expected_impact_score") or 0
        effort = rec.get("effort_tshirt") or "?"
        owner = rec.get("owner_suggestion") or "?"

        ev_parts: dict[str, str] = {}
        for part in (rec.get("evidence_refs") or "").split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                ev_parts[k.strip()] = v.strip()

        neg_count = ev_parts.get("neg_count", "?")
        severity_avg = ev_parts.get("severity_avg", "?")
        vitals_str = ev_parts.get("vitals_avg", "0")
        try:
            vitals_display = f"{float(vitals_str):.2%}"
        except (ValueError, TypeError):
            vitals_display = vitals_str

        risk = _CATEGORY_RISK.get(cat, "—")

        lines.append(f"#### {i}. {cat_label}")
        lines.append(
            f"**Impacto:** {score:.1f} | **Esforço:** {effort} | **Dono:** {owner} | **Risco:** {risk}"
        )
        lines.append("")
        lines.append(
            f"**Evidência consolidada:** {neg_count} review(s) negativo(s) · "
            f"severidade média {severity_avg}/5 · vitals {vitals_display}"
        )
        lines.append("")

    return lines


def _build_risk_flags(data: dict[str, Any], window: int) -> list[str]:
    lines = [
        "---",
        "",
        "## Flags de Risco",
        "",
    ]

    flags = []

    rating_trend = data["rating_trend"]
    if len(rating_trend) >= 3:
        last_3 = [r.get("avg_rating") for r in rating_trend[-3:] if r.get("avg_rating")]
        if len(last_3) == 3 and last_3[0] > last_3[1] > last_3[2]:
            flags.append(
                "🔴 **Rating em queda por 3+ dias consecutivos.** "
                f"Últimos 3 pontos: {last_3[0]:.1f} → {last_3[1]:.1f} → {last_3[2]:.1f}. "
                "Investigar causas com urgência."
            )

    vitals = data["vitals_by_metric"]
    crash_avg = next(
        (v["avg_value"] for v in vitals if "crash" in (v.get("metric_set") or "").lower()), 0.0
    ) or 0.0
    anr_avg = next(
        (v["avg_value"] for v in vitals if "anr" in (v.get("metric_set") or "").lower()), 0.0
    ) or 0.0

    if crash_avg >= 0.05:
        flags.append(
            f"🔴 **Crash rate crítico: {crash_avg:.2%}** (threshold: 5%). "
            "App quebrando para mais de 1 em 20 sessões. Prioridade máxima."
        )
    elif crash_avg >= 0.02:
        flags.append(
            f"🟡 **Crash rate elevado: {crash_avg:.2%}** (threshold normal: <2%). "
            "Monitorar e identificar versões/dispositivos mais afetados."
        )

    if anr_avg >= 0.03:
        flags.append(
            f"🔴 **ANR rate crítico: {anr_avg:.2%}** (threshold: 3%). "
            "App travando a thread principal com frequência. Revisar operações síncronas."
        )
    elif anr_avg >= 0.01:
        flags.append(
            f"🟡 **ANR rate elevado: {anr_avg:.2%}** (threshold normal: <1%). "
            "Monitorar thread principal e operações de I/O."
        )

    categories = data["categories"]
    cat_names = [c["complaint_category"] for c in categories]
    if "pagamento_assinatura" in cat_names:
        n = next(c["total"] for c in categories if c["complaint_category"] == "pagamento_assinatura")
        flags.append(
            f"🔴 **{n} queixa(s) sobre Pagamento/Assinatura.** "
            "Qualquer problema nesta categoria impacta diretamente a receita. "
            "Investigar e resolver com prioridade máxima."
        )
    if "login_autenticacao" in cat_names:
        n = next(c["total"] for c in categories if c["complaint_category"] == "login_autenticacao")
        flags.append(
            f"🟡 **{n} queixa(s) sobre Login/Autenticação.** "
            "Bloqueio de acesso causa abandono imediato do app."
        )

    overall = data["overall_rating"]
    avg_r = overall.get("avg_rating")
    if avg_r and avg_r < 3.0:
        flags.append(
            f"🔴 **Rating médio abaixo de 3.0 ({avg_r:.1f}).** "
            "App em risco de receber badge negativo no Play Store. Ação urgente necessária."
        )

    if not flags:
        flags.append("🟢 Nenhum flag de risco crítico identificado no período. Continuar monitorando.")

    lines.extend(f"- {flag}" for flag in flags)
    lines.append("")
    return lines


def _build_crash_diagnosis_weekly(data: dict[str, Any]) -> list[str]:
    """Seção de diagnóstico de crash com narrativa para stakeholders e devs."""
    from play_insights.crash_patterns import analyze_crash_patterns

    vitals = data["vitals_by_metric"]
    crash_by_device = data.get("crash_by_device") or []
    crash_by_version = data.get("crash_by_version") or []

    crash_avg = next(
        (v.get("avg_value") or 0.0 for v in vitals if "crash" in (v.get("metric_set") or "").lower()),
        0.0,
    )
    if crash_avg < 0.001:
        return []

    diag = analyze_crash_patterns(crash_avg, crash_by_device, crash_by_version)

    lines: list[str] = [
        "---",
        "",
        f"## Diagnóstico de Crashes — {diag.severity_label}",
        "",
        "### Para Stakeholders — O Que Está Acontecendo",
        "",
        diag.stakeholder_summary,
        "",
        f"> **Impacto estimado no negócio:** {diag.business_impact}",
        "",
    ]

    if diag.hotspot_summary:
        lines.append(diag.hotspot_summary)
        lines.append("")

    lines += [
        "### Para o Time de Desenvolvimento — Onde Investigar",
        "",
        f"**Padrão detectado:** {diag.technical_cause}",
        "",
        "**Próximos passos recomendados (em ordem de prioridade):**",
        "",
    ]
    for i, rec in enumerate(diag.dev_recommendations, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    return lines


def _build_performance_section_weekly(data: dict[str, Any]) -> list[str]:
    perf = data.get("performance_vitals") or []
    lines = [
        "---",
        "",
        "## Performance de UI e Startup",
        "",
    ]
    if not perf:
        lines.append("_Dados de rendering/startup ainda não coletados._")
        lines.append("")
        return lines
    lines.append("| Métrica | Média | Pico | Dias com dados |")
    lines.append("|---------|-------|------|----------------|")
    for row in perf:
        ms = row.get("metric_set") or "?"
        avg = row.get("avg_pct") or 0.0
        mx = row.get("max_pct") or 0.0
        days = row.get("days_with_data") or 0
        label = "Slow Rendering (≥1s frame)" if "rendering" in ms.lower() else ("Slow Start" if "start" in ms.lower() else ms)
        lines.append(f"| {label} | {avg:.1f}% | {mx:.1f}% | {days}d |")
    lines.append("")
    return lines


def _build_version_regression_weekly(data: dict[str, Any]) -> list[str]:
    crash_by_version = data.get("crash_by_version") or []
    if not crash_by_version:
        return []
    lines = [
        "---",
        "",
        "## Análise por Versão do App",
        "",
        "| Versão | Crash Rate Médio | Dias | Período |",
        "|--------|-----------------|------|---------|",
    ]
    for row in crash_by_version:
        ver = row.get("app_version") or "?"
        pct = row.get("crash_avg_pct") or 0.0
        days = row.get("days_with_data") or 0
        first = str(row.get("first_seen") or "?")[:10]
        last = str(row.get("last_seen") or "?")[:10]
        lines.append(f"| {ver} | {pct:.1f}% | {days}d | {first} → {last} |")
    lines.append("")
    from play_insights.thresholds import detect_regression
    regression = detect_regression(crash_by_version)
    if regression.get("has_regression"):
        d = regression
        lines.append(
            f"> ⚠️ **Regressão:** Versão `{d['current_version']}` piorou "
            f"**+{d['delta_pp']:.1f}pp (+{d['pct_change']:.0f}%)** vs. `{d['prev_version']}`."
        )
        lines.append("")
    return lines


def _build_category_persistence(data: dict[str, Any]) -> list[str]:
    persistence = data.get("category_persistence") or []
    if not persistence:
        return []
    lines = [
        "---",
        "",
        "## Problemas Persistentes — Quanto Tempo Cada Categoria Está Presente",
        "",
        "| Categoria | Presente desde | Semanas | Reviews | Status |",
        "|-----------|---------------|---------|---------|--------|",
    ]
    for row in persistence:
        cat = row.get("complaint_category") or "?"
        label = _CATEGORY_LABELS.get(cat, cat)
        first = str(row.get("first_seen") or "?")[:10]
        weeks = row.get("weeks_present") or 0
        total = row.get("total_reviews") or 0
        status = "🔴 Crônico" if weeks >= 4 else ("🟡 Recorrente" if weeks >= 2 else "🟠 Novo")
        lines.append(f"| {label} | {first} | {weeks} sem. | {total} | {status} |")
    lines.append("")
    return lines


def _build_crash_vs_reviews_correlation(data: dict[str, Any]) -> list[str]:
    weekly = data.get("weekly_crash_vs_reviews") or []
    if not weekly:
        return []
    lines = [
        "---",
        "",
        "## Correlação: Crash Rate × Reviews Negativos por Semana",
        "",
        "| Semana | Crash Rate | Reviews Negativos |",
        "|--------|------------|------------------|",
    ]
    for row in weekly:
        week = str(row.get("week") or "?")[:10]
        crash = row.get("crash_avg_pct") or 0.0
        neg = row.get("neg_reviews") or 0
        lines.append(f"| {week} | {crash:.1f}% | {neg} |")
    lines.append("")
    # Simple correlation insight
    if len(weekly) >= 3:
        high_crash_weeks = [r for r in weekly if (r.get("crash_avg_pct") or 0) > 20]
        if high_crash_weeks:
            total_neg_in_high = sum(r.get("neg_reviews") or 0 for r in high_crash_weeks)
            total_neg_all = sum(r.get("neg_reviews") or 0 for r in weekly)
            if total_neg_all > 0:
                pct = round(total_neg_in_high / total_neg_all * 100)
                lines.append(
                    f"> Semanas com crash >20% concentram **{pct}%** dos reviews negativos do período."
                )
                lines.append("")
    return lines


def _build_urgent_alerts_weekly(data: dict[str, Any]) -> list[str]:
    urgent = data.get("urgent_reviews") or []
    if not urgent:
        return []
    lines = [
        "---",
        "",
        "## 🚨 Alertas de Urgência — Reviews com Situação Crítica",
        "",
        f"**{len(urgent)} review(s) com indicadores de urgência no período:**",
        "",
    ]
    for r in urgent[:5]:
        text = r.get("comment_text") or ""
        text = text.strip()[:250]
        stars = r.get("star_rating", "?")
        cat = r.get("complaint_category") or "?"
        cat_label = _CATEGORY_LABELS.get(cat, cat)
        d = str(r.get("ingest_date") or "?")[:10]
        lines.append(f"> \"{text}\"")
        lines.append(f"> _⭐ {stars} · {cat_label} · {d}_")
        lines.append("")
    return lines


def _fmt_rate(v: float | None) -> str:
    if v is None:
        return "N/D"
    return f"{v * 100:.2f}%"


def _fmt_ms(v: float | None) -> str:
    if v is None:
        return "N/D"
    return f"{int(v):,}ms"


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "N/D"
    return f"{v:.2f}%"


def _clarity_status(kpi: str, value: float | None) -> str:
    if value is None:
        return "⬜"
    from play_insights.clarity_analysis import KPI_THRESHOLDS, _LOWER_IS_BETTER
    t = KPI_THRESHOLDS.get(kpi)
    if not t:
        return "⬜"
    target = t["target"]
    alert = t["alert"]
    if kpi in _LOWER_IS_BETTER:
        if value <= target:
            return "✅"
        if value <= alert:
            return "⚠️"
        return "🚨"
    else:  # higher is better
        if value >= target:
            return "✅"
        if value >= alert:
            return "⚠️"
        return "🚨"


def _build_clarity_executive_summary(clarity_data: dict) -> list[str]:
    if not clarity_data or not clarity_data.get("current_kpis"):
        return []
    kpis = clarity_data["current_kpis"]
    trends = {t["kpi"]: t for t in clarity_data.get("trend_report", {}).get("kpi_trends", [])}
    baseline_available = clarity_data.get("trend_report", {}).get("baseline_available", False)
    alerts = clarity_data.get("trend_report", {}).get("alerts", [])

    total_sessions = kpis.get("total_sessions", 0)

    lines = [
        "---",
        "",
        "## Web & Checkout Intelligence — Microsoft Clarity",
        "",
        f"_Dados: {kpis.get('snapshot_date', '?')} · "
        f"Sessões: {total_sessions:,} · "
        f"Usuários: {kpis.get('total_users', 0):,} · "
        f"Janela de dados: 3 dias (limitação da API)_",
        "",
    ]

    if total_sessions == 0:
        lines += [
            "> ⚠️ **Sem dados de sessões neste período.** "
            "Verifique se o ingest do Clarity foi executado hoje (`python -m play_insights ingest-clarity`).",
            "",
        ]
        return lines

    if alerts:
        lines.append("> ⚠️ **Alertas de comportamento web detectados:**")
        for a in alerts:
            lines.append(f"> - {a}")
        lines.append("")

    kpi_rows = [
        ("rage_click_rate",       "Rage Click Rate",      _fmt_rate(kpis.get("rage_click_rate"))),
        ("dead_click_rate",       "Dead Click Rate",       _fmt_rate(kpis.get("dead_click_rate"))),
        ("error_click_rate",      "Error Click Rate",      _fmt_rate(kpis.get("error_click_rate"))),
        ("script_error_rate",     "Script Error Rate",     _fmt_rate(kpis.get("script_error_rate"))),
        ("avg_scroll_depth_pct",  "Scroll Depth Médio",    _fmt_pct(kpis.get("avg_scroll_depth_pct"))),
        ("avg_engagement_time_ms","Engagement Time Médio", _fmt_ms(kpis.get("avg_engagement_time_ms"))),
    ]

    baseline_col = "Baseline" if baseline_available else "Baseline (pendente)"
    lines += [
        f"| KPI | Atual | Semana Anterior | {baseline_col} | Tendência | Status |",
        "|-----|-------|-----------------|-----------------|-----------|--------|",
    ]
    for kpi_key, label, cur_str in kpi_rows:
        t = trends.get(kpi_key, {})
        prev_str = _fmt_rate(t.get("previous")) if "rate" in kpi_key else (
            _fmt_pct(t.get("previous")) if "pct" in kpi_key else _fmt_ms(t.get("previous"))
        )
        base_str = _fmt_rate(t.get("baseline")) if "rate" in kpi_key else (
            _fmt_pct(t.get("baseline")) if "pct" in kpi_key else _fmt_ms(t.get("baseline"))
        )
        if t.get("previous") is None:
            prev_str = "N/D"
        if t.get("baseline") is None:
            base_str = "—"
        trend_str = t.get("vs_previous", "N/D")
        status = _clarity_status(kpi_key, kpis.get(kpi_key))
        lines.append(f"| {label} | {cur_str} | {prev_str} | {base_str} | {trend_str} | {status} |")

    lines.append("")
    return lines


def _build_clarity_web_vitals(clarity_data: dict) -> list[str]:
    if not clarity_data or not clarity_data.get("current_kpis"):
        return []
    kpis = clarity_data["current_kpis"]
    trends = {t["kpi"]: t for t in clarity_data.get("trend_report", {}).get("kpi_trends", [])}

    # LCP/INP/CLS are not available in the Clarity Data Export API.
    # They are stored as 0.0 in the DB — treat 0.0 as "not available".
    lcp = kpis.get("avg_lcp_ms") or None
    inp = kpis.get("avg_inp_ms") or None
    cls = kpis.get("avg_cls") or None

    cwv_unavailable = lcp is None and inp is None and cls is None

    if cwv_unavailable:
        return [
            "### Core Web Vitals",
            "",
            "> ℹ️ LCP, INP e CLS não estão disponíveis na Clarity Data Export API. "
            "Para Core Web Vitals, utilize o Google Search Console ou CrUX.",
            "",
        ]

    lines = [
        "### Core Web Vitals",
        "",
        "| Métrica | Valor | Meta Google | Status | Tendência |",
        "|---------|-------|-------------|--------|-----------|",
        f"| LCP (Largest Contentful Paint) | {_fmt_ms(lcp)} | < 2.500ms | {_clarity_status('avg_lcp_ms', lcp)} | {trends.get('avg_lcp_ms', {}).get('vs_previous', 'N/D')} |",
        f"| INP (Interaction to Next Paint) | {_fmt_ms(inp)} | < 200ms | {_clarity_status('avg_inp_ms', inp)} | {trends.get('avg_inp_ms', {}).get('vs_previous', 'N/D')} |",
        f"| CLS (Cumulative Layout Shift) | {f'{cls:.3f}' if cls is not None else 'N/D'} | < 0.10 | {_clarity_status('avg_cls', cls)} | {trends.get('avg_cls', {}).get('vs_previous', 'N/D')} |",
        "",
    ]

    # Narrative for worst CWV
    worst = None
    if lcp and lcp > 4000:
        worst = ("LCP", f"{int(lcp):,}ms acima do threshold do Google ({int(lcp - 2500):,}ms de excesso)", "avg_lcp_ms")
    elif inp and inp > 500:
        worst = ("INP", f"{int(inp)}ms — interações com delay perceptível pelo usuário", "avg_inp_ms")
    elif cls and cls > 0.25:
        worst = ("CLS", f"{cls:.3f} — layout instável causando cliques errados", "avg_cls")

    if worst:
        lines += [
            f"> 🚨 **{worst[0]}: {worst[1]}**",
            "",
        ]

    return lines


def _build_clarity_device_breakdown(clarity_data: dict) -> list[str]:
    if not clarity_data or not clarity_data.get("cross_reference"):
        return []

    cross_ref = clarity_data["cross_reference"]
    if not cross_ref:
        return []

    lines = [
        "### Breakdown por Dispositivo (Clarity)",
        "",
        "| Dispositivo | Sessões | Rage Click Rate | Crash Rate (Play) | Risco |",
        "|-------------|---------|-----------------|-------------------|-------|",
    ]
    for item in cross_ref[:8]:
        device = item.get("device") or "N/D"
        sessions = f"{item.get('sessions') or 0:,}"
        rage = _fmt_rate(item.get("rage_click_rate_clarity"))
        crash = _fmt_rate(item.get("crash_rate_play"))
        risk = "🔴 Alto" if (item.get("risk_score") or 0) > 0.001 else ("🟡 Médio" if (item.get("risk_score") or 0) > 0.0001 else "🟢 Baixo")
        lines.append(f"| {device} | {sessions} | {rage} | {crash} | {risk} |")

    lines.append("")
    return lines


def _build_clarity_cross_reference(clarity_data: dict) -> list[str]:
    if not clarity_data or not clarity_data.get("cross_reference"):
        return []

    cross_ref = [c for c in clarity_data["cross_reference"] if (c.get("crash_rate_play") or 0) > 0 and (c.get("rage_click_rate_clarity") or 0) > 0]
    if not cross_ref:
        return [
            "### Cross-Reference: Play Store × Clarity",
            "",
            "_Nenhum dispositivo com dados em ambas as plataformas nesta semana._",
            "",
        ]

    lines = [
        "### Cross-Reference: Play Store × Clarity — Dispositivos de Duplo Risco",
        "",
        "> Dispositivos com problemas em **ambas** as plataformas — maior risco de abandono do usuário.",
        "",
        "| Dispositivo | Crash Rate (App) | Rage Click Rate (Site) | Risk Score | Prioridade |",
        "|-------------|-----------------|----------------------|------------|------------|",
    ]
    for item in cross_ref[:5]:
        device = item.get("device") or "N/D"
        crash = _fmt_rate(item.get("crash_rate_play"))
        rage = _fmt_rate(item.get("rage_click_rate_clarity"))
        risk = item.get("risk_score") or 0
        prio = "🔴 Crítico" if risk > 0.001 else ("🟠 Alto" if risk > 0.0001 else "🟡 Médio")
        lines.append(f"| {device} | {crash} | {rage} | {risk:.6f} | {prio} |")

    lines.append("")

    if cross_ref:
        top = cross_ref[0]
        lines += [
            f"> **{top.get('device', '?')}:** "
            f"{_fmt_rate(top.get('crash_rate_play'))} crash rate no app + "
            f"{_fmt_rate(top.get('rage_click_rate_clarity'))} rage click rate no site = "
            "experiência completamente comprometida em ambos os canais.",
            "",
        ]

    return lines


def _build_clarity_trends(clarity_data: dict) -> list[str]:
    if not clarity_data or not clarity_data.get("trend_report"):
        return []

    trend_report = clarity_data["trend_report"]
    kpi_trends = trend_report.get("kpi_trends", [])
    if not kpi_trends:
        return []

    lines = [
        "### Tendência de KPIs Web (Clarity)",
        "",
        f"_Baseline disponível: {'Sim' if trend_report.get('baseline_available') else 'Não (acumular 7+ dias de dados)'}_",
        "",
        "| KPI | Atual | vs. Semana Anterior | vs. Baseline |",
        "|-----|-------|---------------------|--------------|",
    ]

    kpi_labels = {
        "rage_click_rate": "Rage Click Rate",
        "dead_click_rate": "Dead Click Rate",
        "error_click_rate": "Error Click Rate",
        "script_error_rate": "Script Error Rate",
        "avg_scroll_depth_pct": "Scroll Depth Médio",
        "avg_engagement_time_ms": "Engagement Time Médio",
        "avg_lcp_ms": "LCP",
        "avg_inp_ms": "INP",
        "avg_cls": "CLS",
    }

    for t in kpi_trends:
        kpi = t.get("kpi", "")
        label = kpi_labels.get(kpi, kpi)
        cur = t.get("current", 0.0)
        alert_marker = " ⚠️" if t.get("is_alert") else ""

        if "rate" in kpi:
            cur_str = _fmt_rate(cur)
        elif "pct" in kpi:
            cur_str = _fmt_pct(cur)
        elif "ms" in kpi:
            cur_str = _fmt_ms(cur)
        else:
            cur_str = f"{cur:.4f}"

        vs_prev = t.get("vs_previous", "N/D")
        vs_base = t.get("vs_baseline", "N/D")
        lines.append(f"| {label}{alert_marker} | {cur_str} | {vs_prev} | {vs_base} |")

    lines.append("")
    return lines


def _build_clarity_dev_section(clarity_data: dict) -> list[str]:
    if not clarity_data or not clarity_data.get("current_kpis"):
        return []

    kpis = clarity_data["current_kpis"]
    lines = ["### Para o Time de Desenvolvimento (Clarity)", ""]

    issues_found = False

    rage = kpis.get("rage_click_rate") or 0.0
    if rage > 0.04:
        issues_found = True
        lines += [
            f"**🔴 Rage Click Rate crítico: {_fmt_rate(rage)}** — usuários clicando repetidamente em elementos que não respondem.",
            "",
            "Causas prováveis e próximos passos:",
            "1. Abrir Clarity Dashboard → Rage Clicks → identificar os elementos/páginas mais afetados",
            "2. Verificar se há event listeners faltando ou com `e.preventDefault()` bloqueando a ação",
            "3. Adicionar feedback visual de loading (spinner/skeleton) em botões de ação",
            "4. Checar se há debounce excessivo em handlers de click causando atraso perceptível",
            "5. Validar que botões de CTA (comprar, confirmar, pagar) respondem em < 100ms",
            "",
        ]
    elif rage > 0.02:
        issues_found = True
        lines += [
            f"**⚠️ Rage Click Rate elevado: {_fmt_rate(rage)}** — investigar elementos mais clicados sem resposta.",
            "",
            "1. Identificar via Clarity Session Replay as páginas com maior concentração de rage clicks",
            "2. Revisar feedback visual de ações assíncronas (checkout, carregamento de ingressos)",
            "",
        ]

    script_err = kpis.get("script_error_rate") or 0.0
    if script_err > 0.02:
        issues_found = True
        lines += [
            f"**🔴 Script Error Rate crítico: {_fmt_rate(script_err)}** — erros JavaScript bloqueando interação silenciosamente.",
            "",
            "1. Abrir DevTools Console em uma sessão Clarity para capturar stack traces",
            "2. Verificar se há erros em bundles JavaScript após deploy recente",
            "3. Checar compatibilidade de features (Promise, fetch, optional chaining) com browsers mais antigos",
            "4. Revisar integrações de terceiros (analytics, payment, tag manager) — são fontes frequentes",
            "",
        ]
    elif script_err > 0.005:
        issues_found = True
        lines += [
            f"**⚠️ Script Error Rate acima do target: {_fmt_rate(script_err)}**",
            "1. Monitorar console de erros no próximo deploy",
            "2. Verificar se erros aumentaram após mudança recente de bundle",
            "",
        ]

    lcp = kpis.get("avg_lcp_ms") or 0.0
    if lcp > 4000:
        issues_found = True
        lines += [
            f"**🔴 LCP crítico: {_fmt_ms(lcp)}** — página demorando para renderizar o conteúdo principal.",
            "",
            "1. Auditar imagens acima da dobra: converter para WebP/AVIF e adicionar `loading='eager'` apenas no hero",
            "2. Verificar TTFB (Time to First Byte) — se > 600ms, investigar server-side rendering ou cache de CDN",
            "3. Eliminar render-blocking resources (CSS inline critical, defer scripts não-críticos)",
            "4. Verificar fontes: usar `font-display: swap` e preload das fontes principais",
            "",
        ]
    elif lcp > 2500:
        issues_found = True
        lines += [
            f"**⚠️ LCP acima do target Google: {_fmt_ms(lcp)}** (meta: < 2.500ms)",
            "1. Usar `<link rel='preload'>` para imagens hero e recursos críticos",
            "2. Habilitar compressão Brotli/Gzip no servidor",
            "",
        ]

    inp = kpis.get("avg_inp_ms") or 0.0
    if inp > 500:
        issues_found = True
        lines += [
            f"**🔴 INP crítico: {_fmt_ms(inp)}** — interações com delay perceptível pelo usuário.",
            "",
            "1. Identificar handlers de evento pesados — usar `requestIdleCallback` ou `scheduler.postTask`",
            "2. Verificar se há third-party scripts bloqueando o main thread (analytics, chat widgets)",
            "3. Quebrar tarefas longas (> 50ms) com `setTimeout(0)` ou workers",
            "",
        ]
    elif inp > 200:
        issues_found = True
        lines += [
            f"**⚠️ INP acima do target: {_fmt_ms(inp)}** (meta: < 200ms)",
            "1. Perfil do main thread com Chrome DevTools Performance",
            "2. Verificar event handlers síncronos em listas longas (virtualização recomendada)",
            "",
        ]

    if not issues_found:
        lines += [
            "✅ Nenhum problema técnico crítico identificado nesta semana.",
            "Continuar monitorando Rage Clicks e Core Web Vitals semanalmente.",
            "",
        ]

    return lines


def generate_weekly_report(
    repo: DuckDBRepository,
    window: int = 30,
    output_suffix: str = "",
    clarity_data: dict | None = None,
) -> Path:
    today = date.today().isoformat()
    timestamp = datetime.now(tz=timezone.utc).isoformat()

    path = Path("docs/research") / f"play-quality{output_suffix}-{today}.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    data = _fetch_weekly_data(repo, window=window)

    # Threshold violations summary for header
    violations = data.get("threshold_violations") or []
    crash_trend = data.get("crash_trend")
    violation_summary = format_violation_summary(violations) if violations else ""

    lines: list[str] = [
        f"# Weekly Play Quality Intelligence — {today}",
        "",
        f"_Gerado em {timestamp} · Fonte: {repo.db_path} · Janela: {window} dias_",
        "",
    ]
    if violation_summary:
        lines.append(violation_summary)
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.extend(_build_narrative(data, window))
    lines.extend(_build_risk_flags(data, window))
    lines.extend(_build_rating_trend(data))
    lines.extend(_build_category_deep_dives(data, window))
    lines.extend(_build_technical_hotspots(data))
    lines.extend(_build_crash_diagnosis_weekly(data))
    lines.extend(_build_performance_section_weekly(data))
    lines.extend(_build_version_regression_weekly(data))
    lines.extend(_build_category_persistence(data))
    lines.extend(_build_crash_vs_reviews_correlation(data))
    urgent = _build_urgent_alerts_weekly(data)
    if urgent:
        lines.extend(urgent)
    lines.extend(_build_impact_matrix(data))
    lines.extend(_build_strategic_roadmap(data))

    # Clarity web intelligence (if available)
    if clarity_data and not clarity_data.get("skipped"):
        lines.extend(_build_clarity_executive_summary(clarity_data))
        lines.extend(_build_clarity_web_vitals(clarity_data))
        lines.extend(_build_clarity_device_breakdown(clarity_data))
        lines.extend(_build_clarity_cross_reference(clarity_data))
        lines.extend(_build_clarity_trends(clarity_data))
        lines.extend(_build_clarity_dev_section(clarity_data))

    # Install trends (if available)
    install_rows = data.get("install_rows") or []
    if install_rows:
        lines += [
            "---",
            "",
            "## Tendência de Instalações",
            "",
            "| Data | Instalações | Desinstalações | Dispositivos Ativos |",
            "|------|-------------|----------------|---------------------|",
        ]
        for row in install_rows:
            d = str(row.get("date") or "?")[:10]
            inst = row.get("installs") or 0
            uninst = row.get("uninstalls") or 0
            active = row.get("active_devices") or 0
            lines.append(f"| {d} | {inst} | {uninst} | {active} |")
        lines.append("")

    lines += [
        "---",
        "",
        f"_Relatório semanal gerado em {timestamp}_",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
