---
description: Criar materiais de vendas e go-to-market
argument-hint: [gerar <tipo>] (opcional)
---

# /sales - Materiais de Vendas

Aciona o agente Sales-Enabler para criar materiais comerciais.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, apresentar catalogo e perguntar o que gerar.

## Pre-requisitos

- PRD ou specs definidos
- Analise competitiva (recomendado)
- Insights de discovery (recomendado)

## Catalogo de Materiais

**APRESENTACOES**
a) Sales Deck (empresa/produto/feature)
b) One-pager (problema->solucao->prova->CTA)
c) Pitch deck para investidores

**COMPETITIVO**
d) Battlecards por concorrente
e) Matriz comparativa de mercado
f) Playbooks taticos por concorrente

**VENDAS**
g) Playbook por etapa do funil
h) Talk tracks (roteiros por persona)
i) Scripts de discovery
j) Objection handling
k) Guia de demo

**COMUNICACAO**
l) Email templates
m) WhatsApp templates
n) Sequencias de nurturing

**CASES E PROVAS**
o) Case brief
p) ROI calculator

**CAPACITACAO**
q) Onboarding 30-60-90
r) FAQs e glossario

## O que fazer

1. **Apresentar catalogo** (se sem argumentos)
2. **Perguntar:**
   - Quais materiais priorizar?
   - Qual o objetivo?
   - Publico-alvo? (SDR, AE, CSM)
   - Mercado/persona foco?

3. **Coletar insumos necessarios**
   - Buscar PRD e posicionamento
   - Verificar analise competitiva
   - Coletar quotes de discovery

4. **Produzir material**
   - Usar estrutura padrao do tipo
   - Marcar [PLACEHOLDER] quando faltar dados
   - Versionar (v1.0)

## REGRAS CRITICAS

- NUNCA inventar dados de produto, precos, prazos ou SLAs
- Sempre solicitar fonte ou marcar como [PLACEHOLDER]
- Versionar toda entrega

## Output

Criar arquivos em `docs/sales/` com estrutura especifica do tipo.

## Exemplos

```
/sales
/sales gerar battlecard para Eventbrite
/sales gerar one-pager
/sales gerar playbook para etapa discovery
/sales gerar talk-track para Organizador Iniciante
```
