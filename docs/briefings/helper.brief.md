# /helper - Briefing

**Foco**: Coleta de contexto da empresa
**Fase**: 0 (primeiro agente)
**Depende**: Nada

## Comandos
- `/setup <url ou empresa>` - Coleta contexto inicial

## Output
- `.context/empresa.md` - Contexto da organizacao

## O que faz
- Coleta missao, visao, produtos, publico-alvo
- Identifica diferenciais e constraints
- Mapeia metas e OKRs
- Pesquisa proativamente informacoes publicas

## Nao faz
- Pesquisa de mercado -> /research
- Pesquisa de usuarios -> /discovery

-> Detalhes: `.claude/agents/helper.md`
