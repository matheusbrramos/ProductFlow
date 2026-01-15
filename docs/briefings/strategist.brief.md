# /strategist - Briefing

**Foco**: PRD, requisitos e epicos
**Fase**: 3 (apos /discovery)
**Depende**: Insights de /discovery e /research

## Comandos
- `/prd <feature>` - PRD completo
- `/spec <feature>` - Quick spec
- `/prioritize <lista>` - Priorizacao RICE

## Output
- `docs/prd/{feature}.md` - PRDs e specs

## O que faz
- Define O QUE e POR QUE (nunca COMO)
- Cria requisitos funcionais e nao-funcionais
- Define epicos de alto nivel
- Marca ambiguidades com [NEEDS CLARIFICATION]
- Garante rastreabilidade a evidencias

## Nao faz
- Pesquisa de usuarios -> /discovery
- User stories detalhadas -> /stories
- Decisoes tecnicas -> time de engenharia

-> Detalhes: `.claude/agents/strategist.md`
