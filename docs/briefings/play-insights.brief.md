# /play-insights - Briefing

**Foco**: Inteligencia operacional da Google Play  
**Fase**: Contínua (monitoramento e melhoria)  
**Depende**: Config de ambiente + acesso APIs Google Play/BigQuery

## Comandos
- `/play-insights ingest [--days N]`
- `/play-insights analyze [--window 7d]`
- `/play-insights report --mode daily|weekly`
- `/play-insights reply --mode dry-run|publish`

## Output
- `docs/discovery/play-voc-YYYY-MM-DD.md`
- `docs/research/play-quality-YYYY-MM-DD.md`
- `.productflow/memory/alerts-YYYY-MM-DD.json`
- `.productflow/memory/reply-dryrun-YYYY-MM-DD.json`

## O que faz
- Coleta reviews e sinais de qualidade (crash/anr/errors)
- Classifica reclamacoes e sentimento (PT-BR/EN)
- Prioriza recomendacoes por impacto
- Suporta resposta a reviews com guardrails

## Nao faz
- Substituir analytics de jornada detalhada (GA4/Firebase)
- Publicar replies sem controles de seguranca

