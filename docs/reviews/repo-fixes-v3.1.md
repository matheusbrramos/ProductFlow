# ProductFlow v3.1 Repository Fixes

## Auditoria Baseline

### Warnings do Validador (17 total)

**Briefings com referencias quebradas:**
1. `helper.brief.md`: `/helper` (inexistente)
2. `researcher.brief.md`: `/trends`, `/researcher`, `/competitors`, `/sizing`, `/helper` (inexistentes)
3. `sales-enabler.brief.md`: `/sales-enabler` (inexistente)
4. `story-writer.brief.md`: `/story-writer`, `/strategist`, `/expand`, `/split`, `/map` (inexistentes)
5. `strategist.brief.md`: `/prioritize`, `/strategist`, `/spec` (inexistentes)
6. `supervisor.brief.md`: `/supervisor` (inexistente)

**Estrutura:**
- Diretorio ausente: `.context`

### Versao Inconsistente
- Nenhuma referencia a v3.0 encontrada (ja corrigido anteriormente)

---

## Correcoes Aplicadas

### PASSO 1: Briefings Corrigidos

| Arquivo | Problema | Solucao |
|---------|----------|---------|
| helper.brief.md | `/helper` | Removido titulo, mantido `/setup` |
| researcher.brief.md | `/trends`, `/competitors`, `/sizing`, `/researcher`, `/helper` | Documentado como modos do `/research` |
| strategist.brief.md | `/strategist`, `/spec`, `/prioritize` | Removido `/spec` e `/prioritize`, mantido `/prd` |
| story-writer.brief.md | `/story-writer`, `/strategist`, `/expand`, `/split`, `/map` | Documentado como tecnicas internas |
| sales-enabler.brief.md | `/sales-enabler` | Removido titulo, mantido `/sales` |
| supervisor.brief.md | `/supervisor` | Removido titulo, mantido `/pf-review` |

### PASSO 2: Contrato de Escrita Padronizado

- Agentes read-only nao prometem mais criar arquivos
- Documentado: "Slash commands criam arquivos, subagents geram conteudo"

### PASSO 3: Versao Padronizada

- Todas referencias agora usam v3.1

### PASSO 4: Estrutura Minima

- Criado `.context/.gitkeep`
- Ajustado `.gitignore` com excecao para `.gitkeep`

### PASSO 5: Subagent Architect

- Criado `.claude/agents/architect.md`
- Atualizado `/pf-spec` para referenciar o agente

### PASSO 6: Validador Melhorado

- Adicionada checagem de "Crio arquivos" em agentes read-only
- Adicionada checagem de versao em pf-init

### PASSO 7: Script de Release

- Criado `scripts/release.sh` usando `git archive`

---

## Resultado Final

```
python scripts/validate_productflow.py
# Esperado: 0 warnings, 0 errors
```
