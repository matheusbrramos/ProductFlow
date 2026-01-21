#!/usr/bin/env python3
"""
ProductFlow Doctor / Validator v3.2
Valida a estrutura, seguranca e consistencia do ProductFlow.

Uso:
    python scripts/validate_productflow.py [check]

Checks disponiveis:
    estrutura - Valida diretorios essenciais
    agentes   - Valida consistencia dos agentes
    comandos  - Valida consistencia dos comandos
    seguranca - Valida configuracoes de seguranca
    lixo      - Procura artefatos suspeitos
    all       - Executa todas as validacoes (default)

Verifica:
    - YAML frontmatter de todos commands e agents
    - Campos obrigatorios (description para commands, name e description para agents)
    - Conflitos com comandos built-in do Claude Code
    - Referencias a comandos inexistentes nos briefings/README
    - Seguranca (settings.local.json, .gitignore)
    - Artefatos de lixo (tmpclaude-*, nul, etc)
"""

import os
import re
import sys
import subprocess
from pathlib import Path

# Comandos built-in do Claude Code que devem ser evitados
BUILTIN_COMMANDS = {
    'init', 'review', 'status', 'help', 'clear', 'config',
    'compact', 'cost', 'doctor', 'login', 'logout', 'memory',
    'mcp', 'model', 'permissions', 'resume', 'terminal-setup',
    'vim', 'bug', 'ide', 'listen', 'pr-comments', 'remember'
}

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def add_error(self, msg):
        self.errors.append(f"ERRO: {msg}")

    def add_warning(self, msg):
        self.warnings.append(f"AVISO: {msg}")

    def add_info(self, msg):
        self.info.append(f"INFO: {msg}")

    @property
    def has_errors(self):
        return len(self.errors) > 0

    def print_results(self):
        print("\n" + "="*60)
        print("  RESULTADO DA VALIDACAO PRODUCTFLOW")
        print("="*60 + "\n")

        if self.errors:
            print("ERROS CRITICOS:")
            for e in self.errors:
                print(f"  [X] {e}")
            print()

        if self.warnings:
            print("AVISOS:")
            for w in self.warnings:
                print(f"  [!] {w}")
            print()

        if self.info:
            print("INFORMACOES:")
            for i in self.info:
                print(f"  [i] {i}")
            print()

        if not self.errors and not self.warnings:
            print("[OK] Todas as validacoes passaram!\n")
        elif self.errors:
            print(f"[FALHA] Validacao falhou com {len(self.errors)} erro(s)\n")
        else:
            print(f"[AVISO] Validacao passou com {len(self.warnings)} aviso(s)\n")


def parse_frontmatter(content):
    """Extrai o frontmatter YAML de um arquivo markdown."""
    if not content.startswith('---'):
        return None

    # Encontra o segundo ---
    end = content.find('---', 3)
    if end == -1:
        return None

    frontmatter_text = content[3:end].strip()

    # Parse simples de YAML (sem dependencia externa)
    result = {}
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Remove aspas
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            result[key] = value

    return result


def validate_commands(result):
    """Valida todos os arquivos em .claude/commands/"""
    commands_dir = Path('.claude/commands')

    if not commands_dir.exists():
        result.add_error(".claude/commands/ nao encontrado")
        return

    command_files = list(commands_dir.glob('*.md'))

    if not command_files:
        result.add_error("Nenhum comando encontrado em .claude/commands/")
        return

    result.add_info(f"Encontrados {len(command_files)} comandos")

    for cmd_file in command_files:
        # Nome do comando (sem .md)
        cmd_name = cmd_file.stem

        # Verifica conflito com built-ins
        if cmd_name in BUILTIN_COMMANDS:
            result.add_error(f"{cmd_file}: Conflito com comando built-in /{cmd_name}")

        # Le o conteudo
        try:
            content = cmd_file.read_text(encoding='utf-8')
        except Exception as e:
            result.add_error(f"{cmd_file}: Erro ao ler arquivo - {e}")
            continue

        # Valida frontmatter
        frontmatter = parse_frontmatter(content)

        if frontmatter is None:
            result.add_error(f"{cmd_file}: Frontmatter YAML ausente ou invalido")
            continue

        # Verifica campos obrigatorios
        if 'description' not in frontmatter or not frontmatter['description']:
            result.add_error(f"{cmd_file}: Campo 'description' ausente no frontmatter")

        # Verifica argument-hint (opcional, mas recomendado)
        if 'argument-hint' not in frontmatter:
            result.add_warning(f"{cmd_file}: Campo 'argument-hint' ausente (recomendado)")


