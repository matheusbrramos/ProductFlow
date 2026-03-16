# TODO - Google Play App Intelligence Agent

## Project
- [ ] Project name: Play Rating Recovery Agent
- [ ] Owner: Matheus Ramos
- [ ] Status: In Progress
- [ ] Target package configured (replace `com.seu.app`)
- [ ] Timezone configured (`America/Sao_Paulo`)

## Access, Safety, Environment
- [ ] Play Console access validated
- [ ] GCP project ready
- [ ] Android Publisher API enabled
- [ ] Play Developer Reporting API enabled
- [ ] Service account created
- [ ] Least-privilege IAM applied
- [ ] Secrets stored outside repo
- [ ] `REPLY_PUBLISH_ENABLED=false` default confirmed
- [ ] Manual approval token flow documented
- [ ] Kill-switch documented
- [ ] Real token refresh validated

## Foundation
- [x] Package structure created in `src/play_insights/`
- [x] `pyproject.toml` added (Python 3.11+)
- [x] Pytest markers `live_api` and `warehouse`
- [x] `tests/unit/` and `tests/integration/` created
- [x] Smoke import/version test
- [x] `README-DEV.md` with run/test commands
- [ ] Unit gate executed: `pytest -m "not live_api and not warehouse"`

## Config and Logging
- [x] Typed config loader implemented
- [x] Required env vars enforced
- [x] Optional env defaults implemented
- [x] Structured logging implemented
- [x] Fail-fast validation and messages
- [x] Unit tests for config behavior

## Auth
- [x] ADC auth module implemented
- [x] Token refresh implemented
- [x] Live auth test added
- [ ] Gate executed: `pytest -m live_api -k auth`

## Reviews Ingestion
- [x] Reviews API client with pagination
- [x] Normalized review schema
- [x] Live integration test added
- [x] Empty/sparse response handling

## BigQuery - reviews_raw
- [x] BigQuery repository module
- [x] `reviews_raw` table schema and partitioning
- [x] Idempotent upsert strategy
- [x] Warehouse integration test added
- [x] CLI command: `ingest-reviews`
- [ ] Dedupe gate executed in real env

## Reporting API - Vitals
- [x] Reporting API client for crash/anr
- [x] Dimension support in query payload
- [x] Live vitals tests added
- [x] Low/no-data handling path

## BigQuery - vitals_daily
- [x] `vitals_daily` schema at daily grain
- [x] Idempotent write path
- [x] Warehouse test added
- [x] CLI command: `ingest-vitals`
- [ ] Partition query gate executed

## Error/Issue Ingestion
- [x] Error/issues collection path with endpoint fallback
- [x] `error_issues` schema
- [x] Persistence path
- [x] Live + warehouse tests added
- [x] Graceful degradation implemented

## Unified Ingest
- [x] CLI `ingest` orchestrator added
- [x] Runs reviews + vitals + errors
- [x] Includes summary and failures
- [x] E2E CLI integration test scaffolded (guarded by env)
- [x] Non-zero exit on partial failure

## VOC Classification
- [x] PT-BR + EN language detection
- [x] Taxonomy categories implemented
- [x] `reviews_enriched` schema/persistence
- [x] Unit tests for classifier
- [ ] Warehouse linkage gate executed with real review ids

## Sentiment, Severity, Intent
- [x] Sentiment implemented
- [x] Severity implemented
- [x] Intent implemented
- [x] Persisted in `reviews_enriched`
- [x] Unit tests added
- [ ] Warehouse completeness gate executed

## Prioritization
- [x] Review/vitals/issues join logic implemented
- [x] Impact scoring formula implemented
- [x] Evidence refs included
- [x] `recommendations` table write path
- [ ] Warehouse generation gate executed
- [ ] Rerun stability checked

## Daily Output
- [x] Markdown daily report generation
- [x] JSON alert artifact generation
- [x] Top categories/segments/actions included
- [ ] Integration execution gate with live warehouse data
- [x] Source timestamp metadata included

## Weekly Output
- [x] Weekly strategic markdown generation
- [x] Trend/clusters/hotspots/recommendations sections
- [x] CLI report mode selector in place
- [ ] Weekly generation gate executed in live warehouse

## Reply Engine
- [x] Dry-run response generation
- [x] Hard guardrails for blocked categories/confidence
- [x] Dry-run queue artifact path
- [x] Publish mode implemented behind controls
- [x] `reply_audit` BigQuery table path
- [ ] Guarded publish live test executed

## ProductFlow Integration
- [x] `.claude/commands/play-insights.md`
- [x] `.claude/agents/play-insights.md`
- [x] `docs/briefings/play-insights.brief.md`
- [x] `CLAUDE.md` updated with new command/agent
- [ ] Validator run: `python scripts/validate_productflow.py`

