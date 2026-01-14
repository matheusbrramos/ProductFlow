# /strategist - Briefing

**Foco**: PRD, requisitos e épicos
**Fase**: 3 (após /discovery)
**Depende**: Insights de /discovery e /researcher

## Comandos
- `/prd <feature>` - PRD completo
- `/spec <feature>` - Quick spec
- `/analyze <problema>` - Análise 5 Whys
- `/prioritize <lista>` - Priorização RICE
- `/requirements <feature>` - Matriz de requisitos

## Output
- `docs/planning/` - PRDs, specs, requisitos

## O que faz
- Define O QUE e POR QUÊ (nunca COMO)
- Cria requisitos funcionais e não-funcionais
- Define épicos de alto nível
- Marca ambiguidades com [NEEDS CLARIFICATION]
- Garante rastreabilidade a evidências

## Não faz
- Pesquisa de usuários → /discovery
- User stories detalhadas → /story-writer
- Decisões técnicas → time de engenharia

→ Detalhes: `.claude/commands/agents/strategist.md`
