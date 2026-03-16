---
description: "Analise de usuarios, entrevistas, OST e JTBD"
argument-hint: "<acao> [dados] (analyze, interview, ost, jtbd, synthesize)"
---

# /discovery - Analise de Usuarios

Realiza pesquisa qualitativa de usuarios usando o agente Discovery.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, perguntar:
- Qual acao deseja? (analyze, interview, ost, jtbd, synthesize)
- Quais dados ou contexto fornecer?

## Pre-requisitos

Verificar se `.context/empresa.md` existe. Se nao existir, orientar a rodar `/setup` primeiro.

## Acoes Disponiveis

### analyze <dados>
Analisa transcricoes de entrevistas, surveys ou dados qualitativos.

**O que fazer:**
1. Processar dados fornecidos
2. Extrair quotes relevantes
3. Identificar padroes (critico, importante, relevante)
4. Mapear Jobs-to-be-Done
5. Sugerir oportunidades

### interview <perfil>
Prepara guia de entrevista para um perfil especifico.

**O que fazer:**
1. Definir objetivo da entrevista
2. Criar estrutura (abertura, contexto, experiencia, momento critico)
3. Incluir dicas de conducao
4. Gerar perguntas no formato correto (comportamento, nao hipotetico)

### ost <outcome>
Cria ou atualiza Opportunity Solution Tree.

**O que fazer:**
1. Definir outcome de negocio
2. Mapear oportunidades dos usuarios
3. Listar solucoes por oportunidade
4. Sugerir experimentos de validacao

### jtbd <contexto>
Mapeia Jobs-to-be-Done de um segmento.

**O que fazer:**
1. Identificar job principal
2. Mapear jobs secundarios
3. Usar formato: QUANDO [situacao] QUERO [motivacao] PARA QUE [resultado]

### synthesize
Consolida todos os insights de discovery em um documento.

## Output

Criar arquivo com formato: `docs/discovery/{tema}-YYYY-MM-DD.md`

## Estrutura do Output

```markdown
# Analise de Discovery - [Tema]

**Data:** YYYY-MM-DD
**Entrevistas:** N
**Perfil:** [descricao]

## Jobs-to-be-Done
### Job Principal
### Jobs Relacionados

## Padroes Identificados
### Critico (N/N mencionaram)
### Importante (N/N mencionaram)
### Relevante (N/N mencionaram)

## Oportunidades
## Recomendacoes
## Anexo: Quotes
```

## Proximos passos sugeridos

- `/prd <feature>` - Criar especificacao
- `/research` - Complementar com pesquisa de mercado

## Exemplos

```
/discovery analyze [transcricoes]
/discovery interview "organizadores que fizeram so 1 evento"
/discovery ost "aumentar retencao de 30% para 45%"
/discovery jtbd "organizadores de eventos corporativos"
/discovery synthesize
```
