# ProductFlow - Script de Instalacao Nao-Destrutiva (Windows PowerShell)
# Execute na pasta raiz do seu projeto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ProductFlow v3.1 - Instalacao" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Timestamp para backups
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = ".productflow-backup-$timestamp"

# URL do repositorio
$repoUrl = "https://github.com/matheusbrramos/ProductFlow/archive/refs/heads/main.zip"
$tempZip = "productflow-temp.zip"
$tempDir = "ProductFlow-main"

# Funcao para fazer backup
function Backup-IfExists {
    param([string]$path)
    if (Test-Path $path) {
        if (!(Test-Path $backupDir)) {
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        }
        Copy-Item -Path $path -Destination $backupDir -Recurse -Force
        Write-Host "  Backup criado: $backupDir\$(Split-Path $path -Leaf)" -ForegroundColor Yellow
    }
}

# Funcao para merge seguro de diretorio
function Safe-MergeDir {
    param([string]$src, [string]$dest)

    if (!(Test-Path $src)) { return }

    if (!(Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    }

    Get-ChildItem -Path $src -File | ForEach-Object {
        $destFile = Join-Path $dest $_.Name
        if (Test-Path $destFile) {
            Write-Host "  Arquivo existente preservado: $destFile" -ForegroundColor Yellow
            Copy-Item -Path $_.FullName -Destination "$destFile.new" -Force
        } else {
            Copy-Item -Path $_.FullName -Destination $dest -Force
        }
    }
}

Write-Host "Baixando ProductFlow..." -ForegroundColor Green

try {
    # Baixar ZIP
    Invoke-WebRequest -Uri $repoUrl -OutFile $tempZip

    # Extrair
    Expand-Archive -Path $tempZip -DestinationPath "." -Force

    # Verificar se ja existe .claude (instalacao anterior ou projeto existente)
    if (Test-Path ".claude") {
        Write-Host "AVISO: Pasta .claude ja existe!" -ForegroundColor Yellow
        Write-Host "Fazendo backup e merge seguro..." -ForegroundColor Yellow

        # Backup completo
        Backup-IfExists ".claude"

        # Merge seguro de agents
        Write-Host "Atualizando agents..." -ForegroundColor Green
        Safe-MergeDir "$tempDir\.claude\agents" ".claude\agents"

        # Merge seguro de commands
        Write-Host "Atualizando commands..." -ForegroundColor Green
        Safe-MergeDir "$tempDir\.claude\commands" ".claude\commands"
    } else {
        Write-Host "Instalando .claude/..." -ForegroundColor Green
        Copy-Item -Path "$tempDir\.claude" -Destination ".claude" -Recurse -Force
    }

    # CLAUDE.md - apenas se nao existir
    if (Test-Path "CLAUDE.md") {
        Write-Host "CLAUDE.md ja existe, mantendo versao atual" -ForegroundColor Yellow
        Copy-Item -Path "$tempDir\CLAUDE.md" -Destination "CLAUDE.md.new" -Force
        Write-Host "  Nova versao salva em CLAUDE.md.new para comparacao" -ForegroundColor Cyan
    } else {
        Copy-Item -Path "$tempDir\CLAUDE.md" -Destination "CLAUDE.md" -Force
    }

    # Criar estrutura de pastas (nunca sobrescreve existentes)
    Write-Host "Criando estrutura de pastas..." -ForegroundColor Green

    $pastas = @(
        ".context",
        "docs\briefings",
        "docs\templates",
        "docs\discovery",
        "docs\research",
        "docs\prd",
        "docs\sdd",
        "docs\stories",
        "docs\sales",
        "docs\reviews",
        ".productflow\snapshots",
        ".productflow\memory",
        "scripts"
    )

    foreach ($pasta in $pastas) {
        if (!(Test-Path $pasta)) {
            New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        }
    }

    # Copiar briefings e templates (merge seguro)
    if (Test-Path "$tempDir\docs\briefings") {
        Safe-MergeDir "$tempDir\docs\briefings" "docs\briefings"
    }
    if (Test-Path "$tempDir\docs\templates") {
        Safe-MergeDir "$tempDir\docs\templates" "docs\templates"
    }

    # Copiar validador
    if (Test-Path "$tempDir\scripts\validate_productflow.py") {
        Copy-Item -Path "$tempDir\scripts\validate_productflow.py" -Destination "scripts\" -Force
    }

    # Limpar temporarios
    Remove-Item -Path $tempZip -Force
    Remove-Item -Path $tempDir -Recurse -Force

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ProductFlow instalado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""

    if (Test-Path $backupDir) {
        Write-Host "Backup criado em: $backupDir" -ForegroundColor Yellow
        Write-Host ""
    }

    Write-Host "Estrutura criada:" -ForegroundColor Cyan
    Write-Host "  .claude/agents/     - 7 subagents especializados"
    Write-Host "  .claude/commands/   - 10 slash commands"
    Write-Host "  .context/           - Contexto do projeto"
    Write-Host "  docs/               - Artefatos de trabalho"
    Write-Host "  docs/sdd/           - Software Design Documents"
    Write-Host "  .productflow/       - Estado interno"
    Write-Host "  scripts/            - Utilitarios"
    Write-Host "  CLAUDE.md           - Regras globais"
    Write-Host ""
    Write-Host "Slash Commands disponiveis:" -ForegroundColor Cyan
    Write-Host "  /setup       - Iniciar contexto"
    Write-Host "  /research    - Pesquisa de mercado"
    Write-Host "  /discovery   - Analise de usuarios"
    Write-Host "  /prd         - Criar PRD"
    Write-Host "  /pf-spec     - Criar SDD"
    Write-Host "  /stories     - User stories"
    Write-Host "  /sales       - Materiais de vendas"
    Write-Host "  /pf-review   - Revisao de qualidade"
    Write-Host "  /pf-status   - Status do projeto"
    Write-Host "  /pf-init     - Ajuda rapida"
    Write-Host ""
    Write-Host "Para validar a instalacao:" -ForegroundColor Cyan
    Write-Host "  python scripts\validate_productflow.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Para comecar, abra o Claude Code e execute:" -ForegroundColor Yellow
    Write-Host "  /setup www.suaempresa.com.br" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "Erro durante instalacao: $_" -ForegroundColor Red

    # Limpar em caso de erro
    if (Test-Path $tempZip) { Remove-Item -Path $tempZip -Force }
    if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force }
}
