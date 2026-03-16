# TODO Matheus - Execução Passo a Passo (Play Insights)

## Como usar este arquivo
- Marque cada passo apenas quando tiver evidência.
- Preencha `Data`, `Evidência` e `Observações`.
- Se travar, registre no bloco de `Bloqueios`.

## Dados do projeto
- Projeto: Play Rating Recovery Agent
- Owner: Matheus Ramos
- Package name alvo: `com.seu.app` (substituir)
- Timezone: `America/Sao_Paulo`

---

## Bloco A - Pré-requisitos Google (obrigatório)

### Passo A1 - Confirmar app e acessos
- [ ] Tenho acesso ao app correto no Play Console
- [ ] Tenho permissão para API access no Play Console
- [ ] Tenho acesso ao projeto GCP correto
- Data:
- Evidência (link/screenshot):
- Observações:

### Passo A2 - Ativar APIs no GCP
- [ ] `androidpublisher.googleapis.com`
- [ ] `playdeveloperreporting.googleapis.com`
- [ ] `bigquery.googleapis.com`
- Data:
- Evidência:
- Observações:

### Passo A3 - Service Account
- [ ] Service account criada
- [ ] Chave JSON gerada e guardada com segurança
- [ ] Permissões mínimas configuradas no GCP
- Data:
- Evidência:
- Observações:

### Passo A4 - Vincular GCP no Play Console
- [ ] Projeto GCP vinculado em `Setup > API access`
- [ ] Service account adicionada ao app
- [ ] Acesso de leitura de reviews habilitado
- [ ] Acesso de reporting/vitals habilitado
- Data:
- Evidência:
- Observações:

---

## Bloco B - Configuração local (máquina do Matheus)

### Passo B1 - Variáveis de ambiente
- [ ] `GCP_PROJECT_ID` definido
- [ ] `BQ_DATASET` definido
- [ ] `PLAY_PACKAGE_NAME` definido com package real
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` apontando para JSON válido
- [ ] `REPLY_PUBLISH_ENABLED=false`
- [ ] `TIMEZONE=America/Sao_Paulo`
- Data:
- Evidência (`echo $env:...`):
- Observações:

### Passo B2 - Instalar dependências
- [ ] `python -m pip install -e .[dev]`
- [ ] `python -m ruff check src tests`
- Data:
- Evidência:
- Observações:

### Passo B3 - Validar testes locais
- [ ] `python -m pytest -m "not live_api and not warehouse"`
- [ ] `python -m pytest -m live_api -k auth`
- [ ] `python -m pytest -m live_api`
- [ ] `python -m pytest -m warehouse`
- Data:
- Evidência (output resumido):
- Observações:

---

## Bloco C - Rodar pipeline ponta a ponta local

### Passo C1 - Ingestão
- [ ] `python -m play_insights ingest --days 7`
- [ ] Sem erro de autenticação
- [ ] Sem erro de permissão em BigQuery
- Data:
- Evidência:
- Observações:

### Passo C2 - Análise
- [ ] `python -m play_insights analyze --window 7d`
- [ ] `reviews_enriched` populada
- [ ] `recommendations` populada
- Data:
- Evidência:
- Observações:

### Passo C3 - Relatório diário
- [ ] `python -m play_insights report --mode daily`
- [ ] Arquivo criado em `docs/discovery/play-voc-YYYY-MM-DD.md`
- [ ] JSON criado em `.productflow/memory/alerts-YYYY-MM-DD.json`
- Data:
- Evidência:
- Observações:

### Passo C4 - Relatório semanal
- [ ] `python -m play_insights report --mode weekly`
- [ ] Arquivo criado em `docs/research/play-quality-YYYY-MM-DD.md`
- Data:
- Evidência:
- Observações:

### Passo C5 - Replies em dry-run
- [ ] `python -m play_insights reply --mode dry-run`
- [ ] Arquivo criado em `.productflow/memory/reply-dryrun-YYYY-MM-DD.json`
- [ ] Guardrails funcionando (itens bloqueados não entram)
- Data:
- Evidência:
- Observações:

---

## Bloco D - GitHub Actions (automação)

### Passo D1 - Secrets no GitHub
- [ ] `GCP_PROJECT_ID`
- [ ] `BQ_DATASET`
- [ ] `PLAY_PACKAGE_NAME`
- [ ] `GCP_SERVICE_ACCOUNT_JSON`
- Data:
- Evidência:
- Observações:

### Passo D2 - Workflow diário
- [ ] Rodou `Play Insights Daily` com sucesso
- [ ] Ingest + Analyze + Daily report + Reply dry-run concluídos
- Data:
- Evidência (link da run):
- Observações:

### Passo D3 - Workflow semanal
- [ ] Rodou `Play Insights Weekly` com sucesso
- [ ] Weekly report gerado
- Data:
- Evidência (link da run):
- Observações:

---

## Bloco E - Governança para publish de replies (somente depois)

### Passo E1 - Aprovação de negócio
- [ ] Política de resposta aprovada (tom, SLAs, escalonamento)
- [ ] Dono de aprovação definido
- Data:
- Evidência:
- Observações:

### Passo E2 - Habilitar publish com segurança
- [ ] `REPLY_PUBLISH_ENABLED=true` apenas no ambiente controlado
- [ ] `REPLY_PUBLISH_APPROVAL_TOKEN` configurado
- [ ] Teste controlado com poucos itens
- [ ] Auditoria em `reply_audit` validada
- Data:
- Evidência:
- Observações:

### Passo E3 - Kill switch
- [ ] Procedimento testado para voltar `REPLY_PUBLISH_ENABLED=false`
- [ ] Time sabe executar rollback
- Data:
- Evidência:
- Observações:

---

## Bloco F - Critérios de aceite do projeto
- [ ] 2+ semanas com job diário estável
- [ ] 2 relatórios semanais revisados com produto/engenharia
- [ ] Qualidade das recomendações aprovada
- [ ] Qualidade do dry-run de respostas aprovada
- [ ] KPI baseline registrado (nota média, share 1-2 estrelas, crash/anr)
- [ ] Decisão formal de go-live registrada
- Data da conclusão:
- Evidência final:
- Observações finais:

---

## Comandos rápidos (copiar e colar)
```powershell
python -m pip install -e .[dev]
python -m ruff check src tests
python -m pytest -m "not live_api and not warehouse"
python -m pytest -m live_api -k auth
python -m pytest -m live_api
python -m pytest -m warehouse
python -m play_insights ingest --days 7
python -m play_insights analyze --window 7d
python -m play_insights report --mode daily
python -m play_insights report --mode weekly
python -m play_insights reply --mode dry-run
```

---

## Bloqueios e pendências
- [ ] Bloqueio 1:
- [ ] Bloqueio 2:
- [ ] Bloqueio 3:

