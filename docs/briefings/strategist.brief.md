# Strategist Agent - Briefing

**Foco**: PRD, requisitos e epicos
**Fase**: 3 (apos `/discovery`)
**Depende**: Insights de `/discovery` e `/research`

## Como Invocar
- `/prd <feature>` - PRD completo

**Nota**: Para priorizacao RICE ou specs rapidas, inclua no argumento do `/prd` (ex: `/prd "<feature> com priorizacao"`).

## Output
- `docs/prd/{feature}.md` - PRDs

## O que faz
- Define O QUE e POR QUE (nunca COMO)
- Cria requisitos funcionais e nao-funcionais
- Define epicos de alto nivel
- Marca ambiguidades com [NEEDS CLARIFICATION]
- Garante rastreabilidade a evidencias

## Nao faz
- Pesquisa de usuarios -> `/discovery`
- User stories detalhadas -> `/stories`
- Decisoes tecnicas -> time de engenharia
- Design tecnico -> `/pf-spec`

-> Detalhes: `.claude/agents/strategist.md`
