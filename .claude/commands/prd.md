---
description: "Criar Product Requirements Document completo"
argument-hint: "<nome da feature ou produto>"
---

# /prd - Criar Product Requirements Document

Cria PRD completo usando o agente Strategist.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, perguntar o nome da feature ou produto.

## Pre-requisitos

1. Verificar se `.context/empresa.md` existe
2. Recomendado: Discovery e pesquisa de mercado concluidos

Se pre-requisitos nao atendidos, orientar quais comandos rodar primeiro.

## O que fazer

1. **Entender o problema**
   - Analisar evidencias de discovery
   - Verificar analise competitiva
   - Questionar premissas

2. **Criar PRD completo** com todas as secoes:
   - Sumario Executivo (problema, evidencias, solucao, outcome)
   - Contexto (JTBD, personas, jornada)
   - Requisitos Funcionais (detalhados, categorizados, priorizados)
   - Requisitos Nao-Funcionais (performance, seguranca, compliance, etc)
   - Escopo (in/out, premissas, restricoes)
   - Epicos (alto nivel)
   - Metricas de Sucesso
   - Riscos

3. **Marcar ambiguidades**
   - Usar [NEEDS CLARIFICATION] para questoes pendentes
   - Listar premissas a validar

4. **Garantir rastreabilidade**
   - Cada requisito linkado a evidencia
   - Referencias a docs de discovery e research

## REGRAS CRITICAS

- Definir O QUE e POR QUE, nunca o COMO
- Nao escrever codigo ou fazer decisoes tecnicas
- Nao incluir features especulativas
- Todos os requisitos devem ser testaveis

## Output

Criar arquivo: `docs/prd/{feature}.md`

Usar estrutura completa do PRD com todas as secoes obrigatorias.

## Proximos passos sugeridos

- `/pf-review` - Revisar qualidade do PRD
- `/stories <feature>` - Detalhar user stories
- `/pf-spec <feature>` - Criar Software Design Document

## Exemplos

```
/prd "Alertas inteligentes de vendas"
/prd "Sistema de autenticacao"
/prd "Modulo de relatorios"
```
