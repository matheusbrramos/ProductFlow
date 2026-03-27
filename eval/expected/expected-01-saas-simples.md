# Estrutura Esperada - Brief 01: SaaS Simples

## Arquivos que DEVEM ser criados

### 1. Contexto

```
.context/empresa.md
```

**Secoes obrigatorias:**
- [ ] Dados Basicos (nome, site, segmento)
- [ ] Missao e Posicionamento
- [ ] Projeto Atual (nome, problema, objetivo)
- [ ] Stakeholders
- [ ] Restricoes
- [ ] Criterios de Sucesso
- [ ] Fontes Consultadas

### 2. Pesquisa

```
docs/research/concorrentes-relatorios-YYYY-MM-DD.md
```

**Secoes obrigatorias:**
- [ ] Sumario Executivo
- [ ] Analise por Concorrente (Basecamp, Asana, Monday)
- [ ] Comparativo de Features
- [ ] Oportunidades Identificadas
- [ ] Fontes Consultadas

### 3. PRD

```
docs/prd/modulo-relatorios-automaticos.md
```

**Secoes obrigatorias:**
- [ ] Sumario Executivo
  - [ ] Problema (clientes gastam 4h/semana)
  - [ ] Evidencias
  - [ ] Solucao Proposta
  - [ ] Outcome (reducao 75%, NPS > 8)
- [ ] Contexto (JTBD, personas)
- [ ] Requisitos Funcionais
- [ ] Requisitos Nao-Funcionais
- [ ] Escopo (in/out)
- [ ] Metricas de Sucesso
- [ ] [NEEDS CLARIFICATION] se houver

### 4. Stories

```
docs/stories/modulo-relatorios-automaticos.md
```

**Secoes obrigatorias:**
- [ ] Referencia ao PRD
- [ ] Pelo menos 3 User Stories
- [ ] Formato Como/Quero/Para
- [ ] Acceptance Criteria em Gherkin
- [ ] Prioridade e Estimativa

### 5. Review

```
docs/reviews/modulo-relatorios-automaticos-review.md
```

**Secoes obrigatorias:**
- [ ] Sumario com score
- [ ] Status (Aprovado/Correcoes)
- [ ] Issues identificados (se houver)
- [ ] Recomendacao

## Criterios de Qualidade

### PRD

| Criterio | Esperado |
|----------|----------|
| Problema claro | Sim - "4h/semana em relatorios manuais" |
| Metricas definidas | Sim - "75% reducao" e "NPS > 8" |
| Restricoes respeitadas | Sim - MVP 2 meses, 3 devs, Google Analytics |
| Requisitos testaveis | Todos devem ser verificaveis |

### Stories

| Criterio | Esperado |
|----------|----------|
| Cobertura de requisitos | Todas as features do PRD |
| INVEST | Independentes, estimaveis, testaveis |
| Gherkin valido | Given/When/Then corretos |

## Red Flags (Falhas Criticas)

- [ ] PRD sem metricas de sucesso
- [ ] Stories sem acceptance criteria
- [ ] Requisitos que ignoram restricoes (ex: features que nao cabem em 2 meses)
- [ ] Falta de rastreabilidade entre docs
- [ ] Codigo ou decisoes tecnicas no PRD (deve ser O QUE, nao COMO)
