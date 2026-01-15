---
description: Pesquisa de mercado e analise de concorrentes
argument-hint: <tema ou lista de concorrentes>
---

# /research - Pesquisa de Mercado e Concorrentes

Realiza pesquisa de mercado e analise competitiva usando o agente Researcher.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, perguntar o que pesquisar:
- Lista de concorrentes para analise competitiva
- Segmento de mercado para sizing (TAM/SAM/SOM)
- Tema para tendencias

## Pre-requisitos

Verificar se `.context/empresa.md` existe. Se nao existir, orientar a rodar `/setup` primeiro.

## O que fazer

### Para Analise de Concorrentes
1. Identificar concorrentes (da entrada ou pesquisar)
2. Para cada concorrente, coletar:
   - Dados basicos (fundacao, sede, tamanho)
   - Produto (features, precos, tecnologia)
   - Posicionamento (publico-alvo, diferenciais)
   - Presenca digital (reviews, notas, redes)
   - Analise critica (forcas, fraquezas)
3. Criar comparativo consolidado
4. Identificar gaps e oportunidades

### Para Market Sizing
1. Pesquisar TAM (Total Addressable Market)
2. Calcular SAM (Serviceable Addressable Market)
3. Estimar SOM (Serviceable Obtainable Market)
4. Documentar metodologia e fontes

### Para Tendencias
1. Identificar tendencias em alta
2. Mapear tendencias em declinio
3. Destacar tendencias emergentes

## Output

Criar arquivo com formato: `docs/research/{tema}-YYYY-MM-DD.md`

Para analise competitiva, tambem criar/atualizar: `.context/competidores-{projeto}.md`

## Estrutura do Output

```markdown
# [Titulo da Pesquisa]

**Data:** YYYY-MM-DD
**Analista:** /research
**Fontes:** [N] sites consultados

## Sumario Executivo
[Principais insights]

## [Conteudo especifico do tipo de pesquisa]

## Oportunidades Identificadas
## Recomendacoes
## Fontes Consultadas
```

## Proximos passos sugeridos

- `/discovery` - Pesquisa de usuarios
- `/prd <feature>` - Criar especificacao

## Exemplos

```
/research Eventbrite, Ingresse, Tickets For Fun
/research "plataformas de ticketing no Brasil"
/research sizing "SaaS de RH no Brasil"
/research trends "eventos hibridos"
```
