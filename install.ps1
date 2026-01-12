# ProductFlow - Script de Instalação (Windows PowerShell)
# Execute na pasta raiz do seu projeto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ProductFlow - Instalação" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se já existe .claude
if (Test-Path ".claude") {
    Write-Host "AVISO: Pasta .claude já existe!" -ForegroundColor Yellow
    $resposta = Read-Host "Deseja sobrescrever? (s/n)"
    if ($resposta -ne "s") {
        Write-Host "Instalação cancelada." -ForegroundColor Red
        exit
    }
    Remove-Item -Recurse -Force ".claude"
}

# URL do repositório (substitua pelo seu)
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
    Copy-Item -Path "$tempDir\CLAUDE.md" -Destination "CLAUDE.md" -Force

    # Criar estrutura de pastas
    Write-Host "Criando estrutura de pastas..." -ForegroundColor Green

    $pastas = @(
        ".context",
        "docs\discovery",
        "docs\research",
        "docs\planning\stories",
        "docs\sales\battlecards",
        "docs\sales\playbooks",
        "docs\sales\templates",
        "docs\reviews",
        ".productflow\snapshots",
        ".productflow\memory"
    )

    foreach ($pasta in $pastas) {
        if (!(Test-Path $pasta)) {
            New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        }
    }

    # Limpar temporários
    Remove-Item -Path $tempZip -Force
    Remove-Item -Path $tempDir -Recurse -Force

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ProductFlow instalado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Estrutura criada:" -ForegroundColor Cyan
    Write-Host "  .claude/commands/agents/    - 6 agentes especializados"
    Write-Host "  .claude/commands/quick/     - Comandos rápidos"
    Write-Host "  .context/                   - Contexto do projeto"
    Write-Host "  docs/                       - Documentação gerada"
    Write-Host "  CLAUDE.md                   - Regras globais"
    Write-Host ""
    Write-Host "Para começar, abra o Claude Code e execute:" -ForegroundColor Yellow
    Write-Host "  @helper /setup www.suaempresa.com.br" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "Erro durante instalação: $_" -ForegroundColor Red

    # Limpar em caso de erro
    if (Test-Path $tempZip) { Remove-Item -Path $tempZip -Force }
    if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force }
}
