---
description: ProductFlow - Inicializacao Rapida
---

# ProductFlow - Inicializacao Rapida

Sistema de **7 subagents especializados** para Product Management.

## Fluxo Sequencial

```
/setup -> /research -> /discovery -> /prd -> /stories -> /sales
                                                            |
                                                      /review (qualidade)
```

## Slash Commands

| Comando | Descricao | Output |
|---------|-----------|--------|
| `/setup <site>` | Contexto da empresa | `.context/empresa.md` |
| `/research <tema>` | Mercado e concorrentes | `docs/research/{tema}-YYYY-MM-DD.md` |
| `/discovery <acao>` | Pesquisa de usuarios | `docs/discovery/{tema}-YYYY-MM-DD.md` |
| `/prd <feature>` | PRD completo | `docs/prd/{feature}.md` |
| `/stories <feature>` | User stories | `docs/stories/{feature}.md` |
| `/sales` | Materiais de vendas | `docs/sales/` |
| `/review <artefato>` | Revisao de qualidade | `docs/reviews/{feature}-review.md` |
| `/status` | Status do projeto | (terminal) |

## Subagents (`.claude/agents/`)

| Subagent | Foco |
|----------|------|
| helper | Coleta contexto (proativo) |
| researcher | Mercado, concorrentes (paralelo) |
| discovery | OST, JTBD, entrevistas |
| strategist | PRD, requisitos |
| story-writer | User stories, acceptance criteria |
| sales-enabler | Materiais de vendas |
| supervisor | Revisao de qualidade |

## Contexto Persistente

| Arquivo | Criado por | Conteudo |
|---------|------------|----------|
| `.context/empresa.md` | /setup | Missao, produtos, publico, diferenciais |
| `.context/competidores-{x}.md` | /research | Analise competitiva, TAM/SAM/SOM |

## Contrato de Outputs

| Fase | Diretorio | Formato |
|------|-----------|---------|
| Research | `docs/research/` | `{tema}-YYYY-MM-DD.md` |
| Discovery | `docs/discovery/` | `{tema}-YYYY-MM-DD.md` |
| PRD | `docs/prd/` | `{feature}.md` |
| Stories | `docs/stories/` | `{feature}.md` |
| Sales | `docs/sales/` | varios |
| Reviews | `docs/reviews/` | `{feature}-review.md` |

## Principios Core

1. **Parceria Senior**: Questionar, orientar, apontar riscos
2. **Validacao PM**: Tudo precisa aprovacao do PM
3. **Evidencia > Opiniao**: Basear em dados
4. **Contexto Primeiro**: Sempre carregar `.context/empresa.md`

## Quick Start

```bash
# 1. Setup inicial
/setup www.suaempresa.com.br

# 2. Pesquisa de mercado
/research Concorrente1, Concorrente2

# 3. Discovery de usuarios
/discovery analyze [dados]

# 4. Criar PRD
/prd "Nome da Feature"

# 5. Detalhar stories
/stories "Nome da Feature"

# 6. Materiais de vendas
/sales

# 7. Revisar qualidade
/review ready
```

## Para Detalhes

- Subagents: `.claude/agents/{agente}.md`
- Commands: `.claude/commands/{comando}.md`
- Briefings: `docs/briefings/{agente}.brief.md`

---
*ProductFlow v3.0*
