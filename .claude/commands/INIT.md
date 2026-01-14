# ProductFlow - Inicialização Rápida

Sistema de **7 agentes especializados** para Product Management.

## Fluxo Sequencial

```
/helper → /researcher → /discovery → /strategist → /story-writer → /sales-enabler
                                                                          ↓
                                                              /supervisor (qualidade)
```

## Agentes

| # | Agente | Foco | Comando |
|---|--------|------|---------|
| 0 | Helper | Contexto da empresa | `/helper` |
| 1 | Researcher | Mercado e concorrentes | `/researcher` |
| 2 | Discovery | Pesquisa de usuários | `/discovery` |
| 3 | Strategist | PRD e requisitos | `/strategist` |
| 3.5 | Story-Writer | User stories detalhadas | `/story-writer` |
| 4 | Sales-Enabler | Materiais de vendas | `/sales-enabler` |
| 5 | Supervisor | Revisão de qualidade | `/supervisor` |

## Contexto Persistente

| Arquivo | Criado por | Conteúdo |
|---------|------------|----------|
| `.context/empresa.md` | /helper | Missão, produtos, público, diferenciais |
| `.context/competidores-{x}.md` | /researcher | Análise competitiva, TAM/SAM/SOM |

## Outputs por Fase

| Fase | Diretório | Exemplos |
|------|-----------|----------|
| Research | `docs/research/` | sizing, trends, players |
| Discovery | `docs/discovery/` | entrevistas, OST, JTBD |
| Planning | `docs/planning/` | PRDs, specs |
| Stories | `docs/planning/stories/` | user stories detalhadas |
| Sales | `docs/sales/` | decks, battlecards, playbooks |
| Reviews | `docs/reviews/` | revisões de qualidade |

## Princípios Core

1. **Parceria Sênior**: Questionar, orientar, apontar riscos
2. **Validação PM**: Tudo precisa aprovação do PM
3. **Evidência > Opinião**: Basear em dados
4. **Contexto Primeiro**: Sempre carregar `.context/empresa.md`

## Quick Start

```bash
# 1. Setup inicial
/helper "https://suaempresa.com"

# 2. Pesquisa de mercado
/researcher /competitors "Empresa A, Empresa B"

# 3. Discovery de usuários
/discovery /analyze [dados]

# 4. Criar PRD
/strategist /prd "Nome da Feature"

# 5. Detalhar stories
/story-writer /stories "PRD criado"

# 6. Materiais de vendas
/sales-enabler /catalogo

# 7. Revisar qualidade
/supervisor /review
```

## Para Detalhes

Cada agente tem documentação completa em:
`.claude/commands/agents/{agente}.md`

Briefings resumidos em:
`.claude/commands/briefings/{agente}.brief.md`

---
*ProductFlow v2.0*
