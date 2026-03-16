from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from play_insights.duckdb_repo import DuckDBRepository
from play_insights.thresholds import (
    ThresholdViolation,
    TrendVelocity,
    calculate_trend_velocity,
    check_violations,
    detect_regression,
    format_violation_summary,
)

_SEVERITY_LABELS = {
    5: "Crítico — app inutilizável",
    4: "Alto — função core comprometida",
    3: "Médio — experiência degradada",
    2: "Baixo — incômodo menor",
    1: "Informativo",
}

_INTENT_LABELS = {
    "bug_report": "Bug / Problema técnico",
    "frustration": "Frustração / Experiência negativa",
    "support_request": "Pedido de suporte",
    "feature_request": "Solicitação de funcionalidade",
    "praise": "Elogio",
}

_INTENT_IMPLICATIONS = {
    "bug_report": "Investigar e corrigir — usuário identificou problema técnico específico",
    "frustration": "Priorizar UX — experiência percebida como ruim mesmo sem bug explícito",
    "support_request": "Avaliar FAQ/onboarding — usuário não encontrou resposta sozinho",
    "feature_request": "Registrar no backlog — demanda de funcionalidade identificada",
    "praise": "Identificar o que funciona bem para preservar",
}

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

_CATEGORY_ACTIONS = {
    "estabilidade": "Acionar engenharia para investigar crash logs e traces do período.",
    "performance": "Revisar métricas de tempo de resposta e perfis de memória/CPU.",
    "login_autenticacao": "Verificar fluxo de autenticação, tokens expirados e edge cases de login social.",
    "pagamento_assinatura": "Prioridade máxima — impacto direto em receita. Revisar fluxo de pagamento e cobranças.",
    "usabilidade": "Rodar teste de usabilidade rápido. Identificar os 3 pontos de maior atrito na jornada.",
    "funcionalidade_quebrada": "Reproduzir o bug relatado e abrir issue com severidade alta.",
    "conteudo_confiabilidade": "Auditar os dados/conteúdos citados nas queixas. Verificar fonte e sincronização.",
    "suporte_comunicacao": "Revisar tempos de resposta do suporte e gaps no FAQ/onboarding.",
    "experiencia_compra": "Revisar fluxo completo de compra: checkout, QR code, confirmação, pagamento. Testar em múltiplos dispositivos.",
}


