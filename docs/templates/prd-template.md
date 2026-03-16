# PRD: [Nome da Feature]

**Versao:** 1.0
**Data:** YYYY-MM-DD
**Status:** Draft | Em Revisao | Aprovado
**Owner:** [PM responsavel]

---

## 1. Sumario Executivo

### Problema
[Descricao clara e especifica do problema a ser resolvido]

### Evidencias
| Fonte | Insight | Referencia |
|-------|---------|------------|
| Entrevistas | [insight] | docs/discovery/... |
| Analytics | [dado] | [link/dashboard] |
| Competidores | [gap] | .context/competidores-... |

### Solucao Proposta
[Descricao em alto nivel - O QUE, nao COMO]

### Outcome de Negocio
**Metrica Principal:** [ex: Retencao de 30% -> 45%]
**Prazo:** [ex: Q2 2025]
**Valor Estimado:** [ex: R$500k/ano em receita retida]

---

## 2. Contexto

### Jobs-to-be-Done
| Job | Tipo | Prioridade |
|-----|------|------------|
| Quando [situacao], quero [acao], para [resultado] | Funcional | Alta |
| [job 2] | Emocional | Media |

### Personas Impactadas

#### Persona Principal: [Nome]
- **Perfil:** [descricao]
- **Objetivo:** [o que quer alcancar]
- **Dor Principal:** [frustracao atual]
- **Frequencia de Uso:** [diario/semanal/etc]

#### Persona Secundaria: [Nome]
[mesma estrutura]

### Jornada Atual vs Desejada
| Etapa | Atual | Desejada | Gap |
|-------|-------|----------|-----|
| [etapa 1] | [como e] | [como sera] | [diferenca] |

---

## 3. Requisitos Funcionais

### Categorias de Requisitos

#### RF-CAT-01: [Categoria - ex: Autenticacao]

| ID | Requisito | Prioridade | Evidencia | Testavel |
|----|-----------|------------|-----------|----------|
| RF-001 | O sistema DEVE [acao especifica] | Must | [ref] | Sim |
| RF-002 | O sistema DEVE [acao especifica] | Must | [ref] | Sim |
| RF-003 | O sistema DEVERIA [acao especifica] | Should | [ref] | Sim |

### Detalhamento de Requisitos Criticos

#### RF-001: [Titulo do Requisito]

**Descricao Completa:**
[Descricao detalhada do que o sistema deve fazer]

**Criterios de Aceite:**
- [ ] Dado [pre-condicao], quando [acao], entao [resultado esperado]
- [ ] Dado [pre-condicao], quando [acao], entao [resultado esperado]

**Regras de Negocio:**
- RN-001: [regra especifica]
- RN-002: [regra especifica]

**Cenarios de Excecao:**
| Cenario | Comportamento Esperado |
|---------|------------------------|
| [excecao 1] | [como o sistema deve reagir] |

**Dependencias:**
- Depende de: [RF-XXX]
- Bloqueia: [RF-YYY]

**[NEEDS CLARIFICATION]:** [Se houver ambiguidade, marcar aqui]

---

## 4. Requisitos Nao-Funcionais

### 4.1 Performance

| ID | Requisito | Metrica | Target | Medicao |
|----|-----------|---------|--------|---------|
| RNF-P01 | Tempo de resposta | Latencia p95 | < 200ms | [como medir] |
| RNF-P02 | Throughput | Req/segundo | > 1000 | [como medir] |

### 4.2 Escalabilidade

| ID | Requisito | Metrica | Target |
|----|-----------|---------|--------|
| RNF-E01 | Usuarios simultaneos | Concurrent users | 10.000 |

### 4.3 Disponibilidade

| ID | Requisito | Metrica | Target |
|----|-----------|---------|--------|
| RNF-D01 | Uptime | Disponibilidade | 99.9% |
| RNF-D02 | Recovery | RTO | < 1 hora |

### 4.4 Seguranca

