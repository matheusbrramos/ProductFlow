# ProductFlow - Script de Instalacao (Windows PowerShell)
# Execute na pasta raiz do seu projeto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ProductFlow v3.0 - Instalacao" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se ja existe .claude
if (Test-Path ".claude") {
    Write-Host "AVISO: Pasta .claude ja existe!" -ForegroundColor Yellow
    $resposta = Read-Host "Deseja sobrescrever? (s/n)"
    if ($resposta -ne "s") {
        Write-Host "Instalacao cancelada." -ForegroundColor Red
        exit
    }
    Remove-Item -Recurse -Force ".claude"
}

# URL do repositorio
$repoUrl = "https://github.com/matheusbrramos/ProductFlow/archive/refs/heads/main.zip"
$tempZip = "productflow-temp.zip"
$tempDir = "ProductFlow-main"

Write-Host "Baixando ProductFlow..." -ForegroundColor Green

try {
    # Baixar ZIP
    Invoke-WebRequest -Uri $repoUrl -OutFile $tempZip

    # Extrair
    Expand-Archive -Path $tempZip -DestinationPath "." -Force

    # Copiar arquivos
    Write-Host "Copiando arquivos..." -ForegroundColor Green

    Copy-Item -Path "$tempDir\.claude" -Destination ".claude" -Recurse -Force

    # Copiar CLAUDE.md apenas se nao existir
    if (!(Test-Path "CLAUDE.md")) {
        Copy-Item -Path "$tempDir\CLAUDE.md" -Destination "CLAUDE.md" -Force
    } else {
        Write-Host "CLAUDE.md ja existe, mantendo versao atual" -ForegroundColor Yellow
    }

    # Criar estrutura de pastas
    Write-Host "Criando estrutura de pastas..." -ForegroundColor Green

    $pastas = @(
        ".context",
        "docs\briefings",
        "docs\templates",
        "docs\discovery",
        "docs\research",
        "docs\prd",
        "docs\stories",
        "docs\sales",
        "docs\reviews",
        ".productflow\snapshots",
        ".productflow\memory"
    )

    foreach ($pasta in $pastas) {
        if (!(Test-Path $pasta)) {
            New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        }
    }

    # Copiar briefings e templates se existirem
    if (Test-Path "$tempDir\docs\briefings") {
        Copy-Item -Path "$tempDir\docs\briefings\*" -Destination "docs\briefings\" -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path "$tempDir\docs\templates") {
        Copy-Item -Path "$tempDir\docs\templates\*" -Destination "docs\templates\" -Force -ErrorAction SilentlyContinue
    }

    # Limpar temporarios
    Remove-Item -Path $tempZip -Force
    Remove-Item -Path $tempDir -Recurse -Force

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ProductFlow instalado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Estrutura criada:" -ForegroundColor Cyan
    Write-Host "  .claude/agents/     - 7 subagents especializados"
    Write-Host "  .claude/commands/   - 8 slash commands"
    Write-Host "  .context/           - Contexto do projeto"
    Write-Host "  docs/               - Artefatos de trabalho"
    Write-Host "  .productflow/       - Estado interno"
    Write-Host "  CLAUDE.md           - Regras globais"
    Write-Host ""
    Write-Host "Slash Commands disponiveis:" -ForegroundColor Cyan
    Write-Host "  /setup     - Iniciar contexto"
    Write-Host "  /research  - Pesquisa de mercado"
    Write-Host "  /discovery - Analise de usuarios"
    Write-Host "  /prd       - Criar PRD"
    Write-Host "  /stories   - User stories"
    Write-Host "  /sales     - Materiais de vendas"
    Write-Host "  /review    - Revisao de qualidade"
    Write-Host "  /status    - Status do projeto"
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
