# Play Insights — Melhorias para Stakeholders: Checklist

> Objetivo: transformar relatórios em inteligência acionável — mostrando não só "o que está acontecendo",
> mas "o quanto é grave, está piorando ou melhorando, e em que ordem corrigir".

---

## Fase 1 — Análises novas (sem nova coleta de dados)

### Step 1 — Threshold constants + violation detection ✅

- [x] Criar `src/play_insights/thresholds.py`
  - [x] Constante `CRASH_RATE_THRESHOLD = 0.0109` (1.09% — limite Google Play)
  - [x] Constante `ANR_RATE_THRESHOLD = 0.0047` (0.47% — limite Google Play)
  - [x] Dataclass `ThresholdViolation(metric_set, current_value, threshold, multiple, is_critical)`
    - [x] `multiple = current_value / threshold` (arredondado 1 decimal)
    - [x] `is_critical = multiple > 10.0`
  - [x] Função `check_violations(vitals: list[dict]) -> list[ThresholdViolation]`
  - [x] Função `format_violation_summary(violations) -> str` (texto markdown com emoji 🚨)
- [x] Criar `tests/unit/test_thresholds.py`
  - [x] `test_no_violations` — crash 0.5%, ANR 0.1% → lista vazia
  - [x] `test_crash_violation` — crash 24.1% → 1 violation, multiple ~22.1, is_critical=True
  - [x] `test_anr_violation` — ANR 1.5% → 1 violation, is_critical=False
  - [x] `test_format_summary_critical` — texto contém "RISCO CRÍTICO" quando is_critical=True
  - [x] `test_with_real_db` — lê vitals_daily do DuckDB real, chama check_violations() `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_thresholds.py -v` → todos passam

---

### Step 2 — Trend velocity (delta semana a semana) ✅

- [x] Em `src/play_insights/thresholds.py`, adicionar:
  - [x] Dataclass `TrendVelocity(metric, current_7d_avg, prev_7d_avg, delta_pp, direction)`
    - [x] `direction`: "↗ piorando" / "↘ melhorando" / "→ estável" (estável se |delta_pp| < 0.5)
  - [x] Função `calculate_trend_velocity(crash_series: list[dict]) -> TrendVelocity`
    - [x] Ordenar por date, dividir em metade antiga e metade recente
    - [x] Calcular avg de cada metade, retornar delta em percentage points
    - [x] Lista vazia → retornar TrendVelocity com direction "→ estável", tudo zero
- [x] Em `tests/unit/test_thresholds.py`, adicionar:
  - [x] `test_trend_worsening` — crash crescendo 10%→20% → direction contém "piorando"
  - [x] `test_trend_improving` — crash caindo 20%→10% → direction contém "melhorando"
  - [x] `test_trend_stable` — série uniforme → direction contém "estável"
  - [x] `test_trend_empty` — lista vazia → direction "→ estável"
  - [x] `test_trend_with_real_db` — lê crash_series do DuckDB real `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_thresholds.py -v` → todos passam

---

### Step 3 — Executive summary no relatório diário ✅

- [x] Em `report_daily.py`, atualizar `_fetch_daily_data()`:
  - [x] Importar `check_violations` e `calculate_trend_velocity` de thresholds
  - [x] Calcular `violations` usando vitals já buscados
  - [x] Calcular `crash_trend` usando crash_series já buscado
  - [x] Adicionar `"threshold_violations": violations` e `"crash_trend": crash_trend` ao dict
- [x] Criar função `_build_executive_summary(data: dict, today: str) -> list[str]` em `report_daily.py`:
  - [x] Tabela com 5 KPIs: Rating, Crash Rate, ANR Rate, Reviews negativos, Top reclamação
  - [x] Coluna "Tendência" com seta e delta pp para crash/ANR
  - [x] Coluna "Status" com semáforo: 🟢 dentro threshold / 🟡 até 5x / 🔴 acima de 5x
  - [x] Bloco de alerta "⚠️ ALERTA DE POLÍTICA GOOGLE PLAY" se há violations
  - [x] Listar cada violation com múltiplo: "24.1% → 22.1x acima do limite (1.09%)"