| ID | Requisito | Categoria | Criticidade |
|----|-----------|-----------|-------------|
| RNF-S01 | Dados em transito DEVEM usar TLS 1.3+ | Criptografia | Critica |
| RNF-S02 | Autenticacao DEVE usar MFA para admins | Acesso | Alta |

### 4.5 Compliance

| ID | Requisito | Regulacao | Obrigatorio |
|----|-----------|-----------|-------------|
| RNF-C01 | Consentimento explicito para coleta de dados | LGPD | Sim |

### 4.6 Usabilidade

| ID | Requisito | Standard | Target |
|----|-----------|----------|--------|
| RNF-U01 | Acessibilidade | WCAG | Nivel AA |
| RNF-U05 | Responsividade | Breakpoints | Mobile, Tablet, Desktop |

---

## 5. Escopo

### Incluido (Must Have - MVP)
| Item | Justificativa | RF Relacionado |
|------|---------------|----------------|
| [funcionalidade 1] | [evidencia] | RF-001, RF-002 |

### Incluido se possivel (Should Have)
| Item | Justificativa | Condicao |
|------|---------------|----------|
| [funcionalidade 3] | [evidencia] | Se houver tempo |

### Explicitamente Fora de Escopo
| Item | Motivo | Quando considerar |
|------|--------|-------------------|
| [item 1] | [justificativa] | v2 / Q3 |

### Premissas
- [Premissa 1 que estamos assumindo como verdadeira]
- [Premissa 2]

### Restricoes
- [Restricao de prazo/budget/tecnica/regulatoria]

---

## 6. Epicos

### Lista de Epicos

| Epic | Descricao | Requisitos | Prioridade |
|------|-----------|------------|------------|
| Epic-01 | [Nome descritivo] | RF-001 a RF-005 | Must Have |
| Epic-02 | [Nome descritivo] | RF-006 a RF-010 | Should Have |

### Detalhamento de Epicos

#### Epic-01: [Nome do Epic]
**Objetivo**: [O que este epico entrega]
**Requisitos cobertos**: RF-001, RF-002, RF-003
**Personas impactadas**: [personas]
**Valor de negocio**: [descricao do valor]

---

**NOTA**: Para detalhamento em user stories com acceptance criteria,
use `/stories` apos aprovacao deste PRD.

---

## 7. Metricas de Sucesso

### Metricas Primarias (OKRs)
| Metrica | Baseline | Target | Prazo | Medicao |
|---------|----------|--------|-------|---------|
| [metrica 1] | [atual] | [objetivo] | [data] | [como medir] |

### Metricas Secundarias (Health Metrics)
| Metrica | Baseline | Alerta se | Medicao |
|---------|----------|-----------|---------|
| [metrica 1] | [atual] | [threshold] | [como] |

### Criterios de Rollback
- Se [metrica X] cair abaixo de [threshold], reverter
- Se [incidentes] > [N] em [periodo], reverter

---

## 8. Riscos

| ID | Risco | Probabilidade | Impacto | Mitigacao |
|----|-------|---------------|---------|-----------|
| R01 | [descricao do risco] | Alta/Media/Baixa | Alto/Medio/Baixo | [acao preventiva] |

### Dependencias Externas
| Dependencia | Owner | Status | Impacto se atrasar |
|-------------|-------|--------|-------------------|
| [sistema/time] | [nome] | [status] | [impacto] |

---

## 9. [NEEDS CLARIFICATION]

### Pendentes de Decisao
| ID | Questao | Opcoes | Impacto | Owner | Deadline |
|----|---------|--------|---------|-------|----------|
| NC-01 | [pergunta especifica] | A, B, C | [impacto] | [quem decide] | [data] |

### Premissas a Validar
| Premissa | Como validar | Status |
|----------|--------------|--------|
| [premissa] | [metodo] | Pendente/Validado |

---

## Historico de Versoes

| Versao | Data | Autor | Mudancas |
|--------|------|-------|----------|
| 1.0 | YYYY-MM-DD | [nome] | Versao inicial |
