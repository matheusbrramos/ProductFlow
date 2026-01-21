# Estrutura Esperada - Brief 02: Fintech Complexa

## Arquivos que DEVEM ser criados

### 1. Contexto

```
.context/empresa.md
```

**Secoes obrigatorias:**
- [ ] Dados Basicos (nome, site, segmento Fintech)
- [ ] Regulacao (BACEN, LGPD)
- [ ] Projeto Atual
- [ ] Multiplas Personas (Gestor, Analista, Compliance)
- [ ] Restricoes detalhadas
- [ ] Criterios de Sucesso com thresholds

### 2. Pesquisa

```
docs/research/concorrentes-antecipacao-YYYY-MM-DD.md
```

**Secoes obrigatorias:**
- [ ] Sumario Executivo
- [ ] Analise por Concorrente (4 concorrentes)
- [ ] Comparativo de Features
- [ ] Comparativo de Taxas/Precos (se disponivel)
- [ ] Analise Regulatoria
- [ ] Gaps de Mercado
- [ ] Oportunidades

### 3. Discovery

```
docs/discovery/entrevista-gestor-financeiro-YYYY-MM-DD.md
docs/discovery/entrevista-analista-risco-YYYY-MM-DD.md
```

**Secoes obrigatorias por entrevista:**
- [ ] Perfil do entrevistado
- [ ] Jobs-to-be-Done identificados
- [ ] Padroes (se houver multiplas entrevistas)
- [ ] Oportunidades

### 4. PRD

```
docs/prd/antecipacao-recebiveis.md
```

**Secoes obrigatorias:**
- [ ] Sumario Executivo
- [ ] Contexto com 3 Personas
- [ ] Requisitos Funcionais categorizados
  - [ ] Solicitacao de antecipacao
  - [ ] Analise de risco automatica
  - [ ] Aprovacao/Rejeicao
  - [ ] Auditoria
- [ ] Requisitos Nao-Funcionais DETALHADOS
  - [ ] Performance (SLA < 2 min)
  - [ ] Seguranca (LGPD, criptografia)
  - [ ] Compliance (BACEN)
  - [ ] Auditoria (log completo)
- [ ] Escopo claro (in/out)
- [ ] Riscos identificados
- [ ] [NEEDS CLARIFICATION] para decisoes pendentes

### 5. SDD (Opcional mas esperado para complexidade alta)

```
docs/sdd/antecipacao-recebiveis.md
```

**Secoes obrigatorias:**
- [ ] Arquitetura proposta
- [ ] Integracao com bureaus (Serasa/SPC)
- [ ] Seguranca e auditoria
- [ ] Performance e escalabilidade

### 6. Stories

```
docs/stories/antecipacao-recebiveis.md
```

**Secoes obrigatorias:**
- [ ] Stories para cada persona
- [ ] Cobertura de happy path e edge cases
- [ ] Cenarios de erro/rejeicao
- [ ] Stories de auditoria/compliance

### 7. Materiais de Vendas

```
docs/sales/battlecard-creditas.md
```

**Secoes obrigatorias:**
- [ ] Pitch curto
- [ ] Comparativo Nos vs Eles
- [ ] Diferenciais
- [ ] Quando eles ganham
- [ ] Quando nos ganhamos

### 8. Review

```
docs/reviews/antecipacao-recebiveis-review.md
```

## Criterios de Qualidade

### PRD

| Criterio | Esperado |
|----------|----------|
| Requisitos regulatorios | BACEN e LGPD explicitamente cobertos |
| Performance | SLA < 2 min mencionado |
| Seguranca | Auditoria completa especificada |
| Metricas com threshold | R$ 10M/mes, 60% automatico, < 2% inadimplencia |
| Multiplas personas | 3 personas com jornadas distintas |

### Stories

| Criterio | Esperado |
|----------|----------|
| Cobertura de personas | Stories para Gestor, Analista, Compliance |
| Edge cases | Rejeicao, timeout, dados incompletos |
| Compliance | Stories de auditoria e log |

### Battlecard

| Criterio | Esperado |
|----------|----------|
| Sem dados inventados | Apenas informacoes pesquisadas |
| Diferenciais claros | Baseados em gaps identificados |
| Objecoes | Pelo menos 3 objecoes comuns |

## Red Flags (Falhas Criticas)

- [ ] Ignorar requisitos de compliance/BACEN
- [ ] PRD sem mencao a LGPD
- [ ] SLA de performance nao especificado
- [ ] Stories sem cenarios de rejeicao
- [ ] Falta de auditoria nas specs
- [ ] Battlecard com dados inventados
- [ ] Metricas sem thresholds especificos do brief
- [ ] Requisitos que excedem restricoes (time de 3 devs ignorado)

## Diferenciais Positivos

- [ ] OST (Opportunity Solution Tree) criada
- [ ] ADRs (Architecture Decision Records) no SDD
- [ ] Matriz de risco documentada
- [ ] Fluxo de rollback definido
- [ ] Feature flags propostos
