# ============================================================
# Play Insights - Agendador de Relatorio Semanal
# Windows Task Scheduler - toda segunda as 08:00
# ============================================================
#
# USO:
#   1. Abra o PowerShell como Administrador
#   2. Execute:
#      powershell -ExecutionPolicy Bypass -File scripts\setup_scheduler_windows.ps1
#
# Para remover a tarefa:
#   Unregister-ScheduledTask -TaskName "PlayInsights-WeeklyReport" -Confirm:$false
#
# Para ver o status:
#   Get-ScheduledTask -TaskName "PlayInsights-WeeklyReport"
# ============================================================

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------
# Configuracoes
# ---------------------------------------------------------------
$TaskName   = "PlayInsights-WeeklyReport"
$ProjectDir = $PSScriptRoot | Split-Path -Parent
$ScriptPath = Join-Path $ProjectDir "scripts\send_weekly_report.py"
$PythonExe  = (Get-Command python -ErrorAction SilentlyContinue).Source
$DayOfWeek  = "Monday"
$RunAt      = "08:00"

# ---------------------------------------------------------------
# Validacoes
# ---------------------------------------------------------------
if (-not $PythonExe) {
    Write-Error "Python nao encontrado no PATH. Instale e tente novamente."
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script nao encontrado: $ScriptPath"
    exit 1
}

$EnvFile = Join-Path $ProjectDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Error "Arquivo .env nao encontrado em: $EnvFile"
    exit 1
}

$EnvContent = Get-Content $EnvFile -Raw
$MissingVars = @()
foreach ($Var in @("SMTP_USER", "SMTP_APP_PASSWORD", "REPORT_RECIPIENTS")) {
    if ($EnvContent -notmatch "(?m)^${Var}=.+") {
        $MissingVars += $Var
    }
}
if ($MissingVars.Count -gt 0) {
    Write-Warning "Variaveis nao configuradas no .env:"
    $MissingVars | ForEach-Object { Write-Warning "  - $_" }
    $Continue = Read-Host "Deseja continuar mesmo assim? (s/N)"
    if ($Continue -ne "s" -and $Continue -ne "S") { exit 1 }
}

# ---------------------------------------------------------------
# Criar a tarefa agendada
# ---------------------------------------------------------------
Write-Host ""
Write-Host "Configurando tarefa agendada..."
Write-Host "  Nome:      $TaskName"
Write-Host "  Diretorio: $ProjectDir"
Write-Host "  Python:    $PythonExe"
Write-Host "  Script:    $ScriptPath"
Write-Host "  Agenda:    Todo $DayOfWeek as $RunAt"
Write-Host ""

$Existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "Removendo tarefa existente com mesmo nome..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument """$ScriptPath""" `
    -WorkingDirectory $ProjectDir

$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek $DayOfWeek `
    -At $RunAt

$TaskSettings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 15) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $TaskSettings `
    -Principal $Principal `
    -Description "Play Insights - relatorio semanal automatico" `
    | Out-Null

Write-Host ""
Write-Host "Tarefa agendada criada com sucesso!"
Write-Host ""
Write-Host "PROXIMOS PASSOS:"
Write-Host "  1. Teste sem enviar:"
Write-Host "     python scripts\send_weekly_report.py --dry-run"
Write-Host ""
Write-Host "  2. Teste com envio real:"
Write-Host "     python scripts\send_weekly_report.py"
Write-Host ""
Write-Host "  3. Para forcar execucao agora:"
Write-Host "     Start-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "  4. Para ver status e ultima execucao:"
Write-Host "     Get-ScheduledTaskInfo -TaskName $TaskName"
Write-Host ""
