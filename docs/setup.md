# ProductFlow - Guia de Setup

## Pré-requisitos

- **Claude Code CLI** instalado e configurado
- **Git** (opcional, mas recomendado)
- **Python 3.8+** (para scripts de validação)

## Instalação Rápida

### Linux/macOS
```bash
cd ProductFlow
./install.sh
```

### Windows
```powershell
cd ProductFlow
.\install.ps1
```

## Configuração do Claude Code

### 1. Criar settings.local.json

O ProductFlow usa um arquivo de configuração local para definir permissões do Claude Code.

```bash
# Copiar o template
cp .claude/settings.example.json .claude/settings.local.json
```

### 2. Ajustar Permissões

Edite `.claude/settings.local.json` conforme suas necessidades:

```json
{
  "permissions": {
    "allow": [
      "Skill(INIT)",
      "Bash(git status)",
      "Bash(git add:*)",
      "Bash(git commit:*)"
    ],
    "deny": []
  }
}
```

### 3. Permissões Disponíveis

| Permissão | Descrição | Risco |
|-----------|-----------|-------|
| `Skill(INIT)` | Permite inicializar skills | Baixo |
| `Bash(git status)` | Verificar status do repo | Baixo |
| `Bash(git diff:*)` | Ver diferenças | Baixo |
| `Bash(git add:*)` | Adicionar arquivos ao staging | Médio |
| `Bash(git commit:*)` | Criar commits | Médio |
| `Bash(git push:*)` | Enviar para remote | **Alto** |
| `Bash(python:*)` | Executar scripts Python | **Alto** |
| `Bash(pip install:*)` | Instalar pacotes Python | **Alto** |

**Recomendação de Segurança**: Use a allowlist mínima necessária para seu workflow.

## Estrutura de Diretórios

Após instalação, a estrutura deve ser:

```
ProductFlow/
├── .claude/
│   ├── agents/           # Subagents especializados
│   ├── commands/         # Slash commands
│   ├── settings.example.json  # Template (versionado)
│   └── settings.local.json    # Suas permissões (NÃO versionado)
├── .context/             # Contexto do seu projeto (criar empresa.md, etc)
├── .productflow/         # Runtime (snapshots, memória)
├── docs/
│   ├── briefings/        # Briefings dos agentes
│   ├── templates/        # Templates PRD/SDD
│   └── ...               # Seus documentos gerados
└── scripts/              # Scripts utilitários
```

## Primeiros Passos

1. **Criar contexto do projeto**:
   ```bash
   # Criar arquivo de contexto da empresa/projeto
   echo "# Contexto do Projeto" > .context/empresa.md
   ```

2. **Inicializar ProductFlow**:
   ```
   /pf-init
   ```

3. **Verificar instalação**:
   ```
   /pf-doctor
   ```

## Arquivos Sensíveis

### O que NÃO versionar:

| Arquivo | Motivo |
|---------|--------|
| `.claude/settings.local.json` | Contém permissões específicas do usuário |
| `.context/*` | Dados específicos do seu projeto |
| `.productflow/*` | Runtime e memória local |
| `docs/discovery/*`, `docs/prd/*`, etc | Documentos gerados do seu projeto |

### Verificar .gitignore

O `.gitignore` já está configurado para ignorar esses arquivos. Verifique com:

```bash
git status --ignored
```

## Troubleshooting

### "settings.local.json não encontrado"

```bash
cp .claude/settings.example.json .claude/settings.local.json
```

### "Permissão negada para comando X"

Adicione a permissão em `settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(comando:*)"
    ]
  }
}
```

### Validar instalação

```bash
python scripts/validate_productflow.py
```

ou use o comando:

```
/pf-doctor
```

## Referências

- [README.md](../README.md) - Documentação principal
- [CLAUDE.md](../CLAUDE.md) - Regras e princípios do ProductFlow
- [decisions.md](decisions.md) - Decisões de arquitetura (se existir)
