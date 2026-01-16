---
description: "Mostrar status atual do projeto ProductFlow e artefatos criados"
argument-hint: "[agente ou artefato] (opcional)"
---

# /pf-status - Status do Projeto

Mostra o status atual do projeto e artefatos criados.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento, mostrar status geral.
Se argumento fornecido, mostrar status especifico.

## O que fazer

1. **Verificar existencia dos arquivos de contexto**
   - `.context/empresa.md`
   - `.context/competidores-*.md`

2. **Verificar artefatos em cada fase**
   - `docs/research/` - Pesquisas de mercado
   - `docs/discovery/` - Analises de usuarios
   - `docs/prd/` - PRDs e specs
   - `docs/stories/` - User stories
   - `docs/sales/` - Materiais de vendas
   - `docs/reviews/` - Revisoes

3. **Identificar pendencias**
   - [PLACEHOLDER] nao resolvidos
   - [NEEDS CLARIFICATION] pendentes
   - Proximas etapas sugeridas

## Output

Exibir status no formato:

```
STATUS DO PROJETO - [Nome]

CONTEXTO
[x] .context/empresa.md
[ ] .context/competidores-{projeto}.md

PESQUISA
[ ] Concorrentes mapeados
[ ] Market sizing
[ ] Tendencias

DISCOVERY
[ ] Entrevistas analisadas
[ ] OST criada
[ ] JTBD mapeados

ESPECIFICACAO
[ ] PRD criado
[ ] User stories
[ ] Requisitos detalhados

SALES ENABLEMENT
[ ] Battlecards
[ ] Materiais de vendas

REVISAO
[ ] Consistencia verificada
[ ] Gaps resolvidos
[ ] Aprovado para proxima fase

PENDENCIAS
- [Lista de itens pendentes]

PROXIMO PASSO SUGERIDO
- [Recomendacao baseada no estado atual]
```

## Variacoes

### /pf-status discovery
Mostrar apenas status da fase de discovery.

### /pf-status prd
Mostrar apenas status de PRDs.

### /pf-status <arquivo>
Mostrar status de um artefato especifico.

## Exemplos

```
/pf-status
/pf-status discovery
/pf-status prd
/pf-status docs/prd/alertas.md
```
