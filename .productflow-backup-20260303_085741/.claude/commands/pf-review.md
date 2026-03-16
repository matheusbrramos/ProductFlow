---
description: "Revisao de qualidade de artefatos ProductFlow"
argument-hint: "<artefato ou acao> (arquivo, consistency, gaps, ready)"
---

# /pf-review - Revisao de Qualidade

Aciona o agente Supervisor para revisar artefatos.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, perguntar o que revisar.

## Acoes Disponiveis

### /pf-review <arquivo>
Revisao completa de um artefato especifico.

**O que fazer:**
1. Ler o artefato
2. Aplicar checklist apropriado (PRD, story, battlecard, etc)
3. Verificar criterios: completude, clareza, evidencia, testabilidade, consistencia
4. Identificar issues por severidade
5. Sugerir correcoes especificas

### /pf-review consistency
Verifica consistencia entre todos os artefatos do projeto.

**O que fazer:**
1. Listar todos os artefatos existentes
2. Verificar alinhamento entre eles
3. Identificar contradicoes
4. Criar matriz de consistencia

### /pf-review gaps
Lista todos os gaps e pendencias.

**O que fazer:**
1. Verificar [PLACEHOLDER] nao resolvidos
2. Verificar [NEEDS CLARIFICATION] pendentes
3. Identificar informacoes faltantes
4. Listar por severidade

### /pf-review ready
Verifica se projeto esta pronto para aprovacao.

**O que fazer:**
1. Executar todos os checklists
2. Verificar bloqueadores criticos
3. Listar pendencias
4. Dar recomendacao final

## Criterios de Revisao

| Criterio | Pergunta |
|----------|----------|
| Completude | Falta alguma secao obrigatoria? |
| Clareza | Esta claro e sem ambiguidades? |
| Evidencia | Afirmacoes tem suporte? |
| Testabilidade | Requisitos sao verificaveis? |
| Consistencia | Alinha com outros artefatos? |
| Acionabilidade | Da para agir com base nisso? |

## Niveis de Severidade

- **Critico**: Bloqueia aprovacao - deve corrigir
- **Importante**: Impacta qualidade - recomenda correcao
- **Sugestao**: Melhoria opcional
- **Informativo**: Apenas registro

## Output

Criar arquivo: `docs/reviews/{feature}-review.md`

## Estrutura do Output

```markdown
# Revisao: [Nome do Artefato]

**Revisor:** /pf-review
**Data:** YYYY-MM-DD
**Versao Revisada:** vX.Y
**Status:** Aprovado | Aprovado com ressalvas | Requer correcoes

## Sumario
| Criterio | Status | Observacao |

**Score Geral:** [X]/10

## Pontos Positivos

## Issues Identificados
### Critico
### Importante
### Sugestao

## Pendencias

## Recomendacao
[ ] Aprovar como esta
[ ] Aprovar apos correcoes menores
[ ] Retornar para correcoes

**Proximos Passos:**
```

## Exemplos

```
/pf-review docs/prd/alertas.md
/pf-review consistency
/pf-review gaps
/pf-review ready
```
