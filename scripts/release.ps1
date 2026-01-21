# =============================================================================
# ProductFlow Release Script (Windows PowerShell)
# Gera um zip limpo a partir do git, sem arquivos de workspace ou sensíveis.
#
# Uso:
#   .\scripts\release.ps1 [versao]
#   .\scripts\release.ps1 3.2
#
# Requisitos:
#   - Git instalado e no PATH
#   - Executar na raiz do repositório
# =============================================================================

param(
    [string]$Version = (Get-Date -Format "yyyyMMdd")
)

$ErrorActionPreference = "Stop"

$OutputDir = "dist"
$OutputFile = "ProductFlow-v$Version.zip"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  ProductFlow Release Builder v3.2" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Versao: $Version"
Write-Host "Output: $OutputDir\$OutputFile"
Write-Host ""

# Verifica se estamos em um repo git
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Execute este script na raiz do repositorio git" -ForegroundColor Red
    Write-Host "      cd ProductFlow; .\scripts\release.ps1"
    exit 1
}

# Cria diretório de saída
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Verifica se ha mudancas nao commitadas
$status = git status --porcelain
if ($status) {
    Write-Host "AVISO: Ha mudancas nao commitadas. Considere commitar antes do release." -ForegroundColor Yellow
    $response = Read-Host "Continuar mesmo assim? (s/N)"
    if ($response -notmatch "^[Ss]$") {
        exit 1
    }
}

# Validação de segurança: verifica se settings.local.json está no .gitignore
$cached = git ls-files --cached | Select-String "settings.local.json"
if ($cached) {
    Write-Host "ERRO: settings.local.json esta versionado! Remova antes do release:" -ForegroundColor Red
    Write-Host "      git rm --cached .claude\settings.local.json"
    exit 1
}

# Cria o zip usando git archive
Write-Host "Criando arquivo $OutputFile..."
git archive --format=zip --prefix=ProductFlow/ HEAD -o "$OutputDir\$OutputFile"

# Mostra resultado
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Release criado com sucesso!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Caminho: $OutputDir\$OutputFile"

$size = (Get-Item "$OutputDir\$OutputFile").Length / 1KB
Write-Host "Tamanho: $([math]::Round($size, 2)) KB"
Write-Host ""

Write-Host "Arquivos incluidos (apenas rastreados pelo git):"
Write-Host "---------------------------------------------"
git archive --format=tar HEAD | tar -t 2>$null | Select-String -Pattern "\.(md|sh|ps1|py|json)$" | Select-Object -First 25

Write-Host "..."
Write-Host ""

# Validação
$hasSettings = git ls-files --cached | Select-String "settings.local.json"
$hasQuarantine = git ls-files --cached | Select-String ".quarantine"

Write-Host "Validacao:"
if ($hasSettings) {
    Write-Host "  - settings.local.json: INCLUSO (ERRO!)" -ForegroundColor Red
} else {
    Write-Host "  - settings.local.json: NAO incluso (OK)" -ForegroundColor Green
}

if ($hasQuarantine) {
    Write-Host "  - .quarantine/: INCLUSO (ERRO!)" -ForegroundColor Red
} else {
    Write-Host "  - .quarantine/: NAO incluso (OK)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Para verificar o conteudo completo:"
Write-Host "  Expand-Archive -Path '$OutputDir\$OutputFile' -DestinationPath temp -Force; Get-ChildItem temp -Recurse"
Write-Host ""
Write-Host "Para instalar a partir do release:"
Write-Host "  Expand-Archive '$OutputDir\$OutputFile' -DestinationPath . ; cd ProductFlow; .\install.ps1"