## CI / Automation
- [x] Daily workflow created
- [x] Weekly workflow created
- [x] Secrets contract documented in workflow env
- [ ] CI execution validated in GitHub
- [ ] End-to-end live validation command executed

## Hardening
- [ ] Add retry/backoff wrapper for API calls
- [ ] Add explicit quota throttling
- [ ] Add schema evolution notes
- [ ] Add data retention policy notes
- [ ] Add PII minimization checks
- [ ] Add on-call runbook
- [ ] Add rollback runbook for publish incidents

## Acceptance
- [ ] 2+ weeks daily runs successful
- [ ] 2 weekly reports reviewed
- [ ] Recommendation quality approved
- [ ] Dry-run reply quality approved
- [ ] Publish governance approved
- [ ] KPI baseline captured
- [ ] Launch decision signed off

## Verification Commands
- [ ] `pytest -m "not live_api and not warehouse"`
- [ ] `pytest -m live_api`
- [ ] `pytest -m warehouse`
- [ ] `python -m play_insights ingest`
- [ ] `python -m play_insights analyze --window 7d`
- [ ] `python -m play_insights report --mode daily`
- [ ] `python -m play_insights report --mode weekly`
- [ ] `python -m play_insights reply --mode dry-run`
- [ ] `python scripts/validate_productflow.py`

---

---

# Tuning de Sistema e Banco de Dados Q2

**Objetivo:** Liberar 8–10 GB de RAM para uso do usuário com IA e novos projetos,
mantendo os serviços Q2 rodando em background sem impacto.

**Contexto:** validate_ptbr_content.py consumia 4+ GB varrendo toda a pasta Q2.
DuckDB sem índices, sem fechar conexões, sem limite de linhas em query(). Tarefas agendadas
colidindo no mesmo horário. Processos Python rodando em prioridade Normal competindo com o usuário.

---

## CHUNK A — DuckDB: Ciclo de vida e segurança de queries

### Passo 1: Context Manager e `close()` no DuckDBRepository

- [ ] Escrever teste: `DuckDBRepository` funciona como context manager (`with` statement)
- [ ] Escrever teste: após `close()`, usar `_conn` levanta exceção
- [ ] Escrever teste: `close()` explícito não levanta erro
- [ ] Implementar `close()` em `DuckDBRepository` chamando `self._conn.close()`
- [ ] Implementar `__enter__` retornando `self`
- [ ] Implementar `__exit__` chamando `close()` independente de exceção
- [ ] Atualizar funções do pipeline para fechar a conexão ao final
- [ ] Rodar `python -m pytest tests/unit/test_duckdb_repo.py -v` — todos passando
- [ ] Rodar `python -m pytest tests/unit/ -m "not live_api" -q` — 70+ passando

### Passo 2: Limite de linhas no `query()`

- [ ] Escrever teste: inserir 200 rows, `query(..., max_rows=50)` retorna exatamente 50
- [ ] Escrever teste: `logging.WARNING` emitido quando resultado foi truncado
- [ ] Escrever teste: `query("SELECT ... LIMIT 10")` retorna 10 sem warning
- [ ] Modificar `query()` para aceitar `max_rows: int = 50_000`
- [ ] Usar `fetchmany(max_rows)` em vez de `fetchall()`
- [ ] Emitir `logging.warning` quando `len(rows) == max_rows`
- [ ] Confirmar que todos os callers existentes continuam funcionando
- [ ] Rodar `python -m pytest tests/unit/ -m "not live_api" -q` — 70+ passando

### Passo 3: Índices nas tabelas DuckDB

- [ ] Escrever teste: índice `idx_vitals_date_metric` existe em `vitals_daily`
- [ ] Escrever teste: índice `idx_reviews_raw_date` existe em `reviews_raw`
- [ ] Escrever teste: índice `idx_enriched_category` existe em `reviews_enriched`
- [ ] Implementar `_ensure_indexes()` com os 6 índices:
  - [ ] `idx_vitals_date_metric` em `vitals_daily(date, metric_set)`
  - [ ] `idx_vitals_package` em `vitals_daily(package_name, date)`
  - [ ] `idx_reviews_raw_date` em `reviews_raw(ingest_date)`
  - [ ] `idx_reviews_raw_id` em `reviews_raw(review_id)`
  - [ ] `idx_enriched_category` em `reviews_enriched(complaint_category)`
  - [ ] `idx_enriched_date` em `reviews_enriched(ingest_date)`
- [ ] Chamar `_ensure_indexes()` no `__init__` após `memory_limit` e `threads`
- [ ] Proteger com `try/except` para tabelas ainda não existentes
- [ ] Escrever teste de `EXPLAIN` verificando uso de índice em query de vitals
- [ ] Rodar `python -m pytest tests/unit/ -m "not live_api" -q` — passando
- [ ] Aplicar índices no banco real via `python -c "...DuckDBRepository('play_insights.duckdb')..."`
- [ ] Confirmar com: `python -m play_insights maintenance`

