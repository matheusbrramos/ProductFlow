# ProductFlow

Sistema de agentes especializados para Product Managers usando Claude Code.

**ProductFlow** é seu parceiro sênior para as etapas anteriores ao desenvolvimento de produto: discovery, pesquisa de mercado, especificação e go-to-market.

---

## Instalação Rápida

### Opção 1: Clonar direto na pasta do seu projeto

```bash
# Na raiz do seu projeto, execute:
git clone https://github.com/matheusbrramos/ProductFlow.git .productflow-temp
cp -r .productflow-temp/.claude .claude
cp .productflow-temp/CLAUDE.md CLAUDE.md
rm -rf .productflow-temp

# Crie as pastas de contexto
mkdir -p .context docs/discovery docs/research docs/planning/stories docs/sales docs/reviews .productflow/snapshots .productflow/memory
```

### Opção 2: Download manual

1. Baixe o ZIP do repositório
2. Copie a pasta `.claude` para a raiz do seu projeto
3. Copie o arquivo `CLAUDE.md` para a raiz do seu projeto
4. Crie as pastas necessárias (veja estrutura abaixo)

### Opção 3: Script de instalação (Windows PowerShell)

```powershell
# Execute no PowerShell na pasta do seu projeto:
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/matheusbrramos/ProductFlow/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### Opção 4: Script de instalação (Linux/Mac)

```bash
# Execute no terminal na pasta do seu projeto:
curl -sSL https://raw.githubusercontent.com/matheusbrramos/ProductFlow/main/install.sh | bash
```

---

## Estrutura de Pastas

Após instalação, seu projeto terá:

```
seu-projeto/
├── CLAUDE.md                    # Regras globais do ProductFlow
├── .claude/
│   └── commands/
│       ├── agents/              # 6 agentes especializados
│       │   ├── helper.md
│       │   ├── discovery.md
│       │   ├── researcher.md
│       │   ├── strategist.md
│       │   ├── sales-enabler.md
│       │   └── supervisor.md
│       └── quick/               # Comandos rápidos
│           ├── setup.md
│           ├── discovery.md
│           ├── competitors.md
│           ├── prd.md
│           ├── sales.md
│           ├── review.md
│           └── status.md
├── .context/                    # Contexto do projeto (criado pelos agentes)
│   ├── empresa.md
│   └── competidores-{projeto}.md
├── docs/
│   ├── discovery/               # Insights de usuários
│   ├── research/                # Pesquisas de mercado
│   ├── planning/                # PRDs e specs
│   │   └── stories/             # User stories
│   ├── sales/                   # Materiais de vendas
│   └── reviews/                 # Revisões de qualidade
└── .productflow/
    ├── snapshots/               # Estados do projeto
    └── memory/                  # Contexto persistente
```

---

## Agentes Disponíveis

| Agente | Comando | Responsabilidade |
|--------|---------|------------------|
| **Helper** | `@helper` | Coleta contexto da empresa (proativo) |
| **Discovery** | `@discovery` | Entrevistas, OST, JTBD (Teresa Torres) |
| **Researcher** | `@researcher` | Mercado, concorrentes (execução paralela) |
| **Strategist** | `@strategist` | PRD, requisitos, user stories |
| **Sales-Enabler** | `@sales-enabler` | Materiais de vendas e GTM |
| **Supervisor** | `@supervisor` | Revisão de qualidade e consistência |

---

## Comandos Rápidos

| Comando | Descrição |
|---------|-----------|
| `/setup <site>` | Inicia contexto do projeto |
| `/discovery <ação>` | Análise de usuários |
| `/competitors <lista>` | Análise de concorrentes |
| `/prd <feature>` | Cria PRD completo |
| `/sales` | Materiais de vendas |
| `/review` | Revisão de qualidade |
| `/status` | Status do projeto |

---

## Fluxo de Trabalho Típico

```
1. /setup www.suaempresa.com.br    # Contexto da empresa
        ↓
2. /discovery analyze [dados]       # Insights de usuários
   /competitors Conc1, Conc2        # Análise de mercado
        ↓
3. /prd "Nome da Feature"           # Especificação completa
        ↓
4. /sales                           # Materiais de vendas
        ↓
5. /review ready                    # Validação final
```

---

## Princípios do ProductFlow

1. **Parceria Sênior**: Agentes questionam e orientam, não apenas executam
2. **Qualidade > Economia**: Prioriza profundidade sobre velocidade
3. **Validação pelo PM**: Todo artefato é validado antes de avançar
4. **Proatividade**: Agentes pesquisam automaticamente quando possível
5. **Consistência**: Supervisor garante alinhamento entre artefatos

---

## Requisitos

- [Claude Code](https://claude.ai/code) instalado
- Acesso à internet (para pesquisas dos agentes)

---

## Exemplos de Uso

### Iniciando um novo projeto

```
Você: @helper /setup www.sympla.com.br

Helper: Pesquisando informações sobre Sympla...
[Apresenta dados coletados automaticamente]
[Faz perguntas sobre o que não encontrou]
[Cria .context/empresa.md]
```

### Analisando concorrentes

```
Você: @researcher /competitors Eventbrite, Ingresse, Blueticket

Researcher: Lançando análise paralela de 3 concorrentes...
[Sub-agente 1] Analisando Eventbrite...
[Sub-agente 2] Analisando Ingresse...
[Sub-agente 3] Analisando Blueticket...
[Consolida em .context/competidores-sympla.md]
```

### Criando PRD

```
Você: @strategist /prd "Alertas inteligentes de vendas"

Strategist: Verificando contexto e evidências...
[Cria PRD completo com requisitos F/NF detalhados]
[Marca ambiguidades com [NEEDS CLARIFICATION]]
```

---

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

---

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## Autor

Criado com Claude Code.

---

**ProductFlow v1.0** - Seu parceiro sênior para Product Management
