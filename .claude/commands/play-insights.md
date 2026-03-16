---
description: "Operar pipeline de inteligencia da Google Play (ingest, analise, relatorios e replies)."
argument-hint: "<acao> [opcoes] (ingest, analyze, report, reply)"
---

# /play-insights - Play Intelligence Pipeline

Executa o pipeline de inteligencia da Google Play com dados reais de API.

## Entrada

```
$ARGUMENTS
```

## Acoes

### ingest [--days N]
Executa ingestao completa:
- reviews
- vitals (crash/anr)
- errors/issues

### analyze [--window 7d]
Classifica VOC, calcula scores e gera recomendacoes priorizadas.

### report --mode daily|weekly
Gera artefatos de:
- diario: `docs/discovery/play-voc-YYYY-MM-DD.md`
- semanal: `docs/research/play-quality-YYYY-MM-DD.md`

### reply --mode dry-run|publish
Opera respostas para reviews:
- dry-run: gera fila em `.productflow/memory/reply-dryrun-YYYY-MM-DD.json`
- publish: publica respostas com guardrails e auditoria

## Requisitos

- Variaveis de ambiente obrigatorias configuradas:
  - `GCP_PROJECT_ID`
  - `BQ_DATASET`
  - `PLAY_PACKAGE_NAME`
  - `GOOGLE_APPLICATION_CREDENTIALS`

## Exemplo

```bash
python -m play_insights ingest --days 7
python -m play_insights analyze --window 7d
python -m play_insights report --mode daily
python -m play_insights reply --mode dry-run
```