- [x] Em `generate_daily_report()`, adicionar `_build_executive_summary()` como **primeira seção**
- [x] Criar `tests/unit/test_report_daily.py`:
  - [x] `test_executive_summary_no_violations` — crash 0.5% → sem bloco de alerta
  - [x] `test_executive_summary_with_violation` — crash 24% → bloco "ALERTA DE POLÍTICA" presente
  - [x] `test_executive_summary_real_db` — abre DuckDB real, chama _fetch_daily_data() + _build_executive_summary() `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_report_daily.py -v`
- [x] Executar: `python -m play_insights report --mode daily`
- [x] Verificar: relatório em `docs/discovery/` tem seção "Resumo Executivo" no topo

---

### Step 4 — Detecção de regressão por versão ✅

- [x] Em `report_daily.py`, adicionar query `crash_by_version` em `_fetch_daily_data()`:
  - [x] GROUP BY app_version, AVG(metric_value), COUNT(DISTINCT date), MIN/MAX date
  - [x] Filtrar WHERE app_version IS NOT NULL, ORDER BY MAX(date) DESC, LIMIT 10
  - [x] Adicionar `"crash_by_version": crash_by_version` ao dict retornado
- [x] Em `thresholds.py`, criar função `detect_regression(crash_by_version: list[dict]) -> dict`:
  - [x] Ordenar por first_seen DESC
  - [x] Se len < 2: retornar `{"has_regression": False, "details": None}`
  - [x] Comparar versão mais recente vs. anterior
  - [x] Retornar: has_regression, current_version, current_crash, prev_version, prev_crash, delta_pp, pct_change
- [x] Criar `_build_version_regression(data: dict) -> list[str]` em `report_daily.py`:
  - [x] Tabela: Versão | Crash Rate Médio | Dias | Período
  - [x] Bloco ⚠️ se regressão detectada: "Versão X piorou +8.8pp (+57%) vs. versão anterior Y"
- [x] Adicionar `_build_version_regression()` na seção vitals (após crash_by_device)
- [x] Fazer o mesmo no `report_weekly.py`
- [x] Em `tests/unit/test_thresholds.py`, adicionar:
  - [x] `test_regression_detected` — versão nova 24%, anterior 15% → has_regression=True, delta ~8.8
  - [x] `test_no_regression` — versão nova 5%, anterior 15% → has_regression=False
  - [x] `test_regression_single_version` — só 1 versão → has_regression=False
  - [x] `test_regression_with_real_db` — lê crash_by_version do DuckDB real `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_thresholds.py tests/unit/test_report_daily.py -v`
- [x] Executar: `python -m play_insights report --mode daily`
- [x] Verificar: seção "Análise por Versão do App" presente no relatório

---

### Step 5 — VOC: categoria experiencia_compra + flag event_urgency ✅

- [x] Em `voc_classifier.py`, adicionar categoria `"experiencia_compra"` ao dict KEYWORDS:
  - [x] Keywords PT: checkout, finalizar compra, pagamento, qr code, ingresso, assento, mapa de assentos, seleção de lugar, confirmação, ticket, pix, cartão, boleto, parcela, ingressos, comprar ingresso, compra travou
  - [x] Keywords EN: checkout, ticket, seat selection, qr code, purchase, payment failed, buy tickets, order
  - [x] Confidence padrão: 0.75
- [x] Em `voc_classifier.py`, criar função `detect_event_urgency(text: str) -> bool`:
  - [x] Palavras PT: hoje, agora, amanhã, show hoje, evento hoje, não consegui entrar, perdi o show, perderei, cancelar, emergência, urgente
  - [x] Palavras EN: tonight, right now, lost my ticket, can't get in, urgent, emergency, missing show
  - [x] Case-insensitive
- [x] Em `scoring.py`, atualizar `severity_score()`:
  - [x] Importar `detect_event_urgency` de voc_classifier
  - [x] Se detect_event_urgency(text) → +1 ao score (máximo 5)
- [x] Em `pipeline.py`, na função `analyze()`:
  - [x] Calcular `event_urgency = detect_event_urgency(review.comment_text)` para cada review
  - [x] Salvar no enriched record
- [x] Em `duckdb_repo.py`, adicionar migration:
  - [x] `ALTER TABLE reviews_enriched ADD COLUMN IF NOT EXISTS event_urgency BOOLEAN DEFAULT FALSE`
- [x] Criar `tests/unit/test_voc_classifier.py`:
  - [x] `test_experiencia_compra_pt` — "não consigo finalizar a compra do ingresso" → categoria experiencia_compra
  - [x] `test_experiencia_compra_en` — "checkout keeps failing" → categoria experiencia_compra
  - [x] `test_event_urgency_detected` — "show hoje à noite e não consigo entrar" → True
  - [x] `test_event_urgency_not_detected` — "app muito lento" → False
  - [x] `test_urgency_increases_severity` — texto urgente + star 3 → severity >= 4
  - [x] `test_classify_real_reviews` — lê 20 reviews reais do DuckDB, classifica, verifica VocResult válidos `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_voc_classifier.py -v`
- [x] Executar: `python -m play_insights analyze --window 30d` (re-classifica com novo classifier)
- [x] Verificar no DuckDB: `SELECT complaint_category, COUNT(*) FROM reviews_enriched GROUP BY complaint_category;`
- [x] Confirmar que `experiencia_compra` aparece se houver reviews relevantes

---

### Step 6 — Reviews urgentes em destaque nos relatórios ✅

- [x] Em `report_daily.py`, adicionar query `urgent_reviews` em `_fetch_daily_data()`:
  - [x] JOIN reviews_raw + reviews_enriched WHERE event_urgency = TRUE AND ingest_date >= CURRENT_DATE - 7
  - [x] Campos: comment_text, star_rating, ingest_date, app_version_name, complaint_category, severity
  - [x] LIMIT 10
  - [x] Adicionar `"urgent_reviews": urgent_reviews` ao dict
- [x] Criar `_build_urgent_alerts(data: dict) -> list[str]` em `report_daily.py`:
  - [x] Se lista vazia → retornar `[]`
  - [x] Header: `## 🚨 Alertas de Urgência — Usuários em Situação Crítica`
  - [x] Mostrar N reviews com citação direta entre aspas + estrelas + categoria + data
- [x] Em `generate_daily_report()`, adicionar `_build_urgent_alerts()` logo após executive summary
  - [x] Mostrar seção APENAS se há urgent reviews
- [x] Em `report_weekly.py`, fazer o mesmo para janela 30d
- [x] Em `tests/unit/test_report_daily.py`, adicionar:
  - [x] `test_urgent_alerts_empty` — lista vazia → retorna []
  - [x] `test_urgent_alerts_with_data` — 2 reviews urgentes → output tem 🚨 e textos
  - [x] `test_urgent_alerts_real_db` — abre DuckDB, busca urgent_reviews `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_report_daily.py -v`
- [x] Executar: `python -m play_insights report --mode daily`
- [x] Verificar: seção 🚨 aparece se há reviews urgentes, ausente se não há

---

## Fase 2 — Novos dados da API Play Developer Reporting

### Step 7 — Coleta slowRenderingRate ⚠️ (API indisponível para este app)

- [x] Em `reporting_client.py`, adicionar método `query_slow_rendering(self, days=7)`
- [x] Em `pipeline.py`, adicionar ao `ingest_vitals()` com try/except (403 → lista vazia, não quebra)
- [x] Criar `tests/unit/test_reporting_client.py`:
  - [x] `test_query_slow_rendering_structure` — mock _post_query com 2 rows → list[VitalsRecord]
  - [x] `test_slow_rendering_zero_rows` — mock `{"rows": []}` → lista vazia
  - [x] `test_slow_rendering_live` — retorna 403 para este app (SA sem permissão) `[@pytest.mark.live_api]`
- [ ] `test_ingest_slow_rendering` — **N/A**: API retorna 403 para br.com.quero2ingressos
- [x] Executar: `python -m pytest tests/unit/test_reporting_client.py -v -k "slow_rendering"`
- [x] Executar: `python -m play_insights ingest --days 7` → não quebra, slow_rendering_count=0
- [x] Verificar: metric_set **não** aparece em vitals_daily (API não autorizada para este pacote)