def validate_agents(result):
    """Valida todos os arquivos em .claude/agents/"""
    agents_dir = Path('.claude/agents')

    if not agents_dir.exists():
        result.add_error(".claude/agents/ nao encontrado")
        return

    agent_files = list(agents_dir.glob('*.md'))

    if not agent_files:
        result.add_error("Nenhum agente encontrado em .claude/agents/")
        return

    result.add_info(f"Encontrados {len(agent_files)} agentes")

    for agent_file in agent_files:
        # Le o conteudo
        try:
            content = agent_file.read_text(encoding='utf-8')
        except Exception as e:
            result.add_error(f"{agent_file}: Erro ao ler arquivo - {e}")
            continue

        # Valida frontmatter
        frontmatter = parse_frontmatter(content)

        if frontmatter is None:
            result.add_error(f"{agent_file}: Frontmatter YAML ausente ou invalido")
            continue

        # Verifica campos obrigatorios para agents
        if 'name' not in frontmatter or not frontmatter['name']:
            result.add_error(f"{agent_file}: Campo 'name' ausente no frontmatter")

        if 'description' not in frontmatter or not frontmatter['description']:
            result.add_error(f"{agent_file}: Campo 'description' ausente no frontmatter")

        # Verifica se name eh lowercase com hifens
        if 'name' in frontmatter:
            name = frontmatter['name']
            if name != name.lower() or ' ' in name:
                result.add_warning(f"{agent_file}: 'name' deve ser lowercase com hifens: {name}")

        # Verifica contrato de escrita: agentes com disallowedTools Write/Edit nao devem prometer criar arquivos
        has_write_disabled = 'disallowedTools' in frontmatter or 'Write' in content.split('disallowedTools')[0] if 'disallowedTools' in content else False
        if 'disallowedTools' in content:
            disallowed_section = content.split('disallowedTools')[1].split('---')[0] if '---' in content.split('disallowedTools')[1] else content.split('disallowedTools')[1][:200]
            if 'Write' in disallowed_section or 'Edit' in disallowed_section:
                # Verifica se promete criar arquivos
                if 'Crio arquivos' in content or 'Crio o arquivo' in content:
                    result.add_warning(f"{agent_file}: Agente com Write/Edit bloqueado promete 'Crio arquivos' (use 'Entrego conteudo')")


def find_command_references(content):
    """Encontra todas as referencias a comandos (formato /comando) no conteudo."""
    # Pattern para /comando (excluindo paths como /docs/... ou ./scripts/)
    pattern = r'(?<![a-zA-Z0-9/.])/([a-zA-Z][a-zA-Z0-9-]*)\b'
    matches = re.findall(pattern, content)
    # Filtra paths comuns que nao sao comandos
    excluded = {'scripts', 'docs', 'claude', 'context', 'productflow', 'usr', 'bin', 'bash'}
    return {m for m in matches if m.lower() not in excluded}


def validate_references(result):
    """Verifica referencias a comandos inexistentes."""
    commands_dir = Path('.claude/commands')

    if not commands_dir.exists():
        return

    # Lista de comandos existentes
    existing_commands = {f.stem for f in commands_dir.glob('*.md')}

    # Adiciona comandos built-in validos
    valid_commands = existing_commands | BUILTIN_COMMANDS

    # Arquivos para verificar
    files_to_check = []

    # Briefings
    briefings_dir = Path('docs/briefings')
    if briefings_dir.exists():
        files_to_check.extend(briefings_dir.glob('*.md'))

    # README e CLAUDE.md
    if Path('README.md').exists():
        files_to_check.append(Path('README.md'))
    if Path('CLAUDE.md').exists():
        files_to_check.append(Path('CLAUDE.md'))

    # Commands (referencias internas)
    files_to_check.extend(commands_dir.glob('*.md'))

    for file_path in files_to_check:
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            continue

        refs = find_command_references(content)

        for ref in refs:
            if ref not in valid_commands:
                # Verifica se pode ser um comando antigo renomeado
                if ref in ['review', 'status', 'init']:
                    result.add_warning(f"{file_path}: Referencia a /{ref} (renomeado para /pf-{ref})")
                else:
                    result.add_warning(f"{file_path}: Referencia a comando inexistente /{ref}")


def validate_version(result):
    """Verifica se a versao esta consistente."""
    pf_init = Path('.claude/commands/pf-init.md')
    if pf_init.exists():
        content = pf_init.read_text(encoding='utf-8')
        if 'v3.2' not in content:
            result.add_warning("pf-init.md: Versao nao esta atualizada para v3.2")


