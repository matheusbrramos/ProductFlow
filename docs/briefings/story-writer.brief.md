# /story-writer - Briefing

**Foco**: User stories e acceptance criteria
**Fase**: 3.5 (apos /prd)
**Depende**: PRD aprovado de /strategist

## Selecao de Modelo
**Sempre pergunta ao PM qual modelo usar**:
1. Completo (Sonnet/Opus) - Stories complexas
2. Economico (Haiku) - Stories simples
3. Automatico - Agente decide

## Comandos
- `/stories <feature>` - Quebra PRD em stories
- `/expand <story-id>` - Expande com mais contexto
- `/split <story-id>` - Divide story grande
- `/map <feature>` - Cria story map

## Output
- `docs/stories/{feature}.md` - Stories detalhadas

## O que faz
- Transforma requisitos em stories (Como/Quero/Para)
- Escreve acceptance criteria em Gherkin
- Cobre edge cases e excecoes
- Mapeia dependencias entre stories
- Estima complexidade

## Nao faz
- Definir requisitos -> /prd
- Mudar escopo do PRD
- Escrever codigo

-> Detalhes: `.claude/agents/story-writer.md`
