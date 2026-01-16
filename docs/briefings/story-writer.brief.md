# Story Writer Agent - Briefing

**Foco**: User stories e acceptance criteria
**Fase**: 3.5 (apos `/prd`)
**Depende**: PRD aprovado

## Selecao de Modelo
**Sempre pergunta ao PM qual modelo usar**:
1. Completo (Sonnet/Opus) - Stories complexas
2. Economico (Haiku) - Stories simples
3. Automatico - Agente decide

## Como Invocar
- `/stories <feature>` - Quebra PRD em stories

**Tecnicas internas** (usadas automaticamente pelo agente):
- **expand**: Expande story com mais contexto
- **split**: Divide story grande em menores
- **map**: Cria story map visual

Estas tecnicas sao aplicadas internamente conforme necessidade, nao sao comandos separados.

## Output
- `docs/stories/{feature}.md` - Stories detalhadas

## O que faz
- Transforma requisitos em stories (Como/Quero/Para)
- Escreve acceptance criteria em Gherkin
- Cobre edge cases e excecoes
- Mapeia dependencias entre stories
- Estima complexidade

## Nao faz
- Definir requisitos -> `/prd`
- Mudar escopo do PRD
- Escrever codigo

-> Detalhes: `.claude/agents/story-writer.md`
