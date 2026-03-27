# ============================================================
# Play Insights - Database Cleanup Launcher
# PowerShell wrapper para executar o cleanup com as variaveis
# de ambiente carregadas do arquivo .env
#
# Este script e executado pelo Windows Task Scheduler
# ============================================================

param(
    [switch]$Verbose = $false
)

# Configuracoes
$ProjectDir = $PSScriptRoot | Split-Path -Parent
$EnvFile = Join-Path $ProjectDir ".env"
$ScriptPath = Join-Path $ProjectDir "scripts/cleanup_database.py"
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source

# Carregar variaveis de ambiente do .env
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^=;]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# Executar o script Python
if ($Verbose) {
    & $PythonExe $ScriptPath
} else {
    & $PythonExe $ScriptPath 2>&1 | Out-Null
}

exit $LASTEXITCODE