def validate_security(result):
    """Valida configuracoes de seguranca."""
    # Verifica se settings.local.json esta no .gitignore
    gitignore = Path('.gitignore')
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8')
        if 'settings.local.json' not in content:
            result.add_error(".gitignore: settings.local.json nao esta listado")
        else:
            result.add_info("settings.local.json esta no .gitignore")

        if '.quarantine' not in content:
            result.add_warning(".gitignore: .quarantine/ nao esta listado")
    else:
        result.add_error(".gitignore nao encontrado")

    # Verifica se settings.local.json esta versionado (usando git)
    try:
        output = subprocess.run(
            ['git', 'ls-files', '--cached'],
            capture_output=True, text=True, timeout=5
        )
        if 'settings.local.json' in output.stdout:
            result.add_error("settings.local.json esta versionado! Use: git rm --cached .claude/settings.local.json")
        else:
            result.add_info("settings.local.json NAO esta versionado (OK)")
    except Exception:
        result.add_warning("Nao foi possivel verificar git ls-files")

    # Verifica se settings.example.json existe
    if not Path('.claude/settings.example.json').exists():
        result.add_warning("settings.example.json nao encontrado (recomendado criar template)")


def validate_trash(result):
    """Procura artefatos de lixo."""
    trash_patterns = [
        ('tmpclaude-*', 'Diretorios temporarios do Claude Code'),
        ('nul', 'Artefato de sistema Windows'),
        ('NUL', 'Artefato de sistema Windows'),
        ('__pycache__', 'Cache Python'),
        ('.DS_Store', 'Arquivo de sistema macOS'),
        ('Thumbs.db', 'Arquivo de sistema Windows'),
    ]

    found_trash = []

    # Procura no diretorio atual e subpastas
    for pattern, desc in trash_patterns:
        if '*' in pattern:
            matches = list(Path('.').glob(f'**/{pattern}'))
        else:
            matches = list(Path('.').glob(f'**/{pattern}'))

        for match in matches:
            # Ignora .quarantine e .git
            match_str = str(match)
            if '.quarantine' in match_str or '.git' in match_str:
                continue
            found_trash.append((match_str, desc))

    if found_trash:
        for path, desc in found_trash:
            result.add_warning(f"Lixo encontrado: {path} ({desc})")
    else:
        result.add_info("Nenhum artefato de lixo encontrado")


def validate_structure(result):
    """Valida a estrutura de pastas do projeto."""
    required_dirs = [
        '.claude/agents',
        '.claude/commands',
        '.context',
        'docs/briefings',
        'docs/templates',
        'docs/prd',
        'docs/sdd',
        'docs/stories',
        'docs/reviews',
        'docs/research',
        'docs/discovery',
        'docs/sales',
        '.productflow/snapshots',
        '.productflow/memory'
    ]

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            result.add_warning(f"Diretorio ausente: {dir_path}")


def main():
    """Funcao principal."""
    print("\n" + "="*60)
    print("  PRODUCTFLOW DOCTOR v3.2")
    print("="*60)

    # Parse argumentos
    check = 'all'
    if len(sys.argv) > 1:
        check = sys.argv[1].lower()

    valid_checks = ['estrutura', 'agentes', 'comandos', 'seguranca', 'lixo', 'all']
    if check not in valid_checks:
        print(f"\nCheck invalido: {check}")
        print(f"Checks disponiveis: {', '.join(valid_checks)}")
        sys.exit(1)

    result = ValidationResult()

    # Verifica se esta na raiz do projeto
    if not Path('.claude').exists():
        print("\nERRO: Execute este script na raiz do projeto ProductFlow")
        print("       (onde existe a pasta .claude/)")
        sys.exit(1)

    steps = []
    if check in ['all', 'comandos']:
        steps.append(("Validando comandos...", validate_commands))
    if check in ['all', 'agentes']:
        steps.append(("Validando agentes...", validate_agents))
    if check in ['all']:
        steps.append(("Validando referencias...", validate_references))
    if check in ['all', 'estrutura']:
        steps.append(("Validando estrutura...", validate_structure))
    if check in ['all']:
        steps.append(("Validando versao...", validate_version))
    if check in ['all', 'seguranca']:
        steps.append(("Validando seguranca...", validate_security))
    if check in ['all', 'lixo']:
        steps.append(("Procurando lixo...", validate_trash))

    for i, (msg, func) in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] {msg}")
        func(result)

    result.print_results()

    # Exit code
    sys.exit(1 if result.has_errors else 0)


if __name__ == '__main__':
    main()