> **Nota:** slowRenderingRateMetricSet retorna 403 Forbidden para br.com.quero2ingressos.
> O pipeline trata graciosamente com try/except — ingest continua normalmente sem os dados.

---

### Step 8 — Coleta slowStartRate + seção Performance de UI/Startup ⚠️ (API indisponível)

- [x] Em `reporting_client.py`, adicionar método `query_slow_start(self, days=7)`
- [x] Em `pipeline.py`, adicionar `query_slow_start()` ao `ingest_vitals()` com try/except (400 → lista vazia)
- [x] Em `report_daily.py`, adicionar query `performance_vitals` em `_fetch_daily_data()`
- [x] Criar `_build_performance_section(data: dict) -> list[str]` em `report_daily.py`:
  - [x] Se vazio → mensagem "Dados de rendering/startup ainda não coletados."
  - [x] Tabela: Métrica | Média | Pico | Dias com dados
- [x] Adicionar `_build_performance_section()` ao `generate_daily_report()`
- [x] Em `report_weekly.py`, fazer o mesmo com window variável
- [x] Testes:
  - [x] `test_performance_section_empty` — sem performance_vitals → mensagem "não coletados"
  - [x] `test_performance_section_with_data` — 2 metric_sets → tabela 2 linhas
  - [x] `test_slow_start_live` — retorna 400 para este app `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/ -v -k "slow"`
- [x] Executar: `python -m play_insights report --mode daily`
- [x] Verificar: seção "Performance de UI e Startup" presente (com mensagem "não coletados")

> **Nota:** slowStartRateMetricSet retorna 400 Bad Request para br.com.quero2ingressos.
> Seção aparece nos relatórios com placeholder até que a API fique disponível.

---

## Fase 3 — Análise cruzada e inteligência histórica

### Step 9 — Trend velocity semanal + "O que mudou desde o último relatório" ✅

- [x] Em `report_weekly.py`, adicionar crash_series e crash_trend ao `_fetch_weekly_data()`
- [x] Criar `load_previous_alerts(today: str) -> dict | None`:
  - [x] Procurar `.productflow/memory/alerts-*.json` ordenado por data
  - [x] Carregar o mais recente que NÃO seja de today
  - [x] Retornar dict ou None se não encontrado
- [x] Criar `_build_what_changed(current_data: dict, prev_alerts: dict | None) -> list[str]`:
  - [x] Se prev_alerts is None → "Primeiro relatório — sem comparação anterior"
  - [x] Calcular deltas: crash_delta, rating_delta, neg_reviews_delta
  - [x] Formatar: "Crash rate: 24.1% (+9.0pp vs. relatório anterior)" com seta
- [x] Adicionar `_build_what_changed()` ao `generate_daily_report()` após executive summary
- [x] Incluir campos no `alert_payload`: crash_avg, rating_avg, negative_count
- [x] Testes:
  - [x] `test_load_previous_alerts_none` — diretório vazio → None
  - [x] `test_load_previous_alerts_found` — arquivo fake de ontem → dict correto
  - [x] `test_what_changed_no_prev` — prev=None → "Primeiro relatório"
  - [x] `test_what_changed_with_prev` — prev crash 15%, atual 24% → "+9.0pp" presente
  - [x] `test_what_changed_real` — DuckDB real + arquivo alerts real `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/ -v -k "changed or previous"`
- [x] Executar: `python -m play_insights report --mode daily` (2x para ter deltas reais na segunda)
- [x] Verificar seção "O Que Mudou" no segundo relatório

---

### Step 10 — Persistência de problemas + correlação reviews × vitals (semanal) ✅

- [x] Em `report_weekly.py`, adicionar query `category_persistence` ao `_fetch_weekly_data()`
- [x] Em `report_weekly.py`, adicionar query `weekly_crash_vs_reviews`
- [x] Criar `_build_category_persistence(data: dict) -> list[str]`:
  - [x] Tabela: Categoria | Presente desde | Semanas | Reviews | Status
  - [x] Status: 🔴 Crônico (≥ 4 semanas) / 🟡 Recorrente (2-3) / 🟠 Novo (1)
