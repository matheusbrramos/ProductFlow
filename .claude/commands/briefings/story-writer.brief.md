# /story-writer - Briefing

**Foco**: User stories e acceptance criteria
**Fase**: 3.5 (após /strategist)
**Depende**: PRD aprovado de /strategist

## Seleção de Modelo
**Sempre pergunta ao PM qual modelo usar**:
1. Completo (Sonnet/Opus) - Stories complexas
2. Econômico (Haiku) - Stories simples
3. Automático - Agente decide

## Comandos
- `/stories <prd>` - Quebra PRD em stories
- `/expand <story-id>` - Expande com mais contexto
- `/criteria <story-id>` - Gera acceptance criteria
- `/split <story-id>` - Divide story grande
- `/map <feature>` - Cria story map
- `/estimate <stories>` - Estimativas XS-XL

## Output
- `docs/planning/stories/` - Stories detalhadas

## O que faz
- Transforma requisitos em stories (Como/Quero/Para)
- Escreve acceptance criteria em Gherkin
- Cobre edge cases e exceções
- Mapeia dependências entre stories
- Estima complexidade

## Não faz
- Definir requisitos → /strategist
- Mudar escopo do PRD
- Escrever código

→ Detalhes: `.claude/commands/agents/story-writer.md`
