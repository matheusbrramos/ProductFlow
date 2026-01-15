# /researcher - Briefing

**Foco**: Pesquisa de mercado e concorrentes
**Fase**: 1 (apos /helper, antes de /discovery)
**Depende**: `.context/empresa.md`

## Comandos
- `/research <tema>` - Pesquisa de mercado e concorrentes
- `/competitors <lista>` - Analise competitiva paralela
- `/sizing <segmento>` - TAM/SAM/SOM
- `/trends <segmento>` - Tendencias de mercado

## Output
- `.context/competidores-{projeto}.md` - Analise consolidada
- `docs/research/{tema}-YYYY-MM-DD.md` - Pesquisas

## O que faz
- Analisa 5+ concorrentes em paralelo
- Dimensiona mercado com metodologia clara
- Identifica gaps e oportunidades
- Documenta todas as fontes

## Nao faz
- Pesquisa de usuarios -> /discovery
- Criar PRD -> /prd

-> Detalhes: `.claude/agents/researcher.md`