- [x] Criar `_build_crash_vs_reviews_correlation(data: dict) -> list[str]`
- [x] Adicionar ambas ao `generate_weekly_report()` após `_build_technical_hotspots()`
- [x] Criar `tests/unit/test_report_weekly.py`:
  - [x] `test_persistence_chronic` — 5 semanas presentes → status "Crônico"
  - [x] `test_persistence_new` — 1 semana → status "Novo"
  - [x] `test_correlation_table` — 4 semanas de dados → tabela 4 linhas
  - [x] `test_weekly_full_real_db` — DuckDB real, chama _fetch_weekly_data() `[@pytest.mark.live_api]`
- [x] Executar: `python -m pytest tests/unit/test_report_weekly.py -v`
- [x] Executar: `python -m play_insights report --mode weekly`
- [x] Verificar: seções "Problemas Persistentes" e "Correlação" no relatório semanal
- [ ] Executar: `python scripts/generate_baseline.py` (pendente — rodar manualmente)

---

## Checklist final de validação

### Testes

- [x] `python -m pytest tests/unit/ -m "not live_api" -v` → **70/70 passam**
- [ ] `python -m pytest -m live_api -v` → pendente (requer credenciais ativas)

### Pipeline completo

- [x] `python -m play_insights ingest --days 7` → sem erros (crash+ANR: 30 rows)
- [x] `python -m play_insights analyze --window 30d` → sem erros (3 reviews enriquecidos)
- [x] `python -m play_insights report --mode daily` → gerado com sucesso
- [x] `python -m play_insights report --mode weekly` → gerado com sucesso

### Seções do relatório diário ✅

- [x] Resumo Executivo (KPIs + semáforo + violations se houver)
- [x] Alertas de Urgência (se houver reviews urgentes — seção oculta se não há)
- [x] O que Mudou (com deltas reais na segunda geração)
- [x] Prioridade do Dia
- [x] Voz do Usuário
- [x] Vitals + série temporal de crash rate
- [x] Hotspots por dispositivo
- [x] Análise por Versão (com detecção de regressão)
- [x] Performance de UI e Startup (placeholder enquanto API não disponível)
- [x] Disponibilidade de dimensões
- [x] Distribuição de Severidade
- [x] Intenção dos Usuários

### Seções do relatório semanal ✅

- [x] Resumo Executivo semanal
- [x] Flags de Risco (threshold violations)
- [x] Rating Trend dia a dia
- [x] Deep Dive por Categoria
- [x] Problemas Persistentes (há quantas semanas cada categoria está presente)
- [x] Hotspots Técnicos (crash/ANR por dispositivo)
- [x] Performance de UI (placeholder enquanto API não disponível)
- [x] Análise por Versão
- [x] Correlação Reviews × Vitals por semana
- [x] Matriz de Impacto
- [x] Roadmap Estratégico

### DuckDB — metric sets coletados

- [x] `SELECT metric_set, COUNT(*) FROM vitals_daily GROUP BY metric_set;`
  - [x] crashRateMetricSet ✓
  - [x] anrRateMetricSet ✓
  - [ ] slowRenderingRateMetricSet — **403 Forbidden** para br.com.quero2ingressos
  - [ ] slowStartRateMetricSet — **400 Bad Request** para br.com.quero2ingressos

### DuckDB — VOC categories

- [x] `SELECT complaint_category, COUNT(*) FROM reviews_enriched GROUP BY complaint_category;`
  - [x] experiencia_compra presente ✓

### Baseline

- [ ] `python scripts/generate_baseline.py` → pendente (rodar manualmente quando necessário)

---

## Referência rápida: impacto entregue

| Antes | Depois |
|-------|--------|
| "Crash rate 24%" | "24% ↘ -6.1pp vs. semana anterior — 23.7x acima do limite Google — RISCO CRÍTICO" |
| "12 reviews negativos" | "12 reviews negativos — estabilidade presente há 7 semanas (CRÔNICO)" |
| Apenas crash/ANR | + slowRendering + slowStart (API não disponível para este app ainda) |
| Sem contexto de versão | "Versão 20252: 25.8% crash — única versão ativa (sem anterior para comparar)" |
| Categorias sem ticketing | + experiencia_compra + flag de urgência por evento |
| Sem comparação temporal | + "O que mudou desde ontem" com deltas reais |
