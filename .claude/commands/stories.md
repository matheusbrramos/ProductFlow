---
description: "Criar user stories detalhadas com acceptance criteria"
argument-hint: "<feature ou PRD>"
---

# /stories - Criar User Stories Detalhadas

Cria user stories detalhadas usando o agente Story-Writer.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, perguntar qual feature ou PRD detalhar.

## Pre-requisitos

1. PRD aprovado (criado por /prd)
2. `.context/empresa.md` deve existir

Se PRD nao existir, orientar a rodar `/prd` primeiro.

## Selecao de Modelo

**SEMPRE perguntar ao PM antes de comecar:**

```
Qual modelo voce deseja usar para esta sessao de escrita de stories?

1. **Modelo completo** (Sonnet/Opus) - Para stories complexas com muitos edge cases
2. **Modelo economico** (Haiku) - Para stories simples e bem definidas
3. **Deixar eu decidir** - Vou sugerir baseado na complexidade da tarefa

Aguardo sua escolha antes de prosseguir.
```

## O que fazer

1. **Analisar PRD ou feature**
   - Identificar requisitos funcionais
   - Entender personas e JTBD
   - Mapear epicos

2. **Quebrar em user stories**
   - Formato: Como [persona] Quero [acao] Para [beneficio]
   - Garantir independencia (INVEST)
   - Manter rastreabilidade aos requisitos

3. **Escrever acceptance criteria**
   - Formato Gherkin (Given/When/Then)
   - Cobrir cenario principal (happy path)
   - Cobrir excecoes e edge cases

4. **Adicionar metadata**
   - Prioridade (P0/P1/P2/P3)
   - Estimativa (XS/S/M/L/XL)
   - Dependencias entre stories
   - Definition of Done

## Output

Criar arquivo: `docs/stories/{feature}.md`

## Estrutura do Output

```markdown
# User Stories - [Feature]

**PRD:** [referencia]
**Data:** YYYY-MM-DD
**Modelo usado:** [completo/economico]

## Story Map
[Visualizacao opcional]

## Stories

### US-001: [Titulo]
**Epic:** [nome]
**Requisitos:** [RF-XXX]

**Como** [persona]
**Quero** [acao]
**Para** [beneficio]

#### Acceptance Criteria
```gherkin
Scenario: [descricao]
  Given [contexto]
  When [acao]
  Then [resultado]
```

**Prioridade:** P0
**Estimativa:** M
**Dependencias:** -
```

## Proximos passos sugeridos

- `/pf-review` - Revisar qualidade das stories
- Entregar para time de desenvolvimento

## Exemplos

```
/stories "Alertas inteligentes"
/stories docs/prd/autenticacao.md
```
