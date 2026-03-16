---
description: "Validar instalacao e consistencia do ProductFlow"
argument-hint: "[check] (opcional: estrutura, agentes, comandos, seguranca, all)"
---

# /pf-doctor - Validador do ProductFlow

Valida a instalacao, estrutura e consistencia do ProductFlow. Identifica problemas e sugere correcoes.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento, executar validacao completa (`all`).

## Checks Disponiveis

### /pf-doctor estrutura
Valida presenca de diretorios e arquivos essenciais.

### /pf-doctor agentes
Valida consistencia dos agentes (.claude/agents/).

### /pf-doctor comandos
Valida consistencia dos comandos (.claude/commands/).

### /pf-doctor seguranca
Valida configuracoes de seguranca.

### /pf-doctor all
Executa todas as validacoes.

## O que validar

### 1. ESTRUTURA (Diretorios Essenciais)

Verificar existencia de:

```
[REQUIRED]
- .claude/
- .claude/agents/
- .claude/commands/
- .context/
- docs/
- docs/templates/
- docs/briefings/
- scripts/

[OPTIONAL - com .gitkeep]
- docs/discovery/
- docs/research/
- docs/prd/
- docs/sdd/
- docs/stories/
- docs/sales/
- docs/reviews/
- .productflow/
```

### 2. SEGURANCA

Verificar:

```
[CRITICAL]
- settings.local.json NAO deve estar versionado (git ls-files)
- settings.local.json deve estar no .gitignore
- .quarantine/ deve estar no .gitignore

[WARNING]
- tmpclaude-* diretorios presentes
- arquivo "nul" presente
- Outros artefatos de sistema
```

### 3. AGENTES (Consistencia)

Para cada agente em .claude/agents/:

```
[REQUIRED - Front Matter]
- name: presente
- description: presente
- tools: lista definida
- disallowedTools: lista definida (pode ser vazia)
- model: definido

[REQUIRED - Secoes]
- <ROLE>
- <GOALS>
- <INPUTS_REQUIRED>
- <PROCESS>
- <OUTPUTS>
- <QUALITY_BAR>
- <EDGE_CASES>
- <HANDOFF>
```

### 4. COMANDOS (Consistencia)

Para cada comando em .claude/commands/:

```
[REQUIRED - Front Matter]
- description: presente
- argument-hint: presente

[REQUIRED - Secoes]
- ## Entrada (com $ARGUMENTS)
- ## O que fazer
- ## Output
- ## Exemplos
```

### 5. LIXO (Artefatos Suspeitos)

Procurar e listar:

```
[SHOULD NOT EXIST]
- tmpclaude-*-cwd/ (qualquer nivel)
- arquivo "nul" ou "NUL"
- .DS_Store (no root)
- Thumbs.db (no root)
- __pycache__/ (em qualquer nivel)
```

## Output

Exibir relatorio no formato:

```
==================================================
  PRODUCTFLOW DOCTOR - Relatorio de Validacao
==================================================

[ESTRUTURA]
  [OK] .claude/ existe
  [OK] .claude/agents/ existe (7 arquivos)
  [OK] .claude/commands/ existe (11 arquivos)
  [WARN] docs/sdd/ nao existe (criar com .gitkeep)
  ...

[SEGURANCA]
  [OK] settings.local.json no .gitignore
  [OK] settings.local.json NAO versionado
  [FAIL] .quarantine/ nao esta no .gitignore
  ...

[AGENTES]
  [OK] helper.md - estrutura completa
  [WARN] researcher.md - faltando secao <EDGE_CASES>
  [FAIL] supervisor.md - tools: nao definido
  ...

[COMANDOS]
  [OK] setup.md - estrutura completa
  [WARN] prd.md - faltando secao "## Exemplos"
  ...

[LIXO]
  [OK] Nenhum tmpclaude-* encontrado
  [FAIL] Arquivo "nul" encontrado na raiz
  [WARN] 3 diretorios __pycache__/ encontrados
  ...

==================================================
  SUMARIO
==================================================

  Total de checks: 45
  OK: 38
  WARN: 5
  FAIL: 2

  Status geral: REQUER CORRECOES

==================================================
  ACOES RECOMENDADAS
==================================================

  1. [FAIL] Adicionar .quarantine/ ao .gitignore
  2. [FAIL] Remover arquivo "nul" da raiz
  3. [WARN] Criar docs/sdd/.gitkeep
  4. [WARN] Adicionar secao <EDGE_CASES> ao researcher.md
  5. [WARN] Limpar diretorios __pycache__/

==================================================
```

## Niveis de Status

| Status | Significado | Acao |
|--------|-------------|------|
| `[OK]` | Check passou | Nenhuma |
| `[WARN]` | Problema menor | Recomenda correcao |
| `[FAIL]` | Problema critico | Deve corrigir |

## Status Geral

- **SAUDAVEL**: Todos OK, nenhum WARN ou FAIL
- **ATENCAO**: Alguns WARNs, nenhum FAIL
- **REQUER CORRECOES**: Pelo menos 1 FAIL

## Exemplos

```
/pf-doctor
/pf-doctor all
/pf-doctor estrutura
/pf-doctor agentes
/pf-doctor seguranca
```

## Script Equivalente

Para rodar validacao sem Claude Code:

```bash
python scripts/validate_productflow.py
```
