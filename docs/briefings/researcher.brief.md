# Researcher Agent - Briefing

**Foco**: Pesquisa de mercado e concorrentes
**Fase**: 1 (apos `/setup`, antes de `/discovery`)
**Depende**: `.context/empresa.md`

## Como Invocar
- `/research <tema>` - Pesquisa geral de mercado
- `/research competitors "<lista>"` - Analise competitiva (modo competitors)
- `/research sizing "<segmento>"` - TAM/SAM/SOM (modo sizing)
- `/research trends "<segmento>"` - Tendencias de mercado (modo trends)

**Nota**: competitors, sizing e trends sao MODOS do comando `/research`, nao comandos separados.

## Output
- `.context/competidores-{projeto}.md` - Analise consolidada
- `docs/research/{tema}-YYYY-MM-DD.md` - Pesquisas

## O que faz
- Analisa 5+ concorrentes em paralelo
- Dimensiona mercado com metodologia clara
- Identifica gaps e oportunidades
- Documenta todas as fontes

## Nao faz
- Pesquisa de usuarios -> `/discovery`
- Criar PRD -> `/prd`

-> Detalhes: `.claude/agents/researcher.md`
