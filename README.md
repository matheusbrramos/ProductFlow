# ProductFlow

Sistema de agentes especializados para Product Managers usando Claude Code.

**ProductFlow** e seu parceiro senior para as etapas anteriores ao desenvolvimento de produto: discovery, pesquisa de mercado, especificacao e go-to-market.

---

## Instalacao Rapida

### Opcao 1: Clonar direto na pasta do seu projeto

```bash
# Na raiz do seu projeto, execute:
git clone https://github.com/matheusbrramos/ProductFlow.git .productflow-temp
cp -r .productflow-temp/.claude .claude
cp .productflow-temp/CLAUDE.md CLAUDE.md
rm -rf .productflow-temp

# Crie as pastas de contexto
mkdir -p .context docs/discovery docs/research docs/prd docs/stories docs/sales docs/reviews docs/briefings docs/templates .productflow/snapshots .productflow/memory
```

### Opcao 2: Script de instalacao (Windows PowerShell)

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/matheusbrramos/ProductFlow/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### Opcao 3: Script de instalacao (Linux/Mac)

```bash
curl -sSL https://raw.githubusercontent.com/matheusbrramos/ProductFlow/main/install.sh | bash
```

---

## Estrutura de Pastas

Apos instalacao, seu projeto tera:

```
seu-projeto/
├── CLAUDE.md                    # Regras globais do ProductFlow
├── .claude/
│   ├── agents/                  # 7 subagents especializados
│   │   ├── helper.md
│   │   ├── researcher.md
│   │   ├── discovery.md
│   │   ├── strategist.md
│   │   ├── story-writer.md
│   │   ├── sales-enabler.md
│   │   └── supervisor.md
│   └── commands/                # Slash commands
│       ├── setup.md             # /setup
│       ├── research.md          # /research
│       ├── discovery.md         # /discovery
│       ├── prd.md               # /prd
│       ├── stories.md           # /stories
│       ├── sales.md             # /sales
│       ├── review.md            # /review
│       └── status.md            # /status
├── .context/                    # Contexto do projeto
│   ├── empresa.md               # Criado por /setup
│   └── competidores-{projeto}.md # Criado por /research
├── docs/
│   ├── briefings/               # Resumos dos agentes
│   ├── templates/               # Templates de PRD e SDD
│   ├── research/                # docs/research/{tema}-YYYY-MM-DD.md
│   ├── discovery/               # docs/discovery/{tema}-YYYY-MM-DD.md
│   ├── prd/                     # docs/prd/{feature}.md
│   ├── stories/                 # docs/stories/{feature}.md
│   ├── sales/                   # Materiais de vendas
│   └── reviews/                 # docs/reviews/{feature}-review.md
└── .productflow/
    ├── snapshots/               # Estados do projeto
    └── memory/                  # Contexto persistente
```

---

## Subagents vs Commands

ProductFlow usa dois conceitos do Claude Code:

### Subagents (`.claude/agents/`)

Agentes especializados que podem ser invocados via Task tool para tarefas complexas e autonomas. Cada subagent tem sua propria personalidade e expertise.

| Subagent | Foco |
|----------|------|
| helper | Coleta contexto da empresa (proativo) |
| researcher | Mercado, concorrentes (execucao paralela) |
| discovery | Entrevistas, OST, JTBD (Teresa Torres) |
| strategist | PRD, epicos, requisitos, priorizacao |
| story-writer | User stories detalhadas e acceptance criteria |
| sales-enabler | Materiais de vendas e GTM |
| supervisor | Revisao de qualidade e consistencia |

### Slash Commands (`.claude/commands/`)

Atalhos para acoes comuns. Cada comando usa $ARGUMENTS para receber entrada do usuario.

| Comando | Descricao | Output |
|---------|-----------|--------|
| `/setup <site>` | Inicia contexto do projeto | `.context/empresa.md` |
| `/research <tema>` | Pesquisa de mercado/concorrentes | `docs/research/{tema}-YYYY-MM-DD.md` |
| `/discovery <acao>` | Analise de usuarios | `docs/discovery/{tema}-YYYY-MM-DD.md` |
| `/prd <feature>` | Cria PRD completo | `docs/prd/{feature}.md` |
| `/stories <feature>` | Detalha user stories | `docs/stories/{feature}.md` |
| `/sales` | Materiais de vendas | `docs/sales/` |
| `/review <artefato>` | Revisao de qualidade | `docs/reviews/{feature}-review.md` |
| `/status` | Status do projeto | (exibe no terminal) |

---

## Contrato de Arquivos

### .context/ - Contexto Persistente

Arquivos de contexto que persistem entre sessoes e sao usados por todos os agentes:

- **empresa.md**: Missao, visao, produtos, publico-alvo, diferenciais, metas
- **competidores-{projeto}.md**: Analise competitiva consolidada

### .productflow/ - Estado Interno

- **snapshots/**: Estados salvos do projeto
- **memory/**: Contexto acumulado entre sessoes

### docs/ - Artefatos de Trabalho

Todos os artefatos seguem o padrao de nomenclatura:

```
docs/research/{tema}-YYYY-MM-DD.md
docs/discovery/{tema}-YYYY-MM-DD.md
docs/prd/{feature}.md
docs/stories/{feature}.md
docs/reviews/{feature}-review.md
```

---

## Fluxo de Trabalho Tipico

```
1. /setup www.suaempresa.com.br    # Contexto da empresa
        |
2. /research Conc1, Conc2          # Analise de mercado
   /discovery analyze [dados]       # Insights de usuarios
        |
3. /prd "Nome da Feature"           # Especificacao completa
        |
4. /stories "Nome da Feature"       # User stories detalhadas
        |
5. /sales                           # Materiais de vendas
        |
6. /review ready                    # Validacao final
```

---

## Exemplo Real de Execucao

```bash
# 1. Iniciar contexto
/setup www.sympla.com.br

# 2. Pesquisar mercado
/research Eventbrite, Ingresse, Tickets For Fun

# 3. Criar PRD
/prd "Alertas inteligentes de vendas"

# 4. Detalhar stories
/stories "Alertas inteligentes de vendas"

# 5. Revisar
/review docs/prd/alertas-inteligentes-de-vendas.md
```

---

## Principios do ProductFlow

1. **Parceria Senior**: Agentes questionam e orientam, nao apenas executam
2. **Qualidade > Economia**: Prioriza profundidade sobre velocidade
3. **Validacao pelo PM**: Todo artefato e validado antes de avancar
4. **Evidencia > Opiniao**: Basear em dados e pesquisa
5. **Consistencia**: Supervisor garante alinhamento entre artefatos

---

## Requisitos

- [Claude Code](https://claude.ai/code) instalado
- Acesso a internet (para pesquisas dos agentes)

---

## Contribuindo

Contribuicoes sao bem-vindas! Por favor:

1. Fork o repositorio
2. Crie uma branch para sua feature
3. Faca commit das mudancas
4. Abra um Pull Request

---

## Licenca

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**ProductFlow v3.0** - Seu parceiro senior para Product Management
