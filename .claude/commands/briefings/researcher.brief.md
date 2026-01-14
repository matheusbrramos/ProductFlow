# /researcher - Briefing

**Foco**: Pesquisa de mercado e concorrentes
**Fase**: 1 (após /helper, antes de /discovery)
**Depende**: `.context/empresa.md`

## Comandos
- `/competitors <lista>` - Análise competitiva paralela
- `/sizing <segmento>` - TAM/SAM/SOM
- `/trends <segmento>` - Tendências de mercado
- `/player <nome>` - Análise profunda de um concorrente
- `/compare` - Comparativo lado-a-lado

## Output
- `.context/competidores-{projeto}.md` - Análise consolidada
- `docs/research/` - Sizing, trends, players

## O que faz
- Analisa 5+ concorrentes em paralelo
- Dimensiona mercado com metodologia clara
- Identifica gaps e oportunidades
- Documenta todas as fontes

## Não faz
- Pesquisa de usuários → /discovery
- Criar PRD → /strategist

→ Detalhes: `.claude/commands/agents/researcher.md`
