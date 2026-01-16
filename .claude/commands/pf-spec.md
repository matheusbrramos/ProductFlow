---
description: "Criar Software Design Document (SDD) a partir de um PRD"
argument-hint: "<feature ou PRD>"
---

# /pf-spec - Criar Software Design Document

Cria um SDD (Software Design Document) completo a partir de um PRD aprovado, definindo a arquitetura tecnica e decisoes de implementacao.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, perguntar qual feature ou PRD usar como base.

## Pre-requisitos

1. PRD aprovado deve existir em `docs/prd/`
2. `.context/empresa.md` deve existir

Se PRD nao existir, orientar a rodar `/prd` primeiro.

## O que fazer

1. **Carregar contexto**
   - Ler PRD relacionado
   - Verificar user stories existentes
   - Entender restricoes tecnicas

2. **Criar SDD completo** com todas as secoes:
   - Visao Geral (objetivo, escopo, referencias)
   - Contexto e Restricoes (sistema atual, restricoes tecnicas, premissas)
   - Arquitetura Proposta (diagrama, componentes, fluxo de dados)
   - Design Detalhado (por componente: responsabilidades, interface, modelo de dados)
   - Integracao (dependencias internas/externas, contratos de API)
   - Seguranca (autenticacao, autorizacao, criptografia, auditoria)
   - Performance e Escalabilidade (requisitos, estrategia, caching)
   - Observabilidade (metricas, logs, alertas)
   - Testes (estrategia, dados de teste)
   - Plano de Rollout (fases, feature flags, rollback)
   - Riscos Tecnicos (probabilidade, impacto, mitigacao)
   - Decisoes de Design (ADRs)

3. **Garantir rastreabilidade**
   - Linkar requisitos do PRD
   - Referenciar user stories
   - Conectar com analise competitiva

## REGRAS CRITICAS

- SDD define O COMO tecnico (arquitetura, tecnologias, APIs)
- Deve ser consistente com os requisitos do PRD
- Marcar [NEEDS TECH REVIEW] para decisoes que precisam validacao
- Nao alterar requisitos definidos no PRD

## Output

Criar arquivo: `docs/sdd/{feature}.md`

Usar template em `docs/templates/sdd-template.md`

## Estrutura do Output

```markdown
# SDD: [Nome da Feature]

**Versao:** 1.0
**Data:** YYYY-MM-DD
**Status:** Draft | Em Revisao | Aprovado
**PRD Relacionado:** docs/prd/{feature}.md
**Autor:** [nome]

## 1. Visao Geral
### Objetivo
### Escopo
### Referencias

## 2. Contexto e Restricoes
### Contexto do Sistema
### Restricoes Tecnicas
### Premissas Tecnicas

## 3. Arquitetura Proposta
### Diagrama de Alto Nivel
### Componentes Principais
### Fluxo de Dados

## 4. Design Detalhado
### 4.1 [Componente 1]
#### Responsabilidades
#### Interface
#### Modelo de Dados
#### Comportamento

## 5. Integracao
### Dependencias Internas
### Dependencias Externas
### Contratos de API

## 6. Seguranca
### Autenticacao
### Autorizacao
### Criptografia
### Auditoria

## 7. Performance e Escalabilidade
### Requisitos de Performance
### Estrategia de Escalabilidade
### Caching

## 8. Observabilidade
### Metricas
### Logs
### Alertas

## 9. Testes
### Estrategia de Testes
### Dados de Teste

## 10. Plano de Rollout
### Fases
### Feature Flags
### Rollback

## 11. Riscos Tecnicos

## 12. Decisoes de Design (ADRs)

## Historico de Versoes
## Aprovacoes
```

## Proximos passos sugeridos

- `/pf-review docs/sdd/{feature}.md` - Revisar qualidade do SDD
- `/stories <feature>` - Criar/atualizar user stories com detalhes tecnicos

## Exemplos

```
/pf-spec "Alertas inteligentes de vendas"
/pf-spec docs/prd/autenticacao.md
/pf-spec "Sistema de notificacoes"
```
