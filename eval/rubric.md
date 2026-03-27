# ProductFlow - Rubrica de Avaliacao

## Visao Geral

Esta rubrica define os criterios para avaliar a qualidade dos artefatos gerados pelo ProductFlow. Cada criterio e avaliado em uma escala de 0-3.

## Escala de Pontuacao

| Pontuacao | Significado |
|-----------|-------------|
| 0 | Ausente ou completamente inadequado |
| 1 | Presente mas com problemas significativos |
| 2 | Adequado com pequenas melhorias necessarias |
| 3 | Excelente, sem melhorias necessarias |

---

## 1. CLAREZA (25%)

### 1.1 Linguagem
- Texto claro e sem ambiguidades
- Termos tecnicos explicados quando necessario
- Estrutura logica e facil de seguir

### 1.2 Formatacao
- Uso adequado de headers, listas, tabelas
- Consistencia de estilo entre documentos
- Informacoes faceis de localizar

### 1.3 Objetividade
- Foco no essencial
- Sem repeticoes desnecessarias
- Conclusoes diretas

**Perguntas de Avaliacao:**
- Um novo membro da equipe entenderia sem explicacoes adicionais?
- E possivel agir com base apenas neste documento?
- Ha ambiguidades que precisam ser esclarecidas?

---

## 2. COMPLETUDE (25%)

### 2.1 Cobertura de Requisitos
- Todos os requisitos do brief estao cobertos
- Nenhum requisito critico foi omitido
- Edge cases considerados

### 2.2 Estrutura
- Todas as secoes obrigatorias presentes
- Campos preenchidos (nao apenas placeholders)
- [NEEDS CLARIFICATION] usado quando apropriado

### 2.3 Rastreabilidade
- Requisitos conectados a evidencias
- Stories conectadas ao PRD
- Referencias cruzadas entre documentos

**Perguntas de Avaliacao:**
- Algum requisito do brief foi ignorado?
- Ha secoes vazias ou com apenas placeholders?
- E possivel rastrear cada decisao ate sua origem?

---

## 3. TESTABILIDADE (25%)

### 3.1 Metricas
- Criterios de sucesso mensuráveis
- Thresholds especificos (nao vagos)
- Baseline e meta definidos

### 3.2 Acceptance Criteria
- Formato Gherkin valido
- Cenarios verificaveis
- Edge cases cobertos

### 3.3 Definition of Done
- Criterios claros de conclusao
- Verificacoes possiveis de automatizar
- Sem subjetividade

**Perguntas de Avaliacao:**
- E possivel escrever testes automatizados a partir das specs?
- Duas pessoas diferentes chegariam a mesma conclusao sobre "passou/falhou"?
- Os criterios de sucesso podem ser medidos objetivamente?

---

## 4. CONSISTENCIA (25%)

### 4.1 Interna
- Sem contradicoes dentro do mesmo documento
- Terminologia consistente
- Numeros e dados alinhados

### 4.2 Entre Documentos
- PRD alinha com Discovery
- Stories refletem o PRD
- Battlecards consistentes com pesquisa

### 4.3 Com o Brief
- Restricoes do brief respeitadas
- Metricas do brief incorporadas
- Escopo nao excede o solicitado

**Perguntas de Avaliacao:**
- Ha contradicoes entre documentos?
- Os numeros batem em todos os lugares?
- O escopo respeita as restricoes do brief?

---

## Matriz de Avaliacao por Artefato

### Contexto (.context/empresa.md)

| Criterio | Peso | Descricao |
|----------|------|-----------|
| Dados basicos completos | 20% | Nome, site, segmento, tamanho |
| Projeto definido | 30% | Problema, objetivo, restricoes |
| Fontes documentadas | 20% | URLs e datas de consulta |
| Stakeholders identificados | 15% | Quem decide, quem usa |
| Criterios de sucesso | 15% | Metricas claras |

### Pesquisa (docs/research/)

| Criterio | Peso | Descricao |
|----------|------|-----------|
| Cobertura de concorrentes | 25% | Todos os listados analisados |
| Profundidade da analise | 25% | Features, precos, diferenciais |
| Fontes verificaveis | 20% | URLs, datas |
| Insights acionaveis | 15% | Oportunidades claras |
| Comparativo util | 15% | Tabela comparativa |

### PRD (docs/prd/)

| Criterio | Peso | Descricao |
|----------|------|-----------|
| Problema e evidencias | 20% | Bem fundamentado |
| Requisitos funcionais | 25% | Completos e testaveis |
| Requisitos nao-funcionais | 15% | Performance, seguranca, etc |
| Escopo claro | 20% | In/out definidos |
| Metricas de sucesso | 20% | Mensuraveis e com threshold |

### Stories (docs/stories/)

| Criterio | Peso | Descricao |
|----------|------|-----------|
| Cobertura do PRD | 25% | Todos os requisitos mapeados |
| Formato INVEST | 20% | Independentes, estimaveis, etc |
| Gherkin valido | 25% | Cenarios corretos |
| Edge cases | 15% | Excecoes cobertas |
| Rastreabilidade | 15% | Links para requisitos |

### Review (docs/reviews/)

| Criterio | Peso | Descricao |
|----------|------|-----------|
| Checklist aplicado | 30% | Todos os criterios verificados |
| Issues classificados | 25% | Severidade correta |
| Sugestoes especificas | 25% | Acoes claras |
| Recomendacao fundamentada | 20% | Decisao justificada |

---

## Calculo de Score Final

```
Score = (Clareza * 0.25) + (Completude * 0.25) + (Testabilidade * 0.25) + (Consistencia * 0.25)
```

### Interpretacao do Score

| Score | Classificacao | Acao |
|-------|---------------|------|
| 2.5 - 3.0 | Excelente | Pronto para uso |
| 2.0 - 2.4 | Bom | Pequenos ajustes |
| 1.5 - 1.9 | Adequado | Revisao necessaria |
| 1.0 - 1.4 | Insuficiente | Refazer partes |
| 0.0 - 0.9 | Inadequado | Refazer completamente |

---

## Checklist Rapido

### Antes de Aprovar

- [ ] Brief foi completamente atendido?
- [ ] Restricoes foram respeitadas?
- [ ] Metricas estao mensuraveis?
- [ ] Nao ha contradicoes entre docs?
- [ ] Stories tem acceptance criteria?
- [ ] [NEEDS CLARIFICATION] foram resolvidos?
- [ ] Fontes estao documentadas?

### Red Flags (Reprova Automatica)

- [ ] Requisitos regulatorios ignorados (LGPD, BACEN, etc)
- [ ] Metricas sem threshold especifico
- [ ] Stories sem Gherkin
- [ ] Contradicoes criticas entre documentos
- [ ] Escopo excede restricoes do brief
- [ ] Dados inventados em battlecards
