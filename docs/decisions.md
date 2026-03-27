# ProductFlow - Decisões de Arquitetura

Este documento registra decisões técnicas e de design tomadas durante o desenvolvimento e hardening do ProductFlow.

---

## ADR-001: Separação de settings.local.json do versionamento

**Data**: 2026-01-20
**Status**: Implementado
**Contexto**: O arquivo `settings.local.json` continha permissões específicas do usuário e estava sendo versionado.

**Decisão**:
- Mover `settings.local.json` para `.gitignore`
- Criar template `settings.example.json` com configuração mínima segura
- Documentar processo de setup em `docs/setup.md`

**Consequências**:
- (+) Usuários não expõem suas permissões locais
- (+) Cada usuário pode ter configuração diferente
- (-) Requer passo adicional de setup (copiar template)

---

## ADR-002: Diretório .quarantine/ para artefatos suspeitos

**Data**: 2026-01-20
**Status**: Implementado
**Contexto**: Artefatos como `tmpclaude-*`, arquivo `nul` e outros lixos precisavam ser removidos de forma segura.

**Decisão**:
- Criar diretório `.quarantine/` para mover artefatos antes de deletar
- Adicionar `.quarantine/` ao `.gitignore`
- Manter artefatos em quarentena até confirmação de que são lixo

**Consequências**:
- (+) Remoção segura e reversível
- (+) Permite análise antes de deleção definitiva
- (-) Ocupa espaço temporariamente

---

## ADR-003: Padronização de estrutura dos agentes

**Data**: 2026-01-20
**Status**: Implementado
**Contexto**: Agentes tinham estruturas inconsistentes, alguns sem front matter, outros sem seções obrigatórias.

**Decisão**:
- Padronizar front matter com campos obrigatórios: `name`, `description`, `tools`, `disallowedTools`
- Padronizar seções: `<ROLE>`, `<GOALS>`, `<INPUTS_REQUIRED>`, `<OUTPUTS>`, `<PROCESS>`, `<QUALITY_BAR>`, `<EDGE_CASES>`, `<HANDOFF>`
- Ordem das seções deve ser consistente em todos os agentes

**Consequências**:
- (+) Facilita manutenção e onboarding
- (+) Contratos claros entre agentes
- (+) Reduz ambiguidade

---

## ADR-004: Script de release com validação de segurança

**Data**: 2026-01-20
**Status**: Implementado
**Contexto**: Releases manuais podem incluir arquivos sensíveis ou lixo acidentalmente.

**Decisão**:
- Criar `scripts/release.sh` e `scripts/release.ps1`
- Script usa `git archive` para garantir apenas arquivos rastreados
- Validação automática de que `settings.local.json` não está incluído
- Output em diretório `dist/`

**Consequências**:
- (+) Releases consistentes e limpas
- (+) Validação automática de segurança
- (+) Cross-platform (bash + PowerShell)

---

## ADR-005: Comando pf-doctor para validação

**Data**: 2026-01-20
**Status**: Implementado
**Contexto**: Não havia forma automatizada de validar se a instalação está correta.

**Decisão**:
- Criar comando `/pf-doctor` que valida:
  - Presença de diretórios essenciais
  - settings.local.json não versionado
  - Ausência de artefatos de lixo
  - Consistência dos agentes (tools/disallowedTools, seções obrigatórias)
- Output com status: OK / WARN / FAIL

**Consequências**:
- (+) Diagnóstico rápido de problemas
- (+) Padronização de validação
- (+) Facilita troubleshooting

---

## ADR-006: Estrutura eval/ para testes de regressão

**Data**: 2026-01-20
**Status**: Implementado
**Contexto**: Não havia forma de validar se mudanças nos agentes/comandos quebram o fluxo esperado.

**Decisão**:
- Criar pasta `eval/` com:
  - `briefs/` - briefs de exemplo para teste
  - `expected/` - estrutura esperada de output
  - `rubric.md` - critérios de avaliação
  - `run-eval.sh` - script para executar avaliação

**Consequências**:
- (+) Baseline para testes de regressão
- (+) Documentação de comportamento esperado
- (-) Requer manutenção quando fluxo muda

---

## Template para novas decisões

```markdown
## ADR-XXX: [Título]

**Data**: YYYY-MM-DD
**Status**: Proposto | Implementado | Depreciado
**Contexto**: [Descrição do problema ou necessidade]

**Decisão**: [O que foi decidido]

**Consequências**:
- (+) [Benefício]
- (-) [Trade-off]
```