### Passo 4: WAL Checkpoint e comando `maintenance`

- [ ] Adicionar `PRAGMA wal_autocheckpoint=100` no `__init__` (após demais configs)
- [ ] Escrever teste: pragma foi aplicado — verificar via query
- [ ] Implementar `maintenance()` com `CHECKPOINT` + `VACUUM` + `SELECT duckdb_tables()`
- [ ] Adicionar subcomando `maintenance` ao CLI em `src/play_insights/__main__.py`
- [ ] Subcomando: carrega `Settings.from_env()`, chama `maintenance()`, imprime tamanhos
- [ ] Escrever teste unitário: `maintenance()` retorna dict com `status == "ok"`
- [ ] Rodar `python -m pytest tests/unit/ -m "not live_api" -q` — passando
- [ ] Testar no banco real: `python -m play_insights maintenance` — sem erros

---

## CHUNK B — Windows Scheduler: Reorganização de horários

### Passo 5: Reescalonar PlayInsights para 06:30

- [ ] Atualizar `scripts/setup_scheduler_windows.ps1` — horário de `08:00` para `06:30`
- [ ] Adicionar comentário no script explicando o racional de horários
- [ ] Aplicar na tarefa existente via PowerShell (`Set-ScheduledTask` com novo trigger)
- [ ] Verificar: `.Triggers | Select StartBoundary` mostra `06:30`
- [ ] Verificar: `State == Ready`

### Passo 6: Remover 13h e ajustar 09h→09:30 e 17h→17:30

- [ ] Remover `Q2 Drive Publish - 13h00` via `Unregister-ScheduledTask -Confirm:$false`
- [ ] Confirmar remoção: buscar a tarefa deve retornar erro
- [ ] Atualizar `Q2 Drive Publish - 09h00` para trigger `09:30`
- [ ] Atualizar `Q2 Drive Publish - 17h00` para trigger `17:30`
- [ ] Verificar mapa final — 4 tarefas ativas:
  - [ ] PlayInsights-WeeklyReport: seg 06:30
  - [ ] Q2-Proactive-Tasks-Daily-Refresh: diário 08:00 (não alterado)
  - [ ] Q2 Drive Publish - 09h00: diário 09:30
  - [ ] Q2 Drive Publish - 17h00: diário 17:30
- [ ] `Q2 Drive Publish - 13h00` não existe mais

---

## CHUNK C — Prioridade de Processos

### Passo 7: BelowNormal/Idle para tasks em background

- [ ] Em `scripts/send_weekly_report.py`: adicionar `SetPriorityClass(BELOW_NORMAL_PRIORITY_CLASS)` no início do `main`
- [ ] Verificar prioridade "Abaixo do Normal" no Task Manager ao rodar com `--dry-run`
- [ ] Em `run_publish.ps1`: envolver chamada Python do validate com `Start-Process -Priority Idle -Wait`
- [ ] Verificar `run_publish.ps1 -DryRun` executa sem erros
- [ ] Adicionar comentário `# Process priority: BelowNormal/Idle` nos dois arquivos

### Passo 8: Guard de processo duplicado no validate_ptbr

- [ ] Adicionar verificação de processo antes do validate (`Get-WmiObject | Where CommandLine`)
- [ ] Adicionar Mutex .NET `"Global\ValidatePtbrMutex"` com `WaitOne(0)`
- [ ] Testar: dois terminais simultâneos — segundo deve imprimir `SKIP_MUTEX` e sair
- [ ] Verificar log em `_shared/.drive/logs/` registra entrada `SKIP`
- [ ] Rodar `python -m pytest tests/unit/ -m "not live_api" -v` — 70+ passando
- [ ] Rodar `python -m play_insights maintenance` — sem erros
- [ ] Rodar `python -m play_insights report --mode daily` — sem erros

---

## Verificação Final

- [ ] Mapa do scheduler mostra 4 tarefas com horários corretos
- [ ] `Q2 Drive Publish - 13h00` não existe mais
- [ ] `python -m play_insights maintenance` — status OK, tabelas listadas
- [ ] `python -m pytest tests/unit/ -m "not live_api" -q` — zero falhas
- [ ] Pico de RAM durante weekly report abaixo de 600 MB
- [ ] Task Manager mostra Python background em prioridade "Abaixo do Normal"
- [ ] Atualizar `memory/MEMORY.md` com as mudanças aplicadas

---

## Meta de RAM após tuning completo

| Componente | Antes | Depois |
|---|---|---|
| validate_ptbr (pico) | 4+ GB | < 1.5 GB |
| DuckDB em idle | ~200 MB (WAL aberto) | < 50 MB (conexão fechada) |
| DuckDB em query | sem limite | max 512 MB |
| Execuções de publish/dia | 3x | 2x |
| **Buffer para usuário + IA** | **~2–4 GB** | **8–10 GB** |