def _truncate(text: str, max_chars: int = 280) -> str:
    if not text:
        return ""
    text = text.strip().replace("\n", " ").replace("\r", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text if len(text) <= max_chars else text[:max_chars] + "…"


def _health_signal(avg_rating: float | None, crash_avg: float, neg_pct: float) -> tuple[str, str]:
    if avg_rating is None:
        return "⚪", "Sem dados de rating suficientes"
    if avg_rating >= 4.0 and crash_avg < 0.05 and neg_pct < 30:
        return "🟢", "Saudável"
    if avg_rating >= 3.0 and crash_avg < 0.10:
        return "🟡", "Atenção"
    return "🔴", "Crítico"


def _fetch_daily_data(repo: DuckDBRepository, window: int = 30) -> dict[str, Any]:
    rating_rows = repo.query(f"""
        SELECT
            ROUND(AVG(CAST(star_rating AS DOUBLE)), 2) AS avg_rating,
            COUNT(*) AS total_reviews,
            SUM(CASE WHEN star_rating <= 2 THEN 1 ELSE 0 END) AS negative,
            SUM(CASE WHEN star_rating >= 4 THEN 1 ELSE 0 END) AS positive
        FROM reviews_raw
        WHERE ingest_date >= CURRENT_DATE - {window}
    """)
    rating = rating_rows[0] if rating_rows else {}

    reviews_with_text = repo.query(f"""
        SELECT r.star_rating, r.comment_text, r.reviewer_language, r.app_version_name,
               e.complaint_category, e.severity, e.intent, e.sentiment_label, e.topic_keywords
        FROM reviews_raw r
        JOIN reviews_enriched e ON r.review_id = e.review_id
        WHERE e.sentiment_label = 'neg'
          AND r.ingest_date >= CURRENT_DATE - {window}
        ORDER BY e.severity DESC, r.last_modified_at DESC
        LIMIT 50
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

    severity_dist = repo.query(f"""
        SELECT severity, COUNT(*) AS total
        FROM reviews_enriched
        WHERE ingest_date >= CURRENT_DATE - {window}
          AND sentiment_label = 'neg'
        GROUP BY severity
        ORDER BY severity DESC
    """)

    intent_dist = repo.query(f"""
        SELECT intent, COUNT(*) AS total
        FROM reviews_enriched
        WHERE ingest_date >= CURRENT_DATE - {window}
        GROUP BY intent
        ORDER BY total DESC
    """)

    vitals = repo.query(f"""
        SELECT metric_set,
               ROUND(AVG(metric_value), 6) AS avg_value,
               ROUND(MAX(metric_value), 6) AS max_value,
               COUNT(DISTINCT date) AS days_with_data
        FROM vitals_daily
        WHERE date >= CURRENT_DATE - {window}
        GROUP BY metric_set
        ORDER BY metric_set
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
        LIMIT 20
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

    error_issues_count = repo.query(f"""
        SELECT COUNT(*) AS total FROM error_issues
        WHERE ingest_date >= CURRENT_DATE - {window}
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

    try:
        urgent_reviews = repo.query(f"""
            SELECT r.comment_text, r.star_rating, r.ingest_date, r.app_version_name,
                   e.complaint_category, e.severity
            FROM reviews_raw r
            JOIN reviews_enriched e ON r.review_id = e.review_id
            WHERE e.event_urgency = TRUE
              AND r.ingest_date >= CURRENT_DATE - 7
            ORDER BY r.ingest_date DESC
            LIMIT 10
        """)
    except Exception:  # noqa: BLE001
        urgent_reviews = []

    # Compute derived analytics from already-fetched data
    vitals_list = [{"metric_set": v.get("metric_set"), "avg_value": v.get("avg_value")} for v in vitals]
    threshold_violations = check_violations(vitals_list)
    crash_trend = calculate_trend_velocity(crash_series)

    return {
        "rating": rating,
        "reviews_with_text": reviews_with_text,
        "categories": categories,
        "severity_dist": severity_dist,
        "intent_dist": intent_dist,
        "vitals": vitals,
        "crash_series": crash_series,
        "vitals_dim_gap": vitals_dim_gap[0] if vitals_dim_gap else {},
        "error_issues_count": (error_issues_count[0].get("total", 0) if error_issues_count else 0),
        "crash_by_device": crash_by_device,
        "crash_by_version": crash_by_version,
        "performance_vitals": performance_vitals,
        "urgent_reviews": urgent_reviews,
        "threshold_violations": threshold_violations,
        "crash_trend": crash_trend,
    }


def _build_header(today: str, data: dict[str, Any], window: int) -> list[str]:
    rating = data["rating"]
    vitals = data["vitals"]
    categories = data["categories"]

    avg_r = rating.get("avg_rating")
    total = rating.get("total_reviews", 0) or 0
    neg = rating.get("negative", 0) or 0
    pos = rating.get("positive", 0) or 0
    neg_pct = round(neg / total * 100) if total else 0
    pos_pct = round(pos / total * 100) if total else 0

    crash_avg = next(
        (v["avg_value"] for v in vitals if "crash" in (v.get("metric_set") or "").lower()), 0.0
    ) or 0.0
    anr_avg = next(
        (v["avg_value"] for v in vitals if "anr" in (v.get("metric_set") or "").lower()), 0.0
    ) or 0.0

    health_emoji, health_label = _health_signal(avg_r, crash_avg, neg_pct)

    lines: list[str] = [
        "---",
        "",
        f"**Saúde do App:** {health_emoji} {health_label}",
        "",
        "---",
        "",
        "## Narrativa do Período",
        "",
    ]

    if total == 0:
        lines.append(
            "Nenhum review coletado no período analisado. Verifique a ingestão ou "
            "aguarde novos reviews chegarem ao Play Console."
        )
    else:
        rating_str = f"⭐ {avg_r:.1f}/5.0" if avg_r else "sem rating"
        lines.append(
            f"Nos últimos **{window} dias**, o app recebeu **{total} avaliação(ões)** "
            f"com média {rating_str}. Do total, **{neg} ({neg_pct}%) são negativas** "
            f"e {pos} ({pos_pct}%) são positivas."
        )
        lines.append("")

        if categories:
            top_cat = categories[0]
            cat_label = _CATEGORY_LABELS.get(top_cat["complaint_category"], top_cat["complaint_category"])
            lines.append(
                f"O tema que mais aparece nas queixas é **{cat_label}** — "
                f"{top_cat['total']} relato(s) com severidade média de {top_cat['avg_severity']}/5. "
                "Isso indica que o maior ponto de atrito percebido pelos usuários está nessa área."
            )
            lines.append("")

        vitals_parts = []
        if crash_avg:
            vitals_parts.append(f"crash rate médio de **{crash_avg:.2%}**")
        if anr_avg:
            vitals_parts.append(f"ANR rate médio de **{anr_avg:.2%}**")
        if vitals_parts:
            lines.append(
                f"Do ponto de vista técnico, os vitals apontam {' e '.join(vitals_parts)} "
                f"nos últimos {window} dias."
            )
            lines.append("")

    return lines


def _build_priority_board(recommendations: list[dict[str, Any]]) -> list[str]:
    lines = [
        "---",
        "",
        "## Prioridade do Dia — O Que Atacar Agora",
        "",
        "_Lista curada de ações ordenadas por impacto esperado. "
        "Cada item combina evidências de reviews, vitals e erros._",
        "",
    ]

    if not recommendations:
        lines += [
            "Nenhuma recomendação gerada para hoje. Execute `python -m play_insights analyze` primeiro.",
            "",
        ]
        return lines

    for i, rec in enumerate(recommendations[:5], 1):
        cat = rec.get("complaint_category", "?")
        cat_label = _CATEGORY_LABELS.get(cat, cat)
        score = rec.get("expected_impact_score", 0) or 0
        effort = rec.get("effort_tshirt", "?")
        owner = rec.get("owner_suggestion", "?")

        ev_parts: dict[str, str] = {}
        for part in (rec.get("evidence_refs") or "").split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                ev_parts[k.strip()] = v.strip()

        neg_count = ev_parts.get("neg_count", "?")
        severity_avg = ev_parts.get("severity_avg", "?")
        vitals_avg_str = ev_parts.get("vitals_avg", "0")
        try:
            vitals_avg_f = float(vitals_avg_str)
            vitals_display = f"{vitals_avg_f:.2%}"
        except (ValueError, TypeError):
            vitals_display = vitals_avg_str

        action_hint = _CATEGORY_ACTIONS.get(cat, "Investigar a raiz do problema.")

        lines.append(f"### {i}. {cat_label}")
        lines.append(
            f"**Impacto estimado:** {score:.1f} | **Esforço:** {effort} | **Dono sugerido:** {owner}"
        )
        lines.append("")
        lines.append(
            f"**Evidência:** {neg_count} review(s) negativo(s) · "
            f"severidade média {severity_avg}/5 · vitals avg {vitals_display}"
        )
        lines.append("")
        lines.append(f"**Ação recomendada:** {action_hint}")
        lines.append("")

    return lines


def _build_customer_voice(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Voz do Usuário — O Que Eles Estão Dizendo",
        "",
        "_Citações reais extraídas dos reviews. "
        "Cada voz representa um usuário real com uma experiência real no app._",
        "",
    ]

    reviews = data["reviews_with_text"]
    categories = data["categories"]

    if not categories:
        lines += ["Sem reviews negativos no período para exibir.", ""]
        return lines

    by_cat: dict[str, list[dict]] = {}
    for r in reviews:
        cat = r.get("complaint_category") or "outro"
        by_cat.setdefault(cat, []).append(r)

    for cat_row in categories:
        cat = cat_row["complaint_category"]
        cat_label = _CATEGORY_LABELS.get(cat, cat)
        total = cat_row["total"]
        avg_sev = cat_row["avg_severity"]
        cat_reviews = by_cat.get(cat, [])

        lines.append(f"### {cat_label}")
        lines.append(f"**{total} relato(s)** · severidade média **{avg_sev}/5**")
        lines.append("")

        shown = 0
        for r in cat_reviews[:3]:
            text = _truncate(r.get("comment_text") or "", 280)
            if not text:
                continue
            stars = r.get("star_rating", "?")
            lang = r.get("reviewer_language") or "idioma desconhecido"
            intent_raw = r.get("intent") or ""
            intent = _INTENT_LABELS.get(intent_raw, intent_raw)
            sev = r.get("severity", "?")
            ver = r.get("app_version_name") or "versão não identificada"

            lines.append(f"> \"{text}\"")
            lines.append(
                f"> _⭐ {stars} estrela(s) · {lang} · {intent} · severidade {sev}/5 · {ver}_"
            )
            lines.append("")
            shown += 1

        if shown == 0:
            lines.append("_Reviews desta categoria não possuem texto disponível._")
            lines.append("")

        keywords: set[str] = set()
        for r in cat_reviews:
            kw = r.get("topic_keywords") or ""
            keywords.update(k.strip() for k in kw.split(",") if k.strip())

        if keywords:
            lines.append(f"**Palavras-chave detectadas:** {', '.join(sorted(keywords)[:10])}")
            lines.append("")

        intents_in_cat = [r.get("intent") for r in cat_reviews if r.get("intent")]
        if intents_in_cat:
            dominant_intent = max(set(intents_in_cat), key=intents_in_cat.count)
            intent_label = _INTENT_LABELS.get(dominant_intent, dominant_intent)
            lines.append(
                f"**Padrão observado:** A maioria das queixas desta categoria é classificada como "
                f"**{intent_label}** — {_INTENT_IMPLICATIONS.get(dominant_intent, '')}."
            )
            lines.append("")

    return lines


def _build_vitals_section(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Vitals Técnicos — O Que Sabemos e O Que Não Sabemos",
        "",
    ]

    vitals = data["vitals"]
    categories = data["categories"]
    cat_names = [c["complaint_category"] for c in categories]
    crash_series = data.get("crash_series") or []
    dim_gap = data.get("vitals_dim_gap") or {}
    error_count = data.get("error_issues_count") or 0

    if not vitals:
        lines += ["Sem dados de vitals coletados no período.", ""]
        return lines

    # Summary table
    lines.append("### Resumo do Período")
    lines.append("")
    lines.append("| Métrica | Média | Pico máximo | Dias com dados | Status |")
    lines.append("|---------|-------|-------------|----------------|--------|")

    crash_avg = 0.0
    anr_avg = 0.0

    for v in vitals:
        ms = v.get("metric_set") or "?"
        avg = v.get("avg_value") or 0.0
        mx = v.get("max_value") or 0.0
        days = v.get("days_with_data") or 0

        if "crash" in ms.lower():
            label = "Crash Rate"
            crash_avg = avg
            status = "🟢 OK" if avg < 0.02 else "🟡 Atenção" if avg < 0.05 else "🔴 Crítico"
        elif "anr" in ms.lower():
            label = "ANR Rate"
            anr_avg = avg
            status = "🟢 OK" if avg < 0.01 else "🟡 Atenção" if avg < 0.03 else "🔴 Crítico"
        else:
            label = ms
            status = "—"

        lines.append(
            f"| {label} | {avg:.4f} ({avg:.2%}) | {mx:.4f} ({mx:.2%}) | {days} dias | {status} |"
        )

    lines.append("")

    # Crash rate time series (most recent 14 days)
    if crash_series:
        lines.append("### Evolução do Crash Rate (dias mais recentes primeiro)")
        lines.append("")
        lines.append("| Data | Média diária | Mínimo | Máximo | Segmentos |")
        lines.append("|------|-------------|--------|--------|-----------|")
        worst_day = max(crash_series, key=lambda r: r.get("avg_crash") or 0)
        best_day = min(crash_series, key=lambda r: r.get("avg_crash") or 0)
        for row in crash_series[:14]:
            d = str(row.get("date") or "?")[:10]
            avg = row.get("avg_crash") or 0.0
            mn = row.get("min_crash") or 0.0
            mx = row.get("max_crash") or 0.0
            n = row.get("n_segments") or 0
            flag = " ⬆️ pior" if row is worst_day else (" ⬇️ melhor" if row is best_day else "")
            lines.append(f"| {d} | {avg:.2%}{flag} | {mn:.2%} | {mx:.2%} | {n} |")
        lines.append("")
        lines.append(
            f"> **Pior dia registrado:** {str(worst_day.get('date') or '?')[:10]} — "
            f"crash rate médio de **{(worst_day.get('avg_crash') or 0):.2%}**, "
            f"pico de **{(worst_day.get('max_crash') or 0):.2%}**."
        )
        lines.append(
            f"> **Melhor dia registrado:** {str(best_day.get('date') or '?')[:10]} — "
            f"crash rate médio de **{(best_day.get('avg_crash') or 0):.2%}**."
        )
        lines.append("")

    # Hotspots por device (when data is available)
    crash_by_device = data.get("crash_by_device") or []
    if crash_by_device:
        lines.append("### Hotspots por Dispositivo — Onde os Crashes Mais Acontecem")
        lines.append("")
        lines.append("| Dispositivo | Android | Versão app | Crash Rate Médio | Dias |")
        lines.append("|-------------|---------|-----------|-----------------|------|")
        for row in crash_by_device[:8]:
            device = row.get("device_model") or "?"
            android = row.get("os_version") or "?"
            ver = row.get("app_version") or "?"
            pct = row.get("crash_pct") or 0.0
            days = row.get("days_with_data") or 0
            lines.append(f"| {device} | API {android} | {ver} | {pct:.1f}% | {days}d |")
        lines.append("")
        worst = crash_by_device[0]
        lines.append(
            f"> **Dispositivo mais afetado:** `{worst.get('device_model')}` "
            f"(Android API {worst.get('os_version')}) — {worst.get('crash_pct'):.1f}% "
            f"de crash rate médio em {worst.get('days_with_data')} dia(s)."
        )
        lines.append("")

    # Version regression analysis
    lines.extend(_build_version_regression(data))

    # Data availability declaration
    lines.append("### O Que a API Está (e Não Está) Retornando")
    lines.append("")

    total_rows = dim_gap.get("total_rows") or 0
    with_ver = dim_gap.get("with_app_version") or 0
    with_dev = dim_gap.get("with_device_model") or 0
    with_country = dim_gap.get("with_country") or 0

    lines.append(f"Total de segmentos de vitals na base: **{total_rows}**")
    lines.append("")
    lines.append("| Dimensão | Preenchida | Ausente | Situação |")
    lines.append("|----------|-----------|---------|----------|")
    lines.append(
        f"| Versão do app | {with_ver} | {total_rows - with_ver} | "
        f"{'✅ Disponível' if with_ver > 0 else '❌ Sem dados — não é possível identificar versões afetadas'} |"
    )
    lines.append(
        f"| Modelo de dispositivo | {with_dev} | {total_rows - with_dev} | "
        f"{'✅ Disponível' if with_dev > 0 else '❌ Sem dados — não é possível identificar dispositivos afetados'} |"
    )
    lines.append(
        f"| País | {with_country} | {total_rows - with_country} | "
        f"{'✅ Disponível' if with_country > 0 else '❌ Sem dados — não é possível identificar regiões afetadas'} |"
    )
    lines.append("")
    lines.append(
        f"**Error Issues (stack traces / erros rastreados):** {error_count} registro(s) no período. "
        + ("Sem detalhes de erros específicos disponíveis via API."
           if error_count == 0 else f"{error_count} issue(s) — ver seção de hotspots.")
    )
    lines.append("")
    if with_ver == 0 and with_dev == 0:
        lines.append(
            "> **Limitação dos dados:** A API Play Developer Reporting está retornando crash rate sem "
            "breakdown por versão, dispositivo ou país. Isso impede identificar quais versões ou "
            "aparelhos são mais afetados. **Para investigar a causa raiz dos crashes, acesse diretamente:**"
        )
        lines.append("> - Play Console → Android Vitals → Crashes & ANRs")
        lines.append("> - Firebase Crashlytics (se integrado) → ver stack traces por versão")
        lines.append("")

    # Correlation narrative (evidence-based only)
    if crash_avg > 0.02:
        if "estabilidade" in cat_names or "funcionalidade_quebrada" in cat_names:
            lines.append(
                f"> **Correlação:** Crash rate de **{crash_avg:.2%}** alinhado com queixas de "
                "estabilidade nos reviews."
            )
        else:
            lines.append(
                f"> **Desalinhamento:** Crash rate de **{crash_avg:.2%}** está elevado, "
                "mas os reviews não citam crashes. Usuários afetados podem estar desinstalando "
                "sem deixar avaliação — investigar taxa de retenção."
            )
        lines.append("")

    return lines


def _build_severity_section(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Distribuição de Severidade das Queixas",
        "",
        "| Nível | Queixas | O que significa para produto |",
        "|-------|---------|------------------------------|",
    ]

    severity_dist = data["severity_dist"]
    if not severity_dist:
        lines += ["Sem dados de severidade no período.", ""]
        return lines

    for row in severity_dist:
        sev = row.get("severity") or "?"
        total = row.get("total") or 0
        label = _SEVERITY_LABELS.get(sev, f"Severidade {sev}")
        lines.append(f"| {sev}/5 | {total} | {label} |")

    lines.append("")

    critical = next((r["total"] for r in severity_dist if r.get("severity") == 5), 0) or 0
    high = next((r["total"] for r in severity_dist if r.get("severity") == 4), 0) or 0

    if critical > 0:
        lines.append(
            f"> 🔴 **Alerta crítico:** {critical} review(s) com severidade 5/5 — "
            "esses usuários consideram o app inutilizável. Requer ação imediata."
        )
    elif high > 0:
        lines.append(
            f"> 🟡 **Atenção:** {high} review(s) com severidade 4/5 — "
            "função core do app está comprometida para esses usuários. Priorizar na próxima sprint."
        )
    else:
        lines.append(
            "> 🟢 Nenhuma queixa de severidade crítica ou alta no período. "
            "Continuar monitorando para não perder degradação gradual."
        )

    lines.append("")
    return lines


def _build_intent_section(data: dict[str, Any]) -> list[str]:
    lines = [
        "---",
        "",
        "## Intenção dos Usuários",
        "",
        "_O que os usuários realmente querem? Bugs para corrigir, suporte para oferecer ou features para construir?_",
        "",
        "| Intenção | Total | O que significa para produto |",
        "|----------|-------|------------------------------|",
    ]

    intent_dist = data["intent_dist"]
    if not intent_dist:
        lines += ["Sem dados de intenção no período.", ""]
        return lines

    for row in intent_dist:
        intent = row.get("intent") or "?"
        total = row.get("total") or 0
        label = _INTENT_LABELS.get(intent, intent)
        implication = _INTENT_IMPLICATIONS.get(intent, "—")
        lines.append(f"| {label} | {total} | {implication} |")

    lines.append("")

    # Dominant intent narrative
    top_intent_row = intent_dist[0] if intent_dist else None
    if top_intent_row:
        top_intent = top_intent_row.get("intent") or ""
        top_label = _INTENT_LABELS.get(top_intent, top_intent)
        lines.append(
            f"> **Sinal dominante:** A maioria dos feedbacks é classificada como **{top_label}**. "
            f"{_INTENT_IMPLICATIONS.get(top_intent, '')}"
        )
        lines.append("")

    return lines


def _build_executive_kpi_table(data: dict[str, Any], today: str, window: int) -> list[str]:
    """Build the executive summary KPI table with threshold alerts."""
    rating = data["rating"]
    vitals = data["vitals"]
    categories = data["categories"]
    violations: list[ThresholdViolation] = data.get("threshold_violations") or []
    crash_trend: TrendVelocity = data.get("crash_trend") or TrendVelocity(
        metric="crashRateMetricSet", current_7d_avg=0.0, prev_7d_avg=0.0, delta_pp=0.0, direction="→ estável"
    )

    avg_r = rating.get("avg_rating")
    total = rating.get("total_reviews", 0) or 0
    neg = rating.get("negative", 0) or 0

    crash_avg = next((v.get("avg_value") or 0.0 for v in vitals if "crash" in (v.get("metric_set") or "").lower()), 0.0)
    anr_avg = next((v.get("avg_value") or 0.0 for v in vitals if "anr" in (v.get("metric_set") or "").lower()), 0.0)

    # Semáforo based on threshold multiples
    def _traffic_light(metric_set: str, value: float) -> str:
        v_match = next((v for v in violations if v.metric_set == metric_set), None)
        if v_match is None:
            return "🟢"
        return "🔴" if v_match.multiple > 5.0 else "🟡"

    crash_light = _traffic_light("crashRateMetricSet", crash_avg)
    anr_light = _traffic_light("anrRateMetricSet", anr_avg)

    top_cat = categories[0]["complaint_category"] if categories else "—"
    top_cat_label = _CATEGORY_LABELS.get(top_cat, top_cat)
    top_cat_count = categories[0]["total"] if categories else 0

    rating_str = f"⭐ {avg_r:.1f}" if avg_r else "N/A"
    rating_light = "🟢" if avg_r and avg_r >= 4.0 else ("🟡" if avg_r and avg_r >= 3.0 else "🔴")

    crash_delta_str = f"{crash_trend.direction} ({crash_trend.delta_pp:+.1f}pp)"
    crash_pct_str = f"{crash_avg:.2%}" if crash_avg else "N/A"
    anr_pct_str = f"{anr_avg:.2%}" if anr_avg else "N/A"

    lines = [
        f"## Resumo Executivo — {today}",
        "",
        "| Indicador | Valor | Tendência | Status |",
        "|-----------|-------|-----------|--------|",
        f"| Rating | {rating_str}/5.0 ({total} reviews) | — | {rating_light} |",
        f"| Crash Rate | {crash_pct_str} | {crash_delta_str} | {crash_light} |",
        f"| ANR Rate | {anr_pct_str} | → | {anr_light} |",
        f"| Reviews negativos | {neg} (últ. {window}d) | — | {'🟢' if neg == 0 else '🟡' if neg < 5 else '🔴'} |",
        f"| Top reclamação | {top_cat_label} ({top_cat_count}) | — | — |",
        "",
    ]

    if violations:
        lines.append(format_violation_summary(violations))
        lines.append("")

    return lines


def _build_urgent_alerts(data: dict[str, Any]) -> list[str]:
    """Build urgent reviews alert section — only shown when there are urgent reviews."""
    urgent = data.get("urgent_reviews") or []
    if not urgent:
        return []

    lines = [
        "---",
        "",
        "## 🚨 Alertas de Urgência — Usuários em Situação Crítica",
        "",
        f"**{len(urgent)} review(s) nos últimos 7 dias com indicadores de urgência em evento:**",
        "",
    ]
    for r in urgent:
        text = _truncate(r.get("comment_text") or "", 250)
        stars = r.get("star_rating", "?")
        cat = r.get("complaint_category") or "?"
        cat_label = _CATEGORY_LABELS.get(cat, cat)
        sev = r.get("severity", "?")
        d = str(r.get("ingest_date") or "?")[:10]
        lines.append(f"> \"{text}\"")
        lines.append(f"> _⭐ {stars} · {cat_label} · severidade {sev}/5 · {d}_")
        lines.append("")
    return lines


def _build_version_regression(data: dict[str, Any]) -> list[str]:
    """Build version-by-version crash analysis section."""
    crash_by_version = data.get("crash_by_version") or []
    if not crash_by_version:
        return []

    lines = [
        "### Análise por Versão do App",
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

    regression = detect_regression(crash_by_version)
    if regression.get("has_regression"):
        d = regression
        lines.append(
            f"> ⚠️ **Regressão detectada:** Versão `{d['current_version']}` piorou "
            f"**+{d['delta_pp']:.1f}pp (+{d['pct_change']:.0f}%)** vs. versão anterior `{d['prev_version']}` "
            f"({d['prev_crash']:.1f}% → {d['current_crash']:.1f}%). "
            "Considerar hotfix ou rollback."
        )
        lines.append("")

    return lines


def _build_crash_diagnosis(data: dict[str, Any]) -> list[str]:
    """Seção de diagnóstico de crash com narrativa para stakeholders e devs."""
    from play_insights.crash_patterns import analyze_crash_patterns

    vitals = data["vitals"]
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


def _build_performance_section(data: dict[str, Any]) -> list[str]:
    """Build UI rendering and startup performance section."""
    perf = data.get("performance_vitals") or []

    lines = [
        "---",
        "",
        "## Performance de UI e Startup",
        "",
    ]

    if not perf:
        lines.append("_Dados de rendering/startup ainda não coletados. Execute `python -m play_insights ingest` para coletar._")
        lines.append("")
        return lines

    lines.append("| Métrica | Média | Pico | Dias com dados |")
    lines.append("|---------|-------|------|----------------|")
    for row in perf:
        ms = row.get("metric_set") or "?"
        avg = row.get("avg_pct") or 0.0
        mx = row.get("max_pct") or 0.0
        days = row.get("days_with_data") or 0
        if "rendering" in ms.lower():
            label = "Slow Rendering (≥1s frame)"
        elif "start" in ms.lower():
            label = "Slow Start (cold/warm/hot)"
        else:
            label = ms
        lines.append(f"| {label} | {avg:.1f}% | {mx:.1f}% | {days}d |")
    lines.append("")
    lines.append(
        "> **Referência:** Slow Rendering >30% = usuários experimentando UI travada. "
        "Slow Start >25% = app demora para abrir — impacta retenção na primeira sessão."
    )
    lines.append("")
    return lines


def load_previous_alerts(today: str, memory_dir: Path | None = None) -> dict | None:
    """Load the most recent alerts JSON that is NOT from today."""
    if memory_dir is None:
        memory_dir = Path(".productflow/memory")
    if not memory_dir.exists():
        return None
    alert_files = sorted(memory_dir.glob("alerts-*.json"))
    for f in reversed(alert_files):
        if today not in f.name:
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
    return None


def _build_what_changed(data: dict[str, Any], prev_alerts: dict | None, today: str) -> list[str]:
    """Show delta vs previous report snapshot."""
    lines = [
        "---",
        "",
        "## O Que Mudou Desde o Último Relatório",
        "",
    ]

    if prev_alerts is None:
        lines.append("_Primeiro relatório disponível — sem comparação anterior._")
        lines.append("")
        return lines

    prev_health = prev_alerts.get("health") or {}
    prev_crash_avg = next(
        (v.get("avg_value") or 0.0 for v in (prev_alerts.get("vitals_summary") or []) if "crash" in (v.get("metric_set") or "").lower()),
        None,
    )
    curr_crash_avg = next(
        (v.get("avg_value") or 0.0 for v in data["vitals"] if "crash" in (v.get("metric_set") or "").lower()),
        None,
    )
    prev_rating = prev_health.get("avg_rating")
    curr_rating = data["rating"].get("avg_rating")
    prev_neg = prev_health.get("negative_count", 0) or 0
    curr_neg = data["rating"].get("negative", 0) or 0
    prev_date = prev_alerts.get("date", "?")

    lines.append(f"_Comparando com relatório de {prev_date}_")
    lines.append("")
    lines.append("| Indicador | Anterior | Atual | Delta |")
    lines.append("|-----------|----------|-------|-------|")

    if curr_rating is not None and prev_rating is not None:
        delta_r = curr_rating - prev_rating
        arrow = "↗" if delta_r > 0.05 else ("↘" if delta_r < -0.05 else "→")
        lines.append(f"| Rating | ⭐ {prev_rating:.1f} | ⭐ {curr_rating:.1f} | {arrow} {delta_r:+.2f} |")

    if curr_crash_avg is not None and prev_crash_avg is not None:
        delta_crash_pp = (curr_crash_avg - prev_crash_avg) * 100
        arrow = "↗" if delta_crash_pp > 0.5 else ("↘" if delta_crash_pp < -0.5 else "→")
        lines.append(
            f"| Crash Rate | {prev_crash_avg:.2%} | {curr_crash_avg:.2%} | {arrow} {delta_crash_pp:+.1f}pp |"
        )

    delta_neg = curr_neg - prev_neg
    arrow_neg = "↗" if delta_neg > 0 else ("↘" if delta_neg < 0 else "→")
    lines.append(f"| Reviews negativos | {prev_neg} | {curr_neg} | {arrow_neg} {delta_neg:+d} |")
    lines.append("")
    return lines


def generate_daily_report(
    repo: DuckDBRepository,
    recommendations: list[dict[str, Any]],
    window: int = 30,
    output_suffix: str = "",
) -> tuple[Path, Path]:
    today = date.today().isoformat()
    timestamp = datetime.now(tz=timezone.utc).isoformat()

    data = _fetch_daily_data(repo, window=window)

    report_path = Path("docs/discovery") / f"play-voc{output_suffix}-{today}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    prev_alerts = load_previous_alerts(today)

    lines: list[str] = [
        f"# Daily Play VOC Intelligence — {today}",
        "",
        "---",
        "",
    ]
    lines.extend(_build_executive_kpi_table(data, today, window))
    urgent = _build_urgent_alerts(data)
    if urgent:
        lines.extend(urgent)
    lines.extend(_build_what_changed(data, prev_alerts, today))
    lines.extend(_build_header(today, data, window))
    lines.extend(_build_priority_board(recommendations))
    lines.extend(_build_customer_voice(data))
    lines.extend(_build_vitals_section(data))
    lines.extend(_build_crash_diagnosis(data))
    lines.extend(_build_performance_section(data))
    lines.extend(_build_severity_section(data))
    lines.extend(_build_intent_section(data))

    lines += [
        "---",
        "",
        f"_Relatório gerado em {timestamp} · Fonte: {repo.db_path} · Janela de análise: {window} dias_",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    # Build alert_payload (enriched for use in future "what changed")
    crash_avg = next(
        (v.get("avg_value") or 0.0 for v in data["vitals"] if "crash" in (v.get("metric_set") or "").lower()), None
    )
    alert_payload = {
        "date": today,
        "generated_at": timestamp,
        "health": {
            "avg_rating": data["rating"].get("avg_rating"),
            "total_reviews": data["rating"].get("total_reviews", 0),
            "negative_count": data["rating"].get("negative", 0),
            "positive_count": data["rating"].get("positive", 0),
        },
        "top_categories": data["categories"],
        "severity_distribution": data["severity_dist"],
        "intent_distribution": data["intent_dist"],
        "vitals_summary": data["vitals"],
        "crash_avg": crash_avg,
        "rating_avg": data["rating"].get("avg_rating"),
        "negative_count": data["rating"].get("negative", 0),
        "top_recommendations": recommendations[:5],
    }
    alert_path = Path(".productflow/memory") / f"alerts{output_suffix}-{today}.json"
    alert_path.parent.mkdir(parents=True, exist_ok=True)
    alert_path.write_text(
        json.dumps(alert_payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    return report_path, alert_path
